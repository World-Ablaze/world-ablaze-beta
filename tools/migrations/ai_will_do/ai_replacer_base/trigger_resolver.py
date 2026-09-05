"""
Trigger resolution base class for AI Will Do replacers.

Provides abstract base class for resolving tech → trigger mappings.
"""

import re
from abc import ABC, abstractmethod
from typing import Optional


class BaseTriggerResolver(ABC):
    """
    Base class for resolving technology → trigger mappings.

    Subclasses must implement the mapping methods.
    """

    def __init__(self):
        self._archetype_map: Optional[dict[str, str]] = None
        self._category_map: Optional[dict[str, str]] = None
        self._compiled_patterns: Optional[list[tuple[re.Pattern, str | list[str]]]] = None

    @property
    def archetype_map(self) -> dict[str, str]:
        """Lazy-load archetype mappings."""
        if self._archetype_map is None:
            self._archetype_map = self.get_archetype_mappings()
        return self._archetype_map

    @property
    def category_map(self) -> dict[str, str]:
        """Lazy-load category mappings."""
        if self._category_map is None:
            self._category_map = self.get_category_mappings()
        return self._category_map

    @property
    def name_patterns(self) -> list[tuple[re.Pattern, str | list[str]]]:
        """Lazy-compile name patterns."""
        if self._compiled_patterns is None:
            self._compiled_patterns = []
            for pattern, trigger in self.get_name_pattern_list():
                self._compiled_patterns.append(
                    (re.compile(pattern, re.IGNORECASE), trigger)
                )
        return self._compiled_patterns

    @abstractmethod
    def get_archetype_mappings(self) -> dict[str, str]:
        """
        Return archetype → trigger mappings.

        Example:
            {
                "light_tank_chassis": "WA_AI_RESEARCH_needs_light_armor",
                "medium_tank_chassis": "WA_AI_RESEARCH_needs_medium_armor",
            }
        """
        pass

    @abstractmethod
    def get_category_mappings(self) -> dict[str, str]:
        """
        Return category → trigger mappings.

        Example:
            {
                "cat_light_armor": "WA_AI_RESEARCH_needs_light_armor",
                "cat_mechanized_equipment": "WA_AI_RESEARCH_needs_mechanized",
            }
        """
        pass

    @abstractmethod
    def get_name_pattern_list(self) -> list[tuple[str, str | list[str]]]:
        """
        Return (pattern, trigger) pairs ordered by specificity.

        More specific patterns should come first.
        Trigger can be a string or list of strings for multi-trigger techs.

        Example:
            [
                (r"_td_|tank_destroyer", "WA_AI_RESEARCH_needs_tank_destroyers"),
                (r"light_tank", "WA_AI_RESEARCH_needs_light_armor"),
            ]
        """
        pass

    def resolve_trigger(
        self,
        tech_name: str,
        archetypes: list[str],
        categories: list[str],
        context: Optional[dict] = None
    ) -> Optional[str | list[str]]:
        """
        Resolve trigger using priority chain:
        1. Archetype match (most reliable)
        2. Name pattern match (ordered by specificity)
        3. Category match (fallback)

        Args:
            tech_name: Name of the technology
            archetypes: List of equipment archetypes enabled by this tech
            categories: List of categories the tech belongs to
            context: Optional additional context (e.g., file path, tech block)

        Returns:
            Trigger name string, list of triggers, or None if no match
        """
        # Try archetype first (most reliable)
        for arch in archetypes:
            if arch in self.archetype_map:
                return self.archetype_map[arch]

        # Try name patterns (in order of specificity)
        for pattern, trigger in self.name_patterns:
            if pattern.search(tech_name):
                return trigger

        # Try categories (fallback)
        for cat in categories:
            if cat in self.category_map:
                return self.category_map[cat]

        return None

    def resolve_multiple_triggers(
        self,
        tech_name: str,
        categories: list[str],
        dependencies: list[str]
    ) -> list[str]:
        """
        Resolve multiple triggers for techs that require several (e.g., special forces).

        Args:
            tech_name: Name of the technology
            categories: List of categories the tech belongs to
            dependencies: List of dependency tech names

        Returns:
            List of trigger names
        """
        triggers = []

        # Check categories
        for cat in categories:
            if cat in self.category_map:
                trigger = self.category_map[cat]
                if trigger not in triggers:
                    triggers.append(trigger)

        # Check name patterns
        for pattern, trigger in self.name_patterns:
            if pattern.search(tech_name):
                if isinstance(trigger, list):
                    for t in trigger:
                        if t not in triggers:
                            triggers.append(t)
                else:
                    if trigger not in triggers:
                        triggers.append(trigger)

        # Check dependencies for additional triggers
        for dep in dependencies:
            for pattern, trigger in self.name_patterns:
                if pattern.search(dep):
                    if isinstance(trigger, list):
                        for t in trigger:
                            if t not in triggers:
                                triggers.append(t)
                    else:
                        if trigger not in triggers:
                            triggers.append(trigger)

        return triggers
