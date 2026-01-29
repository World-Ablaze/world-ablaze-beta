"""
State-to-province mapping generator for World Ablaze AI.

This script reads HOI4 state history files and generates a precomputed state->province
mapping file in the World Ablaze AI format.

The output file provides two mappings:
1. State -> [province_ids]: For iterating provinces within a state
2. Province -> state_id: For looking up which state a province belongs to

This module is designed to be:
- Standalone: Can be run directly from command line
- Robust: Handles various state file formats
- Compatible: Outputs in World Ablaze AI's expected format

Key constraints:
- Expects standard HOI4 history/states folder structure
- State files must contain 'id = X' and 'provinces = { ... }' blocks
"""

import argparse
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_state_file(path: Path) -> tuple[int | None, list[int]]:
    """
    Parse a state history file to extract state ID and province list.

    Args:
        path: Path to the state history file.

    Returns:
        A tuple of (state_id, province_list).
        Returns (None, []) if parsing fails.
    """
    try:
        content = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        try:
            content = path.read_text(encoding="latin-1")
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
    # Match 'provinces = {' followed by content until closing '}'
    provinces_match = re.search(
        r"provinces\s*=\s*\{([^}]+)\}",
        content,
        re.MULTILINE | re.DOTALL
    )
    if not provinces_match:
        logger.warning(f"No provinces block found in {path}")
        return state_id, []

    provinces_content = provinces_match.group(1)
    
    # Extract all province IDs (numbers) from the provinces block
    province_ids = [int(p) for p in re.findall(r"\d+", provinces_content)]

    return state_id, province_ids


def parse_all_states(states_dir: Path) -> dict[int, list[int]]:
    """
    Parse all state files in the history/states directory.

    Args:
        states_dir: Path to the history/states directory.

    Returns:
        Dictionary mapping state_id -> list of province_ids.
    """
    state_provinces: dict[int, list[int]] = {}
    
    # Find all .txt files in the states directory
    state_files = list(states_dir.glob("*.txt"))
    logger.info(f"Found {len(state_files)} state files")

    for state_file in state_files:
        state_id, provinces = parse_state_file(state_file)
        if state_id is not None and provinces:
            state_provinces[state_id] = provinces

    logger.info(f"Parsed {len(state_provinces)} states with provinces")
    return state_provinces


def write_wa_ai_format(
    state_provinces: dict[int, list[int]],
    output_path: Path
) -> None:
    """
    Write state-province mappings in World Ablaze AI format.

    Output format:
        WA_AI_MAP_set_state_province_ids_data = {
            # State 1 provinces
            add_to_array = { global.WA_AI_MAP_state_province_ids@1 = 3838 }
            set_variable = { global.WA_AI_MAP_province_state_id^3838 = 1 }
            ...
        }

    Args:
        state_provinces: Dictionary of state_id -> list of province_ids.
        output_path: Path for output file.
    """
    lines: list[str] = []
    lines.append("WA_AI_MAP_set_state_province_ids_data = {")

    total_provinces = 0
    
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
            total_provinces += 1

    lines.append("}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    logger.info(
        f"Wrote {len(state_provinces)} states with {total_provinces} province mappings to {output_path}"
    )


def main() -> None:
    """Main entry point for the state-province mapping generator."""
    parser = argparse.ArgumentParser(
        description="Generate state-to-province mappings for World Ablaze AI.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_state_provinces.py
  python generate_state_provinces.py --states-dir ../history/states --output ../common/scripted_effects/WA_AI_MAP_state_provinces.txt
        """,
    )
    parser.add_argument(
        "--states-dir",
        type=Path,
        default=Path("../history/states"),
        help="Path to the history/states folder (default: ../history/states)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("../common/scripted_effects/WA_AI_MAP_state_provinces.txt"),
        help="Output file path (default: ../common/scripted_effects/WA_AI_MAP_state_provinces.txt)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # Validate paths
    if not args.states_dir.exists():
        logger.error(f"States directory not found at {args.states_dir}")
        return

    # Step 1: Parse all state files
    logger.info(f"Step 1: Parsing state files from {args.states_dir}...")
    state_provinces = parse_all_states(args.states_dir)

    if not state_provinces:
        logger.error("No state-province mappings found!")
        return

    # Step 2: Write output
    logger.info("Step 2: Writing output file...")

    # Ensure output directory exists
    args.output.parent.mkdir(parents=True, exist_ok=True)

    write_wa_ai_format(state_provinces, args.output)

    logger.info("Done!")


if __name__ == "__main__":
    main()
