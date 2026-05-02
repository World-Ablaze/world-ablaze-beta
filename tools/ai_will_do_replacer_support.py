#!/usr/bin/env python3
"""
Support Equipment Technology AI Parser for Hearts of Iron 4 World Ablaze Mod.

Handles support company technologies:
- Engineers
- Recon
- Signal/Radio
- Maintenance
- Logistics
- Medical/Hospital
- Military Police
- Camouflage

Does NOT handle self-propelled variants (SPG, SPAA, TD) - those stay in armor.
"""

import argparse
import sys
from pathlib import Path

from ai_replacer_base import (
    BaseFileProcessor,
    ProcessingStats,
    find_ai_will_do_block,
    generate_ai_will_do_block,
)
from ai_replacer_base.text_utils import (
    extract_start_year,
    extract_categories,
)


class SupportFileProcessor(BaseFileProcessor):
    """
    File processor for support equipment technologies.

    Handles support company equipment only.
    Self-propelled variants (SPG, SPAA, TD) are handled by armor parser.
    """

    def get_file_patterns(self) -> list[str]:
        return [
            "support.txt",
            "support_*.txt",
        ]

    def get_archetype_mappings(self) -> dict[str, str]:
        return {
            "engineer_equipment": "WA_AI_RESEARCH_needs_engineer_company",
            "recon_equipment": "WA_AI_RESEARCH_needs_recon_company",
            "signal_equipment": "WA_AI_RESEARCH_needs_signal_company",
            "maintenance_equipment": "WA_AI_RESEARCH_needs_maintenance_company",
            "logistics_equipment": "WA_AI_RESEARCH_needs_logistics_company",
            "hospital_equipment": "WA_AI_RESEARCH_needs_field_hospitals",
            "military_police_equipment": "WA_AI_RESEARCH_needs_military_police",
            "field_hospital_equipment": "WA_AI_RESEARCH_needs_field_hospitals",
        }

    def get_category_mappings(self) -> dict[str, str]:
        return {
            "cat_support_equipment": "WA_AI_RESEARCH_needs_support",
            "support_tech": "WA_AI_RESEARCH_needs_support",
            "engineers_tech": "WA_AI_RESEARCH_needs_engineer_company",
            "cat_engineers": "WA_AI_RESEARCH_needs_engineer_company",
            "cat_recon": "WA_AI_RESEARCH_needs_recon_company",
            "cat_signal": "WA_AI_RESEARCH_needs_signal_company",
            "cat_maintenance": "WA_AI_RESEARCH_needs_maintenance_company",
            "cat_logistics": "WA_AI_RESEARCH_needs_logistics_company",
            "cat_hospital": "WA_AI_RESEARCH_needs_field_hospitals",
            "cat_military_police": "WA_AI_RESEARCH_needs_military_police",
            "cat_camo": "WA_AI_RESEARCH_needs_camo",
            "cat_camouflage": "WA_AI_RESEARCH_needs_camo",
            "camo_tech": "WA_AI_RESEARCH_needs_camo",
        }

    def get_name_patterns(self) -> list[tuple[str, str | list[str]]]:
        return [
            # Specific support types (most specific first)
            (r"engineer|combat_engineer|field_engineer", "WA_AI_RESEARCH_needs_engineer_company"),
            (r"recon|reconnaissance|scout_company", "WA_AI_RESEARCH_needs_recon_company"),
            (r"signal|radio|communication|field_radio", "WA_AI_RESEARCH_needs_signal_company"),
            (r"maintenance|repair|field_repair", "WA_AI_RESEARCH_needs_maintenance_company"),
            (r"logistics|supply|field_supply", "WA_AI_RESEARCH_needs_logistics_company"),
            (r"hospital|medic|medical|field_hospital", "WA_AI_RESEARCH_needs_field_hospitals"),
            (r"military_police|mp_|field_police", "WA_AI_RESEARCH_needs_military_police"),
            (r"camo|camouflage|false_emplacements", "WA_AI_RESEARCH_needs_camo"),
            # Line artillery (for artillery support companies)
            (r"artillery", "WA_AI_RESEARCH_needs_line_artillery"),
            # Generic support (fallback)
            (r"support_equipment|support_tech", "WA_AI_RESEARCH_needs_support"),
        ]

    def process_file(self, filepath: Path) -> ProcessingStats:
        """
        Process a single support equipment technology file.

        Support techs are straightforward - no complex dependency graphs needed.
        """
        stats = ProcessingStats()
        content, has_bom = self.read_file(filepath)
        original_content = content

        # Find all tech definitions
        techs = self.find_tech_definitions(content)

        # Process in reverse order to maintain positions
        for tech in reversed(techs):
            tech_name = tech['name']
            tech_start = tech['start']
            tech_end = tech['end']
            tech_block = tech['block']

            # Find ai_will_do block
            ai_result = find_ai_will_do_block(content, tech_start, tech_end)
            if ai_result is None:
                continue

            block_start, block_end, block_content = ai_result

            # Check if needs update
            if not self.needs_update(block_content, tech_name, tech_block):
                stats.skipped += 1
                continue

            # Get categories and determine trigger
            categories = extract_categories(tech_block)

            trigger = self.resolve_trigger(tech_name, [], categories, tech_block)

            if trigger is None:
                # Only use file-based inference for support files
                if 'support' in filepath.name.lower():
                    trigger = self._infer_from_file(filepath, tech_name)

            if trigger is None:
                stats.skipped += 1  # Skip unknown techs instead of error
                continue

            # Get start_year
            start_year = extract_start_year(tech_block, block_content)
            if start_year is None:
                stats.errors.append(f"Could not find start_year for {tech_name}")
                stats.skipped += 1
                continue

            # Generate new block
            triggers = [trigger] if isinstance(trigger, str) else trigger
            new_block = generate_ai_will_do_block(triggers, start_year, indent="\t\t")

            # Replace the block
            content = content[:block_start] + new_block + content[block_end:]
            stats.updated += 1

            if self.verbose:
                print(f"  Updated: {tech_name} -> {trigger} (year: {start_year})")

        # Write if changed
        if content != original_content and not self.dry_run:
            self.write_file(filepath, content)

        return stats

    def _infer_from_file(self, filepath: Path, tech_name: str) -> str | None:
        """
        Infer trigger from filename when other methods fail.
        """
        filename = filepath.name.lower()

        if 'support' in filename:
            # Generic support fallback
            return "WA_AI_RESEARCH_needs_support"

        return None


