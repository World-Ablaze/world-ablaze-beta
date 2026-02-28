"""
Province neighbor map generator for World Ablaze AI.

Reads HOI4 map files (definition.csv and provinces.bmp) and generates
a precomputed province adjacency file.
"""

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from core import parse_definition_full
from map_generators.base import BaseMapGenerator, GeneratorConfig

try:
    from PIL import Image
except ImportError:
    raise ImportError(
        "Pillow is required for this generator. Install with: pip install Pillow"
    )


def scan_province_adjacencies(
    image_path: Path,
    rgb_to_province: Dict[Tuple[int, int, int], int],
    logger,
) -> Dict[int, Set[int]]:
    """
    Scan the provinces.bmp image to find adjacent provinces.

    Args:
        image_path: Path to provinces.bmp file.
        rgb_to_province: Mapping from RGB colors to province IDs.
        logger: Logger instance.

    Returns:
        Dictionary mapping province IDs to sets of adjacent province IDs.
    """
    adjacencies: Dict[int, Set[int]] = defaultdict(set)

    logger.info(f"Loading image: {image_path}")
    with Image.open(image_path) as img:
        if img.mode != "RGB":
            img = img.convert("RGB")

        width, height = img.size
        logger.info(f"Image size: {width}x{height} = {width * height:,} pixels")

        pixels = img.load()
        last_percent = 0

        for y in range(height):
            for x in range(width):
                current_rgb = pixels[x, y]
                current_province = rgb_to_province.get(current_rgb)

                if current_province is None:
                    continue

                # Check forward neighbors only to avoid processing twice
                for dy in range(2):  # 0 = same row, 1 = next row
                    for dx in range(-1, 2):  # -1, 0, 1
                        if dy == 0 and dx <= 0:
                            continue

                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            neighbor_rgb = pixels[nx, ny]
                            if neighbor_rgb != current_rgb:
                                neighbor_province = rgb_to_province.get(neighbor_rgb)
                                if neighbor_province is not None:
                                    adjacencies[current_province].add(neighbor_province)
                                    adjacencies[neighbor_province].add(current_province)

            percent = (y * 100) // height
            if percent >= last_percent + 10:
                logger.info(f"Scanning progress: {percent}%")
                last_percent = percent

    logger.info(f"Found adjacencies for {len(adjacencies)} provinces")
    return adjacencies


def parse_special_adjacencies(path: Path, logger) -> List[Tuple[int, int]]:
    """
    Parse adjacencies.csv for special connections (straits, canals).

    Args:
        path: Path to adjacencies.csv file.
        logger: Logger instance.

    Returns:
        List of (province_a, province_b) tuples for special adjacencies.
    """
    special: List[Tuple[int, int]] = []

    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        for row in reader:
            if len(row) < 3:
                continue
            try:
                from_prov = int(row[0])
                to_prov = int(row[1])
                adj_type = row[2].strip().lower() if len(row) > 2 else ""

                # Include non-sea adjacencies
                if adj_type != "sea":
                    special.append((from_prov, to_prov))
            except (ValueError, IndexError):
                continue

    logger.info(f"Parsed {len(special)} special adjacencies from adjacencies.csv")
    return special


def filter_land_adjacencies(
    adjacencies: Dict[int, Set[int]],
    province_type: Dict[int, str],
    logger,
) -> Dict[int, Set[int]]:
    """
    Filter adjacencies to keep only land-to-land connections.

    Args:
        adjacencies: Full adjacency map.
        province_type: Mapping of province IDs to types.
        logger: Logger instance.

    Returns:
        Filtered adjacency map with only land provinces.
    """
    filtered: Dict[int, Set[int]] = defaultdict(set)

    for province, neighbors in adjacencies.items():
        if province_type.get(province) != "land":
            continue

        for neighbor in neighbors:
            if province_type.get(neighbor) == "land":
                filtered[province].add(neighbor)

    logger.info(
        f"Filtered to {len(filtered)} land provinces (from {len(adjacencies)} total)"
    )
    return filtered


class ProvinceConnectionsGenerator(BaseMapGenerator):
    """Generator for province adjacency data."""

    def __init__(self, config=None):
        super().__init__(config)
        self.land_only = True
        self.include_special = True

    @property
    def name(self) -> str:
        return "province_connections"

    @property
    def description(self) -> str:
        return "Generate province neighbor map for World Ablaze AI"

    def get_output_filename(self) -> str:
        return "WA_AI_MAP_province_connections.txt"

    def get_required_inputs(self) -> List[Path]:
        return [
            self.config.map_dir / "definition.csv",
            self.config.map_dir / "provinces.bmp",
        ]

    def process(self) -> Dict[str, Any]:
        """Parse map files and compute adjacencies."""
        map_dir = self.config.map_dir

        self.log_step("Parsing definition.csv...")
        rgb_to_province, province_type = parse_definition_full(
            map_dir / "definition.csv"
        )

        self.log_step("Scanning provinces.bmp for adjacencies...")
        adjacencies = scan_province_adjacencies(
            map_dir / "provinces.bmp", rgb_to_province, self.logger
        )

        adjacencies_path = map_dir / "adjacencies.csv"
        if self.include_special and adjacencies_path.exists():
            self.log_step("Adding special adjacencies...")
            special = parse_special_adjacencies(adjacencies_path, self.logger)
            for prov_a, prov_b in special:
                adjacencies[prov_a].add(prov_b)
                adjacencies[prov_b].add(prov_a)

        if self.land_only:
            self.log_step("Filtering to land provinces only...")
            adjacencies = filter_land_adjacencies(adjacencies, province_type, self.logger)

        return {"adjacencies": adjacencies}

    def format_output(self, data: Dict[str, Any]) -> str:
        """Format adjacency data for output file."""
        adjacencies = data["adjacencies"]

        lines: List[str] = []
        lines.append("WA_AI_MAP_set_province_connections = {")

        total_entries = 0
        for province in sorted(adjacencies.keys()):
            neighbors = sorted(adjacencies[province])
            for neighbor in neighbors:
                lines.append(
                    f"    add_to_array = {{ global.WA_AI_MAP_province_connections_{province} = {neighbor} }}"
                )
                total_entries += 1

        lines.append("}")

        self.logger.info(f"Total: {total_entries} adjacency entries")
        return "\n".join(lines)


def main() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate province neighbor map for World Ablaze AI."
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
        help="Output directory",
    )
    parser.add_argument(
        "--no-land-only",
        action="store_true",
        help="Include all province types, not just land",
    )
    parser.add_argument(
        "--no-special",
        action="store_true",
        help="Skip special adjacencies from adjacencies.csv",
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

    generator = ProvinceConnectionsGenerator(config)
    generator.land_only = not args.no_land_only
    generator.include_special = not args.no_special
    result = generator.run()

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
