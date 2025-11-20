"""File system monitoring for Olympus Transcriber using FSEvents."""

import time
from typing import Callable, Optional
from pathlib import Path

try:
    from fsevents import Observer, Stream
    FSEVENTS_AVAILABLE = True
except ImportError:
    FSEVENTS_AVAILABLE = False

from src.logger import logger
from src.config import config


class FileMonitor:
    """Monitor /Volumes for recorder mount events using FSEvents.
    
    This class uses macOS FSEvents API to efficiently monitor the /Volumes
    directory for changes, specifically watching for when an Olympus recorder
    is connected.
    
    Attributes:
        callback: Function to call when recorder is detected
        observer: FSEvents Observer instance
        is_monitoring: Flag indicating if monitoring is active
    """
    
    def __init__(self, callback: Callable[[], None]):
        """Initialize the file monitor.
        
        Args:
            callback: Function to call when recorder activity is detected
        """
        if not FSEVENTS_AVAILABLE:
            logger.warning(
                "⚠️  FSEvents not available. Install with: "
                "pip install MacFSEvents"
            )
        
        self.callback = callback
        self.observer: Optional[Observer] = None
        self.is_monitoring = False
        self._last_trigger_time = 0.0
        self._debounce_seconds = 2.0  # Prevent multiple rapid triggers
    
    def start(self) -> None:
        """Start monitoring /Volumes for mount events."""
        if not FSEVENTS_AVAILABLE:
            logger.error("Cannot start FSEvents monitor - library not available")
            return
        
        if self.is_monitoring:
            logger.warning("Monitor already running")
            return
        
        try:
            self.observer = Observer()
            
            def on_change(path, mask):
                """Callback for FSEvents changes."""
                current_time = time.time()
                
                # Debounce: Skip if triggered too recently
                if current_time - self._last_trigger_time < self._debounce_seconds:
                    return
                
                # Check if path matches recorder names
                if any(name in path for name in config.RECORDER_NAMES):
                    logger.info(f"📢 Detected recorder activity: {path}")
                    self._last_trigger_time = current_time
                    
                    # Wait for system to fully mount the volume
                    time.sleep(config.MOUNT_MONITOR_DELAY)
                    
                    # Trigger callback
                    try:
                        self.callback()
                    except Exception as e:
                        logger.error(f"Error in callback: {e}", exc_info=True)
            
            # Create stream watching /Volumes
            stream = Stream(on_change, "/Volumes", file_events=False)
            self.observer.schedule(stream)
            
            self.is_monitoring = True
            self.observer.start()
            
            logger.info("✓ FSEvents monitor started (watching /Volumes)")
            
        except Exception as e:
            logger.error(f"Failed to start FSEvents monitor: {e}", exc_info=True)
            self.is_monitoring = False
    
    def stop(self) -> None:
        """Stop monitoring."""
        if not self.observer:
            return
        
        try:
            self.observer.stop()
            self.observer.join(timeout=5.0)
            self.is_monitoring = False
            logger.info("✓ FSEvents monitor stopped")
        except Exception as e:
            logger.error(f"Error stopping monitor: {e}", exc_info=True)

