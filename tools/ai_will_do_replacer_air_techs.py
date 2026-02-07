#!/usr/bin/env python3
"""
Air Technology AI Parser for Hearts of Iron 4 World Ablaze Mod.

This script parses air technology files and replaces ai_will_do blocks with
standardized trigger-based logic using WA_AI_RESEARCH triggers.

This module is designed to be:
- Robust: Handles HOI4's paradox script syntax with nested braces
- Reusable: Can be run multiple times safely
- Configurable: Archetype detection patterns can be easily modified

Key constraints:
- Uses regex for pattern matching on tech names
- Preserves file structure and comments

Usage:
    python air_tech_ai_parser.py              # Dry run (default)
    python air_tech_ai_parser.py --dry-run    # Dry run, show what would change
    python air_tech_ai_parser.py --apply      # Actually apply changes
"""

import re
import sys
import argparse
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class ArchetypeMapping:
    """Maps regex patterns to archetype names and their research triggers."""
    
    pattern: str
    archetype: str
    trigger: str


# Archetype detection patterns - order matters (more specific patterns first)
# Patterns use \d to match numbers and handle both generic (fighter1) and country-specific (_fighter_1) naming
ARCHETYPE_MAPPINGS = [
    # Carrier variants (must come before base types)
    ArchetypeMapping(r'_cv_cas_|^cv_cas\d', 'cv_cas', 'WA_AI_RESEARCH_needs_carrier_cas'),
    ArchetypeMapping(r'_cv_nav_|_cv_naval_bomber_|^cv_naval_bomber\d|^cv_nav_bomber\d', 'cv_naval_bomber', 'WA_AI_RESEARCH_needs_carrier_bombers'),
    ArchetypeMapping(r'_cv_fighter_|^cv_fighter\d|^cv_early_fighter', 'cv_fighter', 'WA_AI_RESEARCH_needs_carrier_fighters'),
    
    # Jet variants (must come before base types)
    ArchetypeMapping(r'_jet_fighter_multirole_', 'jet_multirole', 'WA_AI_RESEARCH_needs_jet_fighters'),
    ArchetypeMapping(r'_jet_strategic_bomber_|_jet_strat_bomber_|_jet_heavy_strategic_|^jet_strategic_bomber\d', 'jet_strategic', 'WA_AI_RESEARCH_needs_jet_strategic_bombers'),
    ArchetypeMapping(r'_jet_tactical_bomber_|_jet_tac_bomber_|^jet_tactical_bomber\d', 'jet_tactical', 'WA_AI_RESEARCH_needs_jet_tactical_bombers'),
    ArchetypeMapping(r'_jet_fighter_|^jet_fighter\d', 'jet_fighter', 'WA_AI_RESEARCH_needs_jet_fighters'),
    ArchetypeMapping(r'_jet_cv_fighter_|^jet_cv_fighter\d', 'jet_cv_fighter', 'WA_AI_RESEARCH_needs_carrier_fighters'),
    ArchetypeMapping(r'_jet_cv_cas_|^jet_cv_cas\d', 'jet_cv_cas', 'WA_AI_RESEARCH_needs_carrier_cas'),
    ArchetypeMapping(r'_jet_cv_naval_bomber_|^jet_cv_naval_bomber\d', 'jet_cv_naval_bomber', 'WA_AI_RESEARCH_needs_carrier_bombers'),
    
    # Heavy strategic bomber (must come before strategic)
    ArchetypeMapping(r'_heavy_strategic_bomber_|_heavy_strat_|^heavy_strategic_bomber\d', 'heavy_strategic', 'WA_AI_RESEARCH_needs_heavy_strategic_bombers'),
    
    # Strategic bomber
    ArchetypeMapping(r'_strategic_bomber_|_strat_bomber_|^strategic_bomber\d', 'strategic', 'WA_AI_RESEARCH_needs_strategic_bombers'),
    
    # Interceptor (must come before fighter)
    ArchetypeMapping(r'_interceptor_|^interceptor\d', 'interceptor', 'WA_AI_RESEARCH_needs_interceptors'),
    
    # Multirole fighter (must come before fighter)
    ArchetypeMapping(r'_fighter_multirole_|_multirole_fighter_|^fighter_multirole\d|^multirole_fighter\d', 'multirole', 'WA_AI_RESEARCH_needs_multirole_fighters'),
    
    # Heavy fighter (must come before standard fighter)
    ArchetypeMapping(r'_heavy_fighter_|^heavy_fighter\d', 'heavy_fighter', 'WA_AI_RESEARCH_needs_heavy_fighters'),
    
    # Standard fighter
    ArchetypeMapping(r'_fighter_\d|_fighter_ad_tech|^fighter\d|^early_fighter$', 'fighter', 'WA_AI_RESEARCH_needs_fighters'),
    
    # Attacker (ground attack, must come before CAS)
    ArchetypeMapping(r'_attacker_|^attacker\d', 'attacker', 'WA_AI_RESEARCH_needs_attackers'),
    
    # CAS
    ArchetypeMapping(r'_cas_|^CAS\d|^cas\d', 'cas', 'WA_AI_RESEARCH_needs_cas'),
    
    # Strike bomber
    ArchetypeMapping(r'_strike_bomber_|^strike_bomber\d', 'strike_bomber', 'WA_AI_RESEARCH_needs_strike_bombers'),
    
    # Fast bomber
    ArchetypeMapping(r'_fast_bomber_|^fast_bomber\d', 'fast_bomber', 'WA_AI_RESEARCH_needs_fast_bombers'),
    
    # Tactical bomber
    ArchetypeMapping(r'_tactical_bomber_|_tac_bomber_|^tactical_bomber\d|^early_bomber$', 'tactical', 'WA_AI_RESEARCH_needs_tactical_bombers'),
    
    # Naval bomber (land-based, not cv)
    ArchetypeMapping(r'_naval_bomber_|_nav_bomber_|^naval_bomber\d', 'naval_bomber', 'WA_AI_RESEARCH_needs_naval_bombers'),
    
    # Jet naval bomber
    ArchetypeMapping(r'_jet_naval_bomber_|_jet_nav_bomber_|^jet_naval_bomber\d', 'jet_naval_bomber', 'WA_AI_RESEARCH_needs_naval_bombers'),
    
    # Patrol (maritime patrol)
    ArchetypeMapping(r'_patrol_|^patrol\d', 'patrol', 'WA_AI_RESEARCH_needs_patrol_planes'),
    
    # Scout plane
    ArchetypeMapping(r'_scout_|^scout_plane\d|^scout_plane$', 'scout', 'WA_AI_RESEARCH_needs_scout_planes'),
    
    # Transport
    ArchetypeMapping(r'transport_plane|_transport_', 'transport', 'WA_AI_RESEARCH_needs_transport_planes'),
    
    # Jet CAS
    ArchetypeMapping(r'_jet_cas_|^jet_cas\d', 'jet_cas', 'WA_AI_RESEARCH_needs_cas'),
    
    # Jet strike bomber
    ArchetypeMapping(r'_jet_strike_bomber_|^jet_strike_bomber\d', 'jet_strike_bomber', 'WA_AI_RESEARCH_needs_strike_bombers'),
    
    # Jet fast bomber
    ArchetypeMapping(r'_jet_fast_bomber_|^jet_fast_bomber\d', 'jet_fast_bomber', 'WA_AI_RESEARCH_needs_fast_bombers'),
    
    # Jet scout
    ArchetypeMapping(r'_jet_scout_|^jet_scout\d', 'jet_scout', 'WA_AI_RESEARCH_needs_scout_planes'),
    
    # Jet interceptor
    ArchetypeMapping(r'_jet_interceptor_|^jet_interceptor\d', 'jet_interceptor', 'WA_AI_RESEARCH_needs_interceptors'),
]


