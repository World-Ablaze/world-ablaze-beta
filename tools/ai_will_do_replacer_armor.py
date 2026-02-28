#!/usr/bin/env python3
"""
Armor Technology AI Parser for Hearts of Iron 4 World Ablaze Mod.

Handles armor technologies:
- Light/Medium/Heavy/Modern tanks
- Tank destroyers (TD)
- Self-propelled artillery (SPG)
- Self-propelled AA (SPAA)
- Armored cars
- Mechanized infantry
- Motorized (trucks)

Uses equipment archetype detection for accurate trigger resolution.
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
    extract_enable_equipments,
)
from ai_replacer_base.block_finder import find_matching_brace


# Global equipment archetype cache (built once, used for all tech files)
EQUIPMENT_ARCHETYPE_CACHE: dict[str, str] = {}


class ArmorFileProcessor(BaseFileProcessor):
    """
    File processor for armor technologies.

    Includes:
    - All tank types (light, medium, heavy, modern, super-heavy)
    - Tank variants (TD, SPG, SPAA)
    - Armored cars
    - Mechanized/Motorized
    """

    def __init__(self, dry_run: bool = False, verbose: bool = False, equipment_path: Optional[Path] = None):
        super().__init__(dry_run=dry_run, verbose=verbose)
        self.equipment_path = equipment_path
        self._archetype_cache: Optional[dict[str, str]] = None

    @property
    def archetype_cache(self) -> dict[str, str]:
        """Lazy-load equipment archetype cache."""
        global EQUIPMENT_ARCHETYPE_CACHE
        if not EQUIPMENT_ARCHETYPE_CACHE and self.equipment_path:
            EQUIPMENT_ARCHETYPE_CACHE = self._build_equipment_archetype_cache(self.equipment_path)
        return EQUIPMENT_ARCHETYPE_CACHE

    def get_file_patterns(self) -> list[str]:
        return [
            "armor_*.txt",
            "tanks_*.txt",
        ]

    def get_archetype_mappings(self) -> dict[str, str]:
        return {
            # Light armor
            "light_tank_chassis": "WA_AI_RESEARCH_needs_light_armor",
            "light_tank_aa_chassis": "WA_AI_RESEARCH_needs_self_propelled_aa",
            "light_tank_artillery_chassis": "WA_AI_RESEARCH_needs_self_propelled_artillery",
            "light_tank_destroyer_chassis": "WA_AI_RESEARCH_needs_tank_destroyers",

            # Medium armor
            "medium_tank_chassis": "WA_AI_RESEARCH_needs_medium_armor",
            "medium_tank_support_chassis": "WA_AI_RESEARCH_needs_medium_armor",
            "medium_tank_aa_chassis": "WA_AI_RESEARCH_needs_self_propelled_aa",
            "medium_tank_artillery_chassis": "WA_AI_RESEARCH_needs_self_propelled_artillery",
            "medium_tank_destroyer_chassis": "WA_AI_RESEARCH_needs_tank_destroyers",

            # Heavy armor
            "heavy_tank_chassis": "WA_AI_RESEARCH_needs_heavy_armor",
            "heavy_tank_aa_chassis": "WA_AI_RESEARCH_needs_self_propelled_aa",
            "heavy_tank_artillery_chassis": "WA_AI_RESEARCH_needs_self_propelled_artillery",
            "heavy_tank_destroyer_chassis": "WA_AI_RESEARCH_needs_tank_destroyers",

            # Super heavy armor (treated as heavy)
            "super_heavy_tank_chassis": "WA_AI_RESEARCH_needs_heavy_armor",
            "super_heavy_tank_aa_chassis": "WA_AI_RESEARCH_needs_self_propelled_aa",
            "super_heavy_tank_artillery_chassis": "WA_AI_RESEARCH_needs_self_propelled_artillery",
            "super_heavy_tank_destroyer_chassis": "WA_AI_RESEARCH_needs_tank_destroyers",

            # Modern armor
            "modern_tank_chassis": "WA_AI_RESEARCH_needs_modern_armor",
            "modern_tank_aa_chassis": "WA_AI_RESEARCH_needs_self_propelled_aa",
            "modern_tank_artillery_chassis": "WA_AI_RESEARCH_needs_self_propelled_artillery",
            "modern_tank_destroyer_chassis": "WA_AI_RESEARCH_needs_tank_destroyers",

            # Armored cars
            "armored_car_chassis": "WA_AI_RESEARCH_needs_armored_cars",

            # Mechanized
            "mechanized_chassis": "WA_AI_RESEARCH_needs_mechanized",
            "amphibious_mechanized_chassis": "WA_AI_RESEARCH_needs_mechanized",
        }

    def get_category_mappings(self) -> dict[str, str]:
        return {
            # Armor categories
            "cat_light_armor": "WA_AI_RESEARCH_needs_light_armor",
            "cat_medium_armor": "WA_AI_RESEARCH_needs_medium_armor",
            "cat_heavy_armor": "WA_AI_RESEARCH_needs_heavy_armor",
            "cat_modern_armor": "WA_AI_RESEARCH_needs_modern_armor",
            "cat_armored_cars": "WA_AI_RESEARCH_needs_armored_cars",
            "cat_mechanized_equipment": "WA_AI_RESEARCH_needs_mechanized",
            "motorized_equipment": "WA_AI_RESEARCH_needs_trucks",

            # Tank variants
            "cat_light_tank_destroyer": "WA_AI_RESEARCH_needs_tank_destroyers",
            "cat_medium_tank_destroyer": "WA_AI_RESEARCH_needs_tank_destroyers",
            "cat_heavy_tank_destroyer": "WA_AI_RESEARCH_needs_tank_destroyers",
            "cat_tank_destroyer": "WA_AI_RESEARCH_needs_tank_destroyers",
            "cat_light_spg": "WA_AI_RESEARCH_needs_self_propelled_artillery",
            "cat_medium_spg": "WA_AI_RESEARCH_needs_self_propelled_artillery",
            "cat_heavy_spg": "WA_AI_RESEARCH_needs_self_propelled_artillery",
            "cat_spg": "WA_AI_RESEARCH_needs_self_propelled_artillery",
            "cat_light_sp_aa": "WA_AI_RESEARCH_needs_self_propelled_aa",
            "cat_medium_sp_aa": "WA_AI_RESEARCH_needs_self_propelled_aa",
            "cat_heavy_sp_aa": "WA_AI_RESEARCH_needs_self_propelled_aa",
            "cat_sp_aa": "WA_AI_RESEARCH_needs_self_propelled_aa",
            "cat_medium_infantry_support": "WA_AI_RESEARCH_needs_self_propelled_artillery",
            "cat_light_infantry_support": "WA_AI_RESEARCH_needs_self_propelled_artillery",
            "cat_heavy_infantry_support": "WA_AI_RESEARCH_needs_self_propelled_artillery",
        }

    def get_name_patterns(self) -> list[tuple[str, str | list[str]]]:
        return [
            # Armored cars (very specific)
            (r"scout_car|armoured_car|armored_car", "WA_AI_RESEARCH_needs_armored_cars"),

            # Tank destroyers (specific)
            (r"_td_|_td$|tank_destroyer", "WA_AI_RESEARCH_needs_tank_destroyers"),

            # Self-propelled artillery (specific)
            (r"_spg_|_spg$|sp_artillery|infantry_support", "WA_AI_RESEARCH_needs_self_propelled_artillery"),

            # Self-propelled AA (specific)
            (r"_aa_|_aa$|_spaa_|sp_anti_air", "WA_AI_RESEARCH_needs_self_propelled_aa"),

            # Amphibious
            (r"amphibious|amph_", "WA_AI_RESEARCH_needs_amphibious_armor"),

            # Base tank types (less specific)
            (r"light_\d|light_tank|light_chassis", "WA_AI_RESEARCH_needs_light_armor"),
            (r"medium_\d|medium_tank|medium_chassis", "WA_AI_RESEARCH_needs_medium_armor"),
            (r"heavy_\d|heavy_tank|heavy_chassis", "WA_AI_RESEARCH_needs_heavy_armor"),
            (r"modern_\d|modern_tank|modern_chassis", "WA_AI_RESEARCH_needs_modern_armor"),

            # Mechanized/Motorized
            (r"mechanized|mechanised", "WA_AI_RESEARCH_needs_mechanized"),
            (r"motorised|motorized", "WA_AI_RESEARCH_needs_trucks"),
        ]

    def _build_equipment_archetype_cache(self, equipment_dir: Path) -> dict[str, str]:
        """
        Parse equipment files and build equipment_name → archetype mapping.
        """
        cache = {}

        if not equipment_dir.exists():
            return cache

        # Parse tank chassis files
        equipment_files = list(equipment_dir.glob("*tank*.txt")) + list(equipment_dir.glob("*chassis*.txt"))

        for eq_file in equipment_files:
            try:
                with open(eq_file, 'r', encoding='utf-8-sig') as f:
                    content = f.read()

                # Find equipment definitions with archetype
                eq_pattern = re.compile(r'^\t([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\{', re.MULTILINE)

                for match in eq_pattern.finditer(content):
                    eq_name = match.group(1)
                    eq_start = match.end() - 1

                    # Skip non-equipment blocks
                    if eq_name in ('equipments', 'upgrades', 'resources', 'limit', 'if', 'OR', 'AND', 'NOT'):
                        continue

                    # Find matching brace
                    try:
                        eq_end = find_matching_brace(content, eq_start) + 1
                    except ValueError:
                        continue

                    eq_block = content[eq_start:eq_end]

                    # Extract archetype
                    arch_match = re.search(r'archetype\s*=\s*([a-zA-Z_][a-zA-Z0-9_]*)', eq_block)
                    if arch_match:
                        archetype = arch_match.group(1)
                        cache[eq_name] = archetype

            except Exception:
                continue

        return cache

    def get_trigger_from_equipment(self, tech_block: str) -> Optional[str]:
        """
        Determine trigger based on equipment archetype.

        This is the most reliable method for armor techs.
        """
        equipments = extract_enable_equipments(tech_block)
        archetype_map = self.get_archetype_mappings()

        for eq_name in equipments:
            if eq_name in self.archetype_cache:
                archetype = self.archetype_cache[eq_name]

                # Direct archetype match
                if archetype in archetype_map:
                    return archetype_map[archetype]

                # Pattern matching on equipment name for variants
                eq_lower = eq_name.lower()
                archetype_lower = archetype.lower()

                # Tank destroyer variants
                if '_td_' in eq_lower or '_td' == eq_lower[-3:] or 'tank_destroyer' in archetype_lower:
                    return "WA_AI_RESEARCH_needs_tank_destroyers"

                # SPG / Infantry support variants
                if '_spg_' in eq_lower or '_spg' == eq_lower[-4:] or 'artillery' in archetype_lower or 'infantry_support' in archetype_lower:
                    return "WA_AI_RESEARCH_needs_self_propelled_artillery"

                # AA variants
                if '_aa_' in eq_lower or '_aa' == eq_lower[-3:] or 'aa_chassis' in archetype_lower:
                    return "WA_AI_RESEARCH_needs_self_propelled_aa"

                # Main tank types based on archetype
                if 'light' in archetype_lower and 'tank' in archetype_lower:
                    return "WA_AI_RESEARCH_needs_light_armor"
                if 'medium' in archetype_lower and 'tank' in archetype_lower:
                    return "WA_AI_RESEARCH_needs_medium_armor"
                if 'heavy' in archetype_lower and 'tank' in archetype_lower:
                    return "WA_AI_RESEARCH_needs_heavy_armor"
                if 'super_heavy' in archetype_lower and 'tank' in archetype_lower:
                    return "WA_AI_RESEARCH_needs_heavy_armor"
                if 'modern' in archetype_lower and 'tank' in archetype_lower:
                    return "WA_AI_RESEARCH_needs_modern_armor"
                if 'support' in archetype_lower:
                    if 'medium' in archetype_lower:
                        return "WA_AI_RESEARCH_needs_medium_armor"
                    if 'light' in archetype_lower:
                        return "WA_AI_RESEARCH_needs_light_armor"
                    if 'heavy' in archetype_lower:
                        return "WA_AI_RESEARCH_needs_heavy_armor"

        return None

    def resolve_trigger(
        self,
        tech_name: str,
        archetypes: list[str],
        categories: list[str],
        tech_block: str = "",
    ) -> Optional[str | list[str]]:
        """
        Override to add equipment archetype detection.

        Priority:
        1. Equipment archetype (most reliable for armor)
        2. Name pattern match
        3. Category match
        """
        # Try equipment archetype first (most reliable for armor)
        if tech_block:
            archetype_trigger = self.get_trigger_from_equipment(tech_block)
            if archetype_trigger:
                return archetype_trigger

        # Fall back to base resolution
        return super().resolve_trigger(tech_name, archetypes, categories, tech_block)

    def process_file(self, filepath: Path) -> ProcessingStats:
        """
        Process a single armor technology file.

        Uses two-pass approach with equipment archetype detection.
        """
        stats = ProcessingStats()
        content, has_bom = self.read_file(filepath)
        original_content = content

        # Build tech graph for dependency analysis
        graph = build_tech_graph(content)
        trigger_cache: dict[str, Optional[list[str]]] = {}

        # Find all tech definitions
        techs = self.find_tech_definitions(content)

        # First pass: Build trigger cache using equipment archetypes
        for tech in techs:
            tech_name = tech['name']
            tech_block = tech['block']

            categories = extract_categories(tech_block)
            trigger = self.resolve_trigger(tech_name, [], categories, tech_block)

            if trigger:
                trigger_cache[tech_name] = [trigger] if isinstance(trigger, str) else trigger
            else:
                trigger_cache[tech_name] = None

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

            # Get reachable triggers
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


def get_armor_tech_files(base_path: Path) -> list[Path]:
    """Get all armor technology files to process."""
    tech_path = base_path / 'common' / 'technologies'
    files = []

    # Armor files
    for filepath in tech_path.glob('armor_*.txt'):
        files.append(filepath)

    # Tank files
    for filepath in tech_path.glob('tanks_*.txt'):
        files.append(filepath)

    return sorted(files)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Refactor ai_will_do blocks in HOI4 armor tech files'
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be changed without making changes')
    parser.add_argument('--apply', action='store_true',
                        help='Actually apply changes')
    parser.add_argument('--file', type=str,
                        help='Process a single file instead of all armor tech files')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed output')
    args = parser.parse_args()

    # --apply overrides --dry-run
    dry_run = not args.apply

    # Get the base path (parent of tools directory)
    base_path = Path(__file__).parent.parent
    tech_path = base_path / 'common' / 'technologies'
    equipment_path = base_path / 'common' / 'units' / 'equipment'

    if args.file:
        files = [Path(args.file)]
        if not files[0].exists():
            files = [tech_path / args.file]
    else:
        files = get_armor_tech_files(base_path)

    processor = ArmorFileProcessor(
        dry_run=dry_run,
        verbose=args.verbose,
        equipment_path=equipment_path
    )

    # Pre-build equipment cache
    print("Building equipment archetype cache...")
    _ = processor.archetype_cache
    print(f"  Found {len(EQUIPMENT_ARCHETYPE_CACHE)} equipment definitions")
    print()

    total_stats = ProcessingStats()

    print(f"Processing {len(files)} armor technology files...")
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
