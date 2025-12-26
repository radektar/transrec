"""Integration tests for volume detection using simulated volumes.

These tests simulate real-world scenarios of volume mounting/unmounting
without requiring physical USB drives or SD cards. They test the complete
flow from FSEvents callback through volume detection to callback triggering.

Tests cover scenarios from MANUAL_TESTING_PHASE_1.md:
- Watch mode "auto" - automatic detection
- Watch mode "specific" - only watched volumes
- Watch mode "manual" - no auto-detection
- Different audio formats
- Empty volumes
- System volumes
- Multiple volumes
"""

import pytest
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import after mocking to avoid circular import issues
from src.config.settings import UserSettings
from src.config.defaults import defaults


@pytest.fixture
def mock_callback():
    """Create a mock callback function."""
    return Mock()


@pytest.fixture
def simulated_volumes_dir(tmp_path):
    """Create a simulated /Volumes directory structure."""
    volumes_dir = tmp_path / "Volumes"
    volumes_dir.mkdir()
    return volumes_dir


def _setup_file_monitor_mocks(monkeypatch, simulated_volumes_dir):
    """Helper function to setup mocks for file_monitor module.
    
    Returns:
        tuple: (FileMonitor, file_monitor_module, callback_holder)
        callback_holder is a dict with 'callback' key that will be set when Stream is called
    """
    import sys
    
    # Mock logger/config BEFORE importing file_monitor to avoid circular imports
    mock_logger = MagicMock()
    mock_config = MagicMock()
    mock_config.MOUNT_MONITOR_DELAY = 0.0
    
    # Create mock modules
    mock_logger_module = MagicMock()
    mock_logger_module.logger = mock_logger
    
    mock_config_module = MagicMock()
    mock_config_module.config = mock_config
    
    # Temporarily replace in sys.modules BEFORE any imports
    original_logger = sys.modules.get('src.logger')
    original_config = sys.modules.get('src.config')
    
    sys.modules['src.logger'] = mock_logger_module
    sys.modules['src.config'] = mock_config_module
    
    # Use a shared dict to hold the callback
    callback_holder = {'callback': None}
    
    try:
        # Now import after mocking
        from src.file_monitor import FileMonitor
        import src.file_monitor as file_monitor_module
        
        # Patch module attributes
        monkeypatch.setattr(file_monitor_module, 'FSEVENTS_AVAILABLE', True)
        monkeypatch.setattr(file_monitor_module.time, 'sleep', Mock())
        file_monitor_module.config.MOUNT_MONITOR_DELAY = 0.0
        
        # Monkeypatch Path("/Volumes")
        original_path = Path
        def mock_path(path_str):
            if path_str == "/Volumes":
                return simulated_volumes_dir
            return original_path(path_str)
        
        monkeypatch.setattr(file_monitor_module, "Path", mock_path)
        
        # Mock Stream - capture callback in shared holder
        mock_stream_class = MagicMock()
        def capture_stream(callback, path, **kwargs):
            callback_holder['callback'] = callback
            return MagicMock()
        mock_stream_class.side_effect = capture_stream
        monkeypatch.setattr(file_monitor_module, 'Stream', mock_stream_class)
        
        # Mock Observer
        mock_observer_instance = MagicMock()
        mock_observer_class = MagicMock(return_value=mock_observer_instance)
        monkeypatch.setattr(file_monitor_module, 'Observer', mock_observer_class)
        
        return FileMonitor, file_monitor_module, callback_holder
    finally:
        # Restore original modules
        if original_logger is not None:
            sys.modules['src.logger'] = original_logger
        elif 'src.logger' in sys.modules:
            del sys.modules['src.logger']
            
        if original_config is not None:
            sys.modules['src.config'] = original_config
        elif 'src.config' in sys.modules:
            del sys.modules['src.config']


