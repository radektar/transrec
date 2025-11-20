"""Configuration module for Olympus Transcriber."""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Config:
    """Central configuration for Olympus Transcriber application.
    
    Attributes:
        RECORDER_NAMES: List of possible volume names for the recorder
        TRANSCRIBE_DIR: Directory where transcriptions are saved
        STATE_FILE: JSON file tracking last sync time
        LOG_DIR: Directory for application logs
        LOG_FILE: Path to main log file
        WHISPER_MODEL: Whisper model size (tiny, base, small, medium, large)
        WHISPER_LANGUAGE: Language code for transcription (pl, en, or None for auto)
        WHISPER_DEVICE: Device to use (cpu or auto-detect)
        WHISPER_CPP_PATH: Path to whisper.cpp binary executable
        WHISPER_CPP_MODELS_DIR: Directory containing whisper.cpp models
        TRANSCRIPTION_TIMEOUT: Maximum time allowed for transcription (60 minutes)
        PERIODIC_CHECK_INTERVAL: Fallback check interval (seconds)
        MOUNT_MONITOR_DELAY: Wait time after mount detection (seconds)
        AUDIO_EXTENSIONS: Supported audio file formats
        ENABLE_SUMMARIZATION: Whether to generate summaries using LLM
        LLM_PROVIDER: LLM provider name (claude, openai, ollama)
        LLM_MODEL: Model name for the selected provider
        LLM_API_KEY: API key for LLM provider (from environment)
        SUMMARY_MAX_WORDS: Maximum words in generated summary
        TITLE_MAX_LENGTH: Maximum length for generated title (characters)
        DELETE_TEMP_TXT: Whether to delete temporary TXT files after MD creation
    """
    
    # Recorder detection
    RECORDER_NAMES: List[str] = None
    
    # Directories
    TRANSCRIBE_DIR: Path = None
    LOG_DIR: Path = None
    
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
    
    # Markdown template
    MD_TEMPLATE: str = """---
title: "{title}"
date: {date}
recording_date: {recording_date}
source: {source_file}
duration: {duration}
tags: [transcription]
---

{summary}

## Transkrypcja

{transcript}
"""
    
    def __post_init__(self):
        """Initialize default values after dataclass initialization."""
        if self.RECORDER_NAMES is None:
            self.RECORDER_NAMES = ["LS-P1", "OLYMPUS", "RECORDER"]
        
        if self.TRANSCRIBE_DIR is None:
            # Obsidian vault path for transcriptions
            self.TRANSCRIBE_DIR = Path(
                "/Users/radoslawtaraszka/Library/Mobile Documents/"
                "iCloud~md~obsidian/Documents/Obsidian/11-Transcripts"
            )
        
        if self.LOG_DIR is None:
            self.LOG_DIR = Path.home() / "Library" / "Logs"
        
        if self.STATE_FILE is None:
            self.STATE_FILE = Path.home() / ".olympus_transcriber_state.json"
        
        if self.LOG_FILE is None:
            self.LOG_FILE = self.LOG_DIR / "olympus_transcriber.log"
        
        if self.AUDIO_EXTENSIONS is None:
            self.AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".wma"}
        
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
        
        # Load LLM API key from environment
        if self.LLM_API_KEY is None:
            if self.LLM_PROVIDER == "claude":
                self.LLM_API_KEY = os.getenv("ANTHROPIC_API_KEY")
            elif self.LLM_PROVIDER == "openai":
                self.LLM_API_KEY = os.getenv("OPENAI_API_KEY")
            elif self.LLM_PROVIDER == "ollama":
                # Ollama doesn't require API key, but we can use base URL
                self.LLM_API_KEY = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        # Disable summarization if API key is missing (unless Ollama)
        # Note: logger is imported lazily to avoid circular imports
        if self.ENABLE_SUMMARIZATION and self.LLM_PROVIDER != "ollama":
            if not self.LLM_API_KEY:
                # Logger will be initialized later, just disable feature
                self.ENABLE_SUMMARIZATION = False
    
    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.TRANSCRIBE_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)


# Global configuration instance
config = Config()