def get_support_tech_files(base_path: Path) -> list[Path]:
    """Get all support technology files to process."""
    tech_path = base_path / 'common' / 'technologies'
    files = []

    # Support file
    support_file = tech_path / 'support.txt'
    if support_file.exists():
        files.append(support_file)

    # Country-specific support files
    for filepath in tech_path.glob('support_*.txt'):
        files.append(filepath)

    return sorted(files)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Refactor ai_will_do blocks in HOI4 support equipment tech files'
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be changed without making changes')
    parser.add_argument('--apply', action='store_true',
                        help='Actually apply changes')
    parser.add_argument('--file', type=str,
                        help='Process a single file instead of all support tech files')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed output')
    args = parser.parse_args()

    # --apply overrides --dry-run
    dry_run = not args.apply

    # Get the base path (parent of tools directory)
    base_path = Path(__file__).parent.parent
    tech_path = base_path / 'common' / 'technologies'

    if args.file:
        files = [Path(args.file)]
        if not files[0].exists():
            files = [tech_path / args.file]
    else:
        files = get_support_tech_files(base_path)

    processor = SupportFileProcessor(dry_run=dry_run, verbose=args.verbose)

    total_stats = ProcessingStats()

    print(f"Processing {len(files)} support equipment technology files...")
    if dry_run:
        print("(DRY RUN - no changes will be made)")
    print()

    for filepath in files:
        if not filepath.exists():
            print(f"Warning: File not found: {filepath}")
            continue

        stats = processor.process_file(filepath)

        if stats.updated > 0 or stats.errors or args.verbose:
            print(f"{filepath.name}: {stats.updated} updated, {stats.skipped} skipped, {stats.unknown} unknown")
            for error in stats.errors:
                print(f"  WARNING: {error}")

        total_stats.updated += stats.updated
        total_stats.skipped += stats.skipped
        total_stats.unknown += stats.unknown
        total_stats.errors.extend(stats.errors)

    print()
    print(f"Total: {total_stats.updated} blocks updated, {total_stats.skipped} skipped, {total_stats.unknown} unknown")

    if dry_run:
        print("\nThis was a DRY RUN. No files were modified.")
        print("Run with --apply to actually make changes.")

    return 0


if __name__ == '__main__':
    sys.exit(main())
