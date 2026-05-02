"""CSV parsing utilities for HOI4 map files."""

import csv
import logging
from pathlib import Path
from typing import Dict, Set, Tuple

logger = logging.getLogger(__name__)


def parse_definition_for_land_provinces(path: Path) -> Set[int]:
    """
    Parse definition.csv to get only land province IDs.

    Used by: landmass generator.

    Args:
        path: Path to definition.csv.

    Returns:
        Set of land province IDs.
    """
    land_provinces: Set[int] = set()

    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        for row in reader:
            if len(row) < 5:
                continue
            try:
                province_id = int(row[0])
                ptype = row[4].strip().lower()
                if ptype == "land":
                    land_provinces.add(province_id)
            except (ValueError, IndexError):
                continue

    logger.info(f"Found {len(land_provinces)} land provinces")
    return land_provinces


def parse_definition_for_terrain(path: Path) -> Dict[int, str]:
    """
    Parse definition.csv for province terrain types.

    Used by: province_terrain generator.

    Args:
        path: Path to definition.csv.

    Returns:
        Dictionary mapping province_id -> terrain_name.
    """
    province_terrain: Dict[int, str] = {}

    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        for row in reader:
            if len(row) < 7:
                continue
            try:
                province_id = int(row[0])
                province_type = row[4].lower().strip()
                terrain = row[6].lower().strip()

                # Override terrain for sea/lake
                if province_type == "sea":
                    terrain = "ocean"
                elif province_type == "lake":
                    terrain = "lakes"

                province_terrain[province_id] = terrain
            except (ValueError, IndexError):
                continue

    logger.info(f"Parsed {len(province_terrain)} terrain mappings")
    return province_terrain


def parse_definition_for_colors(
    path: Path, land_only: bool = False
) -> Dict[Tuple[int, int, int], int]:
    """
    Parse definition.csv for RGB color to province ID mapping.

    Used by: province_connections, province_positions generators.

    Args:
        path: Path to definition.csv.
        land_only: If True, only return land provinces.

    Returns:
        Dictionary mapping (r, g, b) tuples to province IDs.
    """
    color_to_province: Dict[Tuple[int, int, int], int] = {}

    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        for row in reader:
            if len(row) < 5:
                continue
            try:
                province_id = int(row[0])
                r, g, b = int(row[1]), int(row[2]), int(row[3])
                ptype = row[4].strip().lower()

                if land_only and ptype != "land":
                    continue

                color_to_province[(r, g, b)] = province_id
            except (ValueError, IndexError):
                continue

    logger.info(f"Parsed {len(color_to_province)} province colors")
    return color_to_province


def parse_definition_full(
    path: Path,
) -> Tuple[Dict[Tuple[int, int, int], int], Dict[int, str]]:
    """
    Parse definition.csv for both color mapping and province types.

    Used by: province_connections generator (needs both).

    Args:
        path: Path to definition.csv.

    Returns:
        Tuple of (rgb_to_province, province_type) dictionaries.
    """
    rgb_to_province: Dict[Tuple[int, int, int], int] = {}
    province_type: Dict[int, str] = {}

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
                continue

    logger.info(f"Parsed {len(province_type)} provinces from definition.csv")
    return rgb_to_province, province_type
