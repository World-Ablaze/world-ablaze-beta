"""
Technology dependency graph building and traversal.

Provides utilities for building and navigating tech trees.
"""

import re
from dataclasses import dataclass, field
from typing import Optional

from .text_utils import extract_leads_to_techs, extract_dependencies
from .block_finder import find_matching_brace


@dataclass
class TechGraph:
    """
    Technology dependency graph.

    Attributes:
        forward: tech → children (techs this leads to via leads_to_tech)
        reverse: tech → parents (techs that lead to this)
        prerequisites: tech → dependencies (techs this depends on)
    """
    forward: dict[str, list[str]] = field(default_factory=dict)
    reverse: dict[str, list[str]] = field(default_factory=dict)
    prerequisites: dict[str, list[str]] = field(default_factory=dict)


def build_tech_graph(content: str) -> TechGraph:
    """
    Build dependency graph from tech file content.

    Args:
        content: The file content string

    Returns:
        TechGraph with forward, reverse, and prerequisites edges
    """
    graph = TechGraph()

    # Skip these block names (not actual techs)
    skip_blocks = frozenset({
        'technologies', 'categories', 'path', 'folder', 'sub_technologies',
        'enable_equipments', 'enable_equipment_modules', 'modifier', 'allow',
        'allow_branch', 'on_research_complete', 'research_cost_coeff',
        'XOR', 'OR', 'AND', 'NOT', 'dependencies', 'if', 'limit',
        'create_equipment_variant', 'ai_will_do', 'position', 'name', 'x', 'y',
        'category_special_forces', 'amphibious', 'enable_subunits'
    })

    # Find all technology definitions
    tech_pattern = re.compile(r'^([\t ]*)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\{', re.MULTILINE)

    for match in tech_pattern.finditer(content):
        tech_name = match.group(2)

        if tech_name in skip_blocks:
            continue

        tech_start = match.start()
        brace_start = match.end() - 1

        try:
            tech_end = find_matching_brace(content, brace_start) + 1
        except ValueError:
            continue

        tech_block = content[tech_start:tech_end]

        # Extract leads_to_tech relationships (forward graph)
        leads_to_techs = extract_leads_to_techs(tech_block)
        if leads_to_techs:
            graph.forward[tech_name] = leads_to_techs

            # Build reverse graph
            for child_tech in leads_to_techs:
                if child_tech not in graph.reverse:
                    graph.reverse[child_tech] = []
                if tech_name not in graph.reverse[child_tech]:
                    graph.reverse[child_tech].append(tech_name)

                # Also add to prerequisites (leads_to implies prerequisite)
                if child_tech not in graph.prerequisites:
                    graph.prerequisites[child_tech] = []
                if tech_name not in graph.prerequisites[child_tech]:
                    graph.prerequisites[child_tech].append(tech_name)

        # Extract explicit dependencies
        dependencies = extract_dependencies(tech_block)
        if dependencies:
            if tech_name not in graph.prerequisites:
                graph.prerequisites[tech_name] = []
            graph.prerequisites[tech_name].extend(dependencies)

    return graph


def get_reachable_techs(
    graph: TechGraph,
    start: str,
    direction: str = "forward",
    visited: Optional[set[str]] = None
) -> set[str]:
    """
    Get all techs reachable from start via graph edges.

    Args:
        graph: The technology graph
        start: Starting tech name
        direction: "forward" (children), "reverse" (parents), or "prerequisites"
        visited: Set of already visited techs (for cycle detection)

    Returns:
        Set of reachable tech names (excluding start)
    """
    if visited is None:
        visited = set()

    if start in visited:
        return set()

    visited.add(start)
    reachable = set()

    # Get the appropriate edge map
    if direction == "forward":
        edges = graph.forward
    elif direction == "reverse":
        edges = graph.reverse
    else:  # prerequisites
        edges = graph.prerequisites

    # Follow edges recursively
    if start in edges:
        for neighbor in edges[start]:
            reachable.add(neighbor)
            reachable.update(get_reachable_techs(graph, neighbor, direction, visited.copy()))

    return reachable


def get_reachable_triggers(
    tech_name: str,
    graph: TechGraph,
    trigger_cache: dict[str, Optional[list[str]]],
    visited: Optional[set[str]] = None,
    special_forces_type: Optional[str] = None
) -> set[str]:
    """
    Recursively find all research triggers reachable from a technology via forward edges.

    If a tech is on the path to heavy tanks (even indirectly), it needs the heavy trigger.
    This ensures AI will research all prerequisite techs to reach their desired tank type.

    For special forces techs: only propagate triggers from techs of the SAME type.

    Args:
        tech_name: The technology to start from
        graph: The technology graph
        trigger_cache: Dictionary mapping tech_name → list of trigger names (or None)
        visited: Set of already visited techs (for cycle detection)
        special_forces_type: Optional SF type filter ('paratroopers', 'marines', 'mountaineers')

    Returns:
        Set of trigger names
    """
    if visited is None:
        visited = set()

    if tech_name in visited:
        return set()

    visited.add(tech_name)
    triggers = set()

    # Add this tech's own triggers if it has any
    if tech_name in trigger_cache and trigger_cache[tech_name]:
        triggers.update(trigger_cache[tech_name])

    # Determine if this is a special forces tech and what type
    current_triggers = trigger_cache.get(tech_name, []) or []
    current_sf_type = _get_special_forces_type(current_triggers)

    # If we have a SF type filter and this tech has a different SF type, don't propagate
    if special_forces_type and current_sf_type and current_sf_type != special_forces_type:
        return triggers

    # Recursive forward: check all descendants
    if tech_name in graph.forward:
        for child_tech in graph.forward[tech_name]:
            child_triggers = get_reachable_triggers(
                child_tech, graph, trigger_cache, visited.copy(),
                special_forces_type=current_sf_type or special_forces_type
            )

            # If current tech is SF, filter child triggers to same type
            if current_sf_type:
                child_triggers = _filter_sf_triggers(child_triggers, current_sf_type)

            triggers.update(child_triggers)

    return triggers


def _get_special_forces_type(triggers: list[str]) -> Optional[str]:
    """
    Determine if triggers represent a single special forces type.

    Returns:
        The SF type if exactly one type, None otherwise
    """
    sf_types = []
    for trigger in triggers:
        trigger_lower = trigger.lower()
        if 'paratrooper' in trigger_lower:
            sf_types.append('paratroopers')
        elif 'marine' in trigger_lower:
            sf_types.append('marines')
        elif 'mountaineer' in trigger_lower:
            sf_types.append('mountaineers')

    if len(set(sf_types)) == 1:
        return sf_types[0]
    return None


def _filter_sf_triggers(triggers: set[str], sf_type: str) -> set[str]:
    """
    Filter triggers to only include ones matching the SF type (or non-SF triggers).
    """
    filtered = set()
    for trigger in triggers:
        trigger_lower = trigger.lower()

        # Include if it matches our SF type
        if sf_type == 'paratroopers' and 'paratrooper' in trigger_lower:
            filtered.add(trigger)
        elif sf_type == 'marines' and 'marine' in trigger_lower:
            filtered.add(trigger)
        elif sf_type == 'mountaineers' and 'mountaineer' in trigger_lower:
            filtered.add(trigger)
        # Include non-SF triggers
        elif 'paratrooper' not in trigger_lower and 'marine' not in trigger_lower and 'mountaineer' not in trigger_lower:
            filtered.add(trigger)

    return filtered
