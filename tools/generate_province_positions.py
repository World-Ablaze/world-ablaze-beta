"""
Province position generator for World Ablaze AI.

This script reads HOI4 map files (definition.csv and provinces.bmp) and generates
a precomputed province position mapping file for the World Ablaze AI pathfinding system.

The output file provides X/Y coordinates for each province center, which are used
by WA_AI_MATH_get_distance_between_provinces_a_b for A* pathfinding heuristics.

This module is designed to be:
- Standalone: Can be run directly from command line
- Robust: Handles large BMP files efficiently using chunked processing
- Compatible: Outputs in World Ablaze AI's expected format

Key constraints:
- Requires PIL/Pillow for image processing
- Expects standard HOI4 map folder structure with definition.csv and provinces.bmp
- Only processes land provinces (skips sea/lake for railway pathfinding)
"""

import argparse
import csv
import logging
from collections import defaultdict
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from PIL import Image
except ImportError:
    logger.error("PIL/Pillow is required. Install with: pip install Pillow")
    raise


def parse_definition_csv(definition_path: Path) -> dict[tuple[int, int, int], int]:
    """
    Parse definition.csv to get color -> province_id mapping.

    Args:
        definition_path: Path to the definition.csv file.

    Returns:
        Dictionary mapping (r, g, b) tuples to province IDs.
        Only includes land provinces (not sea/lake).
    """
    color_to_province: dict[tuple[int, int, int], int] = {}

    with open(definition_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        for row in reader:
            if len(row) < 5:
                continue

            try:
                province_id = int(row[0])
                r, g, b = int(row[1]), int(row[2]), int(row[3])
                province_type = row[4].lower()

                # Only include land provinces (skip sea, lake, ocean)
                if province_type == "land":
                    color_to_province[(r, g, b)] = province_id

            except (ValueError, IndexError) as e:
                logger.debug(f"Skipping row {row}: {e}")
                continue

    logger.info(f"Parsed {len(color_to_province)} land provinces from definition.csv")
    return color_to_province


def calculate_province_positions(
    provinces_bmp_path: Path,
    color_to_province: dict[tuple[int, int, int], int]
) -> dict[int, tuple[int, int]]:
    """
    Calculate province center positions from provinces.bmp.

    Uses a streaming approach to handle large BMP files efficiently.

    Args:
        provinces_bmp_path: Path to the provinces.bmp file.
        color_to_province: Mapping of (r, g, b) -> province_id.

    Returns:
        Dictionary mapping province_id -> (x, y) center position.
    """
    logger.info(f"Loading provinces.bmp from {provinces_bmp_path}...")

    # Accumulators for calculating centroids
    province_x_sum: dict[int, int] = defaultdict(int)
    province_y_sum: dict[int, int] = defaultdict(int)
    province_count: dict[int, int] = defaultdict(int)

    with Image.open(provinces_bmp_path) as img:
        width, height = img.size
        logger.info(f"Map size: {width} x {height}")

        # Convert to RGB if needed
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Process row by row to manage memory
        pixels = img.load()
        for y in range(height):
            if y % 500 == 0:
                logger.debug(f"Processing row {y}/{height}")

            for x in range(width):
                pixel = pixels[x, y]
                if pixel in color_to_province:
                    province_id = color_to_province[pixel]
                    province_x_sum[province_id] += x
                    # HOI4 uses inverted Y (0 at top)
                    province_y_sum[province_id] += (height - 1 - y)
                    province_count[province_id] += 1

    # Calculate centroids
    province_positions: dict[int, tuple[int, int]] = {}
    for province_id in province_count:
        count = province_count[province_id]
        if count > 0:
            avg_x = province_x_sum[province_id] // count
            avg_y = province_y_sum[province_id] // count
            province_positions[province_id] = (avg_x, avg_y)

    logger.info(f"Calculated positions for {len(province_positions)} provinces")
    return province_positions


def write_wa_ai_format(
    province_positions: dict[int, tuple[int, int]],
    output_path: Path
) -> None:
    """
    Write province positions in World Ablaze AI format.

    Output format:
        WA_AI_MAP_set_province_pos = {
            set_variable = { global.WA_AI_MAP_province_x_pos^123 = 456 }
            set_variable = { global.WA_AI_MAP_province_y_pos^123 = 789 }
            ...
        }

    Args:
        province_positions: Dictionary of province_id -> (x, y).
        output_path: Path for output file.
    """
    lines: list[str] = []
    lines.append("WA_AI_MAP_set_province_pos = {")

    for province_id in sorted(province_positions.keys()):
        x, y = province_positions[province_id]
        lines.append(
            f"    set_variable = {{ global.WA_AI_MAP_province_x_pos^{province_id} = {x} }}"
            f"     set_variable = {{ global.WA_AI_MAP_province_y_pos^{province_id} = {y} }}"
        )

    lines.append("}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    logger.info(f"Wrote {len(province_positions)} province positions to {output_path}")


def main() -> None:
    """Main entry point for the province position generator."""
    parser = argparse.ArgumentParser(
        description="Generate province positions for World Ablaze AI pathfinding.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_province_positions.py
  python generate_province_positions.py --game-map "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Hearts of Iron IV\\map"
        """,
    )
    parser.add_argument(
        "--game-map",
        type=Path,
        default=Path(r"C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV\map"),
        help="Path to the HOI4 base game map folder",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("../common/scripted_effects/WA_AI_MAP_province_coordinates.txt"),
        help="Output file path",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # Validate paths
    definition_path = args.game_map / "definition.csv"
    provinces_bmp_path = args.game_map / "provinces.bmp"

    if not definition_path.exists():
        logger.error(f"definition.csv not found at {definition_path}")
        return

    if not provinces_bmp_path.exists():
        logger.error(f"provinces.bmp not found at {provinces_bmp_path}")
        return

    # Step 1: Parse definition.csv
    logger.info("Step 1: Parsing definition.csv...")
    color_to_province = parse_definition_csv(definition_path)

    if not color_to_province:
        logger.error("No provinces found in definition.csv!")
        return

    # Step 2: Calculate province positions from provinces.bmp
    logger.info("Step 2: Calculating province positions from provinces.bmp...")
    province_positions = calculate_province_positions(provinces_bmp_path, color_to_province)

    if not province_positions:
        logger.error("No province positions calculated!")
        return

    # Step 3: Write output
    logger.info("Step 3: Writing output file...")

    # Ensure output directory exists
    args.output.parent.mkdir(parents=True, exist_ok=True)

    write_wa_ai_format(province_positions, args.output)

    logger.info("Done!")


if __name__ == "__main__":
    main()