def detect_archetype(tech_name: str) -> Optional[ArchetypeMapping]:
    """
    Detect the aircraft archetype from a technology name.
    
    Args:
        tech_name: The technology identifier (e.g., 'ger_cas_1', 'fra_interceptor_ad_tech_3')
    
    Returns:
        ArchetypeMapping if a match is found, None otherwise.
    """
    for mapping in ARCHETYPE_MAPPINGS:
        if re.search(mapping.pattern, tech_name, re.IGNORECASE):
            return mapping
    return None


def find_matching_brace(content: str, start_pos: int) -> int:
    """
    Find the position of the closing brace that matches the opening brace at start_pos.
    
    Args:
        content: The file content string
        start_pos: Position of the opening brace '{'
    
    Returns:
        Position of the matching closing brace '}'
    
    Raises:
        ValueError: If no matching brace is found
    """
    if content[start_pos] != '{':
        raise ValueError(f"Expected '{{' at position {start_pos}, got '{content[start_pos]}'")
    
    depth = 1
    pos = start_pos + 1
    
    while pos < len(content) and depth > 0:
        char = content[pos]
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
        pos += 1
    
    if depth != 0:
        raise ValueError(f"No matching brace found for '{{' at position {start_pos}")
    
    return pos - 1  # Return position of the closing brace


