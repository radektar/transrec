# Changelog

All notable changes to Transrec will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### In Progress
- **🚀 Dystrybucja Publiczna (v2.0.0 FREE)** - Szczegółowy plan w [`Docs/PUBLIC-DISTRIBUTION-PLAN.md`](Docs/PUBLIC-DISTRIBUTION-PLAN.md)
  - ✅ **Faza 1:** Uniwersalne źródła nagrań (testy integracyjne zakończone, testy manualne wymagane)
  - ✅ **Faza 2:** System pobierania whisper.cpp/modeli on-demand (COMPLETED)
  - ✅ **Faza 3:** First-run wizard z konfiguracją (COMPLETED ✅ - testy manualne zakończone)
  - ✅ **Faza 4:** Pakowanie z py2app (COMPLETED ✅ - wszystkie testy przechodzą)
  - [ ] **Faza 5:** Code signing & notaryzacja ($99 Apple Developer)
  - [ ] **Faza 6:** Profesjonalny DMG & GitHub Release
  - ✅ **Faza 7:** GUI Settings & polish (COMPLETED ✅ - testy automatyczne przechodzą, testy manualne wymagane)
  - [ ] **Faza 8:** Infrastruktura Freemium (feature flags, placeholder PRO)
  - [ ] **Faza 9:** Pełny redesign UI (nowy instalator, menu, ikony, kolory)

### Planned Features
- **🔒 PRO Features (v2.1.0)** - AI summaries, auto-tagging, cloud sync
- See `BACKLOG.md` for other upcoming features and improvements

---

## [1.15.0] - 2025-01-XX

### Added (Faza 7)
- **Moduł UI** (`src/ui/`)
  - `src/ui/constants.py` - centralne miejsce na stałe UI (łatwe do wymiany przy redesignie)
  - `src/ui/dialogs.py` - reusable funkcje dialogów (date picker, folder picker, about)
- **Date picker dla "Resetuj pamięć"**
  - Dialog z opcjami: 7 dni / 30 dni / Inna data
  - Input daty w formacie YYYY-MM-DD z walidacją
  - Zastępuje prosty dialog z tylko opcją "7 dni"
- **Graficzny wybór folderu w wizardzie**
  - NSOpenPanel dla natywnego dialogu wyboru folderu
  - Fallback na tekstowy input gdy AppKit niedostępne
- **Dialog "O aplikacji"**
  - Nowy MenuItem w menu aplikacji
  - Wyświetla wersję, linki do strony i GitHub, informacje o licencji
- **Testy automatyczne** (`tests/test_ui_constants.py`, `tests/test_ui_dialogs.py`)
  - 18 testów jednostkowych (100% pass rate)
  - Coverage modułu UI: 94% (powyżej wymaganego 80%)
- **Dokumentacja testów manualnych** (`tests/MANUAL_TESTING_PHASE_7.md`)
  - 9 scenariuszy testowych (M7.1-M7.9)
  - Checklist i procedury testowe

### Changed (Faza 7)
- **src/menu_app.py** - użycie nowego modułu UI
  - Metoda `_reset_memory()` używa `choose_date_dialog()`
  - Dodana metoda `_show_about()` z dialogiem O aplikacji
- **src/setup/wizard.py** - użycie folder pickera
  - Metoda `_show_output_config()` używa `choose_folder_dialog()`
  - Dialog z opcjami: Wybierz folder / Użyj domyślnego / Wstecz

### Testing (Faza 7)
- ✅ **Testy automatyczne:** 18/18 przechodzą (100% pass rate)
  - Testy stałych UI (9 testów)
  - Testy dialogów (9 testów)
  - Coverage: 94% dla modułu `src/ui/`
- [ ] **Testy manualne:** 0/9 wykonane (wymagane przed produkcją)
  - M7.1-M7.4: Date picker (różne opcje)
  - M7.5-M7.7: Folder picker (NSOpenPanel)
  - M7.8-M7.9: About dialog

### Technical Details
- Nowy moduł: `src/ui/` przygotowany na przyszły redesign UI
- Stałe UI w `constants.py` - łatwe do wymiany przy Fazie 9
- Funkcje dialogów w `dialogs.py` - reusable i testowalne

---

## [1.14.0] - 2025-12-29

### Added (Faza 4)
- **Pakowanie z py2app** (`setup_app.py`, `scripts/build_app.sh`)
  - Konfiguracja py2app dla macOS bundle (Apple Silicon arm64)
  - Bundle `.app` gotowy do dystrybucji (~45MB)
  - Skrypt automatycznego budowania z weryfikacją
  - Obsługa segfault podczas buildu (znany problem py2app 0.28.9 + Python 3.12.12)
  - Bundle działa poprawnie mimo segfaulta podczas ostatniego kroku weryfikacji
- **Naprawa blokowania UI podczas pobierania zależności**
  - Pobieranie działa w osobnym wątku (nie blokuje UI)
  - Okno dialogowe z aktualnym statusem pobierania
  - Możliwość odświeżania statusu przez użytkownika
  - Notyfikacje o postępie i zakończeniu
- **Dokumentacja testów manualnych** (`tests/MANUAL_TESTING_PHASE_4.md`)
  - Kompletny przewodnik testowania bundle
  - 7 scenariuszy testowych (M4.1-M4.7)
  - Checklist i troubleshooting
  - Instrukcje dla testu na czystym macOS (M4.6)

### Changed (Faza 4)
- **setup_app.py** - Optymalizacja buildu
  - `optimize: 1` (zmniejszone z 2 aby uniknąć segfaulta)
  - `strip: False` (zapobiega segfaultowi podczas sprawdzania importów)
- **scripts/build_app.sh** - Obsługa segfaulta
  - Tymczasowe wyłączenie `set -e` podczas buildu
  - Weryfikacja istnienia bundle mimo segfaulta
  - Ostrzeżenie zamiast błędu gdy bundle istnieje
- **src/setup/wizard.py** - Naprawa logiki pobierania
  - Pobieranie w osobnym wątku z oknem dialogowym
  - Synchronizacja zakończenia pobierania z UI
  - Poprawiona obsługa błędów podczas pobierania
- **BACKLOG.md** - Zaktualizowane zadania Fazy 7
  - Dodano poprawki UX do wykonania
  - Oznaczono naprawione problemy

