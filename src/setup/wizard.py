"""First-run setup wizard."""

import rumps
import threading
from enum import Enum, auto
from typing import Optional

from src.config import UserSettings, SUPPORTED_LANGUAGES, SUPPORTED_MODELS
from src.setup.downloader import DependencyDownloader
from src.setup.permissions import check_full_disk_access, open_fda_preferences
from src.setup.errors import NetworkError, DiskSpaceError, DownloadError
from src.logger import logger


class WizardStep(Enum):
    """Kroki wizarda konfiguracji."""

    WELCOME = auto()
    DOWNLOAD = auto()
    PERMISSIONS = auto()
    SOURCE_CONFIG = auto()
    OUTPUT_CONFIG = auto()
    LANGUAGE = auto()
    AI_CONFIG = auto()
    FINISH = auto()


class SetupWizard:
    """First-run setup wizard."""

    STEPS_ORDER = [
        WizardStep.WELCOME,
        WizardStep.DOWNLOAD,
        WizardStep.PERMISSIONS,
        WizardStep.SOURCE_CONFIG,
        WizardStep.OUTPUT_CONFIG,
        WizardStep.LANGUAGE,
        WizardStep.AI_CONFIG,
        WizardStep.FINISH,
    ]

    def __init__(self):
        """Inicjalizacja wizarda."""
        self.current_step_index = 0
        self.settings = UserSettings.load()
        self.downloader = DependencyDownloader(
            progress_callback=self._on_progress
        )
        self._download_status = ""
        self._download_in_progress = False
        self._download_error: Optional[Exception] = None
        self._download_complete = False
        self._wizard_completed = False

    @staticmethod
    def needs_setup() -> bool:
        """Sprawdź czy wizard jest potrzebny."""
        settings = UserSettings.load()
        return not settings.setup_completed

    @property
    def current_step(self) -> WizardStep:
        """Zwróć aktualny krok wizarda."""
        return self.STEPS_ORDER[self.current_step_index]

    def run(self) -> bool:
        """Uruchom wizard. Zwraca True jeśli ukończony pomyślnie."""
        logger.info("Uruchamianie Setup Wizard")
        
        self._wizard_completed = False
        
        # Uruchom pierwszy krok - wizard działa synchronicznie
        # Każdy krok blokuje do zakończenia (włącznie z pobieraniem)
        self._process_wizard_step()
        
        return self._wizard_completed

    def _process_wizard_step(self):
        """Przetwórz aktualny krok wizarda."""
        if self.current_step == WizardStep.FINISH:
            # Finalizacja
            self._show_finish()
            self.settings.setup_completed = True
            self.settings.save()
            logger.info("Setup Wizard zakończony pomyślnie")
            self._wizard_completed = True
            return
        
        result = self._run_current_step()

        if result == "cancel":
            logger.info("Wizard anulowany przez użytkownika")
            self._wizard_completed = False
            return
        elif result == "back" and self.current_step_index > 0:
            self.current_step_index -= 1
            # Kontynuuj natychmiast (synchronicznie)
            self._process_wizard_step()
        elif result == "next":
            self.current_step_index += 1
            # Kontynuuj natychmiast (synchronicznie)
            self._process_wizard_step()

    def _run_current_step(self) -> str:
        """Wykonaj aktualny krok."""
        step_handlers = {
            WizardStep.WELCOME: self._show_welcome,
            WizardStep.DOWNLOAD: self._show_download,
            WizardStep.PERMISSIONS: self._show_permissions,
            WizardStep.SOURCE_CONFIG: self._show_source_config,
            WizardStep.OUTPUT_CONFIG: self._show_output_config,
            WizardStep.LANGUAGE: self._show_language,
            WizardStep.AI_CONFIG: self._show_ai_config,
        }
        handler = step_handlers.get(self.current_step)
        if handler:
            return handler()
        return "next"

    def _on_progress(self, name: str, progress: float):
        """Callback postępu pobierania - wywoływany z wątku pobierania."""
        self._download_status = f"{name}: {int(progress * 100)}%"
        logger.debug(f"Pobieranie: {self._download_status}")
        
        # Wyślij notyfikację co 10% postępu
        percent = int(progress * 100)
        if percent % 10 == 0 or percent == 100:
            rumps.notification(
                title="Transrec - Pobieranie",
                subtitle=f"{name}",
                message=f"Postęp: {percent}%"
            )

    def _show_welcome(self) -> str:
        """Ekran powitalny."""
        response = rumps.alert(
            title="🎙️ Witaj w Transrec!",
            message=(
                "Transrec automatycznie transkrybuje nagrania "
                "z Twojego dyktafonu lub karty SD.\n\n"
                "Przeprowadzimy Cię przez szybką konfigurację.\n\n"
                "Zajmie to około 3-5 minut."
            ),
            ok="Rozpocznij →",
            cancel="Anuluj",
        )
        return "next" if response == 1 else "cancel"

    def _show_download(self) -> str:
        """Pobieranie zależności - skip jeśli już pobrane."""
        if self.downloader.check_all():
            logger.info("Zależności już zainstalowane - pomijam krok")
            return "next"

        response = rumps.alert(
            title="📥 Pobieranie silnika transkrypcji",
            message=(
                "Transrec wymaga pobrania silnika transkrypcji (~500MB).\n\n"
                "Wymagane komponenty:\n"
                "• whisper.cpp (~10MB)\n"
                "• ffmpeg (~15MB)\n"
                "• Model transkrypcji (~466MB)\n\n"
                "Wymagane jest połączenie z internetem.\n\n"
                "Pobieranie może potrwać kilka minut."
            ),
            ok="Pobierz teraz",
            cancel="Anuluj",
        )

        if response != 1:
            return "cancel"

        # Resetuj flagi
        self._download_in_progress = True
        self._download_complete = False
        self._download_error = None
        self._download_status = "Rozpoczynanie..."

        # Uruchom pobieranie w osobnym wątku
        download_thread = threading.Thread(
            target=self._download_in_background,
            daemon=True,
            name="WizardDownload"
        )
        download_thread.start()

        # Pokaż okno z informacją o pobieraniu (blokuje UI aż do zakończenia)
        # Używamy pętli z alertami co kilka sekund aby informować o postępie
        import time
        while self._download_in_progress:
            # Pokaż aktualny status
            response = rumps.alert(
                title="⏳ Pobieranie w toku...",
                message=(
                    f"Status: {self._download_status}\n\n"
                    "Proszę czekać, pobieranie może potrwać kilka minut.\n"
                    "Nie zamykaj tego okna."
                ),
                ok="Sprawdź status",
                cancel=None,  # Brak przycisku anuluj - nie można przerwać
            )
            # Krótka pauza przed kolejnym sprawdzeniem
            time.sleep(2)

        # Pobieranie zakończone - sprawdź wynik
        if self._download_error:
            error_msg = str(self._download_error)
            if isinstance(self._download_error, NetworkError):
                rumps.alert(
                    title="❌ Brak połączenia",
                    message=f"Brak połączenia z internetem:\n\n{error_msg}",
                    ok="OK",
                )
            elif isinstance(self._download_error, DiskSpaceError):
                rumps.alert(
                    title="❌ Brak miejsca",
                    message=f"Brak miejsca na dysku:\n\n{error_msg}",
                    ok="OK",
                )
            elif isinstance(self._download_error, DownloadError):
                rumps.alert(
                    title="❌ Błąd pobierania",
                    message=f"Nie udało się pobrać zależności:\n\n{error_msg}",
                    ok="OK",
                )
            else:
                rumps.alert(
                    title="❌ Błąd",
                    message=f"Nieoczekiwany błąd:\n\n{error_msg}",
                    ok="OK",
                )
            return "cancel"

        if self._download_complete:
            rumps.alert(
                title="✅ Pobrano",
                message="Silnik transkrypcji został pobrany pomyślnie.",
                ok="Dalej",
            )
            return "next"

        # Nieoczekiwany stan
        return "cancel"

    def _download_in_background(self):
        """Wykonaj pobieranie w tle (w osobnym wątku)."""
        try:
            logger.info("Rozpoczęto pobieranie zależności w tle")
            self.downloader.download_all()
            self._download_complete = True
            logger.info("✓ Pobieranie zakończone pomyślnie")
        except Exception as e:
            logger.error(f"Błąd podczas pobierania: {e}", exc_info=True)
            self._download_error = e
        finally:
            self._download_in_progress = False

    def _show_permissions(self) -> str:
        """Instrukcje Full Disk Access - skip jeśli już nadane."""
        if check_full_disk_access():
            logger.info("FDA już nadane - pomijam krok")
            return "next"

        response = rumps.alert(
            title="🔐 Uprawnienia dostępu do dysków",
            message=(
                "Aby automatycznie wykrywać dyktafon, Transrec "
                "potrzebuje uprawnień 'Full Disk Access'.\n\n"
                "Instrukcja:\n"
                "1. Kliknij 'Otwórz Ustawienia'\n"
                "2. Odblokuj kłódkę 🔒 (hasło administratora)\n"
                "3. Znajdź 'Transrec' i zaznacz ☑\n"
                "4. Wróć do tej aplikacji\n\n"
                "Możesz też pominąć ten krok i wybierać pliki ręcznie."
            ),
            ok="Otwórz Ustawienia",
            cancel="Pomiń",
        )

        if response == 1:
            open_fda_preferences()
            rumps.alert(
                title="Gotowe?",
                message="Kliknij OK gdy nadasz uprawnienia w Ustawieniach Systemowych.",
                ok="OK",
            )

        return "next"

    def _show_source_config(self) -> str:
        """Konfiguracja źródeł nagrań."""
        response = rumps.alert(
            title="📁 Źródła nagrań",
            message=(
                "Skąd pobierać nagrania do transkrypcji?\n\n"
                "• Automatycznie - wykrywa każdy nowy dysk/kartę SD\n"
                "  (zalecane dla większości użytkowników)\n\n"
                "• Określone dyski - tylko wybrane nazwy dysków\n"
                "  (np. LS-P1, ZOOM-H6)"
            ),
            ok="Automatycznie",
            cancel="Określone dyski",
        )

        if response == 1:
            self.settings.watch_mode = "auto"
            self.settings.watched_volumes = []
        else:
            # Pytaj o nazwy dysków
            window = rumps.Window(
                title="Nazwy dysków",
                message="Wpisz nazwy dysków oddzielone przecinkami\n(np. LS-P1, ZOOM-H6):",
                default_text="LS-P1",
                ok="OK",
                cancel="Wstecz",
                dimensions=(300, 24),
            )
            result = window.run()

            if result.clicked == 0:  # Cancel/Wstecz
                return "back"

            volumes = [v.strip() for v in result.text.split(",") if v.strip()]
            self.settings.watch_mode = "specific"
            self.settings.watched_volumes = volumes

        return "next"

    def _show_output_config(self) -> str:
        """Konfiguracja folderu docelowego."""
        window = rumps.Window(
            title="📂 Folder na transkrypcje",
            message=(
                "Gdzie zapisywać pliki z transkrypcjami?\n\n"
                "Domyślnie: folder Obsidian w iCloud\n"
                "(możesz zmienić na dowolny folder)"
            ),
            default_text=self.settings.output_dir,
            ok="OK",
            cancel="Wstecz",
            dimensions=(400, 24),
        )
        result = window.run()

        if result.clicked == 0:
            return "back"

        self.settings.output_dir = result.text.strip()
        return "next"

    def _show_language(self) -> str:
        """Konfiguracja języka transkrypcji."""
        # Lista języków jako tekst
        lang_options = "\n".join(
            [f"• {code}: {name}" for code, name in SUPPORTED_LANGUAGES.items()]
        )

        window = rumps.Window(
            title="🗣️ Język transkrypcji",
            message=(
                f"W jakim języku są Twoje nagrania?\n\n"
                f"Dostępne opcje:\n{lang_options}\n\n"
                f"Wpisz kod języka:"
            ),
            default_text=self.settings.language,
            ok="OK",
            cancel="Wstecz",
            dimensions=(200, 24),
        )
        result = window.run()

        if result.clicked == 0:
            return "back"

        lang = result.text.strip().lower()
        if lang in SUPPORTED_LANGUAGES:
            self.settings.language = lang

        return "next"

    def _show_ai_config(self) -> str:
        """Konfiguracja AI podsumowań (opcjonalne)."""
        response = rumps.alert(
            title="🤖 AI Podsumowania (opcjonalne)",
            message=(
                "Transrec może generować inteligentne podsumowania "
                "i tytuły używając Claude AI.\n\n"
                "Wymaga to klucza API z anthropic.com\n"
                "(koszt ~$0.01-0.05 za transkrypcję)\n\n"
                "Możesz to skonfigurować później w Ustawieniach."
            ),
            ok="Pomiń",
            cancel="Skonfiguruj API",
        )

        if response == 1:  # Pomiń
            self.settings.enable_ai_summaries = False
            return "next"

        # Konfiguracja API key
        window = rumps.Window(
            title="Klucz API Claude",
            message="Wklej klucz API z anthropic.com:",
            default_text="",
            ok="Zapisz",
            cancel="Pomiń",
            dimensions=(350, 24),
        )
        result = window.run()

        if result.clicked == 1 and result.text.strip():
            self.settings.enable_ai_summaries = True
            self.settings.ai_api_key = result.text.strip()
        else:
            self.settings.enable_ai_summaries = False

        return "next"

    def _show_finish(self) -> str:
        """Ekran zakończenia."""
        rumps.alert(
            title="✅ Transrec jest gotowy!",
            message=(
                "Konfiguracja zakończona.\n\n"
                "Podłącz dyktafon lub kartę SD, a Transrec "
                "automatycznie przetworzy Twoje nagrania.\n\n"
                "Ikona 🎙️ pojawi się w pasku menu (góra ekranu).\n\n"
                "Miłego transkrybowania!"
            ),
            ok="🎉 Rozpocznij!",
        )
        return "next"


