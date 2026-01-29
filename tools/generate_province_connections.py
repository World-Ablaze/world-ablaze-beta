"""
Province neighbor map generator for Expert AI compatibility.

This script reads HOI4 map files (definition.csv and provinces.bmp) and generates
a precomputed province adjacency file in the Expert AI format.

This module is designed to be:
- Standalone: Can be run directly from command line
- Configurable: Supports various filtering options
- Compatible: Outputs in Expert AI's expected format

Key constraints:
- Requires Pillow library for BMP image processing
- Expects standard HOI4 map folder structure
"""

import argparse
import csv
import logging
from collections import defaultdict
from pathlib import Path
from typing import Optional

try:
    from PIL import Image
except ImportError:
    raise ImportError(
        "Pillow is required for this script. Install it with: pip install Pillow"
    )

logger = logging.getLogger(__name__)


def parse_definition_csv(path: Path) -> tuple[dict[tuple[int, int, int], int], dict[int, str]]:
    """
    Parse definition.csv to build province mappings.

    Args:
        path: Path to definition.csv file.

    Returns:
        A tuple of two dictionaries:
        - rgb_to_province: Maps (R, G, B) tuples to province IDs
        - province_type: Maps province IDs to their type (land/sea/lake)
    """
    rgb_to_province: dict[tuple[int, int, int], int] = {}
    province_type: dict[int, str] = {}

    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        for row in reader:
            if len(row) < 5:
                continue
            try:
                province_id = int(row[0])
                r, g, b = int(row[1]), int(row[2]), int(row[3])
                ptype = row[4].strip().lower()

                rgb_to_province[(r, g, b)] = province_id
                province_type[province_id] = ptype
            except (ValueError, IndexError):
                # Skip header or malformed rows
                continue

    logger.info(f"Parsed {len(province_type)} provinces from definition.csv")
    return rgb_to_province, province_type


def scan_province_adjacencies(
    image_path: Path,
    rgb_to_province: dict[tuple[int, int, int], int],
) -> dict[int, set[int]]:
    """
    Scan the provinces.bmp image to find adjacent provinces.

    For each pixel, checks 4 neighbors (up, down, left, right).
    If a neighbor has a different color, those provinces are adjacent.

    Args:
        image_path: Path to provinces.bmp file.
        rgb_to_province: Mapping from RGB colors to province IDs.

    Returns:
        Dictionary mapping province IDs to sets of adjacent province IDs.
    """
    adjacencies: dict[int, set[int]] = defaultdict(set)

    logger.info(f"Loading image: {image_path}")
    with Image.open(image_path) as img:
        # Convert to RGB if necessary
        if img.mode != "RGB":
            img = img.convert("RGB")

        width, height = img.size
        logger.info(f"Image size: {width}x{height} = {width * height:,} pixels")

        # Get pixel data for faster access
        pixels = img.load()

        # Scan all pixels - check all surrounding neighbors dynamically
        # In HOI4, provinces are adjacent if they touch at any point (including diagonals)
        last_percent = 0

        for y in range(height):
            for x in range(width):
                current_rgb = pixels[x, y]
                current_province = rgb_to_province.get(current_rgb)

                if current_province is None:
                    continue

                # Dynamically iterate over all surrounding pixels
                # Only check "forward" neighbors (right half + bottom row) to avoid
                # processing each adjacency twice. We add both directions anyway.
                for dy in range(2):  # 0 = same row, 1 = next row
                    for dx in range(-1, 2):  # -1, 0, 1
                        # Skip self and already-checked pixels (left side of same row)
                        if dy == 0 and dx <= 0:
                            continue

                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            neighbor_rgb = pixels[nx, ny]
                            if neighbor_rgb != current_rgb:
                                neighbor_province = rgb_to_province.get(neighbor_rgb)
                                if neighbor_province is not None:
                                    # Add bidirectional adjacency
                                    adjacencies[current_province].add(neighbor_province)
                                    adjacencies[neighbor_province].add(current_province)

            # Progress logging
            percent = (y * 100) // height
            if percent >= last_percent + 10:
                logger.info(f"Scanning progress: {percent}%")
                last_percent = percent

    logger.info(f"Found adjacencies for {len(adjacencies)} provinces")
    return adjacencies


def parse_special_adjacencies(path: Path) -> list[tuple[int, int]]:
    """
    Parse adjacencies.csv for special connections (straits, canals).

    Only includes adjacencies that are not sea-only crossings.

    Args:
        path: Path to adjacencies.csv file.

    Returns:
        List of (province_a, province_b) tuples for special adjacencies.
    """
    special: list[tuple[int, int]] = []

    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        for row in reader:
            if len(row) < 3:
                continue
            try:
                from_prov = int(row[0])
                to_prov = int(row[1])
                adj_type = row[2].strip().lower() if len(row) > 2 else ""

                # Include empty type (land crossing) and non-sea types
                # Skip pure "sea" type as those are naval-only connections
                if adj_type != "sea":
                    special.append((from_prov, to_prov))
            except (ValueError, IndexError):
                # Skip header or malformed rows
                continue

    logger.info(f"Parsed {len(special)} special adjacencies from adjacencies.csv")
    return special