### Testing (Faza 4)
- ✅ **Testy automatyczne:** 14/14 przechodzą (100% pass rate)
  - Testy konfiguracji setup_app.py
  - Testy skryptu budowania
  - Testy struktury bundle
- ✅ **Testy manualne:** 7/7 wykonane (100% completion)
  - ✅ M4.1: Build test - bundle zbudowany, struktura OK, Info.plist OK
  - ✅ M4.2: Launch test - aplikacja uruchamia się bez błędów
  - ✅ M4.3: Menu functionality - wszystkie opcje działają
  - ✅ M4.4: Wizard w bundle - wszystkie kroki działają
  - ✅ M4.5: Dependency download - pobieranie działa, UI nie blokuje
  - ✅ M4.6: Clean system test - aplikacja działa na czystym macOS bez Python
  - ✅ M4.7: Size verification - 43-45MB (akceptowalne dla v2.0.0)
- ✅ **Znalezione problemy (nie blokujące):**
  - Build segfault podczas sprawdzania importów (obsłużony w skrypcie)
  - Rozmiar bundle większy niż docelowy (43MB vs 20MB - akceptowalne)
  - UX: Reset pamięci wymaga date pickera (do poprawy w Fazie 7)
  - UX: Wizard - brak możliwości anulowania w większości kroków (do poprawy w Fazie 7)

### Technical Details
- Bundle lokalizacja: `dist/Transrec.app`
- Rozmiar: 43-45MB (cel: <20MB, ale akceptowalne dla pierwszej wersji)
- Architektura: arm64 (Apple Silicon only)
- Wersja: 2.0.0
- Bundle działa na czystym macOS bez wymagania instalacji Python
- Wszystkie funkcje działają poprawnie w bundle

---

## [1.13.0] - 2025-12-29

### Added (Faza 3)
- **First-Run Wizard** (`src/setup/wizard.py`)
  - 8-krokowy wizard konfiguracji przy pierwszym uruchomieniu
  - Automatyczne pobieranie zależności z progress bar (integracja z Fazą 2)
  - Instrukcja Full Disk Access z linkiem do System Preferences
  - Konfiguracja źródeł nagrań (auto/specific volumes)
  - Wybór folderu docelowego na transkrypcje
  - Wybór języka transkrypcji (pl, en, auto)
  - Opcjonalna konfiguracja AI podsumowań (klucz API Claude)
  - Nawigacja wstecz między krokami
  - Anulowanie wizarda na dowolnym kroku
- **System ustawień użytkownika** (`src/config/`)
  - Klasa `UserSettings` z persystencją do JSON
  - Domyślne wartości w `defaults.py` (języki, modele, ścieżki)
  - Lokalizacja: `~/Library/Application Support/Transrec/config.json`
  - Obsługa load/save z automatycznym tworzeniem katalogów
- **Moduł uprawnień** (`src/setup/permissions.py`)
  - Sprawdzanie Full Disk Access przez próbę dostępu do chronionych katalogów
  - Automatyczne otwieranie System Preferences -> Privacy -> Full Disk Access
  - Sprawdzanie dostępu do konkretnych volumów

### Changed (Faza 3)
- **menu_app.py** - Integracja z wizardem przy starcie
  - Sprawdzanie `SetupWizard.needs_setup()` przed uruchomieniem daemona
  - Uruchamianie wizarda przy pierwszym starcie (z opóźnieniem dla GUI)
  - Przeniesienie logiki pobierania zależności do wizarda (krok 2)
  - Daemon uruchamia się dopiero po zakończeniu wizarda
  - Obsługa anulowania wizarda z komunikatem dla użytkownika

### Testing (Faza 3)
- ✅ Testy jednostkowe: test_user_settings.py (6 testów, 100% pass)
- ✅ Testy jednostkowe: test_permissions.py (6 testów, 100% pass)
- ✅ Testy jednostkowe: test_wizard.py (8 testów, 100% pass)
- ✅ Testy manualne: MANUAL_TESTING_PHASE_3.md (10/16 kluczowych testów przeszło pomyślnie)
  - Weryfikacja przepływu wizarda, integracji z menu_app, zapisywania konfiguracji
  - Znalezione problemy UX zapisane w BACKLOG.md (nie blokują produkcji)

### Technical Details
- Wizard pojawia się tylko gdy `setup_completed == false` w config.json
- Po zakończeniu wizarda: `setup_completed = true` i wszystkie ustawienia zapisane
- Wizard obsługuje skip kroków (pobieranie jeśli już pobrane, FDA jeśli już nadane)
- Integracja z istniejącym `DependencyDownloader` z Fazy 2
- Wszystkie dialogi używają `rumps.alert()` i `rumps.Window()` dla natywnego macOS UX

---

## [1.12.0] - 2025-12-26

### Added (Faza 2)
- **Moduł pobierania zależności** (`src/setup/downloader.py`)
  - Klasa `DependencyDownloader` z automatycznym pobieraniem whisper.cpp i ffmpeg
  - Weryfikacja checksum SHA256 dla bezpieczeństwa
  - Retry logic z exponential backoff (max 3 próby)
  - Resume download dla przerwanych pobierań (Range header)
  - Progress callback dla UI
  - Obsługa błędów: brak internetu, brak miejsca, timeout, serwer niedostępny
- **Custom exceptions** (`src/setup/errors.py`)
  - `DownloadError`, `ChecksumError`, `NetworkError`, `DiskSpaceError`
- **Konfiguracja checksums** (`src/setup/checksums.py`)
  - Słowniki: `VERSIONS`, `CHECKSUMS`, `URLS`, `SIZES`
- **Testy jednostkowe** (`tests/test_downloader.py`)
  - 20 testów pokrywających wszystkie scenariusze (100% pass)
  - Testy P0: sprawdzanie, checksum, network, disk space
  - Testy P1: pobieranie, retry, progress callback
  - Testy P2: resume download, cleanup temp files
- **Testy integracyjne** (`tests/test_downloader_integration.py`)
  - Podstawowa struktura (do rozbudowy po utworzeniu GitHub Release)

