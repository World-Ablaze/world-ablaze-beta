"""
Landmass data generator for World Ablaze AI.

Identifies connected landmasses using flood-fill algorithm on province
adjacency data. Generates province-to-landmass and state-to-landmass mappings.
"""

import re
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from core import parse_definition_for_land_provinces
from map_generators.base import BaseMapGenerator, GeneratorConfig


def parse_province_connections(path: Path, logger) -> Dict[int, Set[int]]:
    """
    Parse the generated province connections file.

    Args:
        path: Path to WA_AI_MAP_province_connections.txt.
        logger: Logger instance.

    Returns:
        Dictionary mapping province IDs to sets of neighbor province IDs.
    """
    adjacencies: Dict[int, Set[int]] = defaultdict(set)

    pattern = re.compile(
        r"add_to_array\s*=\s*\{\s*global\.WA_AI_MAP_province_connections_(\d+)\s*=\s*(\d+)\s*\}"
    )

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            match = pattern.search(line)
            if match:
                province = int(match.group(1))
                neighbor = int(match.group(2))
                adjacencies[province].add(neighbor)
                adjacencies[neighbor].add(province)

    logger.info(f"Parsed {len(adjacencies)} provinces with connections")
    return adjacencies


def parse_state_provinces(
    path: Path, logger
) -> Tuple[Dict[int, List[int]], Dict[int, int]]:
    """
    Parse the generated state provinces file.

    Args:
        path: Path to WA_AI_MAP_state_provinces.txt.
        logger: Logger instance.

    Returns:
        Tuple of (state_to_provinces, province_to_state) dictionaries.
    """
    state_to_provinces: Dict[int, List[int]] = defaultdict(list)
    province_to_state: Dict[int, int] = {}

    state_pattern = re.compile(
        r"add_to_array\s*=\s*\{\s*global\.WA_AI_MAP_state_province_ids@(\d+)\s*=\s*(\d+)\s*\}"
    )
    prov_pattern = re.compile(
        r"set_variable\s*=\s*\{\s*global\.WA_AI_MAP_province_state_id\^(\d+)\s*=\s*(\d+)\s*\}"
    )

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            state_match = state_pattern.search(line)
            if state_match:
                state_id = int(state_match.group(1))
                province_id = int(state_match.group(2))
                state_to_provinces[state_id].append(province_id)
                continue

            prov_match = prov_pattern.search(line)
            if prov_match:
                province_id = int(prov_match.group(1))
                state_id = int(prov_match.group(2))
                province_to_state[province_id] = state_id

    logger.info(
        f"Parsed {len(state_to_provinces)} states with {len(province_to_state)} provinces"
    )
    return dict(state_to_provinces), province_to_state


def flood_fill_landmasses(
    adjacencies: Dict[int, Set[int]],
    land_provinces: Set[int],
    logger,
) -> Dict[int, int]:
    """
    Identify landmasses using flood-fill algorithm.

    Args:
        adjacencies: Province adjacency map.
        land_provinces: Set of land province IDs.
        logger: Logger instance.

    Returns:
        Dictionary mapping province IDs to landmass IDs.
    """
    province_to_landmass: Dict[int, int] = {}
    current_landmass = 0

    # Filter to land-only connections
    land_adjacencies: Dict[int, Set[int]] = {}
    for province in land_provinces:
        if province in adjacencies:
            land_neighbors = adjacencies[province] & land_provinces
            if land_neighbors:
                land_adjacencies[province] = land_neighbors

    logger.info(f"Filtered to {len(land_adjacencies)} land provinces with land neighbors")

    all_land = land_provinces.copy()

    for start_province in sorted(all_land):
        if start_province in province_to_landmass:
            continue

        # New landmass found - flood fill
        current_landmass += 1
        queue = deque([start_province])
        province_to_landmass[start_province] = current_landmass

        while queue:
            province = queue.popleft()
            neighbors = land_adjacencies.get(province, set())

            for neighbor in neighbors:
                if neighbor not in province_to_landmass:
                    province_to_landmass[neighbor] = current_landmass
                    queue.append(neighbor)

    logger.info(
        f"Identified {current_landmass} landmasses across {len(province_to_landmass)} provinces"
    )
    return province_to_landmass


def compute_state_landmasses(
    province_to_landmass: Dict[int, int],
    state_to_provinces: Dict[int, List[int]],
    logger,
) -> Dict[int, int]:
    """
    Compute state-to-landmass mapping.

    Args:
        province_to_landmass: Province to landmass mapping.
        state_to_provinces: State to provinces mapping.
        logger: Logger instance.

    Returns:
        Dictionary mapping state IDs to landmass IDs.
    """
    state_to_landmass: Dict[int, int] = {}

    for state_id, provinces in state_to_provinces.items():
        for province_id in provinces:
            if province_id in province_to_landmass:
                state_to_landmass[state_id] = province_to_landmass[province_id]
                break

    logger.info(f"Mapped {len(state_to_landmass)} states to landmasses")
    return state_to_landmass