def filter_land_adjacencies(
    adjacencies: dict[int, set[int]],
    province_type: dict[int, str],
) -> dict[int, set[int]]:
    """
    Filter adjacencies to keep only land-to-land connections.

    Args:
        adjacencies: Full adjacency map from scan.
        province_type: Mapping of province IDs to types.

    Returns:
        Filtered adjacency map with only land provinces.
    """
    filtered: dict[int, set[int]] = defaultdict(set)

    for province, neighbors in adjacencies.items():
        if province_type.get(province) != "land":
            continue

        for neighbor in neighbors:
            if province_type.get(neighbor) == "land":
                filtered[province].add(neighbor)

    logger.info(
        f"Filtered to {len(filtered)} land provinces "
        f"(from {len(adjacencies)} total)"
    )
    return filtered


def write_WA_AI_format(adjacencies: dict[int, set[int]], output_path: Path) -> None:
    """
    Write adjacencies in Expert AI format.

    Output format:
        WA_AI_MAP_set_province_connections = {
            add_to_array = { global.WA_AI_MAP_province_connections_PROV_A = PROV_B }
            ...
        }

    Args:
        adjacencies: Adjacency map to write.
        output_path: Path for output file.
    """
    lines: list[str] = []
    lines.append("WA_AI_MAP_set_province_connections = {")

    # Sort for deterministic output
    total_entries = 0
    for province in sorted(adjacencies.keys()):
        neighbors = sorted(adjacencies[province])
        for neighbor in neighbors:
            lines.append(
                f"    add_to_array = {{ global.WA_AI_MAP_province_connections_{province} = {neighbor} }}"
            )
            total_entries += 1

    lines.append("}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    logger.info(f"Wrote {total_entries} adjacency entries to {output_path}")


def main() -> None:
    """Main entry point for the province neighbor generator."""
    parser = argparse.ArgumentParser(
        description="Generate province neighbor map for Expert AI compatibility.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_province_connections.py --map-dir map --output WA_MAP_province_connections.txt
  python generate_province_connections.py --map-dir map --no-land-only --include-special
        """,
    )
    parser.add_argument(
        "--map-dir",
        type=Path,
        default=Path("map"),
        help="Path to the map folder (default: map)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("WA_MAP_province_neighbors.txt"),
        help="Output file path (default: WA_MAP_province_neighbors.txt)",
    )
    parser.add_argument(
        "--land-only",
        action="store_true",
        default=True,
        help="Filter to land provinces only (default: True)",
    )
    parser.add_argument(
        "--no-land-only",
        action="store_false",
        dest="land_only",
        help="Include all province types, not just land",
    )
    parser.add_argument(
        "--include-special",
        action="store_true",
        default=True,
        help="Include special adjacencies from adjacencies.csv",
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
    map_dir = args.map_dir
    definition_path = map_dir / "definition.csv"
    provinces_path = map_dir / "provinces.bmp"
    adjacencies_path = map_dir / "adjacencies.csv"

    if not definition_path.exists():
        logger.error(f"definition.csv not found at {definition_path}")
        return

    if not provinces_path.exists():
        logger.error(f"provinces.bmp not found at {provinces_path}")
        return

    # Step 1: Parse definition.csv
    logger.info("Step 1: Parsing definition.csv...")
    rgb_to_province, province_type = parse_definition_csv(definition_path)

    # Step 2: Scan provinces.bmp for adjacencies
    logger.info("Step 2: Scanning provinces.bmp for adjacencies...")
    adjacencies = scan_province_adjacencies(provinces_path, rgb_to_province)

    # Step 3: Add special adjacencies if requested
    if args.include_special and adjacencies_path.exists():
        logger.info("Step 3: Adding special adjacencies...")
        special = parse_special_adjacencies(adjacencies_path)
        for prov_a, prov_b in special:
            adjacencies[prov_a].add(prov_b)
            adjacencies[prov_b].add(prov_a)
    else:
        logger.info("Step 3: Skipping special adjacencies")

    # Step 4: Filter to land-only if requested
    if args.land_only:
        logger.info("Step 4: Filtering to land provinces only...")
        adjacencies = filter_land_adjacencies(adjacencies, province_type)
    else:
        logger.info("Step 4: Keeping all province types")

    # Step 5: Write output
    logger.info("Step 5: Writing output file...")
    write_WA_AI_format(adjacencies, args.output)

    logger.info("Done!")


if __name__ == "__main__":
    main()