def extract_ai_will_do_block(content: str, tech_start: int, tech_end: int) -> Optional[tuple[int, int, str, str]]:
    """
    Extract the ai_will_do block from within a technology definition.
    
    Args:
        content: The file content string
        tech_start: Start position of the technology block
        tech_end: End position of the technology block
    
    Returns:
        Tuple of (start_pos, end_pos, block_content, base_indent) or None if not found
    """
    tech_content = content[tech_start:tech_end]
    
    # Find ai_will_do within the tech block, capturing leading whitespace
    match = re.search(r'(\n(\t*))ai_will_do\s*=\s*\{', tech_content)
    if not match:
        return None
    
    # Get the indentation (tabs before ai_will_do)
    base_indent = match.group(2)
    
    # Calculate absolute position (start from ai_will_do, not the newline)
    ai_will_do_start = tech_start + match.start() + 1  # +1 to skip the newline
    brace_start = tech_start + match.end() - 1  # Position of '{'
    
    try:
        brace_end = find_matching_brace(content, brace_start)
    except ValueError:
        return None
    
    block_content = content[ai_will_do_start:brace_end + 1]
    return (ai_will_do_start, brace_end + 1, block_content, base_indent)


def extract_start_year(content: str, tech_start: int, tech_end: int) -> Optional[str]:
    """
    Extract the start_year from a technology definition.
    
    Args:
        content: The file content string
        tech_start: Start position of the technology block
        tech_end: End position of the technology block
    
    Returns:
        The start_year as a string (e.g., '1936') or None if not found
    """
    tech_content = content[tech_start:tech_end]
    
    # Match start_year = YYYY (with optional quotes)
    match = re.search(r'start_year\s*=\s*"?(\d{4})"?', tech_content)
    if match:
        return match.group(1)
    return None


def extract_leads_to_techs(content: str, tech_start: int, tech_end: int) -> list[str]:
    """
    Extract all leads_to_tech values from path blocks within a technology definition.
    
    Args:
        content: The file content string
        tech_start: Start position of the technology block
        tech_end: End position of the technology block
    
    Returns:
        List of technology names that this tech leads to
    """
    tech_content = content[tech_start:tech_end]
    leads_to_techs = []
    
    # Find all path blocks and extract leads_to_tech values
    # Pattern matches: path = { ... leads_to_tech = tech_name ... }
    path_pattern = re.compile(r'path\s*=\s*\{', re.MULTILINE)
    
    for path_match in path_pattern.finditer(tech_content):
        path_start = tech_start + path_match.end() - 1  # Position of '{'
        try:
            path_end = find_matching_brace(content, path_start) + 1
            path_content = content[path_start:path_end]
            
            # Extract leads_to_tech = tech_name
            leads_match = re.search(r'leads_to_tech\s*=\s*([a-zA-Z_][a-zA-Z0-9_]*)', path_content)
            if leads_match:
                leads_to_techs.append(leads_match.group(1))
        except ValueError:
            continue
    
    return leads_to_techs


