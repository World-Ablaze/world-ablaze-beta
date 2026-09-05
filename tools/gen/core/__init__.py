"""
Core utilities for World Ablaze tools.

Provides shared functionality for file I/O, CSV parsing, logging, and CLI patterns.
"""

from .logging_config import setup_logging, get_logger
from .file_io import read_file_with_bom, write_file_utf8
from .csv_parsers import (
    parse_definition_for_land_provinces,
    parse_definition_for_terrain,
    parse_definition_for_colors,
    parse_definition_full,
)
from .cli import create_base_parser, add_common_arguments, add_path_arguments

__all__ = [
    # Logging
    "setup_logging",
    "get_logger",
    # File I/O
    "read_file_with_bom",
    "write_file_utf8",
    # CSV Parsers
    "parse_definition_for_land_provinces",
    "parse_definition_for_terrain",
    "parse_definition_for_colors",
    "parse_definition_full",
    # CLI
    "create_base_parser",
    "add_common_arguments",
    "add_path_arguments",
]