### Changed (Faza 2)
- **src/config.py** - Nowa lokalizacja zależności
  - `WHISPER_CPP_PATH` domyślnie: `~/Library/Application Support/Transrec/bin/whisper-cli`
  - `WHISPER_CPP_MODELS_DIR` domyślnie: `~/Library/Application Support/Transrec/models/`
  - Dodano `FFMPEG_PATH` dla bundlowanego ffmpeg
  - Backward compatibility z `~/whisper.cpp/` dla developerów
- **src/transcriber.py** - Zmiana `_check_whisper()`
  - Zamiast błędu - warning i zwrócenie False (UI pokazuje ekran pobierania)
  - Sprawdzanie nowej lokalizacji przed fallback do starej
- **src/menu_app.py** - Integracja z downloaderem
  - Metoda `_check_dependencies()` sprawdza zależności przy starcie (z opóźnieniem dla GUI)
  - Metoda `_download_dependencies()` pobiera z progress callback
  - Komunikaty błędów dla użytkownika (NetworkError, DiskSpaceError, DownloadError)
  - Usunięto debug.log zapisy (11 miejsc)
  - Zoptymalizowano progress callback (100x mniej wywołań)
- **src/setup/downloader.py** - Weryfikacja checksum i auto-repair
  - `check_all()` weryfikuje checksum dla wszystkich plików
  - `download_whisper()`, `download_ffmpeg()`, `download_model()` auto-repair przy błędnym checksum
  - Zoptymalizowano progress callback (tylko przy zmianie procentu, nie co 8KB)
- **HTTP client** - Zmiana z urllib na httpx
  - Lepsze wsparcie dla przekierowań GitHub
  - Bardziej nowoczesne API
  - Automatyczne follow_redirects

### Testing (Faza 2)
- ✅ Wszystkie testy jednostkowe przechodzą (20/20, 100% pass rate)
- ✅ Wszystkie testy integracyjne przechodzą (5/5, 100% pass rate)
- ✅ GitHub Release deps-v1.0.0 utworzony i przetestowany
- ✅ Pobieranie whisper-cli, ffmpeg i modelu small działa poprawnie
- ✅ Weryfikacja checksums działa
- ✅ Repo zmienione na publiczne dla FREE release
- ✅ **Testy manualne Fazy 2 zakończone** (2025-12-26)
  - ✅ TEST M1: Pierwsze uruchomienie - wszystkie zależności pobrane
  - ✅ TEST M2: Brak internetu - komunikat błędu działa poprawnie
  - ✅ TEST M3: Resume download - wznawianie pobierania działa
  - ✅ TEST M5: Uszkodzony plik - wykrycie i auto-repair działa
  - ⏳ TEST M4: Brak miejsca na dysku (opcjonalny, pominięty)
  - ⏳ TEST M6: Wolne połączenie (opcjonalny, pominięty)

### Technical Details
- Lokalizacja zależności: `~/Library/Application Support/Transrec/`
  - `bin/whisper-cli` (~10MB)
  - `bin/ffmpeg` (~15MB)
  - `models/ggml-small.bin` (~466MB)
- Timeouty: CHUNK_TIMEOUT=30s, TOTAL_TIMEOUT=1800s (30min)
- Max retries: 3 próby z exponential backoff
- Minimalne miejsce na dysku: 500MB

---

---

## [1.11.0] - 2025-12-17

### Added
- **Cursor Rules dla projektu** (`.cursor/rules/`)
  - `git-workflow.mdc` - Git Flow strategy, branch naming, commit format
  - `freemium-architecture.mdc` - FREE/PRO feature separation, feature flags
  - `project-overview.mdc` - kontekst projektu dla AI
  - `documentation-structure.mdc` - organizacja dokumentacji z cross-references
  - Zaktualizowany `python-rules.mdc` z zasadami v2.0.0

- **System cross-references między dokumentami**
  - Każdy dokument zawiera header z wersją i powiązanymi dokumentami
  - Mapa powiązań w `documentation-structure.mdc`
  - Zasady aktualizacji powiązanych dokumentów przy zmianach

- **Archiwum dokumentacji** (`Docs/archive/`, `archive/`)
  - Stara dokumentacja przeniesiona do archiwum
  - README w każdym archiwum z opisem zawartości

### Changed
- **README.md** - zaktualizowany dla v2.0.0
  - Generic recorder support (nie tylko Olympus LS-P1)
  - FREE/PRO feature table
  - Cross-references do dokumentacji
  - Roadmap v2.0.0 FREE i v2.1.0 PRO

- **Docs/ARCHITECTURE.md** - nowa architektura v2.0.0
  - Menu bar app jako główny interfejs
  - Universal volume detection
  - Feature flags dla freemium
  - PRO features architecture (license_manager, backend API)
  - Diagram z nową strukturą komponentów

- **Docs/API.md** - rozszerzona dokumentacja API
  - Nowe moduły: `markdown_generator`, `state_manager`, `menu_app`, `app_core`
  - PRO moduły: `summarizer`, `tagger`, `license_manager`
  - Zaktualizowane typy i przykłady użycia

- **Docs/FULL_DISK_ACCESS_SETUP.md** - generic volume support
  - Usunięte referencje do konkretnego recordera
  - First-Run Wizard mention
  - Zaktualizowane ścieżki

- **Docs/DEVELOPMENT.md** - zaktualizowany przewodnik
  - Poprawione ścieżki projektu
  - Git Flow workflow
  - Cross-references do innych dokumentów

- **Docs/TESTING-GUIDE.md** - dodane cross-references

### Removed
- `Docs/requirements.md` - redundantny (jest `requirements.txt`)
- `Docs/requirements-dev.md` - redundantny (jest `requirements-dev.txt`)

### Archived
- `Docs/INSTALLATION-GUIDE` → `Docs/archive/`
- `Docs/olympus-setup-cursor.md` → `Docs/archive/`
- `Docs/CURSOR-WORKFLOW.md` → `Docs/archive/`
- `MIGRATION_SUMMARY.md` → `archive/`
- `PROJECT-SUMMARY.md` → `archive/`
- `OBSIDIAN-SETUP.md` → `archive/`

### Documentation
- Wszystkie dokumenty zaktualizowane dla v2.0.0
- Spójna struktura cross-references
- Cursor rules z zasadami Git Flow i freemium

---

## [1.10.0] - 2025-12-12