def build_tech_graph(content: str) -> dict[str, list[str]]:
    """
    Build a dependency graph of technologies from leads_to_tech relationships.
    
    Args:
        content: The file content string
    
    Returns:
        Dictionary mapping tech_name -> list of child tech names (techs this leads to)
    """
    tech_graph: dict[str, list[str]] = {}
    
    # Find all technology definitions
    tech_pattern = re.compile(r'^(\t*)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\{', re.MULTILINE)
    matches = list(tech_pattern.finditer(content))
    
    for match in matches:
        tech_name = match.group(2)
        brace_start = match.end() - 1
        
        # Skip non-technology blocks
        if tech_name in ('technologies', 'categories', 'path', 'folder', 'sub_technologies', 
                        'enable_equipments', 'enable_equipment_modules', 'modifier', 'allow',
                        'allow_branch', 'on_research_complete', 'research_cost_coeff',
                        'XOR', 'OR', 'AND', 'NOT', 'dependencies', 'if', 'limit',
                        'create_equipment_variant'):
            continue
        
        # Find the end of this technology block
        try:
            tech_end = find_matching_brace(content, brace_start) + 1
        except ValueError:
            continue
        
        tech_start = match.start()
        leads_to_techs = extract_leads_to_techs(content, tech_start, tech_end)
        
        if leads_to_techs:
            tech_graph[tech_name] = leads_to_techs
    
    return tech_graph


def get_reachable_archetypes(
    tech_name: str,
    tech_graph: dict[str, list[str]],
    archetype_cache: dict[str, Optional[str]],
    visited: Optional[set[str]] = None
) -> set[str]:
    """
    Recursively find all archetype triggers reachable from a given technology.
    
    Args:
        tech_name: The technology to start from
        tech_graph: Dictionary mapping tech_name -> list of child tech names
        archetype_cache: Dictionary mapping tech_name -> trigger name (or None)
        visited: Set of already visited techs (for cycle detection)
    
    Returns:
        Set of trigger names (e.g., {"WA_AI_RESEARCH_needs_fighters", "WA_AI_RESEARCH_needs_multirole_fighters"})
    """
    if visited is None:
        visited = set()
    
    # Prevent infinite loops from circular references
    if tech_name in visited:
        return set()
    
    visited.add(tech_name)
    triggers = set()
    
    # Add this tech's own archetype trigger if it has one
    if tech_name in archetype_cache and archetype_cache[tech_name]:
        triggers.add(archetype_cache[tech_name])
    
    # Recursively check all children
    if tech_name in tech_graph:
        for child_tech in tech_graph[tech_name]:
            child_triggers = get_reachable_archetypes(child_tech, tech_graph, archetype_cache, visited.copy())
            triggers.update(child_triggers)
    
    return triggers


def generate_date_modifier(start_year: Optional[str], inner_indent: str, deep_indent: str) -> str:
    """Generate the date modifier with unused research slots logic.
    
    Args:
        start_year: Optional start year for date-based modifier (e.g., '1936')
        inner_indent: Indentation for modifier block
        deep_indent: Indentation for nested blocks
    
    Returns:
        Date modifier block string with OR/AND logic for unused research slots
    """
    if not start_year:
        return ""
    
    year = int(start_year)
    early_year = year - 1
    
    return f'''

{inner_indent}modifier = {{
{deep_indent}factor = 0
{deep_indent}OR = {{
{deep_indent}\tAND = {{
{deep_indent}\t\tNOT = {{ has_country_flag = WA_AI_unused_research_slots }}
{deep_indent}\t\tdate < {year}.1.1
{deep_indent}\t}}
{deep_indent}\tAND = {{
{deep_indent}\t\thas_country_flag = WA_AI_unused_research_slots
{deep_indent}\t\tdate < {early_year}.1.1
{deep_indent}\t}}
{deep_indent}}}
{inner_indent}}}'''


