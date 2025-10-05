"""Centralized logging utilities for the Langscrape project."""
from __future__ import annotations

import logging
import os
from typing import Optional, Union

_DEFAULT_LEVEL_NAME = os.getenv("LANGSCRAPE_LOG_LEVEL", "INFO")
_DEFAULT_FORMAT = os.getenv(
    "LANGSCRAPE_LOG_FORMAT",
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def _resolve_level(level: Union[str, int]) -> int:
    """Convert a log level name or integer to a ``logging`` level value."""
    if isinstance(level, int):
        return level

    normalized = (level or "").upper()
    return getattr(logging, normalized, logging.INFO)


def _configure_root_logger() -> logging.Logger:
    """Ensure the Langscrape root logger is configured exactly once."""
    root_logger = logging.getLogger("langscrape")
    if not root_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(_DEFAULT_FORMAT))
        root_logger.addHandler(handler)

    root_logger.setLevel(_resolve_level(_DEFAULT_LEVEL_NAME))
    return root_logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a logger scoped to ``name`` using the shared Langscrape config."""
    root_logger = _configure_root_logger()
    if not name or name == "langscrape":
        return root_logger
    if name.startswith("langscrape."):
        return logging.getLogger(name)
    return root_logger.getChild(name)
