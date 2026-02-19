#!/usr/bin/env python3
"""
Infantry Technology AI Parser for Hearts of Iron 4 World Ablaze Mod.

Handles infantry and special forces technologies:
- Infantry weapons
- Paratroopers
- Marines
- Mountaineers
- Special forces doctrine

This parser handles multi-trigger techs for shared special forces equipment.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

from ai_replacer_base import (
    BaseFileProcessor,
    ProcessingStats,
    TechGraph,
    build_tech_graph,
    get_reachable_triggers,
    find_ai_will_do_block,
    generate_ai_will_do_block,
)
from ai_replacer_base.text_utils import (
    extract_start_year,
    extract_categories,
    extract_dependencies,
)


class InfantryFileProcessor(BaseFileProcessor):
    """
    File processor for infantry and special forces technologies.

    Handles:
    - Infantry weapons
    - Special forces (paratroopers, marines, mountaineers)
    - Multi-trigger techs (e.g., commandos that require all SF types)
    """

    def get_file_patterns(self) -> list[str]:
        return [
            "infantry_*.txt",
            "special_forces_doctrine.txt",
        ]

    def get_archetype_mappings(self) -> dict[str, str]:
        return {
            "infantry_equipment": "WA_AI_RESEARCH_needs_infantry_weapons",
        }

    def get_category_mappings(self) -> dict[str, str]:
        return {
            # Infantry
            "infantry_weapons": "WA_AI_RESEARCH_needs_infantry_weapons",
            "heavy_infantry_weapons": "WA_AI_RESEARCH_needs_infantry_weapons",
            "cat_light_infantry": "WA_AI_RESEARCH_needs_infantry_weapons",

            # Special forces categories
            "para_tech": "WA_AI_RESEARCH_needs_paratroopers",
            "marine_tech": "WA_AI_RESEARCH_needs_marines",
            "mountaineers_tech": "WA_AI_RESEARCH_needs_mountaineers",
            "paratroopers_doctrine": "WA_AI_RESEARCH_needs_paratroopers",
            "cat_marines_doctrine": "WA_AI_RESEARCH_needs_marines",
            "mountaineers_doctrine": "WA_AI_RESEARCH_needs_mountaineers",
        }

    def get_name_patterns(self) -> list[tuple[str, str | list[str]]]:
        return [
            # Special forces (most specific first)
            (r"paratrooper|paratroopers|_para_|paras_", "WA_AI_RESEARCH_needs_paratroopers"),
            (r"_marine|marines|_marines_", "WA_AI_RESEARCH_needs_marines"),
            (r"mountaineer|mountaineers|_mountaineer|ski_troops|rangers", "WA_AI_RESEARCH_needs_mountaineers"),
            # Commandos require all three SF types
            (r"commando|special_forces_doctrine", [
                "WA_AI_RESEARCH_needs_paratroopers",
                "WA_AI_RESEARCH_needs_marines",
                "WA_AI_RESEARCH_needs_mountaineers"
            ]),
            # Generic infantry (fallback)
            (r"infantry_weapons|infantry_equipment|rifles|weapons", "WA_AI_RESEARCH_needs_infantry_weapons"),
        ]

    def determine_special_forces_triggers(
        self,
        tech_name: str,
        categories: list[str],
        dependencies: list[str]
    ) -> list[str]:
        """
        Determine which special forces types are needed for a tech.

        Returns list of trigger names for multi-type techs.
        """
        triggers = []
        category_map = self.get_category_mappings()

        # Check categories for special forces types
        for cat in categories:
            if cat in category_map:
                trigger = category_map[cat]
                if 'paratrooper' in trigger.lower() or 'marine' in trigger.lower() or 'mountaineer' in trigger.lower():
                    if trigger not in triggers:
                        triggers.append(trigger)

        # Check dependencies for special forces techs
        for dep in dependencies:
            if re.search(r'paratrooper|paratroopers|_para', dep, re.IGNORECASE):
                trigger = "WA_AI_RESEARCH_needs_paratroopers"
                if trigger not in triggers:
                    triggers.append(trigger)
            if re.search(r'_marine|marines|_marines', dep, re.IGNORECASE):
                trigger = "WA_AI_RESEARCH_needs_marines"
                if trigger not in triggers:
                    triggers.append(trigger)
            if re.search(r'mountaineer|mountaineers', dep, re.IGNORECASE):
                trigger = "WA_AI_RESEARCH_needs_mountaineers"
                if trigger not in triggers:
                    triggers.append(trigger)
            if re.search(r'commandos', dep, re.IGNORECASE):
                # Commandos require marines
                trigger = "WA_AI_RESEARCH_needs_marines"
                if trigger not in triggers:
                    triggers.append(trigger)

        # If no triggers from categories/dependencies, try tech name patterns
        if not triggers:
            for pattern, trigger in self._compiled_patterns:
                if pattern.search(tech_name):
                    if isinstance(trigger, list):
                        triggers.extend([t for t in trigger if t not in triggers])
                    else:
                        if trigger not in triggers:
                            triggers.append(trigger)
                    break

        return triggers

    def process_file(self, filepath: Path) -> ProcessingStats:
        """
        Process a single infantry/special forces technology file.

        Uses two-pass approach:
        1. Build tech graph and trigger cache
        2. Process techs with proper SF type filtering
        """
        stats = ProcessingStats()
        content, has_bom = self.read_file(filepath)
        original_content = content

        # Build tech graph for dependency analysis
        graph = build_tech_graph(content)
        trigger_cache: dict[str, Optional[list[str]]] = {}

        # Find all tech definitions
        techs = self.find_tech_definitions(content)

        # First pass: Build trigger cache
        for tech in techs:
            tech_name = tech['name']
            tech_block = tech['block']

            categories = extract_categories(tech_block)
            dependencies = extract_dependencies(tech_block)

            # Check if this is a special forces tech
            sf_triggers = self.determine_special_forces_triggers(tech_name, categories, dependencies)

            if sf_triggers:
                trigger_cache[tech_name] = sf_triggers
            else:
                # Not a special forces tech, use regular resolution
                trigger = self.resolve_trigger(tech_name, [], categories, tech_block)
                trigger_cache[tech_name] = [trigger] if trigger else None

        # Second pass: Process techs with dependency propagation
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

            # Get reachable triggers (with SF type filtering)
            reachable_triggers = get_reachable_triggers(
                tech_name, graph, trigger_cache
            )

            # Fallback to direct trigger
            if not reachable_triggers and tech_name in trigger_cache and trigger_cache[tech_name]:
                reachable_triggers = set(trigger_cache[tech_name])

            if not reachable_triggers:
                stats.unknown += 1
                stats.errors.append(f"Could not determine trigger for {tech_name}")
                continue

            # Get start_year
            start_year = extract_start_year(tech_block, block_content)
            if start_year is None:
                stats.errors.append(f"Could not find start_year for {tech_name}")
                stats.skipped += 1
                continue

            # Generate new block
            triggers = sorted(list(reachable_triggers))
            new_block = generate_ai_will_do_block(triggers, start_year, indent="\t\t")

            # Replace the block
            content = content[:block_start] + new_block + content[block_end:]
            stats.updated += 1

            if self.verbose:
                trigger_str = " OR ".join(triggers)
                print(f"  Updated: {tech_name} -> {trigger_str} (year: {start_year})")

        # Write if changed
        if content != original_content and not self.dry_run:
            self.write_file(filepath, content)

        return stats


def get_infantry_tech_files(base_path: Path) -> list[Path]:
    """Get all infantry technology files to process."""
    tech_path = base_path / 'common' / 'technologies'
    files = []

    # Infantry files
    for filepath in tech_path.glob('infantry_*.txt'):
        files.append(filepath)

    # Special forces doctrine
    sf_doctrine = tech_path / 'special_forces_doctrine.txt'
    if sf_doctrine.exists():
        files.append(sf_doctrine)

    return sorted(files)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Refactor ai_will_do blocks in HOI4 infantry tech files'
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be changed without making changes')
    parser.add_argument('--apply', action='store_true',
                        help='Actually apply changes')
    parser.add_argument('--file', type=str,
                        help='Process a single file instead of all infantry tech files')
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
        files = get_infantry_tech_files(base_path)

    processor = InfantryFileProcessor(dry_run=dry_run, verbose=args.verbose)

    total_stats = ProcessingStats()

    print(f"Processing {len(files)} infantry technology files...")
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
