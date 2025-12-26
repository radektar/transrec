"""Configuration module for Olympus Transcriber."""

import os
import shutil
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
    FFMPEG_PATH: Path = None  # Path to ffmpeg binary (Faza 2)
    
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
        """Initialize default values after dataclass initialization."""
        if self.RECORDER_NAMES is None:
            self.RECORDER_NAMES = ["LS-P1", "OLYMPUS", "RECORDER"]
        
        if self.TRANSCRIBE_DIR is None:
            # 1. Priority: environment variable (can be set differently on each Mac)
            env_dir = os.getenv("OLYMPUS_TRANSCRIBE_DIR")
            if env_dir:
                self.TRANSCRIBE_DIR = Path(env_dir).expanduser().resolve()
            else:
                # 2. Fallback: standard Obsidian vault location in iCloud,
                # based on user's home directory (Path.home())
                self.TRANSCRIBE_DIR = (
                    Path.home()
                    / "Library"
                    / "Mobile Documents"
                    / "iCloud~md~obsidian"
                    / "Documents"
                    / "Obsidian"
                    / "11-Transcripts"
                ).resolve()
        
        if self.LOG_DIR is None:
            self.LOG_DIR = Path.home() / "Library" / "Logs"
        
        if self.STATE_FILE is None:
            self.STATE_FILE = Path.home() / ".olympus_transcriber_state.json"
        
        if self.LOG_FILE is None:
            self.LOG_FILE = self.LOG_DIR / "olympus_transcriber.log"
        
        if self.LOCAL_RECORDINGS_DIR is None:
            # Default to ~/.olympus_transcriber/recordings for staging
            self.LOCAL_RECORDINGS_DIR = Path.home() / ".olympus_transcriber" / "recordings"
        
        if self.PROCESS_LOCK_FILE is None:
            self.PROCESS_LOCK_FILE = Path.home() / ".olympus_transcriber" / "transcriber.lock"
        
        if self.AUDIO_EXTENSIONS is None:
            self.AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".wma"}
        
        if self.WHISPER_CPP_PATH is None:
            # Nowa lokalizacja: ~/Library/Application Support/Transrec/bin/
            support_dir = (
                Path.home() / "Library" / "Application Support" / "Transrec"
            )
            new_whisper_path = support_dir / "bin" / "whisper-cli"
            
            # Sprawdź nową lokalizację (Faza 2)
            if new_whisper_path.exists():
                self.WHISPER_CPP_PATH = new_whisper_path
            else:
                # Fallback do starych lokalizacji (backward compatibility)
                whisper_base = Path.home() / "whisper.cpp"
                if (whisper_base / "build" / "bin" / "whisper-cli").exists():
                    self.WHISPER_CPP_PATH = (
                        whisper_base / "build" / "bin" / "whisper-cli"
                    )
                elif (whisper_base / "build" / "bin" / "main").exists():
                    self.WHISPER_CPP_PATH = whisper_base / "build" / "bin" / "main"
                elif (whisper_base / "main").exists():
                    self.WHISPER_CPP_PATH = whisper_base / "main"
                else:
                    # Default - nowa lokalizacja (będzie pobrana przez downloader)
                    self.WHISPER_CPP_PATH = new_whisper_path
        
        if self.WHISPER_CPP_MODELS_DIR is None:
            # Nowa lokalizacja: ~/Library/Application Support/Transrec/models/
            support_dir = (
                Path.home() / "Library" / "Application Support" / "Transrec"
            )
            new_models_dir = support_dir / "models"
            
            # Sprawdź nową lokalizację
            if new_models_dir.exists():
                self.WHISPER_CPP_MODELS_DIR = new_models_dir
            else:
                # Fallback do starej lokalizacji
                self.WHISPER_CPP_MODELS_DIR = Path.home() / "whisper.cpp" / "models"
        
        if self.FFMPEG_PATH is None:
            # Nowa lokalizacja: ~/Library/Application Support/Transrec/bin/ffmpeg
            support_dir = (
                Path.home() / "Library" / "Application Support" / "Transrec"
            )
            new_ffmpeg_path = support_dir / "bin" / "ffmpeg"
            
            # Sprawdź nową lokalizację (Faza 2)
            if new_ffmpeg_path.exists():
                self.FFMPEG_PATH = new_ffmpeg_path
            else:
                # Fallback do systemowego ffmpeg (shutil.which)
                system_ffmpeg = shutil.which("ffmpeg")
                if system_ffmpeg:
                    self.FFMPEG_PATH = Path(system_ffmpeg)
                else:
                    # Default - nowa lokalizacja (będzie pobrana przez downloader)
                    self.FFMPEG_PATH = new_ffmpeg_path
        
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

        if self.ENABLE_LLM_TAGGING and not self.ENABLE_SUMMARIZATION:
            self.ENABLE_LLM_TAGGING = False
    
    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.TRANSCRIBE_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.LOCAL_RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)


# Global configuration instance
config = Config()

