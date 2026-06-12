"""
AI Research Refactor Script for HOI4 World Ablaze

This script parses HOI4 technology files and updates old ai_will_do patterns
to the new standardized pattern using WA_AI_RESEARCH triggers.

Old pattern:
    ai_will_do = {
        factor = 3/4
        modifier = { factor = 30; date > "YEAR.1.1" }
        modifier = { factor = 30; date > "YEAR+1.1.1" }
        modifier = { factor = 30; date > "YEAR+2.1.1" }
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

# Global equipment archetype cache (built once, used for all tech files)
EQUIPMENT_ARCHETYPE_CACHE: dict[str, str] = {}

# Mapping from equipment archetype to research trigger
ARCHETYPE_TO_TRIGGER = {
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
    
    # Super heavy armor
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


# Mapping from tech categories to research triggers
CATEGORY_TO_TRIGGER = {
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
    
    # Infantry categories
    "infantry_weapons": "WA_AI_RESEARCH_needs_infantry_weapons",
    "heavy_infantry_weapons": "WA_AI_RESEARCH_needs_infantry_weapons",
    
    # Artillery categories
    "artillery": "WA_AI_RESEARCH_needs_line_artillery",
    "cat_anti_tank": "WA_AI_RESEARCH_needs_anti_tank",
    "heavy_anti_tank": "WA_AI_RESEARCH_needs_anti_tank",
    "cat_anti_air": "WA_AI_RESEARCH_needs_anti_air",
    "heavy_anti_air": "WA_AI_RESEARCH_needs_anti_air",
    "mot_heavy_artillery": "WA_AI_RESEARCH_needs_heavy_artillery",
    
    # Special Forces categories
    "para_tech": "WA_AI_RESEARCH_needs_paratroopers",
    "marine_tech": "WA_AI_RESEARCH_needs_marines",
    "mountaineers_tech": "WA_AI_RESEARCH_needs_mountaineers",
    "paratroopers_doctrine": "WA_AI_RESEARCH_needs_paratroopers",
    "cat_marines_doctrine": "WA_AI_RESEARCH_needs_marines",
    "mountaineers_doctrine": "WA_AI_RESEARCH_needs_mountaineers",
}

# Tech name patterns to triggers (fallback when category doesn't match)
# Ordered by specificity (more specific patterns first)
TECH_NAME_PATTERNS = [
    # Armored cars (very specific)
    (r"scout_car|armoured_car|armored_car", "WA_AI_RESEARCH_needs_armored_cars"),
    
    # Tank destroyers (specific)
    # Match _td_ (middle), _td$ (end), or tank_destroyer
    (r"_td_|_td$|tank_destroyer", "WA_AI_RESEARCH_needs_tank_destroyers"),
    
    # Self-propelled artillery (specific)
    # Match _spg_ (middle), _spg$ (end), or sp_artillery/infantry_support
    (r"_spg_|_spg$|sp_artillery|infantry_support", "WA_AI_RESEARCH_needs_self_propelled_artillery"),
    
    # Self-propelled AA (specific)
    # Match _aa_ (middle), _aa$ (end), _spaa_, or sp_anti_air
    (r"_aa_|_aa$|_spaa_|sp_anti_air", "WA_AI_RESEARCH_needs_self_propelled_aa"),
    
    # Pack artillery (specific)
    (r"pack_artillery|pack_art", "WA_AI_RESEARCH_needs_pack_artillery"),
    
    # Heavy artillery (specific)
    (r"heavy_artillery|heavy_art|mot_heavy", "WA_AI_RESEARCH_needs_heavy_artillery"),
    
    # Rocket artillery (specific)
    (r"rocket_artillery|rocket_art|katyusha|nebelwerfer|calliope", "WA_AI_RESEARCH_needs_rocket_artillery"),
    
    # Special Forces (specific)
    (r"paratrooper|paratroopers|_para_|paras_", "WA_AI_RESEARCH_needs_paratroopers"),
    (r"_marine|marines|_marines_", "WA_AI_RESEARCH_needs_marines"),
    (r"mountaineer|mountaineers|_mountaineer", "WA_AI_RESEARCH_needs_mountaineers"),
    
    # Anti-tank (specific)
    (r"anti_tank|anti_tank_gun|at_gun", "WA_AI_RESEARCH_needs_anti_tank"),
    
    # Anti-air (specific)
    (r"anti_air|anti_aircraft|aa_gun", "WA_AI_RESEARCH_needs_anti_air"),
    
    # Light armor (less specific)
    (r"light_\d|light_tank|light_chassis", "WA_AI_RESEARCH_needs_light_armor"),
    
    # Medium armor (less specific)
    (r"medium_\d|medium_tank|medium_chassis", "WA_AI_RESEARCH_needs_medium_armor"),
    
    # Heavy armor (less specific)
    (r"heavy_\d|heavy_tank|heavy_chassis", "WA_AI_RESEARCH_needs_heavy_armor"),
    
    # Modern armor (less specific)
    (r"modern_\d|modern_tank|modern_chassis", "WA_AI_RESEARCH_needs_modern_armor"),
    
    # Mechanized (less specific)
    (r"mechanized|mechanised", "WA_AI_RESEARCH_needs_mechanized"),
    
    # Motorized (less specific)
    (r"motorised|motorized", "WA_AI_RESEARCH_needs_trucks"),
    
    # Infantry weapons (fallback for infantry techs)
    (r"infantry_weapons|infantry_equipment", "WA_AI_RESEARCH_needs_infantry_weapons"),
    
    # Artillery (fallback for artillery techs)
    (r"artillery", "WA_AI_RESEARCH_needs_line_artillery"),
]


def build_equipment_archetype_cache(equipment_dir: Path) -> dict[str, str]:
    """
    Parse all equipment files and build a mapping of equipment_name -> archetype.
    
    Args:
        equipment_dir: Path to common/units/equipment directory
    
    Returns:
        Dictionary mapping equipment name to its archetype
    """
    global EQUIPMENT_ARCHETYPE_CACHE
    
    if EQUIPMENT_ARCHETYPE_CACHE:
        return EQUIPMENT_ARCHETYPE_CACHE
    
    cache = {}
    
    # Only parse tank chassis files (they contain the relevant equipment)
    equipment_files = list(equipment_dir.glob("*tank*.txt")) + list(equipment_dir.glob("*chassis*.txt"))
    
    for eq_file in equipment_files:
        try:
            with open(eq_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # Find all equipment definitions with archetype
            # Pattern: equipment_name = { ... archetype = archetype_name ... }
            eq_pattern = re.compile(r'^\t([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\{', re.MULTILINE)
            
            for match in eq_pattern.finditer(content):
                eq_name = match.group(1)
                eq_start = match.end() - 1
                
                # Skip non-equipment blocks
                if eq_name in ('equipments', 'upgrades', 'resources', 'limit', 'if', 'OR', 'AND', 'NOT'):
                    continue
                
                # Find matching brace
                brace_count = 0
                eq_end = eq_start
                for i, char in enumerate(content[eq_start:]):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            eq_end = eq_start + i + 1
                            break
                
                if eq_end <= eq_start:
                    continue
                
                eq_block = content[eq_start:eq_end]
                
                # Extract archetype
                arch_match = re.search(r'archetype\s*=\s*([a-zA-Z_][a-zA-Z0-9_]*)', eq_block)
                if arch_match:
                    archetype = arch_match.group(1)
                    cache[eq_name] = archetype
        except Exception:
            continue
    
    EQUIPMENT_ARCHETYPE_CACHE = cache
    return cache


def extract_enable_equipments(tech_block: str) -> list[str]:
    """
    Extract equipment names from enable_equipments block in a technology.
    
    Args:
        tech_block: The technology block content
    
    Returns:
        List of equipment names
    """
    equipments = []
    
    # Find enable_equipments block
    eq_match = re.search(r'enable_equipments\s*=\s*\{([^}]+)\}', tech_block, re.DOTALL)
    if eq_match:
        eq_content = eq_match.group(1)
        # Extract all equipment names (words on their own lines or separated by whitespace)
        eq_names = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)', eq_content)
        equipments.extend(eq_names)
    
    return equipments


def get_trigger_from_equipment(tech_block: str, archetype_cache: dict[str, str]) -> Optional[str]:
    """
    Determine the research trigger based on equipment archetype.
    
    Args:
        tech_block: The technology block content
        archetype_cache: Mapping of equipment_name -> archetype
    
    Returns:
        Trigger name or None if no match
    """
    equipments = extract_enable_equipments(tech_block)
    
    for eq_name in equipments:
        if eq_name in archetype_cache:
            archetype = archetype_cache[eq_name]
            
            # Try direct archetype match
            if archetype in ARCHETYPE_TO_TRIGGER:
                return ARCHETYPE_TO_TRIGGER[archetype]
            
            # Try pattern matching on archetype name
            archetype_lower = archetype.lower()
            
            # Tank destroyer variants
            if '_td_' in eq_name.lower() or 'tank_destroyer' in archetype_lower or '_td' == eq_name.lower()[-3:]:
                return "WA_AI_RESEARCH_needs_tank_destroyers"
            
            # SPG / Infantry support variants
            if '_spg_' in eq_name.lower() or 'artillery' in archetype_lower or 'infantry_support' in archetype_lower or '_spg' == eq_name.lower()[-4:]:
                return "WA_AI_RESEARCH_needs_self_propelled_artillery"
            
            # AA variants
            if '_aa_' in eq_name.lower() or 'aa_chassis' in archetype_lower or '_aa' == eq_name.lower()[-3:]:
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
            if 'support' in archetype_lower and 'medium' in archetype_lower:
                return "WA_AI_RESEARCH_needs_medium_armor"
            if 'support' in archetype_lower and 'light' in archetype_lower:
                return "WA_AI_RESEARCH_needs_light_armor"
            if 'support' in archetype_lower and 'heavy' in archetype_lower:
                return "WA_AI_RESEARCH_needs_heavy_armor"
    
    return None


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


def extract_dependencies(tech_block: str) -> list[str]:
    """Extract dependency tech names from a technology block."""
    dependencies = []
    dep_match = re.search(r'dependencies\s*=\s*\{([^}]+)\}', tech_block, re.DOTALL)
    if dep_match:
        dep_content = dep_match.group(1)
        # Find all tech names in dependencies (format: tech_name = level)
        dep_techs = re.findall(r'(\w+)\s*=\s*\d+', dep_content)
        dependencies.extend(dep_techs)
    return dependencies


def extract_leads_to_techs(tech_block: str) -> list[str]:
    """
    Extract all leads_to_tech values from path blocks within a technology block.
    
    Args:
        tech_block: The technology block content
    
    Returns:
        List of technology names that this tech leads to
    """
    leads_to_techs = []
    
    # Find all path blocks and extract leads_to_tech values
    # Pattern matches: path = { ... leads_to_tech = tech_name ... }
    path_pattern = re.compile(r'path\s*=\s*\{', re.MULTILINE)
    
    for path_match in path_pattern.finditer(tech_block):
        path_start = path_match.end() - 1  # Position of '{'
        
        # Find matching closing brace
        brace_count = 0
        path_end = path_start
        for i, char in enumerate(tech_block[path_start:]):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    path_end = path_start + i + 1
                    break
        
        if path_end > path_start:
            path_content = tech_block[path_start:path_end]
            
            # Extract leads_to_tech = tech_name
            leads_match = re.search(r'leads_to_tech\s*=\s*([a-zA-Z_][a-zA-Z0-9_]*)', path_content)
            if leads_match:
                leads_to_techs.append(leads_match.group(1))
    
    return leads_to_techs


def build_tech_graph(content: str) -> Tuple[dict[str, list[str]], dict[str, list[str]], dict[str, list[str]]]:
    """
    Build dependency graphs of technologies from leads_to_tech and dependencies relationships.
    
    Args:
        content: The file content string
    
    Returns:
        Tuple of (forward_graph, reverse_dep_graph, prereq_graph) where:
        - forward_graph: tech_name -> list of child tech names (techs this leads to)
        - reverse_dep_graph: tech_name -> list of parent tech names (techs that depend on this)
        - prereq_graph: tech_name -> list of prerequisite tech names (techs this depends on)
    """
    forward_graph: dict[str, list[str]] = {}
    reverse_dep_graph: dict[str, list[str]] = {}
    prereq_graph: dict[str, list[str]] = {}
    
    # Find all technology definitions
    # Accept either tabs or spaces for indentation (some files use spaces)
    tech_pattern = re.compile(r'^([\t ]*)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\{', re.MULTILINE)
    matches = list(tech_pattern.finditer(content))
    
    for match in matches:
        tech_name = match.group(2)
        tech_start = match.start()
        brace_start = match.end() - 1
        
        # Skip non-technology blocks
        if tech_name in ('technologies', 'categories', 'path', 'folder', 'sub_technologies', 
                        'enable_equipments', 'enable_equipment_modules', 'modifier', 'allow',
                        'allow_branch', 'on_research_complete', 'research_cost_coeff',
                        'XOR', 'OR', 'AND', 'NOT', 'dependencies', 'if', 'limit',
                        'create_equipment_variant', 'ai_will_do', 'position', 'name', 'x', 'y',
                        'category_special_forces', 'amphibious', 'enable_equipments', 'enable_subunits'):
            continue
        
        # Find the end of this technology block
        brace_count = 0
        tech_end = brace_start
        for i, char in enumerate(content[brace_start:]):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    tech_end = brace_start + i + 1
                    break
        
        if tech_end <= brace_start:
            continue
        
        tech_block = content[tech_start:tech_end]
        
        # Extract leads_to_tech relationships (forward graph)
        leads_to_techs = extract_leads_to_techs(tech_block)
        if leads_to_techs:
            forward_graph[tech_name] = leads_to_techs
            # Also build prerequisites graph: if A leads_to B, then A is a prerequisite of B
            for child_tech in leads_to_techs:
                if child_tech not in prereq_graph:
                    prereq_graph[child_tech] = []
                if tech_name not in prereq_graph[child_tech]:
                    prereq_graph[child_tech].append(tech_name)
        
        # Extract dependencies (reverse dependency graph AND prerequisites graph)
        dependencies = extract_dependencies(tech_block)
        if dependencies:
            if tech_name not in prereq_graph:
                prereq_graph[tech_name] = []
            prereq_graph[tech_name].extend(dependencies)
        for dep_tech in dependencies:
            if dep_tech not in reverse_dep_graph:
                reverse_dep_graph[dep_tech] = []
            reverse_dep_graph[dep_tech].append(tech_name)
    
    return forward_graph, reverse_dep_graph, prereq_graph


def get_special_forces_type(triggers: list[str]) -> Optional[str]:
    """
    Determine if triggers represent a single special forces type.
    
    Args:
        triggers: List of trigger names
    
    Returns:
        The special forces type ('paratroopers', 'marines', 'mountaineers') if exactly one type,
        None if multiple types or not special forces
    """
    sf_types = []
    for trigger in triggers:
        if 'paratrooper' in trigger.lower():
            sf_types.append('paratroopers')
        elif 'marine' in trigger.lower():
            sf_types.append('marines')
        elif 'mountaineer' in trigger.lower():
            sf_types.append('mountaineers')
    
    # Return the type only if there's exactly one type
    if len(set(sf_types)) == 1:
        return sf_types[0]
    return None


def get_reachable_triggers(
    tech_name: str,
    forward_graph: dict[str, list[str]],
    prereq_graph: dict[str, list[str]],
    trigger_cache: dict[str, Optional[list[str]]],
    categories_cache: dict[str, list[str]],
    visited: Optional[set[str]] = None
) -> set[str]:
    """
    Recursively find all research triggers reachable from a technology via forward dependencies.
    
    If a tech is on the path to heavy tanks (even indirectly), it needs the heavy trigger.
    This ensures AI will research all prerequisite techs to reach their desired tank type.
    
    For special forces techs: only propagate triggers from techs of the SAME type.
    This prevents paratroopers from requiring marines/mountaineers just because they lead to
    shared techs like commandos that require multiple types.
    
    Example: usa_medium_tank_chassis_1 → usa_medium_tank_chassis_2 → ... → heavy tanks
    usa_medium_tank_chassis_1 needs heavy trigger so AI researching heavy tanks will research it.
    
    Example: ger_paratroopers → ger_tech_commandos (requires all 3 types)
    ger_paratroopers should NOT get marines/mountaineers triggers from commandos.
    
    Args:
        tech_name: The technology to start from
        forward_graph: Dictionary mapping tech_name -> list of child tech names (techs this leads to)
        prereq_graph: Dictionary mapping tech_name -> list of prerequisite tech names - NOT USED
        trigger_cache: Dictionary mapping tech_name -> list of trigger names (or None)
        categories_cache: Dictionary mapping tech_name -> list of category names
        visited: Set of already visited techs (for cycle detection)
    
    Returns:
        Set of trigger names (e.g., {"WA_AI_RESEARCH_needs_heavy_armor", "WA_AI_RESEARCH_needs_medium_armor"})
    """
    if visited is None:
        visited = set()
    
    # Prevent infinite loops from circular references
    if tech_name in visited:
        return set()
    
    visited.add(tech_name)
    triggers = set()
    
    # Add this tech's own triggers if it has any
    if tech_name in trigger_cache and trigger_cache[tech_name]:
        triggers.update(trigger_cache[tech_name])
    
    # Determine if this is a special forces tech and what type
    current_triggers = trigger_cache.get(tech_name, []) or []
    current_sf_type = get_special_forces_type(current_triggers)
    
    # Recursive forward: check ALL descendants (techs this leads to, recursively)
    # If ANY tech in the tree is heavy, this tech needs heavy trigger
    # BUT for special forces: only include triggers from techs of the same type
    if tech_name in forward_graph:
        for child_tech in forward_graph[tech_name]:
            child_triggers_list = trigger_cache.get(child_tech, []) or []
            child_sf_type = get_special_forces_type(child_triggers_list)
            
            # If current tech is a special forces tech, only follow children of the same type
            # Skip shared/combined techs (commandos, etc.) that require multiple types
            if current_sf_type is not None:
                if child_sf_type != current_sf_type:
                    # Child is different type or requires multiple types - skip it
                    continue
            
            child_triggers = get_reachable_triggers(
                child_tech, forward_graph, prereq_graph, trigger_cache, categories_cache, visited.copy()
            )
            
            # If current tech is special forces, filter child triggers to only same type
            if current_sf_type is not None:
                filtered_child_triggers = set()
                for trigger in child_triggers:
                    trigger_lower = trigger.lower()
                    if current_sf_type == 'paratroopers' and 'paratrooper' in trigger_lower:
                        filtered_child_triggers.add(trigger)
                    elif current_sf_type == 'marines' and 'marine' in trigger_lower:
                        filtered_child_triggers.add(trigger)
                    elif current_sf_type == 'mountaineers' and 'mountaineer' in trigger_lower:
                        filtered_child_triggers.add(trigger)
                    # Always include non-special-forces triggers (like date modifiers, etc.)
                    elif 'paratrooper' not in trigger_lower and 'marine' not in trigger_lower and 'mountaineer' not in trigger_lower:
                        filtered_child_triggers.add(trigger)
                triggers.update(filtered_child_triggers)
            else:
                # Not a special forces tech - include all triggers
                triggers.update(child_triggers)
    
    return triggers


def determine_special_forces_types(tech_name: str, categories: list[str], dependencies: list[str]) -> list[str]:
    """
    Determine which special forces types are needed for a tech.
    Returns a list of trigger names (e.g., ['WA_AI_RESEARCH_needs_marines', 'WA_AI_RESEARCH_needs_mountaineers']).
    """
    triggers = []
    sf_categories_found = set()
    
    # Check categories for special forces types
    for cat in categories:
        if cat in CATEGORY_TO_TRIGGER:
            trigger = CATEGORY_TO_TRIGGER[cat]
            if 'special_forces' in trigger.lower() or 'paratrooper' in trigger.lower() or 'marine' in trigger.lower() or 'mountaineer' in trigger.lower():
                sf_categories_found.add(cat)
                if trigger not in triggers:
                    triggers.append(trigger)
    
    # Check dependencies for special forces techs
    # Look for patterns like: _paratroopers, _marines, _tech_mountaineers, tech_commandos (which requires marines)
    # Use separate if statements (not elif) to catch all matching types
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
    
    # If no triggers found from categories/dependencies, try tech name patterns
    if not triggers:
        for pattern, trigger in TECH_NAME_PATTERNS:
            if 'paratrooper' in trigger.lower() or 'marine' in trigger.lower() or 'mountaineer' in trigger.lower():
                if re.search(pattern, tech_name, re.IGNORECASE):
                    if trigger not in triggers:
                        triggers.append(trigger)
    
    return triggers


def determine_trigger(tech_name: str, categories: list[str], file_path: Optional[Path] = None, tech_block: str = "", archetype_cache: dict[str, str] = None) -> Optional[str]:
    """
    Determine which WA_AI_RESEARCH trigger to use based on equipment archetype, tech name and categories.
    
    Priority:
    1. Equipment archetype (most reliable for armor techs)
    2. Tech name patterns
    3. Categories (as fallback)
    4. File-based inference
    
    Args:
        tech_name: Name of the technology
        categories: List of category strings from the tech definition
        file_path: Optional path to the file being processed (for context)
        tech_block: Optional full tech block content for equipment extraction
        archetype_cache: Optional equipment name -> archetype mapping
    
    Returns:
        Trigger name string or None if no match found
    """
    # First try equipment archetype (most reliable for armor)
    if tech_block and archetype_cache:
        archetype_trigger = get_trigger_from_equipment(tech_block, archetype_cache)
        if archetype_trigger:
            return archetype_trigger
    
    # Then try tech name patterns (ordered by specificity)
    for pattern, trigger in TECH_NAME_PATTERNS:
        if re.search(pattern, tech_name, re.IGNORECASE):
            return trigger
    
    # Then try categories (less reliable for armor - may have wrong category)
    for cat in categories:
        if cat in CATEGORY_TO_TRIGGER:
            return CATEGORY_TO_TRIGGER[cat]
    
    # Special handling for country-specific files based on filename
    if file_path:
        filename = file_path.name.lower()
        
        # Infantry files
        if filename.startswith('infantry_'):
            # Check for special forces techs first
            if re.search(r'paratrooper|paratroopers|_para_|paras_', tech_name, re.IGNORECASE):
                return "WA_AI_RESEARCH_needs_paratroopers"
            elif re.search(r'_marine|marines|_marines_', tech_name, re.IGNORECASE):
                return "WA_AI_RESEARCH_needs_marines"
            elif re.search(r'mountaineer|mountaineers|_mountaineer', tech_name, re.IGNORECASE):
                return "WA_AI_RESEARCH_needs_mountaineers"
            elif re.search(r'special_forces', tech_name, re.IGNORECASE):
                # Generic special forces tech - check categories to determine which type
                # This will be handled by category matching above, but fallback to checking if any SF type is needed
                # For now, return None to let category matching handle it
                pass
            return "WA_AI_RESEARCH_needs_infantry_weapons"
        
        # Special forces doctrine file
        if filename == 'special_forces_doctrine.txt':
            if re.search(r'paratrooper|paratroopers|paras_', tech_name, re.IGNORECASE):
                return "WA_AI_RESEARCH_needs_paratroopers"
            elif re.search(r'marine|marines', tech_name, re.IGNORECASE):
                return "WA_AI_RESEARCH_needs_marines"
            elif re.search(r'mountaineer|mountaineers|ski_troops|rangers', tech_name, re.IGNORECASE):
                return "WA_AI_RESEARCH_needs_mountaineers"
        
        # Artillery files - try to infer from tech name
        if filename.startswith('artillery_'):
            # Check tech name for specific types
            if re.search(r'pack', tech_name, re.IGNORECASE):
                return "WA_AI_RESEARCH_needs_pack_artillery"
            elif re.search(r'heavy', tech_name, re.IGNORECASE):
                return "WA_AI_RESEARCH_needs_heavy_artillery"
            elif re.search(r'rocket', tech_name, re.IGNORECASE):
                return "WA_AI_RESEARCH_needs_rocket_artillery"
            elif re.search(r'anti_tank|at_gun', tech_name, re.IGNORECASE):
                return "WA_AI_RESEARCH_needs_anti_tank"
            elif re.search(r'anti_air|aa_gun', tech_name, re.IGNORECASE):
                return "WA_AI_RESEARCH_needs_anti_air"
            else:
                # Default to line artillery
                return "WA_AI_RESEARCH_needs_line_artillery"
        
        # Armor files
        if filename.startswith('armor_'):
            if re.search(r'scout_car|armoured_car|armored_car', tech_name, re.IGNORECASE):
                return "WA_AI_RESEARCH_needs_armored_cars"
            elif re.search(r'_td_|_td$|tank_destroyer', tech_name, re.IGNORECASE):
                return "WA_AI_RESEARCH_needs_tank_destroyers"
            elif re.search(r'_spg_|_spg$|sp_artillery|infantry_support', tech_name, re.IGNORECASE):
                return "WA_AI_RESEARCH_needs_self_propelled_artillery"
            elif re.search(r'_aa_|_aa$|sp_anti_air', tech_name, re.IGNORECASE):
                return "WA_AI_RESEARCH_needs_self_propelled_aa"
            elif re.search(r'light', tech_name, re.IGNORECASE):
                return "WA_AI_RESEARCH_needs_light_armor"
            elif re.search(r'medium', tech_name, re.IGNORECASE):
                return "WA_AI_RESEARCH_needs_medium_armor"
            elif re.search(r'heavy', tech_name, re.IGNORECASE):
                return "WA_AI_RESEARCH_needs_heavy_armor"
            elif re.search(r'modern', tech_name, re.IGNORECASE):
                return "WA_AI_RESEARCH_needs_modern_armor"
            elif re.search(r'mechanized|mechanised', tech_name, re.IGNORECASE):
                return "WA_AI_RESEARCH_needs_mechanized"
            elif re.search(r'motorised|motorized', tech_name, re.IGNORECASE):
                return "WA_AI_RESEARCH_needs_trucks"
    
    return None


def is_old_pattern(ai_will_do_block: str) -> bool:
    """
    Check if ai_will_do block uses the old pattern (factor = 3/4/1/0.5/0.7 with date multipliers or tag modifiers).
    
    Old pattern characteristics:
    - Starts with factor = 3, 4, 1, 0.5, 0.7, or any numeric value
    - Has modifiers with date > patterns OR tag-specific modifiers without WA_AI_RESEARCH
    - Does NOT contain WA_AI_RESEARCH triggers
    - Simple patterns with just factor = X (no modifiers) are also old pattern
    """
    # Must not already be new pattern
    if 'WA_AI_RESEARCH' in ai_will_do_block:
        return False
    
    # Check for date > pattern (old style) - this is the key indicator
    has_date_multiplier = re.search(r'date\s*>\s*["\']?\d{4}', ai_will_do_block)
    
    # Check if there are any modifiers at all
    has_modifiers = 'modifier' in ai_will_do_block
    
    # Simple pattern: just factor = X with no modifiers (old pattern)
    if not has_modifiers:
        # Check if it's just a simple factor assignment
        if re.search(r'factor\s*=\s*[\d.]+', ai_will_do_block):
            return True
    
    # Check for factor = 3, 4, 1, or 0.5 at the start (with optional whitespace)
    # Also allow factor = 10 or 20 (used in doctrine techs)
    if re.search(r'factor\s*=\s*[34]', ai_will_do_block):
        if has_date_multiplier:
            return True
    
    # Check for factor = 1 with date multipliers (common in special forces)
    if re.search(r'factor\s*=\s*1\b', ai_will_do_block):
        if has_date_multiplier:
            return True
    
    # Check for factor = 0.5, 0.7, or other decimal values
    if re.search(r'factor\s*=\s*0\.[\d]+', ai_will_do_block):
        # If it has modifiers, check if they're old-style
        if has_modifiers:
            # Check for tag modifiers without WA_AI_RESEARCH (old pattern)
            if re.search(r'tag\s*=\s*(USA|GER|ENG|JAP|SOV|FRA|ITA)', ai_will_do_block):
                if not has_date_multiplier:
                    return True
        else:
            # Simple factor = 0.X with no modifiers is old pattern
            return True
    
    # Also check for modifier blocks with factor = 30 or 11 (old pattern multipliers)
    if re.search(r'modifier\s*=\s*\{[^}]*factor\s*=\s*(30|11)', ai_will_do_block, re.DOTALL):
        return True
    
    return False


def is_already_new_pattern(ai_will_do_block: str) -> bool:
    """
    Check if ai_will_do block already uses the new pattern.
    Returns False if it needs updating (e.g., only checks one type when it should check multiple,
    or uses old date pattern instead of new OR/AND pattern with unused research slots).
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
    
    # If it has WA_AI_RESEARCH, check if it's correctly checking multiple types
    # This will be handled by checking if the tech needs multiple types in process_file
    # For now, return True to skip - we'll handle multi-type updates separately
    return True


