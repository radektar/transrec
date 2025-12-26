"""Default configuration values for Transrec."""

from pathlib import Path
from typing import List

from dataclasses import dataclass, field


@dataclass
class DefaultSettings:
    """Default configuration values.
    
    These values are used when creating new UserSettings instances
    or when migrating from old configuration.
    """
    
    # Watch mode: "auto" | "manual" | "specific"
    WATCH_MODE: str = "auto"
    
    # List of volume names to watch (when watch_mode == "specific")
    DEFAULT_WATCHED_VOLUMES: List[str] = field(default_factory=lambda: [])
    
    # Output directory for transcriptions
    DEFAULT_OUTPUT_DIR: Path = (
        Path.home()
        / "Library"
        / "Mobile Documents"
        / "iCloud~md~obsidian"
        / "Documents"
        / "Obsidian"
        / "11-Transcripts"
    )
    
    # Transcription settings
    DEFAULT_LANGUAGE: str = "pl"
    DEFAULT_WHISPER_MODEL: str = "small"
    
    # AI settings (PRO features - disabled by default in FREE)
    DEFAULT_ENABLE_AI_SUMMARIES: bool = False
    DEFAULT_AI_API_KEY: str = ""
    
    # UI settings
    DEFAULT_SHOW_NOTIFICATIONS: bool = True
    DEFAULT_START_AT_LOGIN: bool = False
    
    # Setup wizard
    DEFAULT_SETUP_COMPLETED: bool = False
    
    # System volumes to ignore
    SYSTEM_VOLUMES: set = field(default_factory=lambda: {
        "Macintosh HD",
        "Recovery",
        "Preboot",
        "VM",
        "Data",
        "System",
        "Update",
    })
    
    # Audio file extensions
    AUDIO_EXTENSIONS: set = field(default_factory=lambda: {
        ".mp3",
        ".wav",
        ".m4a",
        ".wma",
        ".flac",
        ".aac",
        ".ogg",
    })
    
    # Maximum depth for scanning volumes for audio files
    MAX_SCAN_DEPTH: int = 3


# Global instance
defaults = DefaultSettings()



