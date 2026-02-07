"""
Block finding utilities for parsing HOI4 Clausewitz script files.

Provides functions for finding and extracting blocks with proper brace matching.
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class TechBlock:
    """Represents a parsed technology block."""
    name: str
    start: int
    end: int
    indent: str
    content: str
    categories: list[str]
    dependencies: list[str]
    leads_to: list[str]
    start_year: Optional[int]
    archetypes: list[str]


def find_matching_brace(content: str, start: int) -> int:
    """
    Find the closing brace matching the opening brace at start.

    Args:
        content: The file content string
        start: Position of the opening brace '{'

    Returns:
        Position of the matching closing brace '}'

    Raises:
        ValueError: If no matching brace is found or start doesn't point to '{'
    """
    if start >= len(content) or content[start] != '{':
        raise ValueError(f"Expected '{{' at position {start}")

    depth = 1
    pos = start + 1

    while pos < len(content) and depth > 0:
        char = content[pos]
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
        pos += 1

    if depth != 0:
        raise ValueError(f"No matching brace found for '{{' at position {start}")

    return pos - 1  # Return position of the closing brace


def find_ai_will_do_block(
    content: str,
    search_start: int,
    search_end: Optional[int] = None
) -> Optional[tuple[int, int, str]]:
    """
    Find the ai_will_do block within a range.

    Args:
        content: The file content string
        search_start: Start position to search from
        search_end: End position to search to (None = end of content)

    Returns:
        Tuple of (start_pos, end_pos, block_content) or None if not found
    """
    if search_end is None:
        search_end = len(content)

    search_content = content[search_start:search_end]

    # Find ai_will_do = { pattern, skipping commented lines
    for match in re.finditer(r'ai_will_do\s*=\s*\{', search_content):
        match_start = search_start + match.start()

        # Find the start of the line containing this match
        line_start = content.rfind('\n', search_start, match_start)
        if line_start == -1:
            line_start = search_start
        else:
            line_start += 1

        # Get the line up to the match
        line_prefix = content[line_start:match_start]

        # Skip if the line is commented out (has # before ai_will_do)
        if '#' in line_prefix:
            hash_pos = line_prefix.rfind('#')
            if hash_pos >= 0:
                between = line_prefix[hash_pos + 1:]
                if not between.strip() or between.strip().startswith('ai_will_do'):
                    continue

        # Include leading whitespace in block_start to avoid double-indentation
        # when the generator creates the new block with its own indentation
        block_start = line_start
        brace_start = search_start + match.end() - 1

        try:
            brace_end = find_matching_brace(content, brace_start)
            block_end = brace_end + 1
            return (block_start, block_end, content[match_start:block_end])
        except ValueError:
            # Couldn't find matching brace, try next match
            continue

    return None


def find_tech_blocks(content: str) -> list[TechBlock]:
    """
    Find all tech definition blocks in content.

    Note: This is a simpler version that doesn't parse all fields.
    For full parsing, use the DLC splitter module.

    Args:
        content: The file content string

    Returns:
        List of TechBlock objects
    """
    from .text_utils import (
        extract_start_year,
        extract_categories,
        extract_dependencies,
        extract_leads_to_techs,
        extract_enable_equipments,
    )

    blocks = []

    # Skip these block names (not actual techs)
    skip_blocks = frozenset({
        'technologies', 'categories', 'path', 'folder', 'sub_technologies',
        'enable_equipments', 'enable_equipment_modules', 'modifier', 'allow',
        'allow_branch', 'on_research_complete', 'research_cost_coeff',
        'XOR', 'OR', 'AND', 'NOT', 'dependencies', 'if', 'limit',
        'create_equipment_variant', 'ai_will_do', 'position', 'name', 'x', 'y',
        'category_special_forces', 'amphibious', 'enable_subunits'
    })

    # Find tech definitions
    tech_pattern = re.compile(r'^([\t ]*)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\{', re.MULTILINE)

    for match in tech_pattern.finditer(content):
        tech_name = match.group(2)
        indent = match.group(1)

        if tech_name in skip_blocks:
            continue

        tech_start = match.start()
        brace_start = match.end() - 1

        try:
            tech_end = find_matching_brace(content, brace_start) + 1
        except ValueError:
            continue

        tech_content = content[tech_start:tech_end]

        # Extract metadata
        categories = extract_categories(tech_content)
        dependencies = extract_dependencies(tech_content)
        leads_to = extract_leads_to_techs(tech_content)
        start_year = extract_start_year(tech_content)
        equipments = extract_enable_equipments(tech_content)

        blocks.append(TechBlock(
            name=tech_name,
            start=tech_start,
            end=tech_end,
            indent=indent,
            content=tech_content,
            categories=categories,
            dependencies=dependencies,
            leads_to=leads_to,
            start_year=start_year,
            archetypes=equipments,  # Equipment names, not archetypes
        ))

    return blocks


def extract_block_content(content: str, block_name: str) -> Optional[str]:
    """
    Extract content of a named block.

    Args:
        content: The content to search in
        block_name: Name of the block (e.g., 'categories', 'dependencies')

    Returns:
        Block content (inside braces) or None if not found
    """
    pattern = re.compile(rf'{block_name}\s*=\s*\{{', re.MULTILINE)
    match = pattern.search(content)

    if not match:
        return None

    brace_start = match.end() - 1

    try:
        brace_end = find_matching_brace(content, brace_start)
        return content[brace_start + 1:brace_end]
    except ValueError:
        return None
