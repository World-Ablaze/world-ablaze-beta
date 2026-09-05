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
GENERATED_CODE_COMMENT = "# THE FOLLOWING BLOCK IS GENERATED CODE. DO NOT EDIT MANUALLY"

TIERED_VARIANT_TRIGGERS = {
    "light": {
        "td": "WA_AI_RESEARCH_needs_light_tank_destroyers",
        "spg": "WA_AI_RESEARCH_needs_light_self_propelled_guns",
        "spaa": "WA_AI_RESEARCH_needs_light_self_propelled_aa",
        "assault": "WA_AI_RESEARCH_needs_light_assault",
        "infantry_support": "WA_AI_RESEARCH_needs_light_infantry_support",
    },
    "medium": {
        "td": "WA_AI_RESEARCH_needs_medium_tank_destroyers",
        "spg": "WA_AI_RESEARCH_needs_medium_self_propelled_guns",
        "spaa": "WA_AI_RESEARCH_needs_medium_self_propelled_aa",
        "assault": "WA_AI_RESEARCH_needs_medium_assault",
        "infantry_support": "WA_AI_RESEARCH_needs_medium_infantry_support",
    },
    "heavy": {
        "td": "WA_AI_RESEARCH_needs_heavy_tank_destroyers",
        "spg": "WA_AI_RESEARCH_needs_heavy_self_propelled_guns",
        "spaa": "WA_AI_RESEARCH_needs_heavy_self_propelled_aa",
        "assault": "WA_AI_RESEARCH_needs_heavy_assault",
        "infantry_support": "WA_AI_RESEARCH_needs_heavy_infantry_support",
    },
    "modern": {
        "td": "WA_AI_RESEARCH_needs_modern_tank_destroyers",
        "spg": "WA_AI_RESEARCH_needs_modern_self_propelled_guns",
        "spaa": "WA_AI_RESEARCH_needs_modern_self_propelled_aa",
        "assault": "WA_AI_RESEARCH_needs_modern_assault",
        "infantry_support": "WA_AI_RESEARCH_needs_modern_infantry_support",
    },
    "mechanized": {
        "td": "WA_AI_RESEARCH_needs_mechanized_tank_destroyers",
        "spg": "WA_AI_RESEARCH_needs_mechanized_self_propelled_guns",
        "spaa": "WA_AI_RESEARCH_needs_mechanized_self_propelled_aa",
    },
}

MAINLINE_ARMOR_TRIGGERS = frozenset({
    "WA_AI_RESEARCH_needs_light_armor",
    "WA_AI_RESEARCH_needs_medium_armor",
    "WA_AI_RESEARCH_needs_heavy_armor",
    "WA_AI_RESEARCH_needs_modern_armor",
})
MEDIUM_ARMOR_TRIGGER = "WA_AI_RESEARCH_needs_medium_armor"
MODERN_ARMOR_TRIGGER = "WA_AI_RESEARCH_needs_modern_armor"


def resolve_armor_trigger_set(
    tech_name: str,
    graph: TechGraph,
    trigger_cache: dict[str, Optional[list[str]]],
    modern_armor_prefixes: frozenset[str],
) -> set[str]:
    """Resolve direct variant triggers or mainline armor dependency triggers."""
    direct_triggers = set(trigger_cache.get(tech_name) or [])
    direct_mainline_triggers = direct_triggers & MAINLINE_ARMOR_TRIGGERS

    # Specialized variants use only their own role-and-size trigger.
    if direct_triggers and not direct_mainline_triggers:
        return direct_triggers

    # Modern armor is the end of the mainline chain.
    if direct_mainline_triggers == {MODERN_ARMOR_TRIGGER}:
        return direct_triggers

    if direct_mainline_triggers:
        # Mainline tanks inherit every downstream requirement they gate,
        # including mechanized and size-specific tank variants.
        resolved_triggers = direct_triggers | get_reachable_triggers(
            tech_name, graph, trigger_cache
        )

        # Medium armor gates the same country's modern line even when the
        # explicit graph does not carry that relationship through every model.
        tech_prefix = tech_name.partition("_")[0]
        if (
            MEDIUM_ARMOR_TRIGGER in direct_mainline_triggers
            and tech_prefix in modern_armor_prefixes
        ):
            resolved_triggers.add(MODERN_ARMOR_TRIGGER)
        return resolved_triggers

    # Preserve dependency propagation for an otherwise unmapped prerequisite.
    return get_reachable_triggers(tech_name, graph, trigger_cache)