def has_excessive_blank_lines(ai_will_do_block: str) -> bool:
    """
    Check if an ai_will_do block has excessive blank lines (more than one consecutive blank line).
    """
    lines = ai_will_do_block.split('\n')
    consecutive_blanks = 0
    for line in lines:
        if line.strip() == '':
            consecutive_blanks += 1
            if consecutive_blanks > 1:
                return True
        else:
            consecutive_blanks = 0
    return False


def has_blank_lines_before_block(content: str, block_start: int) -> bool:
    """
    Check if there are excessive blank lines (more than 1) before the ai_will_do block,
    or if there's whitespace-only content between the previous line and ai_will_do.
    """
    # Find the start of the line containing ai_will_do
    line_start = content.rfind('\n', 0, block_start)
    if line_start == -1:
        line_start = 0
    else:
        line_start += 1
    
    # Check if there's only whitespace on this line before ai_will_do
    line_before_ai = content[line_start:block_start]
    if line_before_ai.strip() != '' and 'ai_will_do' not in line_before_ai:
        # There's other content on this line, that's wrong
        return True
    
    # Count consecutive blank lines before this line
    blank_line_count = 0
    pos = line_start - 1
    
    while pos >= 0:
        # Find start of previous line
        prev_line_start = content.rfind('\n', 0, pos)
        if prev_line_start == -1:
            prev_line_start = 0
        else:
            prev_line_start += 1
        
        line_content = content[prev_line_start:pos + 1].strip()
        
        if line_content == '':
            blank_line_count += 1
            if blank_line_count > 1:
                return True
        else:
            # Found non-blank line
            break
        
        pos = prev_line_start - 1
    
    return False


