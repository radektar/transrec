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