def get_tiered_variant_trigger(
    archetype_name: str,
    equipment_name: str,
    variant: str,
) -> Optional[str]:
    """Resolve a size-specific tank-role trigger from its archetype, then name."""
    for candidate in (archetype_name.lower(), equipment_name.lower()):
        if "super_heavy" in candidate:
            return TIERED_VARIANT_TRIGGERS["heavy"][variant]
        for tier in ("light", "medium", "heavy", "modern", "mechanized"):
            if tier in candidate:
                return TIERED_VARIANT_TRIGGERS[tier][variant]
    return None


def get_generated_comment_start(content: str, block_start: int) -> tuple[int, bool]:
    """Return a generated marker's start when it is directly above a block."""
    previous_line_end = block_start
    if previous_line_end > 0 and content[previous_line_end - 1] == "\n":
        previous_line_end -= 1
    previous_line_start = content.rfind("\n", 0, previous_line_end) + 1
    previous_line = content[previous_line_start:previous_line_end]
    if previous_line.strip() == GENERATED_CODE_COMMENT:
        return previous_line_start, True
    return block_start, False


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
        self._dependency_contexts: dict[
            Path,
            tuple[TechGraph, dict[str, Optional[list[str]]], frozenset[str]],
        ] = {}

    @property
    def archetype_cache(self) -> dict[str, str]:
        """Lazy-load equipment archetype cache."""
        global EQUIPMENT_ARCHETYPE_CACHE
        if not EQUIPMENT_ARCHETYPE_CACHE and self.equipment_path:
            EQUIPMENT_ARCHETYPE_CACHE = self._build_equipment_archetype_cache(self.equipment_path)
        return EQUIPMENT_ARCHETYPE_CACHE

    def get_dependency_context(
        self,
        technology_directory: Path,
    ) -> tuple[TechGraph, dict[str, Optional[list[str]]], frozenset[str]]:
        """Build one merged dependency graph for every armor technology file."""
        technology_directory = technology_directory.resolve()
        if technology_directory in self._dependency_contexts:
            return self._dependency_contexts[technology_directory]

        graph = TechGraph()
        trigger_cache: dict[str, Optional[list[str]]] = {}
        armor_files = sorted({
            *technology_directory.glob("armor_*.txt"),
            *technology_directory.glob("tanks_*.txt"),
        })

        for armor_file in armor_files:
            content, _ = self.read_file(armor_file)
            file_graph = build_tech_graph(content)
            for attribute in ("forward", "reverse", "prerequisites"):
                merged_edges = getattr(graph, attribute)
                for source, targets in getattr(file_graph, attribute).items():
                    merged_targets = merged_edges.setdefault(source, [])
                    for target in targets:
                        if target not in merged_targets:
                            merged_targets.append(target)

            for tech in self.find_tech_definitions(content):
                trigger = self.resolve_trigger(
                    tech["name"],
                    [],
                    extract_categories(tech["block"]),
                    tech["block"],
                )
                triggers = [trigger] if isinstance(trigger, str) else trigger
                if triggers:
                    merged_triggers = set(trigger_cache.get(tech["name"]) or [])
                    merged_triggers.update(triggers)
                    trigger_cache[tech["name"]] = sorted(merged_triggers)
                elif tech["name"] not in trigger_cache:
                    trigger_cache[tech["name"]] = None

        modern_armor_prefixes = frozenset(
            tech_name.partition("_")[0]
            for tech_name, triggers in trigger_cache.items()
            if MODERN_ARMOR_TRIGGER in (triggers or [])
        )
        context = graph, trigger_cache, modern_armor_prefixes
        self._dependency_contexts[technology_directory] = context
        return context

    def get_file_patterns(self) -> list[str]:
        return [
            "armor_*.txt",
            "tanks_*.txt",
        ]

    def get_archetype_mappings(self) -> dict[str, str]:
        return {
            # Light armor
            "light_tank_chassis": "WA_AI_RESEARCH_needs_light_armor",
            "light_spaa_tank_chassis": "WA_AI_RESEARCH_needs_light_self_propelled_aa",
            "light_tank_artillery_chassis": "WA_AI_RESEARCH_needs_light_self_propelled_guns",
            "light_tank_destroyer_chassis": "WA_AI_RESEARCH_needs_light_tank_destroyers",
            "light_assault_tank_chassis": "WA_AI_RESEARCH_needs_light_assault",
            "light_infantry_support_tank_chassis": "WA_AI_RESEARCH_needs_light_infantry_support",

            # Medium armor
            "medium_tank_chassis": "WA_AI_RESEARCH_needs_medium_armor",
            "medium_tank_support_chassis": "WA_AI_RESEARCH_needs_medium_armor",
            "medium_spaa_tank_chassis": "WA_AI_RESEARCH_needs_medium_self_propelled_aa",
            "medium_tank_artillery_chassis": "WA_AI_RESEARCH_needs_medium_self_propelled_guns",
            "medium_tank_destroyer_chassis": "WA_AI_RESEARCH_needs_medium_tank_destroyers",
            "medium_assault_tank_chassis": "WA_AI_RESEARCH_needs_medium_assault",
            "medium_infantry_support_tank_chassis": "WA_AI_RESEARCH_needs_medium_infantry_support",

            # Heavy armor
            "heavy_tank_chassis": "WA_AI_RESEARCH_needs_heavy_armor",
            "heavy_spaa_tank_chassis": "WA_AI_RESEARCH_needs_heavy_self_propelled_aa",
            "heavy_tank_artillery_chassis": "WA_AI_RESEARCH_needs_heavy_self_propelled_guns",
            "heavy_tank_destroyer_chassis": "WA_AI_RESEARCH_needs_heavy_tank_destroyers",
            "heavy_assault_tank_chassis": "WA_AI_RESEARCH_needs_heavy_assault",
            "heavy_infantry_support_tank_chassis": "WA_AI_RESEARCH_needs_heavy_infantry_support",

            # Super heavy armor (treated as heavy)
            "super_heavy_tank_chassis": "WA_AI_RESEARCH_needs_heavy_armor",
            "super_heavy_spaa_tank_chassis": "WA_AI_RESEARCH_needs_heavy_self_propelled_aa",
            "super_heavy_tank_artillery_chassis": "WA_AI_RESEARCH_needs_heavy_self_propelled_guns",
            "super_heavy_tank_destroyer_chassis": "WA_AI_RESEARCH_needs_heavy_tank_destroyers",

            # Modern armor
            "modern_tank_chassis": "WA_AI_RESEARCH_needs_modern_armor",
            "modern_spaa_tank_chassis": "WA_AI_RESEARCH_needs_modern_self_propelled_aa",
            "modern_tank_artillery_chassis": "WA_AI_RESEARCH_needs_modern_self_propelled_guns",
            "modern_tank_destroyer_chassis": "WA_AI_RESEARCH_needs_modern_tank_destroyers",
            "modern_assault_tank_chassis": "WA_AI_RESEARCH_needs_modern_assault",
            "modern_infantry_support_tank_chassis": "WA_AI_RESEARCH_needs_modern_infantry_support",

            # Armored cars
            "armored_car_chassis": "WA_AI_RESEARCH_needs_armored_cars",

            # Mechanized
            "mechanized_chassis": "WA_AI_RESEARCH_needs_mechanized",
            "amphibious_mechanized_chassis": "WA_AI_RESEARCH_needs_mechanized",
            "mechanized_td_equipment": "WA_AI_RESEARCH_needs_mechanized_tank_destroyers",
            "mechanized_artillery_equipment": "WA_AI_RESEARCH_needs_mechanized_self_propelled_guns",
            "mechanized_aa_equipment": "WA_AI_RESEARCH_needs_mechanized_self_propelled_aa",
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
            "cat_light_tank_destroyer": "WA_AI_RESEARCH_needs_light_tank_destroyers",
            "cat_medium_tank_destroyer": "WA_AI_RESEARCH_needs_medium_tank_destroyers",
            "cat_heavy_tank_destroyer": "WA_AI_RESEARCH_needs_heavy_tank_destroyers",
            "cat_modern_tank_destroyer": "WA_AI_RESEARCH_needs_modern_tank_destroyers",
            "cat_light_td": "WA_AI_RESEARCH_needs_light_tank_destroyers",
            "cat_medium_td": "WA_AI_RESEARCH_needs_medium_tank_destroyers",
            "cat_heavy_td": "WA_AI_RESEARCH_needs_heavy_tank_destroyers",
            "cat_modern_td": "WA_AI_RESEARCH_needs_modern_tank_destroyers",
            "cat_tank_destroyer": "WA_AI_RESEARCH_needs_tank_destroyers",
            "cat_light_spg": "WA_AI_RESEARCH_needs_light_self_propelled_guns",
            "cat_medium_spg": "WA_AI_RESEARCH_needs_medium_self_propelled_guns",
            "cat_heavy_spg": "WA_AI_RESEARCH_needs_heavy_self_propelled_guns",
            "cat_modern_spg": "WA_AI_RESEARCH_needs_modern_self_propelled_guns",
            "cat_light_assault_spg": "WA_AI_RESEARCH_needs_light_assault",
            "cat_medium_assault_spg": "WA_AI_RESEARCH_needs_medium_assault",
            "cat_heavy_assault_spg": "WA_AI_RESEARCH_needs_heavy_assault",
            "cat_modern_assault_spg": "WA_AI_RESEARCH_needs_modern_assault",
            "cat_spg": "WA_AI_RESEARCH_needs_self_propelled_guns",
            "cat_light_sp_aa": "WA_AI_RESEARCH_needs_light_self_propelled_aa",
            "cat_medium_sp_aa": "WA_AI_RESEARCH_needs_medium_self_propelled_aa",
            "cat_heavy_sp_aa": "WA_AI_RESEARCH_needs_heavy_self_propelled_aa",
            "cat_modern_sp_aa": "WA_AI_RESEARCH_needs_modern_self_propelled_aa",
            "cat_light_spaa": "WA_AI_RESEARCH_needs_light_self_propelled_aa",
            "cat_medium_spaa": "WA_AI_RESEARCH_needs_medium_self_propelled_aa",
            "cat_heavy_spaa": "WA_AI_RESEARCH_needs_heavy_self_propelled_aa",
            "cat_modern_spaa": "WA_AI_RESEARCH_needs_modern_self_propelled_aa",
            "cat_sp_aa": "WA_AI_RESEARCH_needs_self_propelled_aa",
            "cat_light_infantry_support": "WA_AI_RESEARCH_needs_light_infantry_support",
            "cat_medium_infantry_support": "WA_AI_RESEARCH_needs_medium_infantry_support",
            "cat_heavy_infantry_support": "WA_AI_RESEARCH_needs_heavy_infantry_support",
            "cat_modern_infantry_support": "WA_AI_RESEARCH_needs_modern_infantry_support",
        }

    def get_name_patterns(self) -> list[tuple[str, str | list[str]]]:
        return [
            # Exact one-off technology names
            (r"^lend_lease_truck$", "WA_AI_RESEARCH_needs_trucks"),

            # Armored cars (very specific)
            (r"scout_car|armoured_car|armored_car", "WA_AI_RESEARCH_needs_armored_cars"),

            # Assault and infantry-support tanks
            (r"^(?=.*light)(?=.*assault)", "WA_AI_RESEARCH_needs_light_assault"),
            (r"^(?=.*medium)(?=.*assault)", "WA_AI_RESEARCH_needs_medium_assault"),
            (r"^(?=.*(?:super_heavy|heavy))(?=.*assault)", "WA_AI_RESEARCH_needs_heavy_assault"),
            (r"^(?=.*modern)(?=.*assault)", "WA_AI_RESEARCH_needs_modern_assault"),
            (r"^(?=.*light)(?=.*infantry_support)", "WA_AI_RESEARCH_needs_light_infantry_support"),
            (r"^(?=.*medium)(?=.*infantry_support)", "WA_AI_RESEARCH_needs_medium_infantry_support"),
            (r"^(?=.*(?:super_heavy|heavy))(?=.*infantry_support)", "WA_AI_RESEARCH_needs_heavy_infantry_support"),
            (r"^(?=.*modern)(?=.*infantry_support)", "WA_AI_RESEARCH_needs_modern_infantry_support"),

            # Tank destroyers (specific)
            (r"^(?=.*mechani[sz]ed)(?=.*(?:_td(?:_|$)|tank_destroyer))", "WA_AI_RESEARCH_needs_mechanized_tank_destroyers"),
            (r"^(?=.*light)(?=.*(?:_td(?:_|$)|tank_destroyer))", "WA_AI_RESEARCH_needs_light_tank_destroyers"),
            (r"^(?=.*medium)(?=.*(?:_td(?:_|$)|tank_destroyer))", "WA_AI_RESEARCH_needs_medium_tank_destroyers"),
            (r"^(?=.*(?:super_heavy|heavy))(?=.*(?:_td(?:_|$)|tank_destroyer))", "WA_AI_RESEARCH_needs_heavy_tank_destroyers"),
            (r"^(?=.*modern)(?=.*(?:_td(?:_|$)|tank_destroyer))", "WA_AI_RESEARCH_needs_modern_tank_destroyers"),
            (r"_td_|_td$|tank_destroyer", "WA_AI_RESEARCH_needs_tank_destroyers"),

            # Self-propelled artillery (specific)
            (r"^(?=.*mechani[sz]ed)(?=.*(?:artillery|_spg(?:_|$)|sp_artillery))", "WA_AI_RESEARCH_needs_mechanized_self_propelled_guns"),
            (r"^(?=.*light)(?=.*(?:_spg(?:_|$)|sp_artillery))", "WA_AI_RESEARCH_needs_light_self_propelled_guns"),
            (r"^(?=.*medium)(?=.*(?:_spg(?:_|$)|sp_artillery))", "WA_AI_RESEARCH_needs_medium_self_propelled_guns"),
            (r"^(?=.*(?:super_heavy|heavy))(?=.*(?:_spg(?:_|$)|sp_artillery))", "WA_AI_RESEARCH_needs_heavy_self_propelled_guns"),
            (r"^(?=.*modern)(?=.*(?:_spg(?:_|$)|sp_artillery))", "WA_AI_RESEARCH_needs_modern_self_propelled_guns"),
            (r"_spg_|_spg$|sp_artillery|infantry_support", "WA_AI_RESEARCH_needs_self_propelled_guns"),

            # Self-propelled AA (specific)
            (r"^(?=.*mechani[sz]ed)(?=.*(?:_aa(?:_|$)|_spaa(?:_|$)|sp_anti_air))", "WA_AI_RESEARCH_needs_mechanized_self_propelled_aa"),
            (r"^(?=.*light)(?=.*(?:_aa(?:_|$)|_spaa(?:_|$)|sp_anti_air))", "WA_AI_RESEARCH_needs_light_self_propelled_aa"),
            (r"^(?=.*medium)(?=.*(?:_aa(?:_|$)|_spaa(?:_|$)|sp_anti_air))", "WA_AI_RESEARCH_needs_medium_self_propelled_aa"),
            (r"^(?=.*(?:super_heavy|heavy))(?=.*(?:_aa(?:_|$)|_spaa(?:_|$)|sp_anti_air))", "WA_AI_RESEARCH_needs_heavy_self_propelled_aa"),
            (r"^(?=.*modern)(?=.*(?:_aa(?:_|$)|_spaa(?:_|$)|sp_anti_air))", "WA_AI_RESEARCH_needs_modern_self_propelled_aa"),
            (r"_aa_|_aa$|_spaa_|sp_anti_air", "WA_AI_RESEARCH_needs_self_propelled_aa"),

            # Amphibious
            (r"amphibious|amph_", "WA_AI_RESEARCH_needs_amphibious_mechanized"),

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

        # Parse tank chassis and mechanized variant files.
        equipment_files = (
            list(equipment_dir.glob("*tank*.txt"))
            + list(equipment_dir.glob("*chassis*.txt"))
            + list(equipment_dir.glob("*mechanized*.txt"))
        )

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
                    return get_tiered_variant_trigger(
                        archetype_lower, eq_lower, "td"
                    ) or "WA_AI_RESEARCH_needs_tank_destroyers"

                # SPG / Infantry support variants
                if '_spg_' in eq_lower or '_spg' == eq_lower[-4:] or 'artillery' in archetype_lower:
                    return get_tiered_variant_trigger(
                        archetype_lower, eq_lower, "spg"
                    ) or "WA_AI_RESEARCH_needs_self_propelled_guns"
                if 'infantry_support' in archetype_lower:
                    return get_tiered_variant_trigger(
                        archetype_lower, eq_lower, "infantry_support"
                    ) or "WA_AI_RESEARCH_needs_self_propelled_guns"
                if 'assault' in archetype_lower and 'tank' in archetype_lower:
                    return get_tiered_variant_trigger(
                        archetype_lower, eq_lower, "assault"
                    )

                # AA variants
                if '_aa_' in eq_lower or '_aa' == eq_lower[-3:] or 'aa_chassis' in archetype_lower:
                    return get_tiered_variant_trigger(
                        archetype_lower, eq_lower, "spaa"
                    ) or "WA_AI_RESEARCH_needs_self_propelled_aa"

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

        # Find all tech definitions
        techs = self.find_tech_definitions(content)
        graph, trigger_cache, modern_armor_prefixes = self.get_dependency_context(
            filepath.parent
        )

        # Second pass: Propagate mainline armor dependencies while keeping
        # specialized tank variants on their direct role-and-size trigger.
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
            replacement_start, has_generated_comment = get_generated_comment_start(
                content, block_start
            )

            resolved_triggers = resolve_armor_trigger_set(
                tech_name, graph, trigger_cache, modern_armor_prefixes
            )

            if not resolved_triggers:
                stats.unknown += 1
                stats.errors.append(f"Could not determine trigger for {tech_name}")
                continue

            # Existing standardized blocks still need regeneration whenever
            # their trigger set no longer matches the resolver.
            needs_update = self.needs_update(block_content, tech_name, tech_block)
            if not has_generated_comment:
                needs_update = True
            if not needs_update:
                found_triggers = set(
                    re.findall(r"WA_AI_RESEARCH_needs_\w+", block_content)
                )
                if found_triggers != resolved_triggers:
                    needs_update = True

            if not needs_update:
                stats.skipped += 1
                continue

            # Get start_year
            start_year = extract_start_year(tech_block, block_content)
            if start_year is None:
                stats.errors.append(f"Could not find start_year for {tech_name}")
                stats.skipped += 1
                continue

            # Generate new block
            triggers = sorted(resolved_triggers)
            generated_ai_will_do = generate_ai_will_do_block(
                triggers, start_year, indent="\t\t"
            )
            new_block = f"\t\t{GENERATED_CODE_COMMENT}\n{generated_ai_will_do}"

            # Replace the block
            content = content[:replacement_start] + new_block + content[block_end:]
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
    base_path = Path(__file__).resolve().parents[3]
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
