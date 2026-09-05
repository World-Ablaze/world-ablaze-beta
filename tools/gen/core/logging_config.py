"""Centralized logging configuration for World Ablaze tools."""

import logging
from typing import Optional


def setup_logging(
    verbose: bool = False,
    debug: bool = False,
    log_file: Optional[str] = None,
    format_string: str = "%(asctime)s - %(levelname)s - %(message)s",
) -> None:
    """
    Configure logging for all tools.

    Args:
        verbose: Enable INFO level logging.
        debug: Enable DEBUG level logging (overrides verbose).
        log_file: Optional path to log file.
        format_string: Log format string.
    """
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING

    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=handlers,
        force=True,  # Reset any existing configuration
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.

    Args:
        name: Logger name (typically __name__ of the calling module).

    Returns:
        Configured logger instance.
    """
    return logging.getLogger(name)