class TestVolumeSimulationAutoMode:
    """Integration tests for auto mode with simulated volumes."""
    
    def test_auto_mode_detects_usb_with_audio(
        self, mock_callback, simulated_volumes_dir, monkeypatch
    ):
        """Test auto mode detects USB drive with audio files."""
        FileMonitor, file_monitor_module, callback_holder = _setup_file_monitor_mocks(
            monkeypatch, simulated_volumes_dir
        )
        
        # Create simulated USB drive with audio
        usb_volume = simulated_volumes_dir / "USB_DRIVE"
        usb_volume.mkdir()
        (usb_volume / "recording1.mp3").touch()
        (usb_volume / "recording2.wav").touch()
        
        # Setup monitor
        monitor = FileMonitor(mock_callback)
        monitor._last_trigger_time = 0.0
        
        # Setup UserSettings for auto mode
        with patch.object(file_monitor_module, 'UserSettings') as mock_user_settings:
            mock_user_settings.load = Mock(return_value=UserSettings(watch_mode="auto"))
            
            monitor.start()
            
            # Get callback from holder (set during monitor.start())
            on_change_callback = callback_holder['callback']
            
            # Simulate FSEvents callback for audio file
            if on_change_callback:
                on_change_callback(str(usb_volume / "recording1.mp3"), 0)
                time.sleep(0.1)
            
            # Callback should have been called
            mock_callback.assert_called_once()
    
    def test_auto_mode_ignores_empty_usb(
        self, mock_callback, simulated_volumes_dir, monkeypatch
    ):
        """Test auto mode ignores USB drive without audio files."""
        FileMonitor, file_monitor_module, callback_holder = _setup_file_monitor_mocks(
            monkeypatch, simulated_volumes_dir
        )
        
        # Create empty USB drive
        empty_usb = simulated_volumes_dir / "EMPTY_USB"
        empty_usb.mkdir()
        (empty_usb / "readme.txt").touch()
        
        monitor = FileMonitor(mock_callback)
        monitor._last_trigger_time = 0.0
        
        with patch.object(file_monitor_module, 'UserSettings') as mock_user_settings:
            mock_user_settings.load = Mock(return_value=UserSettings(watch_mode="auto"))
            
            monitor.start()
            
            # Get callback from holder (set during monitor.start())
            on_change_callback = callback_holder['callback']
            
            if on_change_callback:
                on_change_callback(str(empty_usb / "readme.txt"), 0)
                time.sleep(0.1)
            
            # Callback should NOT have been called
            mock_callback.assert_not_called()
    
    def test_auto_mode_detects_multiple_audio_formats(
        self, mock_callback, simulated_volumes_dir, monkeypatch
    ):
        """Test auto mode detects volumes with various audio formats."""
        FileMonitor, file_monitor_module, callback_holder = _setup_file_monitor_mocks(
            monkeypatch, simulated_volumes_dir
        )
        
        sd_card = simulated_volumes_dir / "SD_CARD"
        sd_card.mkdir()
        
        # Create files with different audio formats
        audio_files = [
            "recording.mp3",
            "recording.wav",
            "recording.m4a",
            "recording.flac",
            "recording.aac",
            "recording.ogg",
        ]
        
        for audio_file in audio_files:
            (sd_card / audio_file).touch()
        
        monitor = FileMonitor(mock_callback)
        monitor._last_trigger_time = 0.0
        
        with patch.object(file_monitor_module, 'UserSettings') as mock_user_settings:
            mock_user_settings.load = Mock(return_value=UserSettings(watch_mode="auto"))
            
            monitor.start()
            
            # Get callback from holder (set during monitor.start())
            on_change_callback = callback_holder['callback']
            
            if on_change_callback:
                on_change_callback(str(sd_card / "recording.mp3"), 0)
                time.sleep(0.1)
            
            # Should detect volume with audio
            mock_callback.assert_called_once()


class TestVolumeSimulationSpecificMode:
    """Integration tests for specific mode with simulated volumes."""
    
    def test_specific_mode_processes_watched_volume(
        self, mock_callback, simulated_volumes_dir, monkeypatch
    ):
        """Test specific mode processes volume in watched list."""
        FileMonitor, file_monitor_module, callback_holder = _setup_file_monitor_mocks(
            monkeypatch, simulated_volumes_dir
        )
        
        watched_volume = simulated_volumes_dir / "SD_CARD"
        watched_volume.mkdir()
        (watched_volume / "audio.mp3").touch()
        
        monitor = FileMonitor(mock_callback)
        monitor._last_trigger_time = 0.0
        
        with patch.object(file_monitor_module, 'UserSettings') as mock_user_settings:
            settings = UserSettings()
            settings.watch_mode = "specific"
            settings.watched_volumes = ["SD_CARD", "USB_DRIVE"]
            mock_user_settings.load = Mock(return_value=settings)
            
            monitor.start()
            
            # Get callback from holder (set during monitor.start())
            on_change_callback = callback_holder['callback']
            
            if on_change_callback:
                on_change_callback(str(watched_volume / "audio.mp3"), 0)
                time.sleep(0.1)
            
            # Should process volume in watched list
            mock_callback.assert_called_once()
    
    def test_specific_mode_ignores_unwatched_volume(
        self, mock_callback, simulated_volumes_dir, monkeypatch
    ):
        """Test specific mode ignores volume not in watched list."""
        FileMonitor, file_monitor_module, callback_holder = _setup_file_monitor_mocks(
            monkeypatch, simulated_volumes_dir
        )
        
        unwatched_volume = simulated_volumes_dir / "OTHER_DEVICE"
        unwatched_volume.mkdir()
        (unwatched_volume / "audio.mp3").touch()
        
        monitor = FileMonitor(mock_callback)
        monitor._last_trigger_time = 0.0
        
        with patch.object(file_monitor_module, 'UserSettings') as mock_user_settings:
            settings = UserSettings()
            settings.watch_mode = "specific"
            settings.watched_volumes = ["SD_CARD", "USB_DRIVE"]
            mock_user_settings.load = Mock(return_value=settings)
            
            monitor.start()
            
            # Get callback from holder (set during monitor.start())
            on_change_callback = callback_holder['callback']
            
            if on_change_callback:
                on_change_callback(str(unwatched_volume / "audio.mp3"), 0)
                time.sleep(0.1)
            
            # Should NOT process volume not in watched list
            mock_callback.assert_not_called()


