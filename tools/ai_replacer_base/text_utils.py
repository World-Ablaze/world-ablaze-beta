"""
Text extraction utilities for parsing HOI4 technology files.

Provides functions for extracting metadata from tech blocks.
"""

import re
from typing import Optional

from .block_finder import find_matching_brace


def extract_start_year(tech_block: str, ai_will_do_block: str = "") -> Optional[int]:
    """
    Extract start_year from a technology block.

    Args:
        tech_block: The full technology block content
        ai_will_do_block: Optional ai_will_do block for fallback extraction

    Returns:
        Year as integer or None if not found
    """
    # First try to get from tech block
    match = re.search(r'start_year\s*=\s*(\d{4})', tech_block)
    if match:
        return int(match.group(1))

    # Fallback: try to extract from date patterns in ai_will_do block
    if ai_will_do_block:
        date_match = re.search(r'date\s*>\s*["\']?(\d{4})', ai_will_do_block)
        if date_match:
            return int(date_match.group(1))

    return None


def extract_categories(tech_block: str) -> list[str]:
    """
    Extract categories from a technology block.

    Args:
        tech_block: The technology block content

    Returns:
        List of category names
    """
    categories = []
    cat_match = re.search(r'categories\s*=\s*\{([^}]+)\}', tech_block, re.DOTALL)
    if cat_match:
        cat_content = cat_match.group(1)
        categories = re.findall(r'(\w+)', cat_content)
    return categories


def extract_dependencies(tech_block: str) -> list[str]:
    """
    Extract dependency tech names from a technology block.

    Args:
        tech_block: The technology block content

    Returns:
        List of dependency tech names
    """
    dependencies = []
    dep_match = re.search(r'dependencies\s*=\s*\{([^}]+)\}', tech_block, re.DOTALL)
    if dep_match:
        dep_content = dep_match.group(1)
        # Dependencies format: tech_name = level
        dep_techs = re.findall(r'(\w+)\s*=\s*\d+', dep_content)
        dependencies.extend(dep_techs)
    return dependencies


def extract_leads_to_techs(tech_block: str) -> list[str]:
    """
    Extract all leads_to_tech values from path blocks within a technology.

    Args:
        tech_block: The technology block content

    Returns:
        List of technology names that this tech leads to
    """
    leads_to_techs = []

    # Find all path blocks and extract leads_to_tech values
    path_pattern = re.compile(r'path\s*=\s*\{', re.MULTILINE)

    for path_match in path_pattern.finditer(tech_block):
        path_start = path_match.end() - 1  # Position of '{'

        try:
            path_end = find_matching_brace(tech_block, path_start) + 1
            path_content = tech_block[path_start:path_end]

            # Extract leads_to_tech = tech_name
            leads_match = re.search(r'leads_to_tech\s*=\s*([a-zA-Z_][a-zA-Z0-9_]*)', path_content)
            if leads_match:
                leads_to_techs.append(leads_match.group(1))
        except ValueError:
            continue

    return leads_to_techs


def extract_enable_equipments(tech_block: str) -> list[str]:
    """
    Extract equipment names from enable_equipments block in a technology.

    Args:
        tech_block: The technology block content

    Returns:
        List of equipment names
    """
    equipments = []

    eq_match = re.search(r'enable_equipments\s*=\s*\{([^}]+)\}', tech_block, re.DOTALL)
    if eq_match:
        eq_content = eq_match.group(1)
        eq_names = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)', eq_content)
        equipments.extend(eq_names)

    return equipments


def extract_sub_technologies(tech_block: str) -> list[str]:
    """
    Extract sub_technologies from a technology block.

    Args:
        tech_block: The technology block content

    Returns:
        List of sub-technology names
    """
    sub_techs = []

    sub_match = re.search(r'sub_technologies\s*=\s*\{([^}]+)\}', tech_block, re.DOTALL)
    if sub_match:
        sub_content = sub_match.group(1)
        sub_names = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)', sub_content)
        sub_techs.extend(sub_names)

    return sub_techs


def extract_folder_info(tech_block: str) -> Optional[dict]:
    """
    Extract folder information from a technology block.

    Args:
        tech_block: The technology block content

    Returns:
        Dict with 'name', 'position' keys or None if not found
    """
    folder_match = re.search(r'folder\s*=\s*\{([^}]+)\}', tech_block, re.DOTALL)
    if not folder_match:
        return None

    folder_content = folder_match.group(1)

    name_match = re.search(r'name\s*=\s*(\w+)', folder_content)
    x_match = re.search(r'position\s*=\s*\{\s*x\s*=\s*(\d+)', folder_content)
    y_match = re.search(r'position\s*=\s*\{[^}]*y\s*=\s*(\d+)', folder_content)

    return {
        'name': name_match.group(1) if name_match else None,
        'x': int(x_match.group(1)) if x_match else None,
        'y': int(y_match.group(1)) if y_match else None,
    }
