#!/usr/bin/env python3
"""
AI Will Do replacer for prospecting decisions.

Replaces all ai_will_do blocks in prospecting decisions with needs-aware versions
that include reactive, cooperative, and proactive layers.

Usage:
    python ai_will_do_replacer_prospecting.py                 # Dry run
    python ai_will_do_replacer_prospecting.py --apply         # Apply changes
    python ai_will_do_replacer_prospecting.py --apply --verbose
"""

import argparse
import sys
from pathlib import Path
from typing import Optional
import re
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from prospecting_decision_analyzer import (
    analyze_decision,
    extract_resource_type,
    DecisionMetadata,
)
from needs_aware_generator import (
    generate_ai_will_do_block,
    extract_existing_modifiers,
)


@dataclass
class ProcessingStats:
    """Statistics from processing."""
    total_decisions: int = 0
    updated: int = 0
    skipped: int = 0
    errors: int = 0
    error_messages: list[str] = None

    def __post_init__(self):
        if self.error_messages is None:
            self.error_messages = []


class ProspectingDecisionProcessor:
    """Main processor for prospecting decisions."""

    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.stats = ProcessingStats()
        self.decisions_file = Path(
            'E:\\Projets\\HOI4\\WA\\world-ablaze-beta\\common\\decisions\\_resource_prospecting.txt'
        )

    def log(self, message: str):
        """Log message if verbose."""
        if self.verbose:
            print(message)

    def read_file(self) -> str:
        """Read the decisions file."""
        with open(self.decisions_file, 'r', encoding='utf-8-sig') as f:
            return f.read()

    def write_file(self, content: str):
        """Write the decisions file."""
        if self.dry_run:
            self.log("DRY RUN: Would write file")
            return

        with open(self.decisions_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Written {self.decisions_file}")

    def extract_decisions(self, content: str) -> list[tuple[str, int, int]]:
        """
        Extract all decision blocks from content using line-based parsing.

        Returns: List of (decision_name, start_line, end_line)
        """
        decisions = []
        lines = content.split('\n')

        for i, line in enumerate(lines):
            # Match decision definition: [tab]decision_name = { #[optional_id]
            match = re.match(r'^\t([a-zA-Z_]\w*)\s*=\s*\{', line)
            if not match:
                continue

            decision_name = match.group(1)

            # Find matching closing brace
            temp_depth = 1
            for j in range(i + 1, len(lines)):
                temp_depth += lines[j].count('{') - lines[j].count('}')
                if temp_depth == 0:
                    decisions.append((decision_name, i, j))
                    break

        return decisions

    def process_decision(self, start_line: int, end_line: int, lines: list[str]) -> Optional[list[str]]:
        """
        Process a single decision and return updated lines or None if unchanged.
        """
        try:
            decision_content = '\n'.join(lines[start_line:end_line + 1])
            decision_name = re.match(r'^\t([a-zA-Z_]\w*)', lines[start_line]).group(1)

            # Check if this decision has a resource
            resource_type = extract_resource_type(decision_content)
            if not resource_type:
                self.log(f"SKIP: {decision_name} - no resource type found")
                self.stats.skipped += 1
                return None

            # Analyze the decision
            metadata = analyze_decision(decision_content, decision_name, start_line, end_line)
            if not metadata:
                self.log(f"SKIP: {decision_name} - analysis failed")
                self.stats.skipped += 1
                return None

            # Find and extract ai_will_do block - match from "ai_will_do" keyword
            ai_will_do_match = re.search(r'ai_will_do\s*=\s*\{', decision_content)
            if not ai_will_do_match:
                self.log(f"SKIP: {decision_name} - no ai_will_do block found")
                self.stats.skipped += 1
                return None

            # Find the closing brace of ai_will_do = { ... }
            brace_start = ai_will_do_match.end() - 1
            brace_count = 1
            end_pos = brace_start + 1

            # Find matching closing brace
            while end_pos < len(decision_content) and brace_count > 0:
                if decision_content[end_pos] == '{':
                    brace_count += 1
                elif decision_content[end_pos] == '}':
                    brace_count -= 1
                end_pos += 1

            # Extract the original block to get modifiers to preserve
            ai_will_do_block = decision_content[ai_will_do_match.start():end_pos]
            preserved_mods = extract_existing_modifiers(ai_will_do_block)

            # Generate new block (all decisions use 2-tab indentation for ai_will_do)
            new_block = generate_ai_will_do_block(metadata, preserved_mods)

            # Find the start of the line containing ai_will_do to preserve line structure
            line_start = decision_content.rfind('\n', 0, ai_will_do_match.start())
            if line_start == -1:
                line_start = 0
            else:
                line_start += 1  # Move past the newline

            # Extract what's before ai_will_do on that line (should be just tabs)
            prefix_before_ai_will_do = decision_content[line_start:ai_will_do_match.start()]

            # Replace: keep prefix (empty or whitespace), add new block, keep suffix after closing brace
            updated_content = (
                decision_content[:line_start] +
                new_block +
                decision_content[end_pos:]
            )

            # Convert back to lines
            updated_lines = updated_content.split('\n')

            self.log(f"UPDATE: {decision_name} ({metadata.resource_type})")
            self.stats.updated += 1
            return updated_lines

        except Exception as e:
            decision_name = re.match(r'^\t([a-zA-Z_]\w*)', lines[start_line]).group(1)
            self.log(f"ERROR: {decision_name} - {str(e)}")
            self.stats.errors += 1
            self.stats.error_messages.append(f"{decision_name}: {str(e)}")
            return None

    def process_file(self) -> str:
        """Process the entire prospecting decisions file."""
        print(f"Processing {self.decisions_file}...")

        content = self.read_file()
        lines = content.split('\n')
        decisions = self.extract_decisions(content)
        self.stats.total_decisions = len(decisions)

        print(f"Found {len(decisions)} decisions to process")

        # Process decisions in reverse order to maintain line positions
        for decision_name, start_line, end_line in reversed(decisions):
            updated = self.process_decision(start_line, end_line, lines)
            if updated:
                # Replace lines
                lines[start_line:end_line + 1] = updated

        return '\n'.join(lines)

    def run(self):
        """Main execution."""
        updated_content = self.process_file()

        # Print summary
        print(f"\n{'='*60}")
        print(f"Processing Summary")
        print(f"{'='*60}")
        print(f"Total decisions:      {self.stats.total_decisions}")
        print(f"Updated:              {self.stats.updated}")
        print(f"Skipped:              {self.stats.skipped}")
        print(f"Errors:               {self.stats.errors}")

        if self.stats.error_messages:
            print(f"\nErrors:")
            for msg in self.stats.error_messages:
                print(f"  - {msg}")

        if self.dry_run:
            print(f"\nDRY RUN - No changes written")
            print(f"To apply changes, run with --apply flag")
        else:
            self.write_file(updated_content)
            print(f"\nSuccessfully applied {self.stats.updated} updates")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Replace ai_will_do blocks in prospecting decisions with needs-aware versions'
    )
    parser.add_argument('--apply', action='store_true', help='Apply changes (default: dry run)')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    processor = ProspectingDecisionProcessor(dry_run=not args.apply, verbose=args.verbose)
    processor.run()


if __name__ == '__main__':
    main()
