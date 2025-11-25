"""Tests for configuration module."""

import pytest
from pathlib import Path
from src.config import Config


def test_config_initialization():
    """Test that Config initializes with default values."""
    config = Config()
    
    assert config.RECORDER_NAMES == ["LS-P1", "OLYMPUS", "RECORDER"]
    assert config.TRANSCRIPTION_TIMEOUT == 3600  # Updated to 60 minutes
    assert config.PERIODIC_CHECK_INTERVAL == 30
    assert config.MOUNT_MONITOR_DELAY == 1


def test_config_paths():
    """Test that Config creates proper paths."""
    config = Config()
    
    assert isinstance(config.TRANSCRIBE_DIR, Path)
    assert isinstance(config.LOG_DIR, Path)
    assert isinstance(config.LOCAL_RECORDINGS_DIR, Path)
    assert isinstance(config.STATE_FILE, Path)
    assert isinstance(config.LOG_FILE, Path)
    
    # Check paths contain expected components
    assert "11-Transcripts" in str(config.TRANSCRIBE_DIR) or "Transcriptions" in str(config.TRANSCRIBE_DIR)
    assert "Logs" in str(config.LOG_DIR)
    assert ".olympus_transcriber" in str(config.LOCAL_RECORDINGS_DIR)
    assert "recordings" in str(config.LOCAL_RECORDINGS_DIR)
    assert ".olympus_transcriber_state.json" in str(config.STATE_FILE)
    assert "olympus_transcriber.log" in str(config.LOG_FILE)


def test_config_audio_extensions():
    """Test that audio extensions are properly set."""
    config = Config()
    
    assert config.AUDIO_EXTENSIONS == {".mp3", ".wav", ".m4a", ".wma"}


def test_config_whisper_cpp_paths():
    """Test that whisper.cpp paths are set."""
    config = Config()
    
    assert config.WHISPER_CPP_PATH is not None
    assert isinstance(config.WHISPER_CPP_PATH, Path)
    assert config.WHISPER_CPP_MODELS_DIR is not None
    assert isinstance(config.WHISPER_CPP_MODELS_DIR, Path)


def test_config_ensure_directories(tmp_path, monkeypatch):
    """Test that ensure_directories creates needed directories."""
    config = Config()
    
    # Override paths to use temp directory
    config.TRANSCRIBE_DIR = tmp_path / "transcriptions"
    config.LOG_DIR = tmp_path / "logs"
    config.LOCAL_RECORDINGS_DIR = tmp_path / "recordings"
    
    # Ensure they don't exist yet
    assert not config.TRANSCRIBE_DIR.exists()
    assert not config.LOG_DIR.exists()
    assert not config.LOCAL_RECORDINGS_DIR.exists()
    
    # Call ensure_directories
    config.ensure_directories()
    
    # Check they were created
    assert config.TRANSCRIBE_DIR.exists()
    assert config.LOG_DIR.exists()
    assert config.LOCAL_RECORDINGS_DIR.exists()