### Added
- **Retranskrypcja plików** - nowa opcja w menu aplikacji pozwalająca na ponowne przetworzenie nagrania, które zostało nieprawidłowo transkrybowane
  - Submenu "Retranskrybuj plik..." z listą ostatnich 10 plików ze staging directory (`~/.olympus_transcriber/recordings/`)
  - Automatyczne usuwanie istniejącej transkrypcji (MD/TXT) przed ponownym przetworzeniem
  - Bezpieczne działanie dzięki ProcessLock - nie koliduje z automatyczną transkrypcją
  - Automatyczne odświeżanie listy plików co 10 sekund
  - Powiadomienia o statusie retranskrypcji (sukces/błąd)

## [1.9.1] - 2025-11-29

### Changed
- **Reduced false recorder detection triggers**: FSEvents monitor now filters out macOS system directories (`.Spotlight-V100`, `.fseventsd`, `.Trashes`) to prevent unnecessary workflow invocations when Spotlight indexes the recorder volume
- **Optimized notification behavior**: System notifications are now sent only when new audio files are found, eliminating spam when recorder is connected but has no new recordings

### Fixed
- Fixed repeated "Recorder detected" notifications triggered by macOS Spotlight indexing activity on the recorder volume
- Reduced log noise from system directory changes that don't represent actual recorder activity

## [1.9.0] - 2025-11-28

### Added
- **macOS Application Bundle (`Transrec.app`)** - Native `.app` wrapper for daemon execution
  - Resolves TCC (Transparency, Consent, and Control) issues with external drive access
  - Enables Full Disk Access configuration for daemon processes
  - Located at `~/Applications/Transrec.app`
- **Full Disk Access setup guide** (`Docs/FULL_DISK_ACCESS_SETUP.md`)
  - Step-by-step instructions for configuring macOS privacy settings
  - Troubleshooting guide for external drive access issues
  - Alternative manual Terminal launch instructions
- **Test script** (`scripts/test_app_wrapper.sh`) - Verifies app configuration and access
- **Project backlog** (`BACKLOG.md`) - Planned features and improvements roadmap:
  - Menu bar app with GUI controls for daemon management
  - Native launcher to replace Automator wrapper
  - Configurable Core ML / CPU mode with automatic fallback
  - Enhanced Core ML stability detection
- macOS native notifications for key events (recorder detected, files found, transcription complete)
- Helper script `scripts/restart_daemon.sh` for easy daemon management
- Improved LaunchAgent configuration (uses `python -m src.main` for better module resolution)
- `start_menu_app.command` + Login Item instructions for automatic tray app startup
- Enhanced error handling in `find_audio_files()`:
  - Specific handling for `OSError` (recorder unmounted during scan)
  - Specific handling for `PermissionError` (Full Disk Access issues)
  - Added `exc_info=True` to all error logs for better debugging
  - Scan completion logging with file count

### Changed
- **Architecture**: Daemon now runs as macOS application bundle instead of direct Python process
  - LaunchAgent updated to use `Transrec.app/Contents/MacOS/Transrec`
  - Login Items configuration now uses `.app` bundle
  - Resolves root cause: macOS TCC blocking `rglob()` access to `/Volumes` for launchd processes
- **Logging**: Reduced verbose debug logging in `find_audio_files()` method
  - Removed per-file debug spam, kept essential scan summary logs
- **Documentation**: Enhanced setup and deployment instructions
  - `QUICKSTART.md`: Added Full Disk Access as mandatory step 6, reorganized daemon setup with `.app` bundle option
  - `INSTALLATION-GUIDE`: Added Full Disk Access as Part 7, `.app` deployment as Part 8, LaunchAgent as Part 9
  - Clear distinction between `.app` bundle (recommended) vs LaunchAgent deployment methods
- Daemon now sends system notifications visible in Notification Center
- Makefile `reload-daemon` command now uses restart script

### Fixed
- **Critical**: Fixed daemon unable to detect files on external recorder (`/Volumes/LS-P1`)
  - Root cause: macOS TCC blocking access to external volumes for processes without Full Disk Access
  - Solution: Application bundle `.app` can be granted Full Disk Access, enabling file detection
- LaunchAgent module import issues by using `python -m` execution
- Improved error messages when recorder becomes unavailable during file scanning
- Better diagnostic information for Full Disk Access permission issues

## [1.8.2] - 2025-11-26

### Changed
- Improved code quality compliance with PEP 8 standards:
  - Added trailing newlines to all source files (`.py`, `.toml`, `.flake8`, `.sh`)
  - Ensures consistency with Black formatter and flake8 linter requirements
- CHANGELOG documentation standardized to English for better accessibility
  - Translated Polish sections (1.6.1, 1.7.0, 1.7.1) to English
  - Maintains consistent language throughout project documentation

### Technical Details
- All Python source files now end with proper newline character
- Configuration files (`.flake8`, `pyproject.toml`) comply with tool requirements
- Shell scripts follow Unix/POSIX standards for text files

## [1.8.1] - 2025-11-25

### Fixed
- Stabilized whisper.cpp fallback from Metal/Core ML to CPU mode by explicitly disabling backends (`WHISPER_COREML=0`, `GGML_METAL_DISABLE=1`), eliminating recurring transcription errors on older devices.
- Stale lock files (`transcriber.lock`) are now detected and automatically cleaned to prevent permanent `process_recorder()` blocking after previous process crashes.

### Testing
- Added unit tests securing CPU fallback configuration and stale lock file handling in `Transcriber`.

## [1.8.0] - 2025-11-25

### Added
- **Automatic LLM-based transcription tagging**:
  - Claude API generates up to 6 Obsidian tags for each new recording
  - Tags based on transcription, summary, and existing tag dictionary
  - Intelligent deduplication and tag normalization (Polish characters → ASCII)
  - Tags added to YAML frontmatter in format `tags: [tag1, tag2, ...]`
- **Tag indexing across entire vault** (`src/tag_index.py`):
  - `TagIndex` scans all `.md` files in `TRANSCRIBE_DIR`
  - Normalizes tags (removes Polish characters, spaces → hyphens)
  - Maintains `normalized → original` mapping to preserve consistency
  - Methods: `build_index()`, `existing_tags()`, `normalize_tag()`, `sanitize_tag_value()`
