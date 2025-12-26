"""Configuration module for Transrec (backward compatible wrapper)."""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

from src.config.settings import UserSettings
from src.config.migration import perform_migration_if_needed
from src.config.defaults import defaults


@dataclass
class Config:
    """Backward-compatible configuration wrapper for Transrec.
    
    This class maintains the old Config interface while using UserSettings
    internally. This allows existing code to continue working while we
    transition to the new configuration system.
    
    Attributes:
        RECORDER_NAMES: List of possible volume names (from watched_volumes or defaults)
        TRANSCRIBE_DIR: Directory where transcriptions are saved (from output_dir)
        STATE_FILE: JSON file tracking last sync time (legacy)
        LOG_DIR: Directory for application logs
        LOG_FILE: Path to main log file
        WHISPER_MODEL: Whisper model size (from whisper_model)
        WHISPER_LANGUAGE: Language code for transcription (from language)
        WHISPER_DEVICE: Device to use (cpu or auto-detect)
        WHISPER_CPP_PATH: Path to whisper.cpp binary executable
        WHISPER_CPP_MODELS_DIR: Directory containing whisper.cpp models
        TRANSCRIPTION_TIMEOUT: Maximum time allowed for transcription (60 minutes)
        PERIODIC_CHECK_INTERVAL: Fallback check interval (seconds)
        MOUNT_MONITOR_DELAY: Wait time after mount detection (seconds)
        AUDIO_EXTENSIONS: Supported audio file formats
        ENABLE_SUMMARIZATION: Whether to generate summaries using LLM (from enable_ai_summaries)
        LLM_PROVIDER: LLM provider name (claude, openai, ollama)
        LLM_MODEL: Model name for the selected provider
        LLM_API_KEY: API key for LLM provider (from ai_api_key)
        SUMMARY_MAX_WORDS: Maximum words in generated summary
        TITLE_MAX_LENGTH: Maximum length for generated title (characters)
        DELETE_TEMP_TXT: Whether to delete temporary TXT files after MD creation
        LOCAL_RECORDINGS_DIR: Local staging directory for copied recorder files
    """
    
    # Recorder detection
    RECORDER_NAMES: List[str] = None
    
    # Directories
    TRANSCRIBE_DIR: Path = None
    LOG_DIR: Path = None
    LOCAL_RECORDINGS_DIR: Path = None  # Local staging area for recorder files
    PROCESS_LOCK_FILE: Path = None  # Lock file preventing overlapping runs
    
    # Files
    STATE_FILE: Path = None
    LOG_FILE: Path = None
    
    # Whisper configuration
    WHISPER_MODEL: str = "small"  # Balanced speed/accuracy: tiny, base, small, medium, large
    WHISPER_LANGUAGE: str = "pl"  # Polish default, can be "en" or None for auto-detect
    WHISPER_DEVICE: str = "cpu"  # Use CPU (whisper.cpp handles Core ML acceleration)
    WHISPER_CPP_PATH: Path = None  # Path to whisper.cpp binary
    WHISPER_CPP_MODELS_DIR: Path = None  # Path to whisper.cpp models directory
    
    # Timeouts and intervals (seconds)
    TRANSCRIPTION_TIMEOUT: int = 3600  # 60 minutes (increased from 30)
    PERIODIC_CHECK_INTERVAL: int = 30  # 30 seconds
    MOUNT_MONITOR_DELAY: int = 1  # 1 second
    
    # Audio formats
    AUDIO_EXTENSIONS: set = None
    
    # LLM/Summarization configuration
    ENABLE_SUMMARIZATION: bool = True
    LLM_PROVIDER: str = "claude"
    LLM_MODEL: str = "claude-3-haiku-20240307"
    LLM_API_KEY: Optional[str] = None
    SUMMARY_MAX_WORDS: int = 200
    TITLE_MAX_LENGTH: int = 60
    DELETE_TEMP_TXT: bool = True

    # Tagging configuration
    ENABLE_LLM_TAGGING: bool = True
    MAX_TAGS_PER_NOTE: int = 6
    MAX_EXISTING_TAGS_IN_PROMPT: int = 150
    MAX_TAGGER_SUMMARY_CHARS: int = 3000
    MAX_TAGGER_TRANSCRIPT_CHARS: int = 1500
    
    # Markdown template
    MD_TEMPLATE: str = """---
title: "{title}"
date: {date}
recording_date: {recording_date}
source: {source_file}
duration: {duration}
tags: [{tags}]
---

{summary}

## Transkrypcja

{transcript}
"""
    
    def __post_init__(self):
        """Initialize default values after dataclass initialization.
        
        This method loads UserSettings and maps values to the old Config interface
        for backward compatibility.
        """
        # Load user settings (with migration if needed)
        self._user_settings = perform_migration_if_needed()
        
        # Map UserSettings to old Config attributes
        if self.RECORDER_NAMES is None:
            # Use watched_volumes if in specific mode, otherwise use defaults
            if self._user_settings.watch_mode == "specific" and self._user_settings.watched_volumes:
                self.RECORDER_NAMES = self._user_settings.watched_volumes
            else:
                # Legacy default for backward compatibility
                self.RECORDER_NAMES = ["LS-P1", "OLYMPUS", "RECORDER"]
        
        if self.TRANSCRIBE_DIR is None:
            self.TRANSCRIBE_DIR = self._user_settings.output_dir
        
        if self.LOG_DIR is None:
            self.LOG_DIR = Path.home() / "Library" / "Logs"
        
        if self.STATE_FILE is None:
            # Keep legacy state file path for backward compatibility
            self.STATE_FILE = Path.home() / ".olympus_transcriber_state.json"
        
        if self.LOG_FILE is None:
            self.LOG_FILE = self.LOG_DIR / "olympus_transcriber.log"
        
        if self.LOCAL_RECORDINGS_DIR is None:
            # Default to ~/.olympus_transcriber/recordings for staging
            self.LOCAL_RECORDINGS_DIR = Path.home() / ".olympus_transcriber" / "recordings"
        
        if self.PROCESS_LOCK_FILE is None:
            self.PROCESS_LOCK_FILE = Path.home() / ".olympus_transcriber" / "transcriber.lock"
        
        if self.AUDIO_EXTENSIONS is None:
            self.AUDIO_EXTENSIONS = defaults.AUDIO_EXTENSIONS
        
        # Map whisper settings from UserSettings
        # Always use UserSettings values (they are the source of truth)
        self.WHISPER_MODEL = self._user_settings.whisper_model
        self.WHISPER_LANGUAGE = self._user_settings.language or "pl"
        
        if self.WHISPER_CPP_PATH is None:
            # Check for common whisper.cpp executable locations
            whisper_base = Path.home() / "whisper.cpp"
            if (whisper_base / "build" / "bin" / "whisper-cli").exists():
                self.WHISPER_CPP_PATH = whisper_base / "build" / "bin" / "whisper-cli"
            elif (whisper_base / "build" / "bin" / "main").exists():
                self.WHISPER_CPP_PATH = whisper_base / "build" / "bin" / "main"
            elif (whisper_base / "main").exists():
                self.WHISPER_CPP_PATH = whisper_base / "main"
            else:
                # Default fallback (will be checked at runtime)
                self.WHISPER_CPP_PATH = whisper_base / "build" / "bin" / "whisper-cli"
        
        if self.WHISPER_CPP_MODELS_DIR is None:
            self.WHISPER_CPP_MODELS_DIR = Path.home() / "whisper.cpp" / "models"
        
        # Map AI settings from UserSettings
        self.ENABLE_SUMMARIZATION = self._user_settings.enable_ai_summaries
        
        # Load LLM API key from UserSettings or environment
        if self.LLM_API_KEY is None:
            if self._user_settings.ai_api_key:
                self.LLM_API_KEY = self._user_settings.ai_api_key
            else:
                # Fallback to environment for backward compatibility
                if self.LLM_PROVIDER == "claude":
                    self.LLM_API_KEY = os.getenv("ANTHROPIC_API_KEY")
                elif self.LLM_PROVIDER == "openai":
                    self.LLM_API_KEY = os.getenv("OPENAI_API_KEY")
                elif self.LLM_PROVIDER == "ollama":
                    # Ollama doesn't require API key, but we can use base URL
                    self.LLM_API_KEY = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        # Disable summarization if API key is missing (unless Ollama)
        if self.ENABLE_SUMMARIZATION and self.LLM_PROVIDER != "ollama":
            if not self.LLM_API_KEY:
                self.ENABLE_SUMMARIZATION = False

        if self.ENABLE_LLM_TAGGING and not self.ENABLE_SUMMARIZATION:
            self.ENABLE_LLM_TAGGING = False
    
    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.TRANSCRIBE_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.LOCAL_RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)


# Global configuration instance
config = Config()

