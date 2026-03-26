#!/usr/bin/env python3
"""
Unified AI Will Do Replacer for Hearts of Iron 4 World Ablaze Mod.

Main entry point that dispatches to appropriate parsers based on file type.
Auto-detects file type from filename patterns.

Parsers:
- Infantry: infantry_*.txt, special_forces_doctrine.txt
- Support: support.txt, support_*.txt
- Armor: armor_*.txt, tanks_*.txt
- Air: air_techs*.txt (uses legacy parser)
- Naval: naval*.txt, MTG_naval.txt (uses legacy parser)
- Industry/Electronics: industry.txt, electronics.txt (uses legacy parser)

Usage:
    python ai_will_do_replacer_all.py                    # Dry run all files
    python ai_will_do_replacer_all.py --apply            # Apply to all files
    python ai_will_do_replacer_all.py --file armor_ger.txt --apply
    python ai_will_do_replacer_all.py --type infantry --apply
"""

import argparse
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# Import new modular parsers
from ai_will_do_replacer_infantry import InfantryFileProcessor, get_infantry_tech_files
from ai_will_do_replacer_support import SupportFileProcessor, get_support_tech_files
from ai_will_do_replacer_armor import ArmorFileProcessor, get_armor_tech_files

# Import legacy parsers (not yet refactored to use base module)
# These work but could be refactored in the future
try:
    from ai_will_do_replacer_air_techs import process_tech_file as process_air_file
    HAS_AIR_PARSER = True
except ImportError:
    HAS_AIR_PARSER = False

try:
    from ai_will_do_replacer_naval import process_file as process_naval_file, get_naval_tech_files
    HAS_NAVAL_PARSER = True
except ImportError:
    HAS_NAVAL_PARSER = False

try:
    from ai_will_do_replacer import process_file as process_industry_file
    HAS_INDUSTRY_PARSER = True
except ImportError:
    HAS_INDUSTRY_PARSER = False


@dataclass
class TotalStats:
    """Aggregated statistics from all processors."""
    updated: int = 0
    skipped: int = 0
    unknown: int = 0
    files_processed: int = 0
    errors: list[str] = field(default_factory=list)


def detect_file_type(filepath: Path) -> Optional[str]:
    """
    Detect the file type from filename patterns.

    Returns:
        File type string ('infantry', 'support', 'armor', 'air', 'naval', 'industry', 'electronics')
        or None if unknown
    """
    name = filepath.name.lower()

    # Infantry patterns
    if name.startswith('infantry_') or name == 'special_forces_doctrine.txt':
        return 'infantry'

    # Support patterns
    if name == 'support.txt' or name.startswith('support_'):
        return 'support'

    # Armor patterns
    if name.startswith('armor_') or name.startswith('tanks_'):
        return 'armor'

    # Air patterns
    if name.startswith('air_techs') or name.startswith('air_'):
        return 'air'

    # Naval patterns
    if name.startswith('naval') or name.startswith('mtg_naval'):
        return 'naval'

    # Industry/Electronics patterns
    if 'industry' in name:
        return 'industry'
    if 'electronic' in name:
        return 'electronics'

    return None


def process_with_new_parser(
    filepath: Path,
    processor,
    dry_run: bool,
    verbose: bool
) -> tuple[int, int, int, list[str]]:
    """
    Process file with new modular parser.

    Returns:
        Tuple of (updated, skipped, unknown, errors)
    """
    stats = processor.process_file(filepath)
    return stats.updated, stats.skipped, stats.unknown, stats.errors


def process_with_air_parser(filepath: Path, dry_run: bool, verbose: bool) -> tuple[int, int, int, list[str]]:
    """Process file with legacy air parser."""
    if not HAS_AIR_PARSER:
        return 0, 0, 0, ["Air parser not available"]

    processed, modified, modifications = process_air_file(filepath, dry_run)
    errors = [m for m in modifications if 'Warning' in m]
    return modified, processed - modified, 0, errors


def process_with_naval_parser(filepath: Path, dry_run: bool, verbose: bool) -> tuple[int, int, int, list[str]]:
    """Process file with legacy naval parser."""
    if not HAS_NAVAL_PARSER:
        return 0, 0, 0, ["Naval parser not available"]

    updated, skipped, messages = process_naval_file(filepath, dry_run=dry_run, verbose=verbose)
    errors = [m for m in messages if 'WARNING' in m]
    return updated, skipped, 0, errors


