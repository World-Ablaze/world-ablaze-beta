"""File I/O utilities with BOM detection and encoding handling."""

from pathlib import Path
from typing import Tuple


def detect_encoding(path: Path) -> Tuple[str, bool]:
    """
    Detect file encoding and BOM presence.

    Args:
        path: Path to the file.

    Returns:
        Tuple of (encoding, has_bom).
    """
    with open(path, "rb") as f:
        first_bytes = f.read(3)
        has_bom = first_bytes == b"\xef\xbb\xbf"
    return ("utf-8-sig" if has_bom else "utf-8", has_bom)


def read_file_with_bom(path: Path) -> Tuple[str, bool]:
    """
    Read file with automatic BOM detection.

    Tries UTF-8 first, falls back to latin-1 if that fails.

    Args:
        path: Path to the file to read.

    Returns:
        Tuple of (content, had_bom).
    """
    _, has_bom = detect_encoding(path)

    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(path, "r", encoding="latin-1") as f:
            content = f.read()

    return content, has_bom


def write_file_utf8(path: Path, content: str, include_bom: bool = False) -> None:
    """
    Write file in UTF-8.

    Args:
        path: Output file path.
        content: File content.
        include_bom: Whether to include BOM (default: False for HOI4 compatibility).
    """
    encoding = "utf-8-sig" if include_bom else "utf-8"
    with open(path, "w", encoding=encoding) as f:
        f.write(content)
