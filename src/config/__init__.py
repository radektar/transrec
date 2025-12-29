"""User configuration module."""

# Import UserSettings and defaults from this package
from src.config.settings import UserSettings
from src.config.defaults import (
    DEFAULT_OUTPUT_DIR,
    DEFAULT_WATCH_MODE,
    DEFAULT_LANGUAGE,
    DEFAULT_MODEL,
    SUPPORTED_LANGUAGES,
    SUPPORTED_MODELS,
    WATCH_MODES,
    SYSTEM_VOLUMES,
    CONFIG_DIR,
    CONFIG_FILE,
)

# Import config from parent module (src.config.py)
# Use importlib to avoid circular import issues
import importlib.util
from pathlib import Path

_parent_config_path = Path(__file__).parent.parent / "config.py"
if _parent_config_path.exists():
    spec = importlib.util.spec_from_file_location("_config_module", _parent_config_path)
    _config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_config_module)
    config = _config_module.config
else:
    # Fallback - this shouldn't happen in normal operation
    config = None

__all__ = [
    "UserSettings",
    "config",
    "DEFAULT_OUTPUT_DIR",
    "DEFAULT_WATCH_MODE",
    "DEFAULT_LANGUAGE",
    "DEFAULT_MODEL",
    "SUPPORTED_LANGUAGES",
    "SUPPORTED_MODELS",
    "WATCH_MODES",
    "SYSTEM_VOLUMES",
    "CONFIG_DIR",
    "CONFIG_FILE",
]