def process_with_industry_parser(filepath: Path, file_type: str, dry_run: bool, verbose: bool) -> tuple[int, int, int, list[str]]:
    """Process file with industry parser."""
    if not HAS_INDUSTRY_PARSER:
        return 0, 0, 0, ["Industry parser not available"]

    stats = process_industry_file(filepath, file_type, dry_run)
    errors = [f"Unknown tech: {tech}" for tech in stats.get('unknown', [])]
    return stats.get('replaced', 0), stats.get('skipped', 0), len(stats.get('unknown', [])), errors


def get_all_tech_files(base_path: Path, file_type: Optional[str] = None) -> dict[str, list[Path]]:
    """
    Get all technology files grouped by type.

    Args:
        base_path: Base path of the mod
        file_type: Optional filter for specific type

    Returns:
        Dictionary mapping file_type -> list of Paths
    """
    tech_path = base_path / 'common' / 'technologies'
    files_by_type: dict[str, list[Path]] = {
        'infantry': [],
        'support': [],
        'armor': [],
        'air': [],
        'naval': [],
        'industry': [],
        'electronics': [],
    }

    if file_type and file_type in files_by_type:
        # Only get files for requested type
        if file_type == 'infantry':
            files_by_type['infantry'] = get_infantry_tech_files(base_path)
        elif file_type == 'support':
            files_by_type['support'] = get_support_tech_files(base_path)
        elif file_type == 'armor':
            files_by_type['armor'] = get_armor_tech_files(base_path)
        elif file_type == 'air':
            files_by_type['air'] = list(tech_path.glob('air_techs*.txt'))
        elif file_type == 'naval':
            if HAS_NAVAL_PARSER:
                files_by_type['naval'] = get_naval_tech_files(base_path)
            else:
                files_by_type['naval'] = list(tech_path.glob('naval*.txt')) + list(tech_path.glob('MTG_naval*.txt'))
        elif file_type == 'industry':
            files_by_type['industry'] = list(tech_path.glob('*industry*.txt'))
        elif file_type == 'electronics':
            files_by_type['electronics'] = list(tech_path.glob('*electronic*.txt'))
    else:
        # Get all files
        files_by_type['infantry'] = get_infantry_tech_files(base_path)
        files_by_type['support'] = get_support_tech_files(base_path)
        files_by_type['armor'] = get_armor_tech_files(base_path)
        files_by_type['air'] = list(tech_path.glob('air_techs*.txt'))
        if HAS_NAVAL_PARSER:
            files_by_type['naval'] = get_naval_tech_files(base_path)
        else:
            files_by_type['naval'] = list(tech_path.glob('naval*.txt')) + list(tech_path.glob('MTG_naval*.txt'))
        files_by_type['industry'] = list(tech_path.glob('*industry*.txt'))
        files_by_type['electronics'] = list(tech_path.glob('*electronic*.txt'))

    return files_by_type


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Unified AI Will Do replacer for HOI4 tech files'
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be changed without making changes (default)')
    parser.add_argument('--apply', action='store_true',
                        help='Actually apply changes')
    parser.add_argument('--file', type=str,
                        help='Process a single file')
    parser.add_argument('--type', type=str,
                        choices=['infantry', 'support', 'armor', 'air', 'naval', 'industry', 'electronics'],
                        help='Process only files of this type')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed output')
    args = parser.parse_args()

    # --apply overrides --dry-run
    dry_run = not args.apply

    # Get the base path (parent of tools directory)
    base_path = Path(__file__).parent.parent
    tech_path = base_path / 'common' / 'technologies'
    equipment_path = base_path / 'common' / 'units' / 'equipment'

    # Initialize processors
    infantry_processor = InfantryFileProcessor(dry_run=dry_run, verbose=args.verbose)
    support_processor = SupportFileProcessor(dry_run=dry_run, verbose=args.verbose)
    armor_processor = ArmorFileProcessor(dry_run=dry_run, verbose=args.verbose, equipment_path=equipment_path)

    total_stats = TotalStats()

    print("=" * 60)
    print("AI Will Do Replacer - Unified Entry Point")
    print("=" * 60)

    if dry_run:
        print("Mode: DRY RUN (no changes will be made)")
    else:
        print("Mode: APPLY CHANGES")
    print()

    # Handle single file
    if args.file:
        filepath = Path(args.file)
        if not filepath.exists():
            filepath = tech_path / args.file
        if not filepath.exists():
            print(f"Error: File not found: {args.file}")
            return 1

        file_type = detect_file_type(filepath)
        if not file_type:
            print(f"Error: Could not detect file type for: {filepath.name}")
            return 1

        print(f"Processing single file: {filepath.name} (type: {file_type})")
        print()

        # Process based on type
        if file_type == 'infantry':
            updated, skipped, unknown, errors = process_with_new_parser(filepath, infantry_processor, dry_run, args.verbose)
        elif file_type == 'support':
            updated, skipped, unknown, errors = process_with_new_parser(filepath, support_processor, dry_run, args.verbose)
        elif file_type == 'armor':
            updated, skipped, unknown, errors = process_with_new_parser(filepath, armor_processor, dry_run, args.verbose)
        elif file_type == 'air':
            updated, skipped, unknown, errors = process_with_air_parser(filepath, dry_run, args.verbose)
        elif file_type == 'naval':
            updated, skipped, unknown, errors = process_with_naval_parser(filepath, dry_run, args.verbose)
        elif file_type in ('industry', 'electronics'):
            updated, skipped, unknown, errors = process_with_industry_parser(filepath, file_type, dry_run, args.verbose)
        else:
            print(f"Error: Unsupported file type: {file_type}")
            return 1

        print(f"Results: {updated} updated, {skipped} skipped, {unknown} unknown")
        for error in errors:
            print(f"  WARNING: {error}")

        return 0

    # Process all files by type
    files_by_type = get_all_tech_files(base_path, args.type)

    # Pre-build equipment cache for armor
    if files_by_type['armor']:
        print("Building equipment archetype cache...")
        _ = armor_processor.archetype_cache
        print(f"  Found {len(armor_processor.archetype_cache)} equipment definitions")
        print()

    # Process each type
    for file_type, files in files_by_type.items():
        if not files:
            continue

        print(f"\n{'='*60}")
        print(f"Processing {file_type.upper()} files ({len(files)} files)")
        print('='*60)

        type_stats = TotalStats()

        for filepath in sorted(files):
            if not filepath.exists():
                continue

            if file_type == 'infantry':
                updated, skipped, unknown, errors = process_with_new_parser(filepath, infantry_processor, dry_run, args.verbose)
            elif file_type == 'support':
                updated, skipped, unknown, errors = process_with_new_parser(filepath, support_processor, dry_run, args.verbose)
            elif file_type == 'armor':
                updated, skipped, unknown, errors = process_with_new_parser(filepath, armor_processor, dry_run, args.verbose)
            elif file_type == 'air':
                updated, skipped, unknown, errors = process_with_air_parser(filepath, dry_run, args.verbose)
            elif file_type == 'naval':
                updated, skipped, unknown, errors = process_with_naval_parser(filepath, dry_run, args.verbose)
            elif file_type in ('industry', 'electronics'):
                updated, skipped, unknown, errors = process_with_industry_parser(filepath, file_type, dry_run, args.verbose)
            else:
                continue

            type_stats.updated += updated
            type_stats.skipped += skipped
            type_stats.unknown += unknown
            type_stats.files_processed += 1
            type_stats.errors.extend(errors)

            if updated > 0 or errors or args.verbose:
                print(f"  {filepath.name}: {updated} updated, {skipped} skipped")
                for error in errors:
                    print(f"    WARNING: {error}")

        print(f"\n{file_type.upper()} subtotal: {type_stats.updated} updated, {type_stats.skipped} skipped, {type_stats.unknown} unknown")

        total_stats.updated += type_stats.updated
        total_stats.skipped += type_stats.skipped
        total_stats.unknown += type_stats.unknown
        total_stats.files_processed += type_stats.files_processed
        total_stats.errors.extend(type_stats.errors)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Files processed: {total_stats.files_processed}")
    print(f"Blocks updated: {total_stats.updated}")
    print(f"Blocks skipped: {total_stats.skipped}")
    print(f"Blocks unknown: {total_stats.unknown}")

    if total_stats.errors:
        print(f"\nWarnings/Errors: {len(total_stats.errors)}")

    if dry_run:
        print("\nThis was a DRY RUN. No files were modified.")
        print("Run with --apply to actually make changes.")

    return 0


if __name__ == '__main__':
    sys.exit(main())
