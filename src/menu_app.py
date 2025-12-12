"""macOS menu bar application for Olympus Transcriber."""

import sys
import threading
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List

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
from src.transcriber import send_notification


class OlympusMenuApp(rumps.App):
    """macOS menu bar application wrapper for Olympus Transcriber."""

    def __init__(self):
        """Initialize menu bar application."""
        if not RUMPS_AVAILABLE:
            raise ImportError(
                "rumps not available. Install with: pip install rumps"
            )

        super(OlympusMenuApp, self).__init__(
            "🎙️",
            template=False
        )

        self.transcriber: Optional[OlympusTranscriber] = None
        self.daemon_thread: Optional[threading.Thread] = None
        self._running = False
        self._retranscription_in_progress = False
        self._retranscription_file: Optional[str] = None

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

        # Retranscribe submenu
        self.retranscribe_menu = rumps.MenuItem("Retranskrybuj plik...")
        self.menu.add(self.retranscribe_menu)

        self.menu.add(rumps.separator)

        self.quit_item = rumps.MenuItem(
            "Zakończ",
            callback=self._quit_app
        )
        self.menu.add(self.quit_item)

        # Start status update timer
        rumps.Timer(self._update_status, 2).start()  # Update every 2 seconds
        
        # Start retranscribe menu refresh timer
        rumps.Timer(self._refresh_retranscribe_menu, 10).start()  # Update every 10 seconds

    def _update_status(self, _):
        """Update status menu item based on current state."""
        # #region agent log
        import json; import datetime; log_path = "/Users/radoslawtaraszka/CODE/Olympus_transcription/.cursor/debug.log"; open(log_path, 'a').write(json.dumps({"location": "menu_app.py:95", "message": "_update_status called", "data": {"transcriber_exists": self.transcriber is not None, "retranscription_in_progress": self._retranscription_in_progress, "retranscription_file": self._retranscription_file}, "timestamp": datetime.datetime.now().timestamp() * 1000, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "A"}) + '\n')
        # #endregion
        if not self.transcriber:
            self.status_item.title = "Status: Nie uruchomiono"
            return

        # Check retranscription first (takes priority)
        if self._retranscription_in_progress:
            filename = self._retranscription_file or "..."
            self.status_item.title = f"Status: Retranskrybowanie {filename}"
            # #region agent log
            import json; import datetime; log_path = "/Users/radoslawtaraszka/CODE/Olympus_transcription/.cursor/debug.log"; open(log_path, 'a').write(json.dumps({"location": "menu_app.py:105", "message": "Status set to retranscribing", "data": {"status_title": self.status_item.title, "filename": filename}, "timestamp": datetime.datetime.now().timestamp() * 1000, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "A"}) + '\n')
            # #endregion
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

    def _get_staged_files(self) -> List[Path]:
        """Get list of audio files in staging directory.
        
        Returns:
            List of audio file paths, sorted by modification time
            (newest first), limited to 10 files
        """
        if not config.LOCAL_RECORDINGS_DIR.exists():
            return []
        
        files = []
        for ext in config.AUDIO_EXTENSIONS:
            # Search both lowercase and uppercase extensions
            files.extend(config.LOCAL_RECORDINGS_DIR.glob(f"*{ext}"))
            files.extend(config.LOCAL_RECORDINGS_DIR.glob(f"*{ext.upper()}"))
        
        # Sort by modification time (newest first) and limit to 10
        sorted_files = sorted(
            files,
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:10]
        
        return sorted_files

    def _refresh_retranscribe_menu(self, _):
        """Refresh the retranscribe submenu with current staged files."""
        # Clear existing submenu items (handle case when _menu is not yet initialized)
        try:
            if self.retranscribe_menu._menu is not None:
                self.retranscribe_menu.clear()
        except (AttributeError, TypeError):
            pass
        
        # Show busy state during retranscription
        if self._retranscription_in_progress:
            busy_item = rumps.MenuItem(
                f"⏳ Retranskrybowanie: {self._retranscription_file or '...'}"
            )
            busy_item.set_callback(None)
            self.retranscribe_menu.add(busy_item)
            return
        
        staged_files = self._get_staged_files()
        
        if not staged_files:
            empty_item = rumps.MenuItem("(brak plików w staging)")
            empty_item.set_callback(None)
            self.retranscribe_menu.add(empty_item)
            return
        
        for audio_file in staged_files:
            try:
                mtime = datetime.fromtimestamp(audio_file.stat().st_mtime)
                date_str = mtime.strftime("%d.%m.%Y %H:%M")
                label = f"📁 {audio_file.name} ({date_str})"
            except OSError:
                label = f"📁 {audio_file.name}"
            
            item = rumps.MenuItem(label)
            # Store file path for callback
            item._audio_path = audio_file
            item.set_callback(self._retranscribe_file_callback)
            self.retranscribe_menu.add(item)

    def _retranscribe_file_callback(self, sender):
        """Handle retranscribe menu item click."""
        audio_path = getattr(sender, '_audio_path', None)
        if not audio_path:
            return
        
        # Check if retranscription already in progress
        if self._retranscription_in_progress:
            rumps.alert(
                "Retranskrypcja w toku",
                f"Poczekaj na zakończenie retranskrypcji:\n{self._retranscription_file}",
                ok="OK"
            )
            return
        
        # Check if automatic transcription is in progress
        if self.transcriber and self.transcriber.state.status == AppStatus.TRANSCRIBING:
            rumps.alert(
                "Transkrypcja w toku",
                "Poczekaj na zakończenie bieżącej transkrypcji.",
                ok="OK"
            )
            return
        
        # Confirm with user
        response = rumps.alert(
            "Retranskrypcja",
            f"Czy na pewno chcesz ponownie transkrybować:\n\n"
            f"{audio_path.name}\n\n"
            f"Istniejąca transkrypcja zostanie usunięta.",
            ok="Tak, retranskrybuj",
            cancel="Anuluj"
        )
        
        if response != 1:  # Cancel
            return
        
        # Set flag BEFORE starting thread
        self._retranscription_in_progress = True
        self._retranscription_file = audio_path.name
        # #region agent log
        import json; import datetime; log_path = "/Users/radoslawtaraszka/CODE/Olympus_transcription/.cursor/debug.log"; open(log_path, 'a').write(json.dumps({"location": "menu_app.py:281", "message": "Retranscription flags set", "data": {"flag": self._retranscription_in_progress, "file": self._retranscription_file}, "timestamp": datetime.datetime.now().timestamp() * 1000, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B"}) + '\n')
        # #endregion
        
        # Send start notification
        send_notification(
            title="Olympus Transcriber",
            subtitle="Rozpoczęto retranskrypcję",
            message=f"Plik: {audio_path.name}"
        )
        
        # Run retranscription in background thread
        def do_retranscribe():
            # #region agent log
            import json; import datetime; log_path = "/Users/radoslawtaraszka/CODE/Olympus_transcription/.cursor/debug.log"; open(log_path, 'a').write(json.dumps({"location": "menu_app.py:293", "message": "Thread started", "data": {"transcriber_exists": self.transcriber is not None, "transcriber.transcriber_exists": self.transcriber.transcriber is not None if self.transcriber else False, "audio_path": str(audio_path)}, "timestamp": datetime.datetime.now().timestamp() * 1000, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B,C"}) + '\n')
            # #endregion
            try:
                if self.transcriber and self.transcriber.transcriber:
                    # #region agent log
                    import json; import datetime; log_path = "/Users/radoslawtaraszka/CODE/Olympus_transcription/.cursor/debug.log"; open(log_path, 'a').write(json.dumps({"location": "menu_app.py:295", "message": "Calling force_retranscribe", "data": {"audio_path": str(audio_path)}, "timestamp": datetime.datetime.now().timestamp() * 1000, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "C"}) + '\n')
                    # #endregion
                    success = self.transcriber.transcriber.force_retranscribe(audio_path)
                    # #region agent log
                    import json; import datetime; log_path = "/Users/radoslawtaraszka/CODE/Olympus_transcription/.cursor/debug.log"; open(log_path, 'a').write(json.dumps({"location": "menu_app.py:297", "message": "force_retranscribe returned", "data": {"success": success}, "timestamp": datetime.datetime.now().timestamp() * 1000, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B,C"}) + '\n')
                    # #endregion
                    
                    if success:
                        # #region agent log
                        import json; import datetime; log_path = "/Users/radoslawtaraszka/CODE/Olympus_transcription/.cursor/debug.log"; open(log_path, 'a').write(json.dumps({"location": "menu_app.py:315", "message": "Sending success notification", "data": {"audio_path": str(audio_path)}, "timestamp": datetime.datetime.now().timestamp() * 1000, "sessionId": "debug-session", "runId": "run2", "hypothesisId": "FIX"}) + '\n')
                        # #endregion
                        send_notification(
                            title="Olympus Transcriber",
                            subtitle="Retranskrypcja zakończona",
                            message=f"Plik: {audio_path.name}"
                        )
                        # #region agent log
                        import json; import datetime; log_path = "/Users/radoslawtaraszka/CODE/Olympus_transcription/.cursor/debug.log"; open(log_path, 'a').write(json.dumps({"location": "menu_app.py:322", "message": "Success notification sent", "data": {}, "timestamp": datetime.datetime.now().timestamp() * 1000, "sessionId": "debug-session", "runId": "run2", "hypothesisId": "FIX"}) + '\n')
                        # #endregion
                    else:
                        # #region agent log
                        import json; import datetime; log_path = "/Users/radoslawtaraszka/CODE/Olympus_transcription/.cursor/debug.log"; open(log_path, 'a').write(json.dumps({"location": "menu_app.py:324", "message": "Sending failure notification", "data": {"audio_path": str(audio_path)}, "timestamp": datetime.datetime.now().timestamp() * 1000, "sessionId": "debug-session", "runId": "run2", "hypothesisId": "FIX"}) + '\n')
                        # #endregion
                        send_notification(
                            title="Olympus Transcriber",
                            subtitle="Retranskrypcja nieudana",
                            message=f"Sprawdź logi: {audio_path.name}"
                        )
            except Exception as e:
                # #region agent log
                import json; import datetime; log_path = "/Users/radoslawtaraszka/CODE/Olympus_transcription/.cursor/debug.log"; open(log_path, 'a').write(json.dumps({"location": "menu_app.py:309", "message": "Exception in thread", "data": {"error": str(e)}, "timestamp": datetime.datetime.now().timestamp() * 1000, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B"}) + '\n')
                # #endregion
                logger.error(f"Retranscribe error: {e}", exc_info=True)
                send_notification(
                    title="Olympus Transcriber",
                    subtitle="Błąd",
                    message=str(e)[:50]
                )
            finally:
                # Always clear flag when done
                # #region agent log
                import json; import datetime; log_path = "/Users/radoslawtaraszka/CODE/Olympus_transcription/.cursor/debug.log"; open(log_path, 'a').write(json.dumps({"location": "menu_app.py:318", "message": "Clearing retranscription flags in finally", "data": {"was_in_progress": self._retranscription_in_progress}, "timestamp": datetime.datetime.now().timestamp() * 1000, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B,E"}) + '\n')
                # #endregion
                self._retranscription_in_progress = False
                self._retranscription_file = None
        
        thread = threading.Thread(target=do_retranscribe, daemon=True)
        thread.start()

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