class TestVolumeSimulationManualMode:
    """Integration tests for manual mode with simulated volumes."""
    
    def test_manual_mode_never_auto_processes(
        self, mock_callback, simulated_volumes_dir, monkeypatch
    ):
        """Test manual mode never auto-processes volumes."""
        FileMonitor, file_monitor_module, callback_holder = _setup_file_monitor_mocks(
            monkeypatch, simulated_volumes_dir
        )
        
        volume = simulated_volumes_dir / "ANY_DEVICE"
        volume.mkdir()
        (volume / "audio.mp3").touch()
        
        monitor = FileMonitor(mock_callback)
        monitor._last_trigger_time = 0.0
        
        with patch.object(file_monitor_module, 'UserSettings') as mock_user_settings:
            mock_user_settings.load = Mock(return_value=UserSettings(watch_mode="manual"))
            
            monitor.start()
            
            # Get callback from holder (set during monitor.start())
            on_change_callback = callback_holder['callback']
            
            if on_change_callback:
                on_change_callback(str(volume / "audio.mp3"), 0)
                time.sleep(0.1)
            
            # Should NOT auto-process in manual mode
            mock_callback.assert_not_called()


class TestVolumeSimulationSystemVolumes:
    """Integration tests for system volume handling."""
    
    def test_system_volumes_always_ignored(
        self, mock_callback, simulated_volumes_dir, monkeypatch
    ):
        """Test that system volumes are always ignored, even with audio."""
        FileMonitor, file_monitor_module, callback_holder = _setup_file_monitor_mocks(
            monkeypatch, simulated_volumes_dir
        )
        
        system_volume = simulated_volumes_dir / "Macintosh HD"
        system_volume.mkdir()
        (system_volume / "audio.mp3").touch()
        
        monitor = FileMonitor(mock_callback)
        monitor._last_trigger_time = 0.0
        
        with patch.object(file_monitor_module, 'UserSettings') as mock_user_settings:
            mock_user_settings.load = Mock(return_value=UserSettings(watch_mode="auto"))
            
            monitor.start()
            
            # Get callback from holder (set during monitor.start())
            on_change_callback = callback_holder['callback']
            
            if on_change_callback:
                on_change_callback(str(system_volume / "audio.mp3"), 0)
                time.sleep(0.1)
            
            # System volumes should never trigger callback
            mock_callback.assert_not_called()


class TestVolumeSimulationMultipleVolumes:
    """Integration tests for multiple volumes scenarios."""
    
    def test_multiple_volumes_auto_mode(
        self, mock_callback, simulated_volumes_dir, monkeypatch
    ):
        """Test auto mode with multiple volumes - only those with audio."""
        FileMonitor, file_monitor_module, callback_holder = _setup_file_monitor_mocks(
            monkeypatch, simulated_volumes_dir
        )
        
        # Volume 1: Has audio - should be detected
        volume1 = simulated_volumes_dir / "USB_DRIVE"
        volume1.mkdir()
        (volume1 / "audio.mp3").touch()
        
        # Volume 2: No audio - should be ignored
        volume2 = simulated_volumes_dir / "EMPTY_DRIVE"
        volume2.mkdir()
        (volume2 / "readme.txt").touch()
        
        # Volume 3: Has audio - should be detected
        volume3 = simulated_volumes_dir / "SD_CARD"
        volume3.mkdir()
        (volume3 / "recording.wav").touch()
        
        monitor = FileMonitor(mock_callback)
        monitor._last_trigger_time = 0.0
        
        with patch.object(file_monitor_module, 'UserSettings') as mock_user_settings:
            mock_user_settings.load = Mock(return_value=UserSettings(watch_mode="auto"))
            
            monitor.start()
            
            # Get callback from holder (set during monitor.start())
            on_change_callback = callback_holder['callback']
            
            # Simulate activity on volume with audio
            if on_change_callback:
                on_change_callback(str(volume1 / "audio.mp3"), 0)
                time.sleep(0.1)
                mock_callback.assert_called_once()
                
                # Reset and test empty volume
                mock_callback.reset_mock()
                monitor._last_trigger_time = 0.0
                
                on_change_callback(str(volume2 / "readme.txt"), 0)
                time.sleep(0.1)
                mock_callback.assert_not_called()
                
                # Reset and test another volume with audio
                monitor._last_trigger_time = 0.0
                
                on_change_callback(str(volume3 / "recording.wav"), 0)
                time.sleep(0.1)
                mock_callback.assert_called_once()