def generate_new_ai_will_do(triggers: set[str], base_indent: str, start_year: Optional[str] = None) -> str:
    """
    Generate a new ai_will_do block using WA_AI_RESEARCH triggers.
    
    Args:
        triggers: Set of research trigger names (e.g., {'WA_AI_RESEARCH_needs_cas', 'WA_AI_RESEARCH_needs_fighters'})
        base_indent: Base indentation for the block (e.g., '\t\t')
        start_year: Optional start year for date-based modifier (e.g., '1936')
    
    Returns:
        New ai_will_do block string with proper indentation
    """
    inner_indent = base_indent + '\t'
    deep_indent = inner_indent + '\t'
    deepest_indent = deep_indent + '\t'
    
    # Build the NOT block with OR logic if multiple triggers
    if len(triggers) == 0:
        # No triggers - this shouldn't happen, but handle gracefully
        not_block = f"{deep_indent}NOT = {{ always = yes }}"
    elif len(triggers) == 1:
        # Single trigger - simple NOT block
        trigger = next(iter(triggers))
        not_block = f"{deep_indent}NOT = {{ {trigger} = yes }}"
    else:
        # Multiple triggers - use OR block
        trigger_lines = []
        sorted_triggers = sorted(triggers)  # Sort for consistent output
        or_indent = deep_indent + '\t'  # Indentation for OR block
        trigger_indent = or_indent + '\t'  # Indentation for triggers inside OR
        for trigger in sorted_triggers:
            trigger_lines.append(f"{trigger_indent}{trigger} = yes")
        not_block = f"{deep_indent}NOT = {{\n{or_indent}OR = {{\n" + "\n".join(trigger_lines) + f"\n{or_indent}}}\n{deep_indent}}}"
    
    # Build the date modifier if start_year is provided
    date_modifier = generate_date_modifier(start_year, inner_indent, deep_indent)
    
    return f'''{base_indent}ai_will_do = {{
{inner_indent}factor = 1

{inner_indent}modifier = {{
{deep_indent}factor = 0
{not_block}
{inner_indent}}}{date_modifier}
{base_indent}}}'''


def process_tech_file(filepath: Path, dry_run: bool = True) -> tuple[int, int, list[str]]:
    """
    Process a single air technology file, replacing ai_will_do blocks.
    
    Uses a two-pass approach:
    1. First pass: Build tech dependency graph and detect all archetypes
    2. Second pass: Compute reachable archetypes and generate ai_will_do blocks
    
    Args:
        filepath: Path to the technology file
        dry_run: If True, don't write changes, just report what would be done
    
    Returns:
        Tuple of (technologies_processed, technologies_modified, list of modifications)
    """
    modifications = []
    
    # Check if file has BOM
    has_bom = False
    with open(filepath, 'rb') as f:
        first_bytes = f.read(3)
        has_bom = first_bytes == b'\xef\xbb\xbf'
    
    # Read file content
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    original_content = content
    techs_processed = 0
    techs_modified = 0
    
    # Find all technology definitions
    # Pattern matches: tech_name = { at the start of a line (with possible indentation)
    tech_pattern = re.compile(r'^(\t*)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\{', re.MULTILINE)
    matches = list(tech_pattern.finditer(content))
    
    # ========================================================================
    # FIRST PASS: Build tech graph and archetype cache
    # ========================================================================
    tech_graph = build_tech_graph(content)
    archetype_cache: dict[str, Optional[str]] = {}
    tech_positions: dict[str, tuple[int, int]] = {}  # tech_name -> (start, end)
    
    for match in matches:
        tech_name = match.group(2)
        tech_start = match.start()
        brace_start = match.end() - 1
        
        # Skip non-technology blocks
        if tech_name in ('technologies', 'categories', 'path', 'folder', 'sub_technologies', 
                        'enable_equipments', 'enable_equipment_modules', 'modifier', 'allow',
                        'allow_branch', 'on_research_complete', 'research_cost_coeff',
                        'XOR', 'OR', 'AND', 'NOT', 'dependencies', 'if', 'limit',
                        'create_equipment_variant'):
            continue
        
        # Find the end of this technology block
        try:
            tech_end = find_matching_brace(content, brace_start) + 1
        except ValueError:
            continue
        
        tech_positions[tech_name] = (tech_start, tech_end)
        
        # Detect archetype and cache it
        archetype = detect_archetype(tech_name)
        if archetype:
            archetype_cache[tech_name] = archetype.trigger
        else:
            archetype_cache[tech_name] = None
    
    # ========================================================================
    # SECOND PASS: Process techs and generate ai_will_do blocks
    # ========================================================================
    # Process in reverse order to maintain positions
    for match in reversed(matches):
        tech_name = match.group(2)
        
        # Skip non-technology blocks
        if tech_name in ('technologies', 'categories', 'path', 'folder', 'sub_technologies', 
                        'enable_equipments', 'enable_equipment_modules', 'modifier', 'allow',
                        'allow_branch', 'on_research_complete', 'research_cost_coeff',
                        'XOR', 'OR', 'AND', 'NOT', 'dependencies', 'if', 'limit',
                        'create_equipment_variant'):
            continue
        
        if tech_name not in tech_positions:
            continue
        
        tech_start, tech_end = tech_positions[tech_name]
        techs_processed += 1
        
        # Compute all reachable archetypes from this tech
        reachable_triggers = get_reachable_archetypes(tech_name, tech_graph, archetype_cache)
        
        # If no reachable triggers, skip (non-aircraft tech with no aircraft children)
        if not reachable_triggers:
            continue
        
        # Extract existing ai_will_do block
        ai_block = extract_ai_will_do_block(content, tech_start, tech_end)
        if not ai_block:
            modifications.append(f"  Warning: No ai_will_do block found in {tech_name}")
            continue
        
        block_start, block_end, old_block, base_indent = ai_block
        
        # Extract start_year for date-based modifier
        start_year = extract_start_year(content, tech_start, tech_end)
        
        # Generate new ai_will_do block with all reachable triggers
        new_block = generate_new_ai_will_do(reachable_triggers, base_indent, start_year)

        # Only replace if the block actually changed
        if new_block != old_block:
            content = content[:block_start] + new_block + content[block_end:]
            techs_modified += 1

            # Build modification message
            year_info = f" (year: {start_year})" if start_year else " (no start_year)"
            triggers_info = ", ".join(sorted(reachable_triggers))
            modifications.append(f"  {tech_name} -> triggers: [{triggers_info}]{year_info}")
    
    # Always rewrite file without BOM if it had BOM or content changed
    if content != original_content or has_bom:
        if not dry_run:
            # Write modified content (use utf-8 without BOM - HOI4 can't handle BOM)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            modifications.append(f"  File updated: {filepath.name}")
    
    return (techs_processed, techs_modified, modifications)


