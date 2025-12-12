"""Tests for file monitor module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.file_monitor import FileMonitor


@pytest.fixture
def mock_callback():
    """Create a mock callback function."""
    return Mock()


def test_file_monitor_initialization(mock_callback):
    """Test FileMonitor initializes correctly."""
    monitor = FileMonitor(mock_callback)
    
    assert monitor.callback == mock_callback
    assert monitor.observer is None
    assert not monitor.is_monitoring


def test_file_monitor_start_without_fsevents(mock_callback):
    """Test start when FSEvents is not available."""
    with patch('src.file_monitor.FSEVENTS_AVAILABLE', False):
        monitor = FileMonitor(mock_callback)
        monitor.start()
        
        assert not monitor.is_monitoring


@patch('src.file_monitor.FSEVENTS_AVAILABLE', True)
@patch('src.file_monitor.Observer')
@patch('src.file_monitor.Stream')
def test_file_monitor_start_success(mock_stream, mock_observer, mock_callback):
    """Test successful start of file monitor."""
    monitor = FileMonitor(mock_callback)
    
    mock_observer_instance = MagicMock()
    mock_observer.return_value = mock_observer_instance
    
    monitor.start()
    
    assert monitor.is_monitoring
    mock_observer_instance.start.assert_called_once()


@patch('src.file_monitor.FSEVENTS_AVAILABLE', True)
def test_file_monitor_start_already_running(mock_callback):
    """Test start when already monitoring."""
    monitor = FileMonitor(mock_callback)
    monitor.is_monitoring = True
    
    with patch('src.file_monitor.Observer'):
        monitor.start()
        # Should not create new observer


def test_file_monitor_stop(mock_callback):
    """Test stop method."""
    monitor = FileMonitor(mock_callback)
    
    mock_observer = MagicMock()
    monitor.observer = mock_observer
    monitor.is_monitoring = True
    
    monitor.stop()
    
    mock_observer.stop.assert_called_once()
    mock_observer.join.assert_called_once()
    assert not monitor.is_monitoring


def test_file_monitor_stop_no_observer(mock_callback):
    """Test stop when no observer exists."""
    monitor = FileMonitor(mock_callback)
    monitor.observer = None
    
    # Should not raise any errors
    monitor.stop()


@patch('src.file_monitor.FSEVENTS_AVAILABLE', True)
@patch('src.file_monitor.Observer')
@patch('src.file_monitor.Stream')
def test_file_monitor_ignores_system_directories(mock_stream, mock_observer, mock_callback):
    """Test that system directories like .Spotlight-V100 are ignored."""
    from src.file_monitor import FileMonitor
    import time
    
    monitor = FileMonitor(mock_callback)
    monitor._last_trigger_time = 0.0  # Reset debounce timer
    
    mock_observer_instance = MagicMock()
    mock_observer.return_value = mock_observer_instance
    
    # Capture the on_change callback
    on_change_callback = None
    def capture_stream(callback, path, **kwargs):
        nonlocal on_change_callback
        on_change_callback = callback
        return MagicMock()
    
    mock_stream.side_effect = capture_stream
    
    monitor.start()
    
    # Simulate FSEvents callback with system directory path
    if on_change_callback:
        on_change_callback("/Volumes/LS-P1/.Spotlight-V100/Store-V2", 0)
        time.sleep(0.1)  # Small delay to ensure callback processing
    
    # Callback should not have been called
    mock_callback.assert_not_called()


@patch('src.file_monitor.FSEVENTS_AVAILABLE', True)
@patch('src.file_monitor.Observer')
@patch('src.file_monitor.Stream')
@patch('src.file_monitor.time.sleep')
def test_file_monitor_triggers_on_valid_path(mock_sleep, mock_stream, mock_observer, mock_callback):
    """Test that valid recorder paths trigger the callback."""
    from src.file_monitor import FileMonitor
    import time
    
    monitor = FileMonitor(mock_callback)
    monitor._last_trigger_time = 0.0  # Reset debounce timer
    
    mock_observer_instance = MagicMock()
    mock_observer.return_value = mock_observer_instance
    
    # Capture the on_change callback
    on_change_callback = None
    def capture_stream(callback, path, **kwargs):
        nonlocal on_change_callback
        on_change_callback = callback
        return MagicMock()
    
    mock_stream.side_effect = capture_stream
    
    monitor.start()
    
    # Simulate FSEvents callback with valid audio file path
    if on_change_callback:
        on_change_callback("/Volumes/LS-P1/Folder/audio.mp3", 0)
        time.sleep(0.1)  # Small delay to ensure callback processing
    
    # Callback should have been called
    mock_callback.assert_called_once()


@patch('src.file_monitor.FSEVENTS_AVAILABLE', True)
@patch('src.file_monitor.Observer')
@patch('src.file_monitor.Stream')
def test_file_monitor_ignores_non_recorder_paths(mock_stream, mock_observer, mock_callback):
    """Test that paths not under recorder volumes are ignored."""
    from src.file_monitor import FileMonitor
    import time
    
    monitor = FileMonitor(mock_callback)
    monitor._last_trigger_time = 0.0  # Reset debounce timer
    
    mock_observer_instance = MagicMock()
    mock_observer.return_value = mock_observer_instance
    
    # Capture the on_change callback
    on_change_callback = None
    def capture_stream(callback, path, **kwargs):
        nonlocal on_change_callback
        on_change_callback = callback
        return MagicMock()
    
    mock_stream.side_effect = capture_stream
    
    monitor.start()
    
    # Simulate FSEvents callback with path not under recorder
    if on_change_callback:
        on_change_callback("/Volumes/OtherDisk/file.txt", 0)
        time.sleep(0.1)  # Small delay to ensure callback processing
    
    # Callback should not have been called
    mock_callback.assert_not_called()






