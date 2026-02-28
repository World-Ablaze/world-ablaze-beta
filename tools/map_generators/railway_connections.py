"""
Railway connection map generator for World Ablaze AI.

Reads HOI4's railways.txt and generates a precomputed railway connection
file for tracking existing railway levels.
"""

from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from map_generators.base import BaseMapGenerator, GeneratorConfig


def parse_railways(path: Path, logger) -> Dict[Tuple[int, int], int]:
    """
    Parse railways.txt to extract railway connections and their levels.

    Args:
        path: Path to railways.txt file.
        logger: Logger instance.

    Returns:
        Dictionary mapping (province_a, province_b) tuples to railway levels.
    """
    connections: Dict[Tuple[int, int], int] = {}
    provinces_with_railways: Set[int] = set()
    line_count = 0
    error_count = 0

    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            if len(parts) < 3:
                logger.warning(f"Line {line_num}: Too few parts: {line}")
                error_count += 1
                continue

            try:
                level = int(parts[0])
                count = int(parts[1])
                provinces = [int(p) for p in parts[2:]]

                if len(provinces) < 2:
                    logger.warning(
                        f"Line {line_num}: Need at least 2 provinces for a railway"
                    )
                    error_count += 1
                    continue

                # Process consecutive province pairs
                for i in range(len(provinces) - 1):
                    prov_a = provinces[i]
                    prov_b = provinces[i + 1]

                    # Store bidirectional connection (keep higher level)
                    key_ab = (prov_a, prov_b)
                    key_ba = (prov_b, prov_a)

                    if level > connections.get(key_ab, 0):
                        connections[key_ab] = level
                    if level > connections.get(key_ba, 0):
                        connections[key_ba] = level

                    provinces_with_railways.add(prov_a)
                    provinces_with_railways.add(prov_b)

                line_count += 1

            except ValueError as e:
                logger.warning(f"Line {line_num}: Parse error: {e}")
                error_count += 1
                continue

    logger.info(
        f"Parsed {line_count} railway lines, "
        f"{len(connections) // 2} unique connections, "
        f"{len(provinces_with_railways)} provinces with railways"
    )
    if error_count > 0:
        logger.warning(f"Encountered {error_count} errors during parsing")

    return connections


class RailwayConnectionsGenerator(BaseMapGenerator):
    """Generator for railway connection level mappings."""

    @property
    def name(self) -> str:
        return "railway_connections"

    @property
    def description(self) -> str:
        return "Generate railway connection map for World Ablaze AI"

    def get_output_filename(self) -> str:
        return "WA_AI_MAP_province_railway_connections.txt"

    def get_required_inputs(self) -> List[Path]:
        return [self.config.map_dir / "railways.txt"]

    def process(self) -> Dict[str, Any]:
        """Parse railways.txt for connection data."""
        self.log_step("Parsing railways.txt...")
        connections = parse_railways(
            self.config.map_dir / "railways.txt", self.logger
        )

        # Print statistics
        level_counts: Dict[int, int] = defaultdict(int)
        for level in connections.values():
            level_counts[level] += 1

        self.logger.info("Railway statistics:")
        for level in sorted(level_counts.keys()):
            count = level_counts[level] // 2
            self.logger.info(f"  Level {level}: {count} connections")

        return {"connections": connections}

    def format_output(self, data: Dict[str, Any]) -> str:
        """Format railway data for output file."""
        connections = data["connections"]

        lines: List[str] = []
        lines.append("WA_AI_MAP_set_province_railway_connections = {")

        # Collect all provinces with railways
        provinces_with_railways: Set[int] = set()
        for prov_a, prov_b in connections.keys():
            provinces_with_railways.add(prov_a)
            provinces_with_railways.add(prov_b)

        # Mark provinces with railway connections
        for province in sorted(provinces_with_railways):
            lines.append(
                f"    set_variable = {{ global.WA_AI_PC_railway_connections^{province} = 1 }}"
            )

        lines.append("")
        lines.append("    # Railway connection levels (bidirectional)")

        # Group by source province
        connections_by_source: Dict[int, List[Tuple[int, int]]] = defaultdict(list)
        for (prov_a, prov_b), level in connections.items():
            connections_by_source[prov_a].append((prov_b, level))

        for source in sorted(connections_by_source.keys()):
            targets = sorted(connections_by_source[source])
            for target, level in targets:
                lines.append(
                    f"    set_variable = {{ global.WA_AI_PC_railway_connection_level_{source}^{target} = {level} }}"
                )

        lines.append("}")

        return "\n".join(lines)


def main() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate railway connection map for World Ablaze AI."
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
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    config = GeneratorConfig(
        map_dir=args.map_dir,
        output_dir=args.output_dir,
        verbose=args.verbose,
        dry_run=args.dry_run,
    )

    generator = RailwayConnectionsGenerator(config)
    result = generator.run()

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
