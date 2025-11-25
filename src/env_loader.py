"""Utilities for loading environment variables from .env files."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


def _resolve_env_path(provided_path: Optional[Path] = None) -> Path:
    """Resolve the .env file path.

    Args:
        provided_path: Optional path override.

    Returns:
        Path to the .env file to load.
    """
    if provided_path:
        return provided_path

    override = os.getenv("OLYMPUS_ENV_FILE")
    if override:
        return Path(override).expanduser()

    return Path(__file__).parent.parent / ".env"


def load_env_file(env_path: Optional[Path] = None) -> bool:
    """Load environment variables from a .env file.

    Args:
        env_path: Optional path override for the .env file.

    Returns:
        True if variables were loaded, False otherwise.
    """
    resolved_path = _resolve_env_path(env_path)

    try:
        from dotenv import load_dotenv  # type: ignore import-untyped
    except ImportError:
        return False

    if not resolved_path.exists():
        return False

    return bool(load_dotenv(resolved_path))

