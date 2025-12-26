"""User settings management for Transrec."""

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional

from src.config.defaults import defaults


def _get_logger():
    """Lazy import logger to avoid circular imports."""
    from src.logger import logger
    return logger


@dataclass
class UserSettings:
    """User settings (persistent configuration).
    
    This class replaces the old Config class and provides a more
    flexible configuration system that supports:
    - Multiple volume sources (not just Olympus)
    - Watch modes (auto, manual, specific)
    - User preferences
    - Setup wizard state
    
    Attributes:
        watch_mode: How to detect volumes ("auto", "manual", "specific")
        watched_volumes: List of volume names to watch (when mode="specific")
        output_dir: Directory where transcriptions are saved
        language: Language code for transcription (pl, en, or None for auto)
        whisper_model: Whisper model size (tiny, base, small, medium, large)
        enable_ai_summaries: Whether AI summaries are enabled (PRO feature)
        ai_api_key: API key for AI provider (PRO feature)
        show_notifications: Whether to show macOS notifications
        start_at_login: Whether to start app at login
        setup_completed: Whether first-run wizard was completed
    """
    
    # Volume detection
    watch_mode: str = defaults.WATCH_MODE
    watched_volumes: List[str] = field(default_factory=list)
    
    # Output directory
    output_dir: Path = defaults.DEFAULT_OUTPUT_DIR
    
    # Transcription settings
    language: str = defaults.DEFAULT_LANGUAGE
    whisper_model: str = defaults.DEFAULT_WHISPER_MODEL
    
    # AI settings (PRO features)
    enable_ai_summaries: bool = defaults.DEFAULT_ENABLE_AI_SUMMARIES
    ai_api_key: Optional[str] = None
    
    # UI settings
    show_notifications: bool = defaults.DEFAULT_SHOW_NOTIFICATIONS
    start_at_login: bool = defaults.DEFAULT_START_AT_LOGIN
    
    # Setup wizard state
    setup_completed: bool = defaults.DEFAULT_SETUP_COMPLETED
    
    @classmethod
    def load(cls) -> "UserSettings":
        """Load settings from file.
        
        Returns:
            UserSettings instance loaded from file, or default if file doesn't exist
        """
        config_path = cls._config_path()
        
        if not config_path.exists():
            _get_logger().info("No user settings found, using defaults")
            return cls()
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Convert string paths to Path objects
            if "output_dir" in data and data["output_dir"]:
                data["output_dir"] = Path(data["output_dir"]).expanduser().resolve()
            
            # Create instance with loaded data
            settings = cls(**data)
            _get_logger().debug(f"Loaded settings from {config_path}")
            return settings
            
        except Exception as e:
            _get_logger().error(f"Error loading settings: {e}", exc_info=True)
            _get_logger().info("Using default settings")
            return cls()
    
    def save(self) -> None:
        """Save settings to file."""
        config_path = self._config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Convert to dict, handling Path objects
            data = asdict(self)
            data["output_dir"] = str(data["output_dir"])
            
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            _get_logger().debug(f"Saved settings to {config_path}")
            
        except Exception as e:
            _get_logger().error(f"Error saving settings: {e}", exc_info=True)
    
    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def _config_path() -> Path:
        """Get path to configuration file.
        
        Returns:
            Path to config.json in Application Support directory
        """
        return (
            Path.home()
            / "Library"
            / "Application Support"
            / "Transrec"
            / "config.json"
        )
    
    def __post_init__(self):
        """Post-initialization: ensure output_dir is a Path object."""
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir).expanduser().resolve()