def needs_multi_type_update(tech_name: str, tech_block: str, ai_will_do_block: str) -> bool:
    """
    Check if a tech that already has WA_AI_RESEARCH needs updating to check multiple types.
    Returns True if the tech depends on multiple SF types but only checks one, or has excessive blank lines.
    """
    if 'WA_AI_RESEARCH' not in ai_will_do_block:
        return False
    
    # Check for excessive blank lines first
    if has_excessive_blank_lines(ai_will_do_block):
        return True
    
    categories = extract_categories(tech_block)
    dependencies = extract_dependencies(tech_block)
    
    # Determine how many SF types this tech needs
    sf_triggers = determine_special_forces_types(tech_name, categories, dependencies)
    
    # If it needs multiple types, check if the ai_will_do block checks all of them
    if len(sf_triggers) > 1:
        # Check if all triggers are present in the ai_will_do block
        for trigger in sf_triggers:
            if trigger not in ai_will_do_block:
                return True  # Missing at least one trigger
    
    return False


def generate_new_ai_will_do(triggers: list[str], start_year: int, indent: str = "\t\t") -> str:
    """
    Generate a new ai_will_do block with the specified trigger(s) and start_year.
    
    Args:
        triggers: List of trigger names (e.g., ['WA_AI_RESEARCH_needs_marines', 'WA_AI_RESEARCH_needs_mountaineers'])
        start_year: Start year for the tech
        indent: Indentation string
    """
    if not triggers:
        return ""
    
    # Generate clean format without extra blank lines
    lines = [f"{indent}ai_will_do = {{"]
    lines.append(f"{indent}\tfactor = 1")
    lines.append("")
    lines.append(f"{indent}\tmodifier = {{")
    lines.append(f"{indent}\t\tfactor = 0")
    
    # Build the NOT condition - require ANY trigger (OR logic)
    # Research if ANY of the triggers is needed, not ALL
    if len(triggers) == 1:
        lines.append(f"{indent}\t\tNOT = {{ {triggers[0]} = yes }}")
    else:
        # Multiple triggers - use OR condition (research if ANY trigger is needed)
        lines.append(f"{indent}\t\tNOT = {{")
        lines.append(f"{indent}\t\t\tOR = {{")
        for trigger in triggers:
            lines.append(f"{indent}\t\t\t\t{trigger} = yes")
        lines.append(f"{indent}\t\t\t}}")
        lines.append(f"{indent}\t\t}}")
    
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
    # Find ai_will_do = { (not commented out)
    # Look for the pattern, but check if it's on a commented line
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
        
        # Skip if the line is commented out (has # before ai_will_do)
        if '#' in line_prefix:
            # Check if # is before ai_will_do (not after)
            hash_pos = line_prefix.rfind('#')
            if hash_pos >= 0:
                # Check if there's only whitespace between # and ai_will_do
                between = line_prefix[hash_pos + 1:]
                if not between.strip() or between.strip().startswith('ai_will_do'):
                    continue  # This line is commented out, skip it
        
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
        
        # If we found a match but couldn't find closing brace, return it anyway
        # (shouldn't happen in valid files)
        return block_start, len(content), content[block_start:]
    
    return -1, -1, ""