def analyze_landmasses(
    province_to_landmass: Dict[int, int],
    state_to_landmass: Dict[int, int],
    logger,
) -> None:
    """Log analysis of identified landmasses."""
    landmass_sizes: Dict[int, int] = defaultdict(int)
    for landmass in province_to_landmass.values():
        landmass_sizes[landmass] += 1

    sorted_landmasses = sorted(landmass_sizes.items(), key=lambda x: -x[1])

    logger.info("Landmass analysis (top 10 by province count):")
    for landmass_id, province_count in sorted_landmasses[:10]:
        state_count = sum(1 for lm in state_to_landmass.values() if lm == landmass_id)
        logger.info(
            f"  Landmass {landmass_id}: {province_count} provinces, {state_count} states"
        )


class LandmassGenerator(BaseMapGenerator):
    """Generator for province and state landmass mappings."""

    @property
    def name(self) -> str:
        return "landmass"

    @property
    def description(self) -> str:
        return "Generate landmass data for World Ablaze AI railway system"

    def get_output_filename(self) -> str:
        return "WA_AI_MAP_landmass_data.txt"

    def get_required_inputs(self) -> List[Path]:
        return [
            self.config.map_dir / "definition.csv",
            self.config.output_dir / "WA_AI_MAP_province_connections.txt",
            self.config.output_dir / "WA_AI_MAP_state_provinces.txt",
        ]

    def process(self) -> Dict[str, Any]:
        """Process landmass data."""
        self.log_step("Parsing definition.csv for land provinces...")
        land_provinces = parse_definition_for_land_provinces(
            self.config.map_dir / "definition.csv"
        )

        self.log_step("Parsing province connections...")
        adjacencies = parse_province_connections(
            self.config.output_dir / "WA_AI_MAP_province_connections.txt", self.logger
        )

        self.log_step("Parsing state provinces...")
        state_to_provinces, province_to_state = parse_state_provinces(
            self.config.output_dir / "WA_AI_MAP_state_provinces.txt", self.logger
        )

        self.log_step("Identifying landmasses via flood-fill...")
        province_to_landmass = flood_fill_landmasses(
            adjacencies, land_provinces, self.logger
        )

        self.log_step("Computing state landmasses...")
        state_to_landmass = compute_state_landmasses(
            province_to_landmass, state_to_provinces, self.logger
        )

        self.log_step("Analyzing landmasses...")
        analyze_landmasses(province_to_landmass, state_to_landmass, self.logger)

        return {
            "province_to_landmass": province_to_landmass,
            "state_to_landmass": state_to_landmass,
        }

    def format_output(self, data: Dict[str, Any]) -> str:
        """Format landmass data for output file."""
        province_to_landmass = data["province_to_landmass"]
        state_to_landmass = data["state_to_landmass"]

        lines: List[str] = []
        lines.append("# Generated landmass data for World Ablaze AI railway system")
        lines.append("# Each landmass ID represents a connected group of land provinces")
        lines.append(
            "# Islands like Japan, UK, etc. have different landmass IDs than continental Asia/Europe"
        )
        lines.append("")
        lines.append("WA_AI_MAP_set_landmass_data = {")

        lines.append("    # Province to landmass mappings")
        for province_id in sorted(province_to_landmass.keys()):
            landmass_id = province_to_landmass[province_id]
            lines.append(
                f"    set_variable = {{ global.WA_AI_MAP_province_landmass^{province_id} = {landmass_id} }}"
            )

        lines.append("")
        lines.append("    # State to landmass mappings")
        for state_id in sorted(state_to_landmass.keys()):
            landmass_id = state_to_landmass[state_id]
            lines.append(
                f"    set_variable = {{ global.WA_AI_MAP_state_landmass^{state_id} = {landmass_id} }}"
            )

        lines.append("}")

        return "\n".join(lines)


def main() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate landmass data for World Ablaze AI railway system."
    )
    parser.add_argument(
        "--map-dir",
        type=Path,
        default=Path("../map"),
        help="Path to the map folder",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("../common/scripted_effects"),
        help="Path to scripted_effects folder (input and output)",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    config = GeneratorConfig(
        map_dir=args.map_dir,
        output_dir=args.output_dir,
        verbose=args.verbose,
        dry_run=args.dry_run,
    )

    generator = LandmassGenerator(config)
    result = generator.run()

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