- **Tagger module** (`src/tagger.py`):
  - Abstract `BaseTagger` class for different LLM providers
  - `ClaudeTagger` implementation with Anthropic API support
  - Prompt construction with existing_tags support (up to 150 tags in prompt)
  - 10s timeout, graceful fallback on API error
  - `get_tagger()` function for easy instance creation
- **Retagging script for existing transcriptions** (`scripts/retag_existing_transcripts.py`):
  - Bulk tag addition to `.md` files without tags or with only `[transcription]`
  - YAML frontmatter parsing, transcript and summary extraction
  - Dry-run mode (preview changes without saving)
  - Detailed logging of changes and errors
  - Uses `TagIndex` and `ClaudeTagger`
- **Tagging configuration** in `src/config.py`:
  - `ENABLE_LLM_TAGGING` (bool, default: True)
  - `MAX_TAGS_PER_NOTE` (int, default: 6)
  - `MAX_EXISTING_TAGS_IN_PROMPT` (int, default: 150)
  - `MAX_TAGGER_SUMMARY_CHARS` (int, default: 3000)
  - `MAX_TAGGER_TRANSCRIPT_CHARS` (int, default: 1500)
- **Extended documentation** in `QUICKSTART.md`:
  - "LLM Tagging" section with configuration instructions
  - Retagging script usage
  - Tagging troubleshooting

### Changed
- **Transcriber workflow** (`src/transcriber.py`):
  - After summary generation, automatic tagging follows (if enabled)
  - `TagIndex` built at transcriber startup
  - Tags passed to `markdown_generator.create_markdown()`
  - Log: "🏷️  Generated N tags: [tag1, tag2, ...]"
- **MarkdownGenerator** (`src/markdown_generator.py`):
  - Method `create_markdown()` accepts optional parameter `tags: Optional[List[str]]`
  - Default `tags=["transcription"]` if not provided
  - Template changed: `tags: [{tags}]` instead of `tags: [transcription]`
  - Tags rendered as `tag1, tag2, tag3` in YAML frontmatter
- **Enhanced Metal/Core ML error detection** (`src/transcriber.py`):
  - New method `_should_retry_without_coreml()` for precise detection
  - Detects messages: `ggml_metal`, `MTLLibrar`, `Core ML`, `tensor API disabled`
  - Automatic retry with `use_coreml=False` flag when Metal error detected
  - Better separation of retry logic vs. fatal error

### Fixed
- **Tag deduplication**: TagIndex prevents duplicates with Polish characters (e.g., `organizacja` vs `organizacja`)
- **Graceful fallback**: If `ENABLE_SUMMARIZATION=False`, automatically disables `ENABLE_LLM_TAGGING`
- **Empty tag handling**: `sanitize_tag_value()` returns empty string instead of error for invalid tags

### Dependencies
- Existing dependency `anthropic>=0.8.0` reused for tagging (no new packages)

### Technical Details
- **Tagger abstraction**: `BaseTagger` enables easy integration of other providers (OpenAI, Ollama)
- **Tag normalization**: Polish characters (`ą`, `ć`, `ę`, ...) → ASCII (`a`, `c`, `e`, ...)
- **Tag sanitization**: Spaces → hyphens, removal of disallowed characters, lowercase
- **Thread-safe tag indexing**: Index built once at startup, used multiple times
- **Graceful degradation**: Missing API key → tagging disabled, log warning, workflow continues
- **Prompt engineering**:
  - Short fragments (3000 chars summary, 1500 chars transcript)
  - Existing tags in comma-separated list
  - JSON output `{"tags": ["tag1", "tag2", ...]}`
- **Retry logic**: API error → return empty list, doesn't interrupt transcription

### Testing
- New tests in `tests/test_tagger.py`:
  - `test_tagger_normalize_tag()` - Polish character normalization
  - `test_tagger_sanitize_tag()` - sanitization to Obsidian format
  - `test_tagger_generate_tags_mock()` - Claude API mocking
  - `test_tagger_api_error_graceful()` - API error handling
- New tests in `tests/test_tag_index.py`:
  - `test_tag_index_build()` - markdown file indexing
  - `test_tag_index_existing_tags()` - tag extraction from vault
- Extended tests in `tests/test_transcriber.py`:
  - `test_transcriber_with_tagging()` - tagging integration in workflow
  - `test_should_retry_without_coreml()` - Metal error detection
- Extended tests in `tests/test_markdown_generator.py`:
  - `test_create_markdown_with_tags()` - custom tags in YAML frontmatter

### Known Limitations
- Tagging requires `ENABLE_SUMMARIZATION=True` and valid Anthropic API key
- Script `retag_existing_transcripts.py` doesn't support files outside `TRANSCRIBE_DIR`
- Maximum 150 existing tags in prompt (context length limitation)
- 10s API timeout may be too short for very long transcriptions

## [1.7.1] - 2025-11-25

### Added
- File-based process lock to ensure only one transcriber instance runs at a time
- Troubleshooting documentation describing Metal error handling and manual lock file removal

### Fixed
- whisper.cpp fallback now detects `ggml_metal`/`MTLLibrar` messages and automatically switches to CPU,
  eliminating series of `Return code -6` errors
- Protected workflow against re-copying/re-processing when second instance starts in parallel

## [1.7.0] - 2025-11-25

### Added
- **Multi-computer support**: Configuration of `OLYMPUS_TRANSCRIBE_DIR` via environment variable
  - Allows application installation on multiple computers with different usernames
  - All instances can point to the same synchronized Obsidian vault directory
  - Prevents transcription duplication between computers
- **Transcription directory validation at startup**:
  - Logging of `TRANSCRIBE_DIR` source (from environment variable or default path)
  - Automatic directory creation if it doesn't exist
  - Warning if directory doesn't appear to be synchronized (iCloud/Obsidian)
  - Detailed error messages with configuration instructions
- Documentation for multi-computer configuration in `DEVELOPMENT.md` and `INSTALLATION-GUIDE`

### Changed
- `TRANSCRIBE_DIR` in `config.py`:
  - First checks environment variable `OLYMPUS_TRANSCRIBE_DIR`
  - If not set, uses default path based on `Path.home()` instead of hardcoded `/Users/radoslawtaraszka/...`
  - Path always resolved to absolute (`.resolve()`)
