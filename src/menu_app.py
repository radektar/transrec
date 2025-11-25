"""macOS menu bar application for Olympus Transcriber."""

import sys
import threading
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

# Load environment variables from project .env so Claude credentials
# are available even when launching the menu app directly.
try:
    from dotenv import load_dotenv

    _ENV_PATH = Path(__file__).parent.parent / ".env"
    if _ENV_PATH.exists():
        load_dotenv(_ENV_PATH)
except ImportError:
    pass

try:
    import rumps
    RUMPS_AVAILABLE = True
except ImportError:
    RUMPS_AVAILABLE = False

from src.env_loader import load_env_file

# Ensure .env variables (e.g., ANTHROPIC_API_KEY) are available before config load
load_env_file()

from src.config import config
from src.logger import logger
from src.app_core import OlympusTranscriber
from src.app_status import AppStatus
from src.state_manager import reset_state


class OlympusMenuApp(rumps.App):
    """macOS menu bar application wrapper for Olympus Transcriber."""

    def __init__(self):
        """Initialize menu bar application."""
        if not RUMPS_AVAILABLE:
            raise ImportError(
                "rumps not available. Install with: pip install rumps"
            )

        super(OlympusMenuApp, self).__init__(
            "Olympus Transcriber",
            template=True
        )

        self.transcriber: Optional[OlympusTranscriber] = None
        self.daemon_thread: Optional[threading.Thread] = None
        self._running = False

        # Create menu items
        self.status_item = rumps.MenuItem("Status: Inicjalizacja...")
        self.menu.add(self.status_item)
        self.menu.add(rumps.separator)

        self.open_logs_item = rumps.MenuItem(
            "Otwórz logi",
            callback=self._open_logs
        )
        self.menu.add(self.open_logs_item)

        self.reset_memory_item = rumps.MenuItem(
            "Resetuj pamięć od...",
            callback=self._reset_memory
        )
        self.menu.add(self.reset_memory_item)

        self.menu.add(rumps.separator)

        self.quit_item = rumps.MenuItem(
            "Zakończ",
            callback=self._quit_app
        )
        self.menu.add(self.quit_item)

        # Start status update timer
        rumps.Timer(self._update_status, 2).start()  # Update every 2 seconds

    def _update_status(self, _):
        """Update status menu item based on current state."""
        if not self.transcriber:
            self.status_item.title = "Status: Nie uruchomiono"
            return

        state = self.transcriber.state
        status_str = state.get_status_string()
        self.status_item.title = f"Status: {status_str}"

        # Update icon based on status
        if state.status == AppStatus.ERROR:
            self.icon = None  # Could set error icon here
        elif state.status == AppStatus.TRANSCRIBING:
            self.icon = None  # Could set processing icon here
        else:
            self.icon = None  # Default icon

    def _open_logs(self, _):
        """Open log file in default editor."""
        log_file = config.LOG_FILE
        if not log_file.exists():
            rumps.alert(
                "Błąd",
                f"Plik logów nie istnieje: {log_file}",
                "OK"
            )
            return

        try:
            # Use macOS 'open' command to open in default editor
            subprocess.run(
                ["open", "-t", str(log_file)],
                check=True,
                timeout=5.0
            )
        except subprocess.TimeoutExpired:
            rumps.alert("Błąd", "Timeout przy otwieraniu logów", "OK")
        except Exception as e:
            rumps.alert(
                "Błąd",
                f"Nie można otworzyć logów: {e}",
                "OK"
            )

    def _reset_memory(self, _):
        """Reset transcription memory to a specific date."""
        # Show simple dialog with date input
        # For simplicity, we'll use a predefined date (7 days ago)
        # In a more advanced version, could use date picker

        response = rumps.alert(
            "Resetuj pamięć",
            "Czy chcesz zresetować pamięć do daty sprzed 7 dni?\n\n"
            "To spowoduje, że przy następnym podłączeniu recordera\n"
            "zostaną przetworzone wszystkie pliki z ostatnich 7 dni.",
            ok="Tak",
            cancel="Anuluj"
        )

        if response == 1:  # "OK" button (1 = OK, 0 = Cancel)
            target_date = datetime.now() - timedelta(days=7)
            success = reset_state(target_date)

            if success:
                rumps.notification(
                    title="Olympus Transcriber",
                    subtitle="Pamięć zresetowana",
                    message=f"Pamięć ustawiona na: {target_date.strftime('%Y-%m-%d')}"
                )
            else:
                rumps.alert(
                    "Błąd",
                    "Nie udało się zresetować pamięci. Sprawdź logi.",
                    ok="OK"
                )

    def _quit_app(self, _):
        """Quit application gracefully."""
        response = rumps.alert(
            "Zakończ",
            "Czy na pewno chcesz zakończyć aplikację?",
            ok="Tak",
            cancel="Anuluj"
        )

        if response == 1:  # "OK" button (1 = OK, 0 = Cancel)
            self._shutdown()
            rumps.quit_application()

    def _shutdown(self):
        """Shutdown transcriber daemon."""
        if self.transcriber:
            logger.info("Shutting down transcriber from menu app...")
            self.transcriber.stop()
            self._running = False

            # Wait for daemon thread to finish
            if self.daemon_thread and self.daemon_thread.is_alive():
                self.daemon_thread.join(timeout=5.0)

    def _run_daemon(self):
        """Run transcriber daemon in background thread."""
        try:
            logger.info("Starting transcriber daemon from menu app...")
            # Don't setup signal handlers in background thread
            self.transcriber = OlympusTranscriber(setup_signals=False)
            self.transcriber.start()
        except Exception as e:
            logger.error(f"Error in daemon thread: {e}", exc_info=True)
            rumps.notification(
                title="Olympus Transcriber",
                subtitle="Błąd",
                message=f"Błąd uruchomienia: {e}"
            )

    def run(self):
        """Start the menu bar application."""
        logger.info("=" * 60)
        logger.info("🚀 Olympus Transcriber Menu App starting...")
        logger.info("=" * 60)

        # Start daemon in background thread
        self._running = True
        self.daemon_thread = threading.Thread(
            target=self._run_daemon,
            daemon=True,
            name="TranscriberDaemon"
        )
        self.daemon_thread.start()

        # Run menu app (blocks until quit)
        super(OlympusMenuApp, self).run()


def main():
    """Main entry point for menu app."""
    if not RUMPS_AVAILABLE:
        print("ERROR: rumps not available. Install with: pip install rumps")
        sys.exit(1)

    try:
        app = OlympusMenuApp()
        app.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

