#!/usr/bin/env python3
"""
AI Will Do Date Pattern Updater for HOI4 World Ablaze Mod.

This script ONLY updates the date modifier pattern in ai_will_do blocks.
It does NOT touch existing trigger logic - only the date < YEAR.1.1 pattern.

Old pattern:
    modifier = {
        factor = 0
        date < 1939.1.1
    }

New pattern:
    modifier = {
        factor = 0
        OR = {
            AND = {
                NOT = { has_country_flag = WA_AI_unused_research_slots }
                date < 1939.1.1
            }
            AND = {
                has_country_flag = WA_AI_unused_research_slots
                date < 1938.1.1
            }
        }
    }

Usage:
    python ai_will_do_date_updater.py                     # Dry run all tech files
    python ai_will_do_date_updater.py --apply             # Apply changes
    python ai_will_do_date_updater.py --file industry.txt # Single file
"""

import argparse
import re
import sys
from pathlib import Path


def find_matching_brace(content: str, start: int) -> int:
    """Find the closing brace matching the opening brace at start."""
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
        raise ValueError(f"No matching brace found")

    return pos - 1


def is_simple_date_pattern(modifier_content: str) -> bool:
    """
    Check if this modifier uses the simple date pattern that needs updating.

    Returns True for:
        modifier = { factor = 0  date < YEAR.1.1 }

    Returns False for (already updated or complex logic):
        modifier = { factor = 0  OR = { ... WA_AI_unused_research_slots ... } }
    """
    # Must have date < pattern
    if not re.search(r'date\s*<\s*\d{4}\.1\.1', modifier_content):
        return False

    # Must NOT have unused_research_slots (already updated)
    if 'WA_AI_unused_research_slots' in modifier_content:
        return False

    # Must NOT have complex nested logic beyond date
    # Simple pattern: only has factor and date
    stripped = modifier_content.strip()

    # Count significant conditions
    has_factor = 'factor' in stripped
    has_date = re.search(r'date\s*<', stripped) is not None
    has_or = re.search(r'\bOR\s*=', stripped) is not None
    has_and = re.search(r'\bAND\s*=', stripped) is not None
    has_not = re.search(r'\bNOT\s*=', stripped) is not None

    # Simple pattern: just factor and date, no OR/AND/NOT
    if has_factor and has_date and not has_or and not has_and and not has_not:
        return True

    return False


def extract_year_from_date(modifier_content: str) -> int | None:
    """Extract the year from date < YEAR.1.1 pattern."""
    match = re.search(r'date\s*<\s*(\d{4})\.1\.1', modifier_content)
    if match:
        return int(match.group(1))
    return None


def generate_new_date_modifier(year: int, indent: str) -> str:
    """Generate the new date modifier with unused_research_slots logic."""
    early_year = year - 1
    return f"""{indent}modifier = {{
{indent}\tfactor = 0
{indent}\tOR = {{
{indent}\t\tAND = {{
{indent}\t\t\tNOT = {{ has_country_flag = WA_AI_unused_research_slots }}
{indent}\t\t\tdate < {year}.1.1
{indent}\t\t}}
{indent}\t\tAND = {{
{indent}\t\t\thas_country_flag = WA_AI_unused_research_slots
{indent}\t\t\tdate < {early_year}.1.1
{indent}\t\t}}
{indent}\t}}
{indent}}}"""


def process_file(filepath: Path, dry_run: bool = True, verbose: bool = False) -> tuple[int, int, list[str]]:
    """
    Process a single file, updating only date modifiers.

    Returns:
        Tuple of (updated_count, skipped_count, messages)
    """
    messages = []
    updated_count = 0
    skipped_count = 0

    # Read file
    with open(filepath, 'rb') as f:
        first_bytes = f.read(3)
        has_bom = first_bytes == b'\xef\xbb\xbf'

    with open(filepath, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    original_content = content

    # Find all modifier blocks with simple date pattern
    # Pattern: modifier = { ... date < YEAR.1.1 ... }
    modifier_pattern = re.compile(r'^([\t ]*)modifier\s*=\s*\{', re.MULTILINE)

    # Process in reverse order to maintain positions
    matches = list(modifier_pattern.finditer(content))

    for match in reversed(matches):
        indent = match.group(1)
        modifier_start = match.start()
        brace_start = match.end() - 1

        try:
            brace_end = find_matching_brace(content, brace_start)
        except ValueError:
            continue

        modifier_end = brace_end + 1
        modifier_content = content[modifier_start:modifier_end]

        # Check if this is a simple date pattern that needs updating
        if not is_simple_date_pattern(modifier_content):
            continue

        # Extract year
        year = extract_year_from_date(modifier_content)
        if year is None:
            continue

        # Generate new modifier
        new_modifier = generate_new_date_modifier(year, indent)

        # Replace
        content = content[:modifier_start] + new_modifier + content[modifier_end:]
        updated_count += 1

        if verbose:
            messages.append(f"  Updated date modifier: date < {year}.1.1")

    # Write if changed
    if content != original_content and not dry_run:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        messages.append(f"  File saved: {filepath.name}")

    return updated_count, skipped_count, messages


def get_all_tech_files(base_path: Path) -> list[Path]:
    """Get all technology files."""
    tech_path = base_path / 'common' / 'technologies'
    return sorted(tech_path.glob('*.txt'))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Update date modifiers in ai_will_do blocks to use WA_AI_unused_research_slots'
    )
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Show what would be changed without making changes (default)')
    parser.add_argument('--apply', action='store_true',
                        help='Actually apply changes')
    parser.add_argument('--file', type=str,
                        help='Process only a specific file')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed output')
    args = parser.parse_args()

    dry_run = not args.apply

    # Get base path
    base_path = Path(__file__).parent.parent
    tech_path = base_path / 'common' / 'technologies'

    if args.file:
        files = [Path(args.file)]
        if not files[0].exists():
            files = [tech_path / args.file]
    else:
        files = get_all_tech_files(base_path)

    print("=" * 60)
    print("AI Will Do Date Pattern Updater")
    print("=" * 60)
    print(f"Mode: {'DRY RUN' if dry_run else 'APPLY CHANGES'}")
    print()
    print("This script ONLY updates date modifiers.")
    print("Existing trigger logic is preserved.")
    print()

    total_updated = 0
    total_skipped = 0

    for filepath in files:
        if not filepath.exists():
            continue

        updated, skipped, messages = process_file(filepath, dry_run, args.verbose)

        if updated > 0 or args.verbose:
            print(f"{filepath.name}: {updated} date modifiers updated")
            for msg in messages:
                print(msg)

        total_updated += updated
        total_skipped += skipped

    print()
    print("=" * 60)
    print(f"Total: {total_updated} date modifiers updated")
    print("=" * 60)

    if dry_run:
        print("\nThis was a DRY RUN. No files were modified.")
        print("Run with --apply to actually make changes.")

    return 0


if __name__ == '__main__':
    sys.exit(main())