def main():
    """
    Main entry point - process all air technology files.
    """
    parser = argparse.ArgumentParser(
        description='Parse air technology files and replace ai_will_do blocks with trigger-based logic.'
    )
    parser.add_argument(
        '--apply', 
        action='store_true',
        help='Actually apply changes (default is dry-run)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true', 
        default=True,
        help='Show what would be changed without modifying files (default)'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Process only a specific file (for testing)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output for each modification'
    )
    
    args = parser.parse_args()
    
    # --apply overrides --dry-run
    dry_run = not args.apply
    
    # Determine project root (script is in tools/)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    tech_dir = project_root / 'common' / 'technologies'
    
    if not tech_dir.exists():
        print(f"Error: Technology directory not found: {tech_dir}")
        return 1
    
    # Find air tech files
    if args.file:
        air_tech_files = [tech_dir / args.file]
        if not air_tech_files[0].exists():
            print(f"Error: File not found: {air_tech_files[0]}")
            return 1
    else:
        air_tech_files = list(tech_dir.glob('air_techs*.txt'))
    
    if not air_tech_files:
        print(f"Error: No air tech files found in {tech_dir}")
        return 1
    
    mode = "DRY RUN" if dry_run else "APPLYING CHANGES"
    print(f"Mode: {mode}")
    print(f"Found {len(air_tech_files)} air technology files")
    print("=" * 60)
    
    total_processed = 0
    total_modified = 0
    
    for filepath in sorted(air_tech_files):
        print(f"\nProcessing: {filepath.name}")
        processed, modified, modifications = process_tech_file(filepath, dry_run)
        total_processed += processed
        total_modified += modified
        
        if args.verbose or modified > 0:
            for mod in modifications:
                print(mod)
        
        print(f"  Techs processed: {processed}, modified: {modified}")
    
    print("\n" + "=" * 60)
    print(f"Summary: {total_modified} technologies would be modified out of {total_processed} processed")
    
    if dry_run:
        print("\nThis was a DRY RUN. No files were modified.")
        print("Run with --apply to actually make changes.")
    else:
        print("\nChanges applied.")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