def extract_tech_context(content: str, ai_will_do_pos: int) -> Tuple[str, str, int]:
    """
    Extract the tech name and full tech block containing this ai_will_do.
    Returns (tech_name, tech_block, tech_start_pos)
    """
    # Search backwards for the tech definition start
    # Look for pattern like "tech_name = {" before ai_will_do
    search_start = max(0, ai_will_do_pos - 3000)  # Look up to 3000 chars before
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


def process_file(filepath: Path, dry_run: bool = False, archetype_cache: dict[str, str] = None) -> Tuple[int, int, list[str]]:
    """
    Process a single technology file using a two-pass approach:
    1. First pass: Build tech graph and trigger cache
    2. Second pass: Process techs and use prerequisite checking to determine triggers
    
    Args:
        filepath: Path to the technology file
        dry_run: If True, don't write changes
        archetype_cache: Equipment name -> archetype mapping (built from equipment files)
    
    Returns (updated_count, skipped_count, messages)
    """
    messages = []
    updated_count = 0
    skipped_count = 0
    
    if archetype_cache is None:
        archetype_cache = {}
    
    # Check if file has BOM
    has_bom = False
    with open(filepath, 'rb') as f:
        first_bytes = f.read(3)
        has_bom = first_bytes == b'\xef\xbb\xbf'
    
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    original_content = content
    
    # ========================================================================
    # FIRST PASS: Build tech graph and trigger cache
    # ========================================================================
    forward_graph, reverse_dep_graph, prereq_graph = build_tech_graph(content)
    trigger_cache: dict[str, Optional[list[str]]] = {}
    categories_cache: dict[str, list[str]] = {}
    tech_positions: dict[str, Tuple[int, int]] = {}  # tech_name -> (start, end)
    tech_blocks_cache: dict[str, str] = {}  # tech_name -> tech_block content
    
    # Find all technology definitions
    # Accept either tabs or spaces for indentation (some files use spaces)
    tech_pattern = re.compile(r'^([\t ]*)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\{', re.MULTILINE)
    matches = list(tech_pattern.finditer(content))
    
    for match in matches:
        tech_name = match.group(2)
        tech_start = match.start()
        brace_start = match.end() - 1
        
        # Skip non-technology blocks
        if tech_name in ('technologies', 'categories', 'path', 'folder', 'sub_technologies', 
                        'enable_equipments', 'enable_equipment_modules', 'modifier', 'allow',
                        'allow_branch', 'on_research_complete', 'research_cost_coeff',
                        'XOR', 'OR', 'AND', 'NOT', 'dependencies', 'if', 'limit',
                        'create_equipment_variant', 'ai_will_do', 'position', 'name', 'x', 'y',
                        'category_special_forces', 'amphibious', 'enable_equipments', 'enable_subunits'):
            continue
        
        # Find the end of this technology block
        brace_count = 0
        tech_end = brace_start
        for i, char in enumerate(content[brace_start:]):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    tech_end = brace_start + i + 1
                    break
        
        if tech_end <= brace_start:
            continue
        
        tech_positions[tech_name] = (tech_start, tech_end)
        tech_block = content[tech_start:tech_end]
        tech_blocks_cache[tech_name] = tech_block
        
        # Determine triggers for this tech
        categories = extract_categories(tech_block)
        categories_cache[tech_name] = categories
        dependencies = extract_dependencies(tech_block)
        
        # Check if this is a special forces tech
        sf_triggers = determine_special_forces_types(tech_name, categories, dependencies)
        
        if sf_triggers:
            trigger_cache[tech_name] = sf_triggers
        else:
            # Not a special forces tech, use equipment archetype first, then categories
            trigger = determine_trigger(tech_name, categories, filepath, tech_block, archetype_cache)
            trigger_cache[tech_name] = [trigger] if trigger else None
    
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
                        'create_equipment_variant', 'ai_will_do', 'position', 'name', 'x', 'y',
                        'category_special_forces', 'amphibious', 'enable_equipments', 'enable_subunits'):
            continue
        
        if tech_name not in tech_positions:
            continue
        
        tech_start, tech_end = tech_positions[tech_name]
        tech_block = content[tech_start:tech_end]
        
        # Find ai_will_do block
        ai_block = find_ai_will_do_block(content, tech_start)
        if ai_block[0] == -1:
            continue
        
        block_start, block_end, block_content = ai_block
        
        # Check if this tech needs updating
        needs_multi_update = needs_multi_type_update(tech_name, tech_block, block_content)
        has_blank_before = has_blank_lines_before_block(content, block_start)
        
        # Check if date pattern needs updating (has WA_AI_RESEARCH but old date pattern)
        needs_date_update = False
        if 'WA_AI_RESEARCH' in block_content and 'date <' in block_content:
            if 'WA_AI_unused_research_slots' not in block_content:
                needs_date_update = True
        
        # Get all reachable triggers (including prerequisites) to check if trigger needs updating
        # This now checks prerequisites (techs this depends on) instead of reverse dependencies
        reachable_triggers = get_reachable_triggers(tech_name, forward_graph, prereq_graph, trigger_cache, categories_cache)
        # If no triggers found, try fallback
        if not reachable_triggers:
            if tech_name in trigger_cache and trigger_cache[tech_name]:
                reachable_triggers = set(trigger_cache[tech_name])
        
        # Check if trigger needs updating (has WA_AI_RESEARCH but wrong trigger)
        needs_trigger_update = False
        if 'WA_AI_RESEARCH' in block_content and reachable_triggers:
            # Extract all WA_AI_RESEARCH triggers from the block
            found_triggers = set(re.findall(r'WA_AI_RESEARCH_needs_\w+', block_content))
            # Check if the found triggers match the reachable triggers
            if found_triggers != reachable_triggers:
                needs_trigger_update = True
        
        # Skip if already using new pattern and doesn't need multi-type update and no blank lines before and no date update needed and no trigger update needed
        if is_already_new_pattern(block_content) and not needs_multi_update and not has_blank_before and not needs_date_update and not needs_trigger_update:
            continue
        
        # Check if it's the old pattern (if not already handled above)
        if not needs_multi_update and not has_blank_before and not needs_date_update and not needs_trigger_update and not is_old_pattern(block_content):
            continue
        
        # Get start_year
        start_year = extract_start_year(tech_block, block_content)
        if not start_year:
            messages.append(f"  WARNING: Could not find start_year for tech '{tech_name}'")
            skipped_count += 1
            continue
        
        # If no triggers found, skip (shouldn't happen, but handle gracefully)
        if not reachable_triggers:
            messages.append(f"  WARNING: Could not determine trigger for tech '{tech_name}'")
            skipped_count += 1
            continue
        
        triggers = sorted(list(reachable_triggers))  # Sort for consistent output
        
        # Use standard indentation (2 tabs for ai_will_do inside a tech definition)
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
        new_block = generate_new_ai_will_do(triggers, start_year, indent)
        
        # Add a single newline before the block if we removed blank lines
        if prefix_start < block_start:
            new_block = "\n" + indent + "ai_will_do" + new_block[new_block.find('ai_will_do') + len('ai_will_do'):]
        
        # Replace (including any blank lines before)
        content = content[:prefix_start] + new_block + content[block_end:]
        
        updated_count += 1
        trigger_str = " AND ".join(triggers) if len(triggers) > 1 else triggers[0]
        messages.append(f"  Updated: {tech_name} -> {trigger_str} (year: {start_year})")
    
    # Always rewrite file without BOM if it had BOM or content changed
    if (content != original_content or has_bom) and not dry_run:
        # Write UTF-8 without BOM (HOI4 parser doesn't handle BOM)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return updated_count, skipped_count, messages


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Refactor ai_will_do blocks in HOI4 tech files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    parser.add_argument('--file', type=str, help='Process a single file instead of all tech files')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed output')
    args = parser.parse_args()
    
    # Get the base path (parent of tools directory)
    base_path = Path(__file__).parent.parent
    tech_path = base_path / 'common' / 'technologies'
    equipment_path = base_path / 'common' / 'units' / 'equipment'
    
    # Build equipment archetype cache
    print("Building equipment archetype cache...")
    archetype_cache = build_equipment_archetype_cache(equipment_path)
    print(f"  Found {len(archetype_cache)} equipment definitions")
    
    if args.file:
        files = [Path(args.file)]
    else:
        # Process all technology files
        files = list(tech_path.glob('*.txt'))
    
    total_updated = 0
    total_skipped = 0
    
    print(f"Processing {len(files)} files...")
    if args.dry_run:
        print("(DRY RUN - no changes will be made)")
    print()
    
    for filepath in sorted(files):
        updated, skipped, messages = process_file(filepath, dry_run=args.dry_run, archetype_cache=archetype_cache)
        
        if updated > 0 or skipped > 0 or args.verbose:
            print(f"{filepath.name}: {updated} updated, {skipped} skipped")
            if args.verbose:
                for msg in messages:
                    print(msg)
        
        total_updated += updated
        total_skipped += skipped
    
    print()
    print(f"Total: {total_updated} blocks updated, {total_skipped} blocks skipped")


if __name__ == '__main__':
    main()