- Enhanced logging at application startup (`app_core.py`):
  - Displays source of `TRANSCRIBE_DIR` configuration
  - Shows whether directory exists and whether it was created
  - Warns about potential synchronization issues

### Fixed
- Issue with installation on multiple computers with different usernames
- Hardcoded user path in configuration

### Technical Details
- Mechanism checking `source: <audio_file>` in YAML frontmatter prevents duplicates between computers
- All instances must point to the same vault directory for full duplicate protection
- Backward compatibility: if `OLYMPUS_TRANSCRIBE_DIR` is not set, uses standard location

### Documentation
- Added section "Multi-Computer Setup: TRANSCRIBE_DIR Configuration" in `DEVELOPMENT.md`
- Extended "Configuration" section in `INSTALLATION-GUIDE` with multi-computer instructions
- Configuration examples via `.env` and `~/.zshrc`

## [1.6.1] - 2025-11-25

### Added
- Enhanced Claude prompt and fallback summary, now including **Key Points** section with priority emojis, *Quotes* block with thematic headings, and richer markdown formatting.
- New tests in `tests/test_summarizer.py` that verify the presence of new sections, emojis, and quotes in LLM responses.

### Changed
- Markdown filenames now use readable format `YY-MM-DD - Title.md`, preserve spaces and remove only forbidden characters for easier browsing in Finder/Obsidian.
- `_sanitize_filename()` preserves spaces and removes only disallowed characters, improving title readability.

### Fixed
- Made `Anthropic` client available at module level in `src/summarizer`, allowing tests to patch it without `AttributeError`.

## [1.6.0] - 2025-11-25

### Added
- **Local staging workflow** for robust transcription processing
  - Audio files are now copied to local staging directory before transcription
  - Staging directory: `~/.olympus_transcriber/recordings/` (configurable via `LOCAL_RECORDINGS_DIR`)
  - Transcription works on local copies, making process resilient to recorder unmounting
  - Original files on recorder remain untouched (never deleted or moved)
- **Improved batch failure handling**
  - `last_sync` timestamp is only updated when ALL files in batch succeed
  - Failed files remain in queue for retry on next sync
  - Prevents losing unprocessed files when batch has partial failures
- **Staging reuse optimization**
  - Existing staged copies are reused if size and mtime match
  - Reduces unnecessary file copying on repeated processing
- **Comprehensive staging tests**
  - Unit tests for staging functionality (`test_stage_audio_file_*`)
  - Integration tests for staging workflow (`test_process_recorder_staging_integration`)
  - Batch failure handling tests (`test_process_recorder_batch_*`)
- **End-to-end test scripts**
  - `test_staging_e2e.sh` - Full E2E test with recorder
  - `test_staging_e2e_wait.sh` - E2E test that waits for recorder connection

### Changed
- **Transcription workflow** now uses staging:
  1. Files are discovered on recorder
  2. Each file is copied to local staging directory (`_stage_audio_file()`)
  3. Transcription runs on staged copy (not original recorder file)
  4. Original files on recorder remain untouched
- **Batch processing logic**:
  - Tracks successes and failures separately (`processed_success`, `processed_failed`)
  - State file (`last_sync`) only updated if `processed_failed == 0`
  - Failed files will be retried on next recorder connection
- **Configuration**:
  - Added `LOCAL_RECORDINGS_DIR` configuration option (default: `~/.olympus_transcriber/recordings/`)
  - Staging directory is automatically created by `ensure_directories()`

### Fixed
- **Recorder unmounting during transcription**: System now handles unstable recorder mounting
  - Files are staged locally before processing
  - Transcription continues even if recorder unmounts mid-process
  - No more "input file not found" errors from unstable mounts
- **Lost files on batch failure**: Files that fail in a batch are no longer lost
  - `last_sync` not updated if any file fails
  - Failed files remain in queue for next sync attempt

### Technical Details
- Staging uses `shutil.copy2()` to preserve file metadata and mtime
- Staging directory structure mirrors recorder structure (same filenames)
- Error handling for staging failures (FileNotFoundError, OSError)
- Logging includes staging activity (DEBUG level: "📋 Staging file", "✓ Staged")

### Documentation
- Updated `ARCHITECTURE.md` with staging workflow description
- Updated `API.md` with `_stage_audio_file()` method documentation
- Updated `TESTING-GUIDE.md` with staging test instructions
- Updated `DEVELOPMENT.md` with staging workflow section and debugging tips

### Testing
- All staging-related unit tests pass (6/6)
- All transcriber tests pass (21/21)
- E2E tests confirm staging works correctly with real recorder
- Verified files remain on recorder after processing

## [1.5.2] - 2025-11-24

### Fixed
- **Notification spam**: Fixed repeated "Recorder wykryty" notifications on periodic checks
  - Notifications now only sent on first recorder detection
  - Periodic checks no longer trigger false "new connection" notifications
- **Unnecessary delays**: Removed 5-second post-mount rescan delay
  - System no longer waits and retries when no new files are found
  - Faster processing workflow

### Changed
- Added `recorder_was_notified` flag to track notification state
- `recorder_monitoring` flag now remains `True` while recorder is connected
- Improved state management for periodic check vs. mount event distinction

### Removed
- `POST_MOUNT_RESYNC_DELAY` configuration option (no longer needed)
- 5-second wait and retry logic after mount

## [1.5.1] - 2025-11-24

### Added
- macOS native notifications for recorder detection and transcription events
- `scripts/restart_daemon.sh` - convenient daemon restart script

### Changed
- LaunchAgent now uses `python -m src.main` instead of direct script execution
- Improved daemon reliability with proper module path resolution

### Fixed
- Fixed `ModuleNotFoundError: No module named 'src'` in LaunchAgent mode

## [1.5.0] - 2025-11-20

### Added
- macOS menu bar application (tray app) for GUI-based operation
- Thread-safe application state management (`AppState`, `AppStatus`)
- Python API for state management (`state_manager.py`)
  - `reset_state()` - Reset transcription memory to specific date
  - `get_last_sync_time()` - Read last sync timestamp
  - `save_sync_time()` - Save current sync timestamp
- Real-time status display in menu bar (idle, scanning, transcribing, error)
- Menu actions:
  - Open logs in default editor
  - Reset memory from GUI
  - Graceful shutdown
- Status updates every 2 seconds in tray app
- Automatic state updates during transcription workflow

