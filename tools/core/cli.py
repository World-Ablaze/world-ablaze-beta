"""Base CLI argument parsing for World Ablaze tools."""

import argparse
from pathlib import Path
from typing import Optional


def create_base_parser(
    description: str,
    epilog: str = "",
) -> argparse.ArgumentParser:
    """
    Create a base argument parser with common structure.

    Args:
        description: Tool description.
        epilog: Examples/additional help text.

    Returns:
        Configured ArgumentParser.
    """
    return argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog,
    )


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Add common arguments used by most tools.

    Adds: -v/--verbose, --debug, --dry-run

    Args:
        parser: ArgumentParser to add arguments to.
    """
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging (very verbose)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )


def add_path_arguments(
    parser: argparse.ArgumentParser,
    map_dir: bool = False,
    output: bool = True,
    default_output: Optional[Path] = None,
    default_map_dir: Optional[Path] = None,
) -> None:
    """
    Add common path arguments.

    Args:
        parser: ArgumentParser to add arguments to.
        map_dir: Whether to add --map-dir argument.
        output: Whether to add --output argument.
        default_output: Default value for --output.
        default_map_dir: Default value for --map-dir.
    """
    if map_dir:
        parser.add_argument(
            "--map-dir",
            type=Path,
            default=default_map_dir or Path("../map"),
            help=f"Path to the map folder (default: {default_map_dir or '../map'})",
        )

    if output:
        parser.add_argument(
            "--output",
            type=Path,
            default=default_output,
            help=f"Output file path (default: {default_output})",
        )
