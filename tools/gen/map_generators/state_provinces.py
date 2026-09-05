"""
State-to-province mapping generator for World Ablaze AI.

Reads HOI4 state history files and generates precomputed state->province
and province->state mappings.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import re
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from core import read_file_with_bom
from map_generators.base import BaseMapGenerator, GeneratorConfig


def parse_state_file(path: Path, logger) -> Tuple[Optional[int], List[int]]:
    """
    Parse a state history file to extract state ID and province list.

    Args:
        path: Path to the state history file.
        logger: Logger instance.

    Returns:
        Tuple of (state_id, province_list). Returns (None, []) if parsing fails.
    """
    try:
        content, _ = read_file_with_bom(path)
    except Exception as e:
        logger.warning(f"Failed to read {path}: {e}")
        return None, []

    # Extract state ID
    id_match = re.search(r"^\s*id\s*=\s*(\d+)", content, re.MULTILINE)
    if not id_match:
        logger.warning(f"No state ID found in {path}")
        return None, []

    state_id = int(id_match.group(1))

    # Extract provinces block
    provinces_match = re.search(
        r"provinces\s*=\s*\{([^}]+)\}", content, re.MULTILINE | re.DOTALL
    )
    if not provinces_match:
        logger.warning(f"No provinces block found in {path}")
        return state_id, []

    provinces_content = provinces_match.group(1)
    province_ids = [int(p) for p in re.findall(r"\d+", provinces_content)]

    return state_id, province_ids


def parse_all_states(states_dir: Path, logger) -> Dict[int, List[int]]:
    """
    Parse all state files in the history/states directory.

    Args:
        states_dir: Path to the history/states directory.
        logger: Logger instance.

    Returns:
        Dictionary mapping state_id -> list of province_ids.
    """
    state_provinces: Dict[int, List[int]] = {}

    state_files = list(states_dir.glob("*.txt"))
    logger.info(f"Found {len(state_files)} state files")

    for state_file in state_files:
        state_id, provinces = parse_state_file(state_file, logger)
        if state_id is not None and provinces:
            state_provinces[state_id] = provinces

    logger.info(f"Parsed {len(state_provinces)} states with provinces")
    return state_provinces


class StateProvincesGenerator(BaseMapGenerator):
    """Generator for state-to-province mappings."""

    @property
    def name(self) -> str:
        return "state_provinces"

    @property
    def description(self) -> str:
        return "Generate state-to-province mappings for World Ablaze AI"

    def get_output_filename(self) -> str:
        return "WA_AI_MAP_state_provinces.txt"

    def get_required_inputs(self) -> List[Path]:
        return [self.config.states_dir]

    def validate_inputs(self) -> List[str]:
        """Override to check for directory instead of file."""
        errors = []
        if not self.config.states_dir.exists():
            errors.append(f"States directory not found: {self.config.states_dir}")
        elif not self.config.states_dir.is_dir():
            errors.append(f"Not a directory: {self.config.states_dir}")
        return errors

    def process(self) -> Dict[str, Any]:
        """Parse all state files."""
        self.log_step(f"Parsing state files from {self.config.states_dir}...")
        state_provinces = parse_all_states(self.config.states_dir, self.logger)

        total_provinces = sum(len(p) for p in state_provinces.values())
        self.logger.info(
            f"Total: {len(state_provinces)} states, {total_provinces} province mappings"
        )

        return {"state_provinces": state_provinces}

    def format_output(self, data: Dict[str, Any]) -> str:
        """Format state-province data for output file."""
        state_provinces = data["state_provinces"]

        lines: List[str] = []
        lines.append("WA_AI_MAP_set_state_province_ids_data = {")

        for state_id in sorted(state_provinces.keys()):
            provinces = state_provinces[state_id]
            if not provinces:
                continue

            lines.append(f"    # State {state_id}")

            for province_id in sorted(provinces):
                # State -> province mapping
                lines.append(
                    f"    add_to_array = {{ global.WA_AI_MAP_state_province_ids@{state_id} = {province_id} }}"
                )
                # Province -> state mapping
                lines.append(
                    f"    set_variable = {{ global.WA_AI_MAP_province_state_id^{province_id} = {state_id} }}"
                )

        lines.append("}")

        return "\n".join(lines)


def main() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate state-to-province mappings for World Ablaze AI."
    )
    parser.add_argument(
        "--states-dir",
        type=Path,
        default=Path("../history/states"),
        help="Path to the history/states folder",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("../common/scripted_effects"),
        help="Output directory",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    config = GeneratorConfig(
        states_dir=args.states_dir,
        output_dir=args.output_dir,
        verbose=args.verbose,
        dry_run=args.dry_run,
    )

    generator = StateProvincesGenerator(config)
    result = generator.run()

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