class TestVolumeSimulationDebouncing:
    """Integration tests for debouncing behavior."""
    
    def test_debouncing_prevents_rapid_triggers(
        self, mock_callback, simulated_volumes_dir, monkeypatch
    ):
        """Test that debouncing prevents rapid callback triggers."""
        FileMonitor, file_monitor_module, callback_holder = _setup_file_monitor_mocks(
            monkeypatch, simulated_volumes_dir
        )
        
        volume = simulated_volumes_dir / "USB_DRIVE"
        volume.mkdir()
        (volume / "audio.mp3").touch()
        
        monitor = FileMonitor(mock_callback)
        monitor._last_trigger_time = 0.0
        monitor._debounce_seconds = 2.0
        
        with patch.object(file_monitor_module, 'UserSettings') as mock_user_settings:
            mock_user_settings.load = Mock(return_value=UserSettings(watch_mode="auto"))
            
            monitor.start()
            
            # Get callback from holder (set during monitor.start())
            on_change_callback = callback_holder['callback']
            
            if on_change_callback:
                # First trigger
                on_change_callback(str(volume / "audio.mp3"), 0)
                time.sleep(0.1)
                assert mock_callback.call_count == 1
                
                # Second trigger immediately after (within debounce window)
                on_change_callback(str(volume / "audio.mp3"), 0)
                time.sleep(0.1)
                # Should still be 1 (debounced)
                assert mock_callback.call_count == 1


class TestVolumeSimulationNestedDirectories:
    """Integration tests for nested directory structures."""
    
    def test_nested_audio_files_detected(
        self, mock_callback, simulated_volumes_dir, monkeypatch
    ):
        """Test that audio files in nested directories are detected."""
        FileMonitor, file_monitor_module, callback_holder = _setup_file_monitor_mocks(
            monkeypatch, simulated_volumes_dir
        )
        
        volume = simulated_volumes_dir / "RECORDER"
        volume.mkdir()
        
        # Create nested structure (within MAX_SCAN_DEPTH=3)
        # Path: RECORDER/Recordings/2025/meeting.mp3 (depth=3)
        nested_path = volume / "Recordings" / "2025"
        nested_path.mkdir(parents=True)
        (nested_path / "meeting.mp3").touch()
        
        monitor = FileMonitor(mock_callback)
        monitor._last_trigger_time = 0.0
        
        with patch.object(file_monitor_module, 'UserSettings') as mock_user_settings:
            mock_user_settings.load = Mock(return_value=UserSettings(watch_mode="auto"))
            
            monitor.start()
            
            # Get callback from holder (set during monitor.start())
            on_change_callback = callback_holder['callback']
            
            if on_change_callback:
                on_change_callback(str(nested_path / "meeting.mp3"), 0)
                time.sleep(0.1)
            
            # Should detect audio in nested directory
            mock_callback.assert_called_once()


class TestVolumeSimulationLegacyRecorder:
    """Integration tests for legacy recorder compatibility."""
    
    def test_legacy_olympus_recorder_detected(
        self, mock_callback, simulated_volumes_dir, monkeypatch
    ):
        """Test that legacy Olympus LS-P1 recorder is still detected."""
        FileMonitor, file_monitor_module, callback_holder = _setup_file_monitor_mocks(
            monkeypatch, simulated_volumes_dir
        )
        
        olympus = simulated_volumes_dir / "LS-P1"
        olympus.mkdir()
        (olympus / "REC001.mp3").touch()
        
        monitor = FileMonitor(mock_callback)
        monitor._last_trigger_time = 0.0
        
        with patch.object(file_monitor_module, 'UserSettings') as mock_user_settings:
            mock_user_settings.load = Mock(return_value=UserSettings(watch_mode="auto"))
            
            monitor.start()
            
            # Get callback from holder (set during monitor.start())
            on_change_callback = callback_holder['callback']
            
            if on_change_callback:
                on_change_callback(str(olympus / "REC001.mp3"), 0)
                time.sleep(0.1)
            
            # Legacy recorder should still work
            mock_callback.assert_called_once()