### Changed
- Refactored `OlympusTranscriber` class from `main.py` to `app_core.py`
- `Transcriber` now supports state update callbacks
- State management functions moved to dedicated `state_manager.py` module
- `main.py` now imports and uses `app_core.OlympusTranscriber`

### Dependencies
- Added `rumps>=0.4.0` for macOS menu bar interface

### Technical Details
- Menu app runs `OlympusTranscriber` in background thread
- State updates are thread-safe using locks
- State manager creates automatic backups before reset
- Menu app provides notifications for user actions

## [1.4.1] - 2025-11-20

### Added
- Helper script to reset transcription memory state:
  - `scripts/reset_recorder_memory.sh`
  - Backs up existing `~/.olympus_transcriber_state.json`
  - Allows setting `last_sync` to a custom date (default: 2025-11-18)
- Helper script to run transcriber with fresh memory:
  - `scripts/run_with_fresh_memory.sh`
  - Resets state and starts `python -m src.main` in one command
- Documentation for memory reset workflow in `README.md`

### Changed
- Recommended development workflow to use helper scripts when
  reprocessing historical recordings

## [1.4.0] - 2025-11-20

### Added
- Markdown document generation with YAML frontmatter for transcriptions
- AI-powered summarization using Claude API (Anthropic)
- Automatic title generation from transcript summaries
- Audio metadata extraction (recording date, duration) using mutagen
- Post-processing pipeline: TXT → Summary → Markdown
- Configurable LLM provider system (Claude, with extensibility for Ollama/OpenAI)
- Safe filename generation with Polish character normalization
- Option to delete temporary TXT files after MD creation (`DELETE_TEMP_TXT`)

### Changed
- Transcription output format changed from `.txt` to `.md` (markdown)
- File naming: now uses `YYYY-MM-DD_Title.md` format based on summary
- Post-processing step added after whisper.cpp transcription

### Configuration
- New config options:
  - `ENABLE_SUMMARIZATION`: Enable/disable AI summarization (default: True)
  - `LLM_PROVIDER`: LLM provider name (default: "claude")
  - `LLM_MODEL`: Model name (default: "claude-3-haiku-20240307")
  - `LLM_API_KEY`: API key (loaded from `ANTHROPIC_API_KEY` env var)
  - `SUMMARY_MAX_WORDS`: Maximum words in summary (default: 200)
  - `TITLE_MAX_LENGTH`: Maximum title length (default: 60)
  - `DELETE_TEMP_TXT`: Delete temporary TXT files (default: True)
  - `MD_TEMPLATE`: Markdown template with YAML frontmatter

### Dependencies
- Added `anthropic>=0.8.0` for Claude API integration
- Added `mutagen>=1.47.0` for audio metadata extraction

### Technical Details
- Summarizer uses abstract base class for easy provider switching
- Graceful fallback when API unavailable (uses filename-based title)
- Timeout protection for API calls (30 seconds)
- Error handling ensures transcription continues even if post-processing fails

### Known Limitations
- Requires Anthropic API key for summarization (set `ANTHROPIC_API_KEY` env var)
- Summarization disabled if API key not found (falls back to basic title)
- Ollama provider not yet implemented (placeholder for future)

## [1.3.0] - 2025-11-20

### Added
- whisper.cpp integration with Core ML support for Apple Silicon
- Automated installation script for whisper.cpp (scripts/install_whisper_cpp.sh)
- Core ML model detection and automatic GPU acceleration on M1/M2/M3 Macs
- CPU fallback when Core ML fails
- Configuration parameters for whisper.cpp paths (WHISPER_CPP_PATH, WHISPER_CPP_MODELS_DIR)

### Changed
- Replaced openai-whisper Python library with whisper.cpp native binary
- Changed default model from "medium" to "small" for 3-4x speed improvement
- Changed default device from auto-detect to "cpu" (whisper.cpp handles Core ML internally)
- Simplified transcription logic - removed MPS-specific error handling
- Updated setup.sh to check for whisper.cpp installation

### Removed
- openai-whisper Python dependency
- PyTorch dependency (no longer needed)
- MPS backend auto-detection logic
- MPS error checking method

### Performance
- 3-4x faster transcription with "small" model vs "medium"
- Up to 10x faster with Core ML acceleration on Apple Silicon
- Reduced memory footprint (no PyTorch runtime)

## [1.2.1] - 2025-11-19

### Fixed
- Automatic fallback to CPU when MPS device fails due to PyTorch sparse tensor incompatibility
- Transcription failures on Apple Silicon caused by MPS backend limitations

### Changed
- Enhanced error detection to identify MPS compatibility issues
- Improved logging to indicate when CPU fallback is used

## [1.2.0] - 2025-11-19

### Added
- GPU acceleration support for Apple Silicon (MPS) and NVIDIA (CUDA)
- Automatic GPU detection and configuration
- macOS metadata file filtering (._* and .DS_Store files)
- GPU availability logging during startup

### Changed
- Increased transcription timeout from 30 to 60 minutes for long recordings
- Enhanced file filtering to skip system files before transcription

### Fixed
- Prevented transcription attempts on macOS resource fork files (._* files)
- Eliminated ffmpeg errors from invalid metadata files

## [1.1.0] - 2025-11-19

### Added
- OpenAI Whisper CLI integration for command-line transcription
- Support for Polish and English language transcription
- Large model support for highest accuracy
- Local, free transcription (no API key required)
- Configurable Whisper model size (tiny, base, small, medium, large)
- Configurable language setting (Polish default, English, or auto-detect)

### Fixed
- FSEvents callback signature causing TypeError in file monitoring
- Transcription hanging due to MacWhisper GUI dependency

### Changed
- Replaced MacWhisper GUI with Whisper CLI
- Updated configuration to use Whisper-specific settings (WHISPER_MODEL, WHISPER_LANGUAGE)
- Updated transcriber to use `shutil.which()` for Whisper detection

### Removed
- MacWhisper dependency and MACWHISPER_PATHS configuration

## [1.0.0] - 2025-11-19

