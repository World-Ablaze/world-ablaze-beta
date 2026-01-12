"""
Naval AI Research Refactor Script for HOI4 World Ablaze

This script parses HOI4 naval technology files and updates old ai_will_do patterns
to the new standardized pattern using WA_AI_RESEARCH triggers.

This module is designed to be:
- Consistent: Uses same ai_will_do format as land technology refactor
- Comprehensive: Handles all naval tech categories (frigates, destroyers, cruisers, etc.)
- Safe: Supports dry-run mode to preview changes before applying

Old pattern:
    ai_will_do = {
        factor = 3
        modifier = { factor = 30; date > "YEAR.1.1" }
        modifier = { factor = 30; date > "YEAR+1.1.1" }
        modifier = { factor = 30; date > "YEAR+2.1.1" }
        modifier = { factor = 0; is_major = no }
        modifier = { factor = 0; tag = CHI ... }
    }

New pattern:
    ai_will_do = {
        factor = 1
        modifier = { factor = 0; NOT = { WA_AI_RESEARCH_needs_X = yes } }
        modifier = { factor = 0; date < YEAR.1.1 }
    }
"""

import re
import os
from pathlib import Path
from typing import Optional, Tuple


# Mapping from naval tech categories to research triggers
NAVAL_CATEGORY_TO_TRIGGER = {
    # Screen ships
    "ff_tech": "WA_AI_RESEARCH_needs_frigates",
    "dd_tech": "WA_AI_RESEARCH_needs_destroyers",
    
    # Cruisers
    "cl_tech": "WA_AI_RESEARCH_needs_light_cruisers",
    "ca_tech": "WA_AI_RESEARCH_needs_heavy_cruisers",
    
    # Capital ships
    "bb_tech": "WA_AI_RESEARCH_needs_battleships",
    "bc_tech": "WA_AI_RESEARCH_needs_battlecruisers",
    "shbb_tech": "WA_AI_RESEARCH_needs_battleships",  # Super-heavy BB same as BB
    
    # Carriers
    "cv_tech": "WA_AI_RESEARCH_needs_carriers",
    
    # Submarines
    "ss_tech": "WA_AI_RESEARCH_needs_submarines",
    
    # Transport (optional - major powers should research)
    "tp_tech": "WA_AI_RESEARCH_needs_transports",
}

# Tech name patterns to triggers (fallback when category doesn't match)
NAVAL_TECH_NAME_PATTERNS = [
    # Frigates
    (r"frigate|corvette|sloop|escort_ship", "WA_AI_RESEARCH_needs_frigates"),
    
    # Destroyers
    (r"destroyer", "WA_AI_RESEARCH_needs_destroyers"),
    
    # Light cruisers
    (r"light_cruiser|cl_", "WA_AI_RESEARCH_needs_light_cruisers"),
    
    # Heavy cruisers
    (r"heavy_cruiser|ca_", "WA_AI_RESEARCH_needs_heavy_cruisers"),
    
    # Battleships
    (r"battleship|bb_|dreadnought", "WA_AI_RESEARCH_needs_battleships"),
    
    # Battlecruisers
    (r"battlecruiser|battle_cruiser|bc_", "WA_AI_RESEARCH_needs_battlecruisers"),
    
    # Carriers
    (r"carrier|cv_", "WA_AI_RESEARCH_needs_carriers"),
    
    # Submarines
    (r"submarine|sub_|u_boat|uboat", "WA_AI_RESEARCH_needs_submarines"),
    
    # Cruiser submarines (specific)
    (r"cruiser_sub|submarine_cruiser", "WA_AI_RESEARCH_needs_cruiser_submarines"),
    
    # Minelayers
    (r"minelayer|mine_layer", "WA_AI_RESEARCH_needs_minelayers"),
    
    # Transport
    (r"transport|landing_craft|amphibious", "WA_AI_RESEARCH_needs_transports"),
]


