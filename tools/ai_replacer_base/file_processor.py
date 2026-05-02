"""
Base file processor for AI Will Do replacers.

Provides abstract base class and common file I/O operations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import re

from .block_finder import find_ai_will_do_block, find_matching_brace
from .text_utils import extract_start_year, extract_categories, extract_dependencies
from .generator import generate_ai_will_do_block


@dataclass
class ProcessingStats:
    """Statistics from processing files."""
    updated: int = 0
    skipped: int = 0
    unknown: int = 0
    errors: list[str] = field(default_factory=list)


class BaseFileProcessor(ABC):
    """
    Abstract base class for all AI Will Do replacers.

    Subclasses must implement:
    - get_file_patterns(): Return glob patterns for files to process
    - get_archetype_mappings(): Return archetype → trigger mappings
    - get_category_mappings(): Return category → trigger mappings
    - get_name_patterns(): Return (regex, trigger) pairs for name matching
    """

    # Blocks to skip when finding tech definitions
    SKIP_BLOCKS = frozenset({
        'technologies', 'categories', 'path', 'folder', 'sub_technologies',
        'enable_equipments', 'enable_equipment_modules', 'modifier', 'allow',
        'allow_branch', 'on_research_complete', 'research_cost_coeff',
        'XOR', 'OR', 'AND', 'NOT', 'dependencies', 'if', 'limit',
        'create_equipment_variant', 'ai_will_do', 'position', 'name', 'x', 'y',
        'category_special_forces', 'amphibious', 'enable_subunits'
    })

    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.stats = ProcessingStats()

        # Compile name patterns once
        self._compiled_patterns: list[tuple[re.Pattern, str | list[str]]] = []
        for pattern, trigger in self.get_name_patterns():
            self._compiled_patterns.append((re.compile(pattern, re.IGNORECASE), trigger))

    @abstractmethod
    def get_file_patterns(self) -> list[str]:
        """Return glob patterns for files this processor handles."""
        pass

    @abstractmethod
    def get_archetype_mappings(self) -> dict[str, str]:
        """Return archetype → trigger mappings."""
        pass

    @abstractmethod
    def get_category_mappings(self) -> dict[str, str]:
        """Return category → trigger mappings."""
        pass

    @abstractmethod
    def get_name_patterns(self) -> list[tuple[str, str | list[str]]]:
        """
        Return (regex_pattern, trigger) pairs for name matching.
        Trigger can be a string or list of strings for multi-trigger techs.
        Ordered by specificity (most specific first).
        """
        pass

    def should_process_file(self, filepath: Path) -> bool:
        """Check if this processor should handle the given file."""
        for pattern in self.get_file_patterns():
            if filepath.match(pattern):
                return True
        return False

    def read_file(self, filepath: Path) -> tuple[str, bool]:
        """
        Read file with BOM detection.

        Returns:
            Tuple of (content, has_bom)
        """
        # Check for BOM
        with open(filepath, 'rb') as f:
            first_bytes = f.read(3)
            has_bom = first_bytes == b'\xef\xbb\xbf'

        # Read content
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            content = f.read()

        return content, has_bom

    def write_file(self, filepath: Path, content: str) -> None:
        """Write file without BOM (HOI4 doesn't handle BOM well)."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    def resolve_trigger(
        self,
        tech_name: str,
        archetypes: list[str],
        categories: list[str],
        tech_block: str = "",
    ) -> Optional[str | list[str]]:
        """
        Resolve trigger using priority chain:
        1. Archetype match (most reliable)
        2. Name pattern match (ordered by specificity)
        3. Category match (fallback)

        Returns:
            Trigger name string, list of triggers, or None if no match
        """
        archetype_map = self.get_archetype_mappings()
        category_map = self.get_category_mappings()

        # Try archetype first
        for arch in archetypes:
            if arch in archetype_map:
                return archetype_map[arch]

        # Try name patterns (in order)
        for pattern, trigger in self._compiled_patterns:
            if pattern.search(tech_name):
                return trigger

        # Try categories
        for cat in categories:
            if cat in category_map:
                return category_map[cat]

        return None

    def is_old_pattern(self, ai_will_do_block: str) -> bool:
        """
        Check if ai_will_do block uses the old pattern.

        Old pattern characteristics:
        - Has date > patterns (multipliers)
        - Does NOT contain WA_AI_RESEARCH triggers
        - Simple factor = X with no WA triggers
        """
        # Must not already be new pattern
        if 'WA_AI_RESEARCH' in ai_will_do_block:
            return False

        # Check for date > pattern (old style) - this is a key indicator
        has_date_multiplier = re.search(r'date\s*>\s*["\']?\d{4}', ai_will_do_block)

        # If it has date > patterns and no WA_AI_RESEARCH, it's old pattern
        # (regardless of factor value - catches factor = 10, 80, etc.)
        if has_date_multiplier:
            return True

        # Check if there are any modifiers at all
        has_modifiers = 'modifier' in ai_will_do_block

        # Simple pattern: just factor = X with no modifiers (old pattern)
        if not has_modifiers:
            if re.search(r'factor\s*=\s*[\d.]+', ai_will_do_block):
                return True

        # Check for factor = 3, 4 with date multipliers
        if re.search(r'factor\s*=\s*[34]', ai_will_do_block):
            if has_date_multiplier:
                return True

        # Check for factor = 1 with date multipliers
        if re.search(r'factor\s*=\s*1\b', ai_will_do_block):
            if has_date_multiplier:
                return True

        # Check for factor = 0.X values
        if re.search(r'factor\s*=\s*0\.[\d]+', ai_will_do_block):
            return True

        # Check for modifier blocks with factor = 30 or 11 (old pattern multipliers)
        if re.search(r'modifier\s*=\s*\{[^}]*factor\s*=\s*(30|11)', ai_will_do_block, re.DOTALL):
            return True

        return False

    def is_already_new_pattern(self, ai_will_do_block: str) -> bool:
        """
        Check if ai_will_do block already uses the new pattern.
        """
        if 'WA_AI_RESEARCH' not in ai_will_do_block:
            return False

        # Check if date modifier uses the new pattern (has WA_AI_unused_research_slots)
        if 'date <' in ai_will_do_block:
            if 'WA_AI_unused_research_slots' not in ai_will_do_block:
                return False

        return True

    def needs_update(self, ai_will_do_block: str, tech_name: str = "", tech_block: str = "") -> bool:
        """Check if an ai_will_do block needs updating."""
        # Old pattern always needs update
        if self.is_old_pattern(ai_will_do_block):
            return True

        # Check for blocks with date < patterns but no WA_AI_RESEARCH trigger
        # (e.g., camo1 which has date < but no trigger)
        if 'date <' in ai_will_do_block and 'WA_AI_RESEARCH' not in ai_will_do_block:
            return True

        # Already new pattern - check if it needs date pattern update
        if 'WA_AI_RESEARCH' in ai_will_do_block and 'date <' in ai_will_do_block:
            if 'WA_AI_unused_research_slots' not in ai_will_do_block:
                return True

        # Check for excessive blank lines
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

    def find_tech_definitions(self, content: str) -> list[dict]:
        """
        Find all technology definitions in content.

        Returns:
            List of dicts with keys: name, start, end, block, indent
        """
        techs = []
        # Accept either tabs or spaces for indentation
        tech_pattern = re.compile(r'^([\t ]*)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\{', re.MULTILINE)

        for match in tech_pattern.finditer(content):
            tech_name = match.group(2)
            indent = match.group(1)
            tech_start = match.start()
            brace_start = match.end() - 1

            # Skip non-technology blocks
            if tech_name in self.SKIP_BLOCKS:
                continue

            # Find the end of this technology block
            try:
                tech_end = find_matching_brace(content, brace_start) + 1
            except ValueError:
                continue

            techs.append({
                'name': tech_name,
                'start': tech_start,
                'end': tech_end,
                'block': content[tech_start:tech_end],
                'indent': indent,
            })

        return techs

    def process_file(self, filepath: Path) -> ProcessingStats:
        """
        Process a single technology file.

        This is the main entry point for processing. Override in subclasses
        for domain-specific logic.
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
            triggers = [trigger] if isinstance(trigger, str) else trigger
            new_block = generate_ai_will_do_block(triggers, start_year, indent="\t\t")

            # Only replace if the block actually changed
            old_block = content[block_start:block_end]
            if new_block != old_block:
                content = content[:block_start] + new_block + content[block_end:]
                stats.updated += 1

                if self.verbose:
                    print(f"  Updated: {tech_name} -> {trigger} (year: {start_year})")
            else:
                stats.skipped += 1

        # Write if changed
        if content != original_content and not self.dry_run:
            self.write_file(filepath, content)

        return stats

    def process_directory(self, directory: Path) -> ProcessingStats:
        """Process all matching files in directory."""
        total_stats = ProcessingStats()

        for pattern in self.get_file_patterns():
            for filepath in directory.glob(pattern):
                stats = self.process_file(filepath)
                total_stats.updated += stats.updated
                total_stats.skipped += stats.skipped
                total_stats.unknown += stats.unknown
                total_stats.errors.extend(stats.errors)

        return total_stats