### Added
- Initial release of Olympus Transcriber
- Automatic detection of Olympus LS-P1 recorder connection
- FSEvents-based monitoring for instant recorder detection
- Periodic fallback checker (30-second interval)
- MacWhisper integration for audio transcription
- Support for multiple audio formats (MP3, WAV, M4A, WMA)
- State management to track last sync time
- Prevents re-transcription of already processed files
- Comprehensive logging system
  - Application log: `~/Library/Logs/olympus_transcriber.log`
  - LaunchAgent stdout: `/tmp/olympus-transcriber-out.log`
  - LaunchAgent stderr: `/tmp/olympus-transcriber-err.log`
- LaunchAgent for automatic startup
- Graceful shutdown on SIGINT/SIGTERM
- 30-minute timeout protection for transcriptions
- Debouncing to prevent multiple rapid triggers
- Thread-safe transcription tracking
- Comprehensive test suite
  - Unit tests for all modules
  - Mock-based testing for external dependencies
  - Fixtures for common test scenarios
- Development tooling
  - Black code formatter configuration
  - Flake8 linter configuration
  - MyPy type checker configuration
  - isort import sorter configuration
  - VS Code/Cursor debug configuration
  - Cursor AI coding rules
- Complete documentation
  - README with quick start guide
  - ARCHITECTURE.md with system design
  - DEVELOPMENT.md with development guide
  - INSTALLATION-GUIDE with step-by-step setup
  - CURSOR-WORKFLOW.md for Cursor IDE users
- Automated setup script (`setup.sh`)
  - Creates necessary directories
  - Generates LaunchAgent plist
  - Loads daemon automatically
  - Validates environment

### Configuration
- Configurable recorder names (LS-P1, OLYMPUS, RECORDER)
- Configurable transcription directory (default: `~/Documents/Transcriptions`)
- Configurable MacWhisper paths
- Configurable timeouts and intervals
- Configurable audio file extensions

### Technical Details
- Python 3.8+ compatible
- macOS-native FSEvents API integration
- Async-ready architecture (threading-based)
- Zero-polling design for efficiency
- Graceful error handling
- Type hints throughout codebase
- PEP 8 compliant code style

### Security
- No credentials stored
- Local-only processing
- User-level LaunchAgent (not root)
- No network communication required

### Known Limitations
- macOS only (uses FSEvents)
- Requires MacWhisper installation
- Single recorder at a time
- Sequential transcription processing

---

## [Unreleased - Future]

### Planned Features
- Obsidian integration for automatic note creation
- N8N webhook notifications
- Web UI for management and monitoring
- SQLite database for transcription history
- Multiple recorder support
- Parallel transcription processing
- Cloud storage integration
- Custom transcription models
- Audio preprocessing options
- Batch transcription management

### Planned Improvements
- Async/await refactoring
- Progress reporting for long transcriptions
- Email notifications on completion
- Automatic error recovery
- Rate limiting for system resources
- Compression of old transcriptions
- Automatic backup to cloud
- Enhanced logging with rotation
- Performance metrics collection
- Health check endpoint

---

## Version History

- **1.14.0** (2025-12-29) - Faza 4: Pakowanie z py2app, bundle .app gotowy do dystrybucji
- **1.13.0** (2025-12-29) - Faza 3: First-run wizard z konfiguracją
- **1.12.0** (2025-12-26) - Faza 2: System pobierania whisper.cpp/modeli on-demand
- **1.11.0** (2025-12-17) - Documentation v2.0.0, Cursor rules, Git Flow strategy
- **1.10.0** (2025-12-12) - File retranscription feature with menu app integration
- **1.9.1** (2025-11-29) - Reduced false recorder detection triggers, optimized notification behavior
- **1.9.0** (2025-11-28) - macOS application bundle, Full Disk Access setup, enhanced error handling, project backlog
- **1.8.2** (2025-11-26) - Code quality improvements, PEP 8 compliance, CHANGELOG standardization
- **1.8.1** (2025-11-25) - Stabilized whisper.cpp CPU fallback, stale lock file detection
- **1.8.0** (2025-11-25) - LLM-based automatic tagging, tag indexing, retag script
- **1.7.1** (2025-11-25) - Process lock + extended Metal → CPU fallback
- **1.7.0** (2025-11-25) - Multi-computer support with OLYMPUS_TRANSCRIBE_DIR configuration
- **1.6.1** (2025-11-25) - Enhanced markdown formatting and Claude prompts
- **1.6.0** (2025-11-25) - Local staging workflow for robust transcription, improved batch failure handling
- **1.5.2** (2025-11-24) - Fixed notification spam and removed unnecessary delays
- **1.5.1** (2025-11-24) - Native notifications and daemon improvements
- **1.5.0** (2025-11-20) - macOS menu bar app with real-time status and GUI controls
- **1.4.1** (2025-11-20) - Helper scripts for memory reset workflow
- **1.4.0** (2025-11-20) - Markdown output with Claude AI summarization
- **1.3.0** (2025-11-20) - whisper.cpp integration with Core ML support
- **1.2.1** (2025-11-19) - MPS compatibility fix with automatic CPU fallback
- **1.2.0** (2025-11-19) - GPU acceleration, macOS metadata filtering, 60-min timeout
- **1.1.0** (2025-11-19) - Whisper CLI integration, FSEvents bug fix
- **1.0.0** (2025-11-19) - Initial release

## Upgrade Guide

### From Development to 1.0.0

If you were using a development version:

1. Backup your state file:

   ```bash
   cp ~/.olympus_transcriber_state.json ~/.olympus_transcriber_state.json.backup
   ```

2. Unload old LaunchAgent:

   ```bash
   launchctl unload ~/Library/LaunchAgents/com.user.olympus-transcriber.plist
   ```

3. Pull latest code:

   ```bash
   cd ~/CODE/Olympus_transcription
   git pull origin main
   ```

4. Update dependencies:

   ```bash
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Run setup script:

   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

6. Verify installation:

   ```bash
   launchctl list | grep olympus-transcriber
   tail -f ~/Library/Logs/olympus_transcriber.log
   ```

## Support

For issues, questions, or contributions:
- Check documentation in `Docs/` directory
- Review logs for errors
- Open an issue on GitHub
- Read `DEVELOPMENT.md` for development setup

## License

MIT License - See LICENSE file for details

## Credits

Developed by Radoslaw Taraszka

Uses:
- whisper.cpp for transcription
- Claude API (Anthropic) for AI summarization
- FSEvents for file system monitoring
- Python standard library
