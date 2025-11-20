"""Main entry point for Olympus Transcriber daemon."""

import sys
import time
import signal
import threading
from pathlib import Path
from typing import Optional

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass

from src.config import config
from src.logger import logger
from src.transcriber import Transcriber
from src.file_monitor import FileMonitor


class OlympusTranscriber:
    """Main application orchestrator.
    
    Manages the lifecycle of the transcriber daemon, coordinating
    FSEvents monitoring, periodic checking, and graceful shutdown.
    
    Attributes:
        transcriber: Transcription engine instance
        monitor: File system monitor instance
        periodic_thread: Background thread for periodic checks
        running: Flag indicating if application is running
    """
    
    def __init__(self):
        """Initialize the application."""
        self.transcriber: Optional[Transcriber] = None
        self.monitor: Optional[FileMonitor] = None
        self.periodic_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        signal_name = signal.Signals(signum).name
        logger.info(f"Received {signal_name}, shutting down...")
        self.stop()
    
    def _periodic_check(self):
        """Periodic check for recorder (fallback if FSEvents misses event).
        
        Runs in a background thread, checking every PERIODIC_CHECK_INTERVAL
        seconds for a connected recorder.
        """
        logger.info(
            f"✓ Periodic checker started "
            f"(interval: {config.PERIODIC_CHECK_INTERVAL}s)"
        )
        
        while self.running:
            try:
                time.sleep(config.PERIODIC_CHECK_INTERVAL)
                
                if not self.running:
                    break
                
                # Only check if recorder is not already being monitored
                if self.transcriber and not self.transcriber.recorder_monitoring:
                    recorder = self.transcriber.find_recorder()
                    if recorder:
                        logger.debug("Periodic check triggered processing")
                        self.transcriber.process_recorder()
            
            except Exception as e:
                logger.error(f"Error in periodic check: {e}", exc_info=True)
        
        logger.info("✓ Periodic checker stopped")
    
    def start(self):
        """Start the transcriber daemon."""
        logger.info("=" * 60)
        logger.info("🚀 Olympus Transcriber starting...")
        logger.info("=" * 60)
        
        # Log configuration
        logger.info(f"📂 Transcription directory: {config.TRANSCRIBE_DIR}")
        logger.info(f"📄 State file: {config.STATE_FILE}")
        logger.info(f"📋 Log file: {config.LOG_FILE}")
        
        # Initialize transcriber
        self.transcriber = Transcriber()
        
        # Initialize file monitor
        self.monitor = FileMonitor(callback=self.transcriber.process_recorder)
        
        # Start FSEvents monitor
        try:
            self.monitor.start()
        except Exception as e:
            logger.error(f"Failed to start file monitor: {e}")
            logger.warning("Continuing with periodic check only")
        
        # Start periodic checker thread
        self.running = True
        self.periodic_thread = threading.Thread(
            target=self._periodic_check,
            daemon=True,
            name="PeriodicChecker"
        )
        self.periodic_thread.start()
        
        logger.info("=" * 60)
        logger.info("✓ All monitors running")
        logger.info("⏳ Waiting for recorder connection...")
        logger.info("   (Press Ctrl+C to stop)")
        logger.info("=" * 60)
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            # Already handled by signal handler, but catch here too
            pass
    
    def stop(self):
        """Stop the transcriber daemon."""
        if not self.running:
            return
        
        logger.info("⏹  Shutting down...")
        
        # Stop running flag
        self.running = False
        
        # Stop file monitor
        if self.monitor:
            try:
                self.monitor.stop()
            except Exception as e:
                logger.error(f"Error stopping monitor: {e}")
        
        # Wait for periodic thread to finish
        if self.periodic_thread and self.periodic_thread.is_alive():
            logger.debug("Waiting for periodic checker to stop...")
            self.periodic_thread.join(timeout=5.0)
        
        logger.info("✓ Shutdown complete")
        logger.info("=" * 60)


def main():
    """Main entry point."""
    try:
        app = OlympusTranscriber()
        app.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()