def extract_start_year(tech_block: str, ai_will_do_block: str = "") -> Optional[int]:
    """
    Extract start_year from a technology block.
    
    Args:
        tech_block: The full technology block
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
        # Look for first date > pattern (usually the start_year)
        date_match = re.search(r'date\s*>\s*["\']?(\d{4})', ai_will_do_block)
        if date_match:
            return int(date_match.group(1))
    
    return None


def extract_categories(tech_block: str) -> list[str]:
    """Extract categories from a technology block."""
    categories = []
    cat_match = re.search(r'categories\s*=\s*\{([^}]+)\}', tech_block, re.DOTALL)
    if cat_match:
        cat_content = cat_match.group(1)
        # Find all category names
        categories = re.findall(r'(\w+)', cat_content)
    return categories


def determine_trigger(tech_name: str, categories: list[str], file_path: Optional[Path] = None) -> Optional[str]:
    """
    Determine which WA_AI_RESEARCH trigger to use based on tech name and categories.
    
    Args:
        tech_name: Name of the technology
        categories: List of category strings from the tech definition
        file_path: Optional path to the file being processed (for context)
    
    Returns:
        Trigger name string or None if no match found
    """
    # First try categories (most reliable)
    for cat in categories:
        if cat in NAVAL_CATEGORY_TO_TRIGGER:
            return NAVAL_CATEGORY_TO_TRIGGER[cat]
    
    # Then try tech name patterns (ordered by specificity)
    for pattern, trigger in NAVAL_TECH_NAME_PATTERNS:
        if re.search(pattern, tech_name, re.IGNORECASE):
            return trigger
    
    return None


def is_old_pattern(ai_will_do_block: str) -> bool:
    """
    Check if ai_will_do block uses the old pattern.
    
    Old pattern characteristics:
    - Has modifiers with date > patterns (factor = 30 multipliers)
    - Has tag-specific modifiers (tag = CHI, tag = SOV, etc.)
    - Has is_major = no modifiers
    - Does NOT contain WA_AI_RESEARCH triggers
    """
    # Must not already be new pattern
    if 'WA_AI_RESEARCH' in ai_will_do_block:
        return False
    
    # Check for date > pattern (old style) - this is the key indicator
    has_date_multiplier = re.search(r'date\s*>\s*["\']?\d{4}', ai_will_do_block)
    
    # Check for factor = 3 or factor = 30 patterns (common in naval techs)
    if re.search(r'factor\s*=\s*[3]', ai_will_do_block):
        if has_date_multiplier:
            return True
    
    # Check for factor = 1 with date multipliers
    if re.search(r'factor\s*=\s*1\b', ai_will_do_block):
        if has_date_multiplier:
            return True
    
    # Check for modifier blocks with factor = 30 (old pattern multipliers)
    if re.search(r'modifier\s*=\s*\{[^}]*factor\s*=\s*30', ai_will_do_block, re.DOTALL):
        return True
    
    # Check for is_major = no pattern (common in naval techs)
    if re.search(r'is_major\s*=\s*no', ai_will_do_block):
        return True
    
    # Check for tag-specific modifiers (tag = CHI, tag = SOV, etc.)
    if re.search(r'tag\s*=\s*(CHI|SOV|PRC|USA|JAP|ENG|GER|FRA|ITA)', ai_will_do_block):
        if has_date_multiplier:
            return True
    
    return False


def is_already_new_pattern(ai_will_do_block: str) -> bool:
    """
    Check if ai_will_do block already uses the new pattern.
    Returns False if it uses old date pattern instead of new OR/AND pattern with unused research slots.
    """
    # If it doesn't have WA_AI_RESEARCH, it's not the new pattern
    if 'WA_AI_RESEARCH' not in ai_will_do_block:
        return False
    
    # Check if date modifier uses the new pattern (has WA_AI_unused_research_slots)
    # If it has a date modifier but doesn't have the new pattern, it needs updating
    if 'date <' in ai_will_do_block:
        if 'WA_AI_unused_research_slots' not in ai_will_do_block:
            # Has date restriction but not the new pattern - needs updating
            return False
    
    return True


def generate_new_ai_will_do(trigger: str, start_year: int, indent: str = "\t\t") -> str:
    """
    Generate a new ai_will_do block with the specified trigger and start_year.
    
    Args:
        trigger: Trigger name (e.g., 'WA_AI_RESEARCH_needs_submarines')
        start_year: Start year for the tech
        indent: Indentation string
    
    Returns:
        Formatted ai_will_do block string
    """
    if not trigger:
        return ""
    
    lines = [f"{indent}ai_will_do = {{"]
    lines.append(f"{indent}\tfactor = 1")
    lines.append("")
    lines.append(f"{indent}\tmodifier = {{")
    lines.append(f"{indent}\t\tfactor = 0")
    lines.append(f"{indent}\t\tNOT = {{ {trigger} = yes }}")
    lines.append(f"{indent}\t}}")
    
    # Build date modifier with unused research slots logic
    early_year = start_year - 1
    lines.append("")
    lines.append(f"{indent}\tmodifier = {{")
    lines.append(f"{indent}\t\tfactor = 0")
    lines.append(f"{indent}\t\tOR = {{")
    lines.append(f"{indent}\t\t\tAND = {{")
    lines.append(f"{indent}\t\t\t\tNOT = {{ has_country_flag = WA_AI_unused_research_slots }}")
    lines.append(f"{indent}\t\t\t\tdate < {start_year}.1.1")
    lines.append(f"{indent}\t\t\t}}")
    lines.append(f"{indent}\t\t\tAND = {{")
    lines.append(f"{indent}\t\t\t\thas_country_flag = WA_AI_unused_research_slots")
    lines.append(f"{indent}\t\t\t\tdate < {early_year}.1.1")
    lines.append(f"{indent}\t\t\t}}")
    lines.append(f"{indent}\t\t}}")
    lines.append(f"{indent}\t}}")
    lines.append(f"{indent}}}")
    
    return "\n".join(lines)


def find_ai_will_do_block(content: str, start_pos: int) -> Tuple[int, int, str]:
    """
    Find the ai_will_do block starting at or after start_pos.
    Returns (start, end, block_content) or (-1, -1, "") if not found.
    Skips commented-out blocks.
    """
    search_content = content[start_pos:]
    
    # Find all potential matches
    for match in re.finditer(r'ai_will_do\s*=\s*\{', search_content):
        match_start = start_pos + match.start()
        
        # Find the start of the line containing this match
        line_start = content.rfind('\n', start_pos, match_start) + 1
        if line_start == 0:
            line_start = start_pos
        
        # Get the line up to the match
        line_prefix = content[line_start:match_start]
        
        # Skip if the line is commented out
        if '#' in line_prefix:
            hash_pos = line_prefix.rfind('#')
            if hash_pos >= 0:
                between = line_prefix[hash_pos + 1:]
                if not between.strip() or between.strip().startswith('ai_will_do'):
                    continue
        
        block_start = match_start
        
        # Find matching closing brace
        brace_count = 0
        in_block = False
        block_end = block_start
        
        for i, char in enumerate(content[block_start:]):
            if char == '{':
                brace_count += 1
                in_block = True
            elif char == '}':
                brace_count -= 1
                if in_block and brace_count == 0:
                    block_end = block_start + i + 1
                    return block_start, block_end, content[block_start:block_end]
        
        return block_start, len(content), content[block_start:]
    
    return -1, -1, ""


def extract_tech_context(content: str, ai_will_do_pos: int) -> Tuple[str, str, int]:
    """
    Extract the tech name and full tech block containing this ai_will_do.
    Returns (tech_name, tech_block, tech_start_pos)
    """
    # Search backwards for the tech definition start
    search_start = max(0, ai_will_do_pos - 5000)  # Look up to 5000 chars before (naval techs can be large)
    before_content = content[search_start:ai_will_do_pos]
    
    # Find the last tech definition before ai_will_do
    # Accept either tabs or spaces for indentation (some files use spaces)
    tech_matches = list(re.finditer(r'^[\t ]+(\w+)\s*=\s*\{', before_content, re.MULTILINE))
    
    if not tech_matches:
        return "", "", -1
    
    last_match = tech_matches[-1]
    tech_name = last_match.group(1)
    tech_start = search_start + last_match.start()
    
    # Find the end of this tech block (matching closing brace)
    brace_count = 0
    in_block = False
    tech_end = tech_start
    
    for i, char in enumerate(content[tech_start:]):
        if char == '{':
            brace_count += 1
            in_block = True
        elif char == '}':
            brace_count -= 1
            if in_block and brace_count == 0:
                tech_end = tech_start + i + 1
                break
    
    return tech_name, content[tech_start:tech_end], tech_start


def process_file(filepath: Path, dry_run: bool = False, verbose: bool = False) -> Tuple[int, int, list[str]]:
    """
    Process a single naval technology file.
    
    Args:
        filepath: Path to the file to process
        dry_run: If True, don't write changes
        verbose: If True, output detailed messages
    
    Returns:
        (updated_count, skipped_count, messages)
    """
    messages = []
    updated_count = 0
    skipped_count = 0
    
    # Check if file has BOM
    has_bom = False
    with open(filepath, 'rb') as f:
        first_bytes = f.read(3)
        has_bom = first_bytes == b'\xef\xbb\xbf'
    
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    original_content = content
    pos = 0
    
    while True:
        # Find next ai_will_do block
        block_start, block_end, block_content = find_ai_will_do_block(content, pos)
        
        if block_start == -1:
            break
        
        pos = block_end  # Move past this block for next iteration
        
        # Get tech context
        tech_name, tech_block, _ = extract_tech_context(content, block_start)
        
        if not tech_name:
            skipped_count += 1
            continue
        
        # Check if date pattern needs updating (has WA_AI_RESEARCH but old date pattern)
        needs_date_update = False
        if 'WA_AI_RESEARCH' in block_content and 'date <' in block_content:
            if 'WA_AI_unused_research_slots' not in block_content:
                needs_date_update = True
        
        # Skip if already using new pattern (including new date pattern)
        if is_already_new_pattern(block_content) and not needs_date_update:
            skipped_count += 1
            if verbose:
                messages.append(f"  SKIP (already new): {tech_name}")
            continue

        # Check if it's the old pattern (or needs date update)
        if not is_old_pattern(block_content) and not needs_date_update:
            skipped_count += 1
            if verbose:
                messages.append(f"  SKIP (not old pattern): {tech_name}")
            continue
        
        # Get start_year
        start_year = extract_start_year(tech_block, block_content)
        if not start_year:
            messages.append(f"  WARNING: Could not find start_year for tech '{tech_name}'")
            skipped_count += 1
            continue
        
        # Get categories
        categories = extract_categories(tech_block)
        
        # Determine trigger
        trigger = determine_trigger(tech_name, categories, filepath)
        if not trigger:
            messages.append(f"  WARNING: Could not determine trigger for tech '{tech_name}' with categories {categories}")
            skipped_count += 1
            continue
        
        # Use standard indentation
        indent = "\t\t"
        
        # Find and remove blank lines before ai_will_do block
        prefix_start = block_start
        while prefix_start > 0:
            prev_char = content[prefix_start - 1]
            if prev_char == '\n':
                line_start = content.rfind('\n', 0, prefix_start - 1)
                if line_start == -1:
                    line_start = 0
                else:
                    line_start += 1
                line_content = content[line_start:prefix_start - 1]
                if line_content.strip() == '':
                    prefix_start = line_start
                else:
                    break
            elif prev_char in ' \t':
                prefix_start -= 1
            else:
                break
        
        # Generate new block
        new_block = generate_new_ai_will_do(trigger, start_year, indent)
        
        # Add a single newline before the block if we removed blank lines
        if prefix_start < block_start:
            new_block = "\n" + indent + "ai_will_do" + new_block[new_block.find('ai_will_do') + len('ai_will_do'):]
        
        # Replace
        content = content[:prefix_start] + new_block + content[block_end:]
        
        # Adjust position for next search
        pos = prefix_start + len(new_block)
        
        updated_count += 1
        messages.append(f"  Updated: {tech_name} -> {trigger} (year: {start_year})")
    
    # Always rewrite file without BOM if it had BOM or content changed
    if (content != original_content or has_bom) and not dry_run:
        # Write UTF-8 without BOM (HOI4 parser doesn't handle BOM)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return updated_count, skipped_count, messages


def get_naval_tech_files(base_path: Path) -> list[Path]:
    """
    Get all naval technology files to process.
    
    Args:
        base_path: Base path of the mod
    
    Returns:
        List of paths to naval tech files
    """
    tech_path = base_path / 'common' / 'technologies'
    files = []
    
    # Generic naval files
    for filename in ['naval.txt', 'MTG_naval.txt']:
        filepath = tech_path / filename
        if filepath.exists():
            files.append(filepath)
    
    # Country-specific naval files (naval_TAG.txt)
    for filepath in tech_path.glob('naval_*.txt'):
        files.append(filepath)
    
    return sorted(files)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Refactor ai_will_do blocks in HOI4 naval tech files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    parser.add_argument('--file', type=str, help='Process a single file instead of all naval tech files')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed output')
    args = parser.parse_args()
    
    # Get the base path (parent of tools directory)
    base_path = Path(__file__).parent.parent
    
    if args.file:
        files = [Path(args.file)]
    else:
        files = get_naval_tech_files(base_path)
    
    total_updated = 0
    total_skipped = 0
    
    print(f"Processing {len(files)} naval technology files...")
    if args.dry_run:
        print("(DRY RUN - no changes will be made)")
    print()
    
    for filepath in files:
        updated, skipped, messages = process_file(filepath, dry_run=args.dry_run, verbose=args.verbose)
        
        if updated > 0 or skipped > 0 or args.verbose:
            print(f"{filepath.name}: {updated} updated, {skipped} skipped")
            for msg in messages:
                print(msg)
        
        total_updated += updated
        total_skipped += skipped
    
    print()
    print(f"Total: {total_updated} blocks updated, {total_skipped} blocks skipped")


if __name__ == '__main__':
    main()
