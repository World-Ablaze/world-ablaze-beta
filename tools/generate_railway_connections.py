"""
Railway connection map generator for World Ablaze AI.

This script reads HOI4's railways.txt and generates a precomputed railway connection
file in the World Ablaze AI format.

The output file is used to track existing railway levels so the AI doesn't try
to rebuild railways that already exist at the target level.

File format of railways.txt:
    level count province1 province2 province3 ...

Example:
    3 4 6521 11444 3207 6282
    Means: Level 3 railway with 4 provinces: 6521 → 11444 → 3207 → 6282

Output format:
    WA_AI_MAP_set_province_railway_connections = {
        set_variable = { global.WA_AI_PC_railway_connections^PROV = 1 }
        set_variable = { global.WA_AI_PC_railway_connection_level_PROV_A^PROV_B = LEVEL }
        ...
    }
"""

import argparse
import logging
from collections import defaultdict
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_railways(path: Path) -> dict[tuple[int, int], int]:
    """
    Parse railways.txt to extract railway connections and their levels.

    Args:
        path: Path to railways.txt file.

    Returns:
        Dictionary mapping (province_a, province_b) tuples to railway levels.
        Both directions are stored (a→b and b→a).
    """
    connections: dict[tuple[int, int], int] = {}
    provinces_with_railways: set[int] = set()

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

                if len(provinces) != count:
                    logger.warning(
                        f"Line {line_num}: Province count mismatch. "
                        f"Expected {count}, got {len(provinces)}"
                    )
                    # Use actual count, not declared count

                if len(provinces) < 2:
                    logger.warning(f"Line {line_num}: Need at least 2 provinces for a railway")
                    error_count += 1
                    continue

                # Process consecutive province pairs
                for i in range(len(provinces) - 1):
                    prov_a = provinces[i]
                    prov_b = provinces[i + 1]

                    # Store bidirectional connection
                    # Keep the higher level if connection already exists
                    key_ab = (prov_a, prov_b)
                    key_ba = (prov_b, prov_a)

                    current_level_ab = connections.get(key_ab, 0)
                    current_level_ba = connections.get(key_ba, 0)

                    if level > current_level_ab:
                        connections[key_ab] = level
                    if level > current_level_ba:
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


def write_wa_ai_format(
    connections: dict[tuple[int, int], int],
    output_path: Path
) -> None:
    """
    Write railway connections in World Ablaze AI format.

    Output format:
        WA_AI_MAP_set_province_railway_connections = {
            set_variable = { global.WA_AI_PC_railway_connections^PROV = 1 }
            set_variable = { global.WA_AI_PC_railway_connection_level_PROV_A^PROV_B = LEVEL }
            ...
        }

    Args:
        connections: Dictionary of (province_a, province_b) -> level.
        output_path: Path for output file.
    """
    lines: list[str] = []
    lines.append("WA_AI_MAP_set_province_railway_connections = {")

    # Collect all provinces that have railways
    provinces_with_railways: set[int] = set()
    for (prov_a, prov_b) in connections.keys():
        provinces_with_railways.add(prov_a)
        provinces_with_railways.add(prov_b)

    # First, mark all provinces that have any railway connection
    for province in sorted(provinces_with_railways):
        lines.append(
            f"    set_variable = {{ global.WA_AI_PC_railway_connections^{province} = 1 }}"
        )

    lines.append("")  # Empty line for readability
    lines.append("    # Railway connection levels (bidirectional)")

    # Then write the connection levels
    # Group by source province for readability
    connections_by_source: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for (prov_a, prov_b), level in connections.items():
        connections_by_source[prov_a].append((prov_b, level))

    for source in sorted(connections_by_source.keys()):
        targets = sorted(connections_by_source[source])
        for target, level in targets:
            lines.append(
                f"    set_variable = {{ global.WA_AI_PC_railway_connection_level_{source}^{target} = {level} }}"
            )

    lines.append("}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    logger.info(
        f"Wrote {len(provinces_with_railways)} province markers and "
        f"{len(connections)} connection levels to {output_path}"
    )


def print_statistics(connections: dict[tuple[int, int], int]) -> None:
    """Print statistics about the railway network."""
    if not connections:
        logger.info("No connections to analyze")
        return

    # Count connections by level
    level_counts: dict[int, int] = defaultdict(int)
    for level in connections.values():
        level_counts[level] += 1

    # Divide by 2 since we store bidirectional
    logger.info("Railway statistics:")
    for level in sorted(level_counts.keys()):
        count = level_counts[level] // 2
        logger.info(f"  Level {level}: {count} connections")

    total_connections = sum(level_counts.values()) // 2
    logger.info(f"  Total unique connections: {total_connections}")


def main() -> None:
    """Main entry point for the railway connection generator."""
    parser = argparse.ArgumentParser(
        description="Generate railway connection map for World Ablaze AI.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_railway_connections.py
  python generate_railway_connections.py --map-dir ../map --output ../common/scripted_effects/WA_AI_MAP_province_railway_connections.txt
        """,
    )
    parser.add_argument(
        "--map-dir",
        type=Path,
        default=Path("../map"),
        help="Path to the map folder (default: ../map)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("../common/scripted_effects/WA_AI_MAP_province_railway_connections.txt"),
        help="Output file path (default: ../common/scripted_effects/WA_AI_MAP_province_railway_connections.txt)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        default=True,
        help="Print railway statistics (default: True)",
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # Validate paths
    railways_path = args.map_dir / "railways.txt"

    if not railways_path.exists():
        logger.error(f"railways.txt not found at {railways_path}")
        return

    # Step 1: Parse railways.txt
    logger.info(f"Step 1: Parsing {railways_path}...")
    connections = parse_railways(railways_path)

    if not connections:
        logger.error("No railway connections found!")
        return

    # Step 2: Print statistics
    if args.stats:
        logger.info("Step 2: Railway statistics...")
        print_statistics(connections)

    # Step 3: Write output
    logger.info("Step 3: Writing output file...")

    # Ensure output directory exists
    args.output.parent.mkdir(parents=True, exist_ok=True)

    write_wa_ai_format(connections, args.output)

    logger.info("Done!")


if __name__ == "__main__":
    main()
