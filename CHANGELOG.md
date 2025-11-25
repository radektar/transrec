# Changelog

All notable changes to Olympus Transcriber will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

## [1.2.1] - 2025-11-19

### Fixed
- Automatic fallback to CPU when MPS device fails due to PyTorch sparse tensor incompatibility
- Transcription failures on Apple Silicon caused by MPS backend limitations

### Changed
- Enhanced error detection to identify MPS compatibility issues
- Improved logging to indicate when CPU fallback is used

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

## [Unreleased]

### Added
- macOS native notifications for key events (recorder detected, files found, transcription complete)
- Helper script `scripts/restart_daemon.sh` for easy daemon management
- Improved LaunchAgent configuration (uses `python -m src.main` for better module resolution)
- `start_menu_app.command` + Login Item instructions for automatic tray app startup

### Changed
- Daemon now sends system notifications visible in Notification Center
- Makefile `reload-daemon` command now uses restart script

### Fixed
- LaunchAgent module import issues by using `python -m` execution

## [1.5.1] - 2025-11-24

### Added
- macOS native notifications for recorder detection and transcription events
- `scripts/restart_daemon.sh` - convenient daemon restart script

### Changed
- LaunchAgent now uses `python -m src.main` instead of direct script execution
- Improved daemon reliability with proper module path resolution

### Fixed
- Fixed `ModuleNotFoundError: No module named 'src'` in LaunchAgent mode

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

## [1.6.1] - 2025-11-25

### Added
- Rozszerzony prompt Claude oraz fallback summary, teraz zawierający sekcję **Kluczowe punkty** z emoji priorytetów, blok *Cytaty* z tematycznymi nagłówkami i bogatsze formatowanie markdown.
- Nowe testy `tests/test_summarizer.py`, które weryfikują obecność nowych sekcji, emoji oraz cytatów w odpowiedziach LLM.

### Changed
- Nazwy plików markdown korzystają z czytelnego formatu `YY-MM-DD - Tytuł.md`, zachowują spacje i usuwają zbędne znaki, by łatwiej było je przeglądać w Finderze/Obsidianie.
- `_sanitize_filename()` zachowuje spacje i usuwa tylko niedozwolone znaki, co poprawia czytelność tytułów.

### Fixed
- Udostępniono klienta `Anthropic` na poziomie modułu `src/summarizer`, dzięki czemu testy mogą go patchować bez błędów `AttributeError`.

## [1.7.0] - 2025-11-25

### Added
- **Multi-computer support**: Konfiguracja `OLYMPUS_TRANSCRIBE_DIR` przez zmienną środowiskową
  - Pozwala na instalację aplikacji na wielu komputerach z różnymi nazwami użytkowników
  - Wszystkie instancje mogą wskazywać na ten sam synchronizowany katalog vaulta Obsidian
  - Zapobiega duplikacji transkrypcji między komputerami
- **Walidacja katalogu transkrypcji przy starcie**:
  - Logowanie źródła `TRANSCRIBE_DIR` (ze zmiennej środowiskowej lub domyślnej ścieżki)
  - Automatyczne tworzenie katalogu jeśli nie istnieje
  - Ostrzeżenie jeśli katalog nie wygląda na synchronizowany (iCloud/Obsidian)
  - Szczegółowe komunikaty błędów z instrukcjami konfiguracji
- Dokumentacja konfiguracji multi-computer w `DEVELOPMENT.md` i `INSTALLATION-GUIDE`

### Changed
- `TRANSCRIBE_DIR` w `config.py`:
  - Najpierw sprawdza zmienną środowiskową `OLYMPUS_TRANSCRIBE_DIR`
  - Jeśli nie ustawiona, używa domyślnej ścieżki opartej na `Path.home()` zamiast twardego `/Users/radoslawtaraszka/...`
  - Ścieżka zawsze rozwiązywana do absolutnej (`.resolve()`)
- Ulepszone logowanie przy starcie aplikacji (`app_core.py`):
  - Wyświetla źródło konfiguracji `TRANSCRIBE_DIR`
  - Pokazuje czy katalog istnieje i czy został utworzony
  - Ostrzega o potencjalnych problemach z synchronizacją

### Fixed
- Problem z instalacją na wielu komputerach z różnymi nazwami użytkowników
- Twardo zakodowana ścieżka użytkownika w konfiguracji

### Technical Details
- Mechanizm sprawdzania `source: <audio_file>` w YAML frontmatter zapobiega duplikatom między komputerami
- Wszystkie instancje muszą wskazywać na ten sam katalog vaulta dla pełnej ochrony przed duplikatami
- Kompatybilność wsteczna: jeśli `OLYMPUS_TRANSCRIBE_DIR` nie jest ustawiona, używa standardowej lokalizacji

### Documentation
- Dodano sekcję "Multi-Computer Setup: TRANSCRIBE_DIR Configuration" w `DEVELOPMENT.md`
- Rozszerzono sekcję "Configuration" w `INSTALLATION-GUIDE` o instrukcje dla wielu komputerów
- Przykłady konfiguracji przez `.env` i `~/.zshrc`

## [1.7.1] - 2025-11-25

### Added
- File-based process lock to ensure tylko jedna instancja transkrybera działa jednocześnie
- Dokumentacja troubleshootingu opisująca obsługę błędów Metal oraz ręczne usuwanie lock file

### Fixed
- whisper.cpp fallback wykrywa teraz komunikaty `ggml_metal`/`MTLLibrar` i automatycznie przełącza się na CPU,
  co eliminuje serię błędów `Return code -6`
- Zabezpieczono workflow przed ponownym kopiowaniem/przetwarzaniem, gdy druga instancja startuje równolegle

## [1.8.0] - 2025-11-25

### Added
- **Automatyczne tagowanie transkrypcji przez LLM**:
  - Claude API generuje do 6 tagów Obsidian dla każdego nowego nagrania
  - Tagi oparte na transkrypcji, podsumowaniu i istniejącym słowniku tagów
  - Inteligentna deduplikacja i normalizacja tagów (polskie znaki → ASCII)
  - Tagi dodawane do YAML frontmatter w formacie `tags: [tag1, tag2, ...]`
- **Indeksowanie tagów z całego vaulta** (`src/tag_index.py`):
  - `TagIndex` skanuje wszystkie pliki `.md` w `TRANSCRIBE_DIR`
  - Normalizuje tagi (usuwa polskie znaki, spacje → myślniki)
  - Utrzymuje mapowanie `normalized → original` dla zachowania spójności
  - Metody: `build_index()`, `existing_tags()`, `normalize_tag()`, `sanitize_tag_value()`
- **Moduł taggera** (`src/tagger.py`):
  - Abstrakcyjna klasa `BaseTagger` dla różnych dostawców LLM
  - Implementacja `ClaudeTagger` z obsługą API Anthropic
  - Prompt construction z obsługą existing_tags (do 150 tagów w promptcie)
  - Timeout 10s, graceful fallback przy błędzie API
  - Funkcja `get_tagger()` dla łatwego tworzenia instancji
- **Skrypt retagowania istniejących transkrypcji** (`scripts/retag_existing_transcripts.py`):
  - Masowe dodanie tagów do plików `.md` bez tagów lub z samym `[transcription]`
  - Parsowanie YAML frontmatter, ekstrakcja transkryptu i podsumowania
  - Dry-run mode (preview zmian bez zapisu)
  - Szczegółowe logowanie zmian i błędów
  - Wykorzystuje `TagIndex` i `ClaudeTagger`
- **Konfiguracja tagowania** w `src/config.py`:
  - `ENABLE_LLM_TAGGING` (bool, default: True)
  - `MAX_TAGS_PER_NOTE` (int, default: 6)
  - `MAX_EXISTING_TAGS_IN_PROMPT` (int, default: 150)
  - `MAX_TAGGER_SUMMARY_CHARS` (int, default: 3000)
  - `MAX_TAGGER_TRANSCRIPT_CHARS` (int, default: 1500)
- **Rozszerzona dokumentacja** w `QUICKSTART.md`:
  - Sekcja "LLM Tagging" z instrukcją konfiguracji
  - Użycie skryptu retagowania
  - Troubleshooting tagowania

### Changed
- **Transcriber workflow** (`src/transcriber.py`):
  - Po wygenerowaniu podsumowania następuje automatyczne tagowanie (jeśli włączone)
  - `TagIndex` budowany przy starcie transkrybera
  - Tagi przekazywane do `markdown_generator.create_markdown()`
  - Log: "🏷️  Generated N tags: [tag1, tag2, ...]"
- **MarkdownGenerator** (`src/markdown_generator.py`):
  - Metoda `create_markdown()` przyjmuje opcjonalny parametr `tags: Optional[List[str]]`
  - Default `tags=["transcription"]` jeśli nie podano
  - Template zmieniony: `tags: [{tags}]` zamiast `tags: [transcription]`
  - Tagi renderowane jako `tag1, tag2, tag3` w YAML frontmatter
- **Ulepszona detekcja błędów Metal/Core ML** (`src/transcriber.py`):
  - Nowa metoda `_should_retry_without_coreml()` dla precyzyjnej detekcji
  - Wykrywanie komunikatów: `ggml_metal`, `MTLLibrar`, `Core ML`, `tensor API disabled`
  - Automatyczny retry z flagą `use_coreml=False` przy wykryciu Metal error
  - Lepsza separacja logiki retry vs. błąd fatalny

### Fixed
- **Deduplikacja tagów**: TagIndex zapobiega duplikatom z polskimi znakami (np. `organizacja` vs `organizacja`)
- **Graceful fallback**: Jeśli `ENABLE_SUMMARIZATION=False`, automatycznie wyłącza `ENABLE_LLM_TAGGING`
- **Empty tag handling**: `sanitize_tag_value()` zwraca pusty string zamiast błędu dla niepoprawnych tagów

### Dependencies
- Istniejąca zależność `anthropic>=0.8.0` wykorzystana dla tagowania (bez nowych pakietów)

### Technical Details
- **Abstrakcja taggera**: `BaseTagger` umożliwia łatwą integrację innych dostawców (OpenAI, Ollama)
- **Normalizacja tagów**: Polskie znaki (`ą`, `ć`, `ę`, ...) → ASCII (`a`, `c`, `e`, ...)
- **Sanityzacja tagów**: Spacje → myślniki, usunięcie niedozwolonych znaków, lowercase
- **Thread-safe tag indexing**: Index budowany raz przy starcie, używany wielokrotnie
- **Graceful degradation**: Brak API key → tagowanie wyłączone, log warning, workflow kontynuowany
- **Prompt engineering**: 
  - Krótkie fragmenty (3000 chars summary, 1500 chars transcript)
  - Existing tags w liście po przecinku
  - JSON output `{"tags": ["tag1", "tag2", ...]}`
- **Retry logic**: Błąd API → return empty list, nie przerywa transkrypcji

### Testing
- Nowe testy `tests/test_tagger.py`:
  - `test_tagger_normalize_tag()` - normalizacja polskich znaków
  - `test_tagger_sanitize_tag()` - sanityzacja do formatu Obsidian
  - `test_tagger_generate_tags_mock()` - mockowanie Claude API
  - `test_tagger_api_error_graceful()` - obsługa błędów API
- Nowe testy `tests/test_tag_index.py`:
  - `test_tag_index_build()` - indeksowanie plików markdown
  - `test_tag_index_existing_tags()` - ekstrakcja tagów z vaulta
- Rozszerzone testy `tests/test_transcriber.py`:
  - `test_transcriber_with_tagging()` - integracja tagowania w workflow
  - `test_should_retry_without_coreml()` - detekcja błędów Metal
- Rozszerzone testy `tests/test_markdown_generator.py`:
  - `test_create_markdown_with_tags()` - custom tagi w YAML frontmatter

### Known Limitations
- Tagowanie wymaga `ENABLE_SUMMARIZATION=True` i ważnego API key Anthropic
- Skrypt `retag_existing_transcripts.py` nie obsługuje plików spoza `TRANSCRIBE_DIR`
- Maksymalnie 150 existing tags w promptcie (ograniczenie context length)
- Timeout API 10s może być za krótki dla bardzo długich transkrypcji

## [1.8.1] - 2025-11-25

### Fixed
- Ustabilizowano fallback whisper.cpp z Metal/Core ML na tryb CPU przez jawne wyłączenie backendów (`WHISPER_COREML=0`, `GGML_METAL_DISABLE=1`), co eliminuje powtarzające się błędy transkrypcji na starszych urządzeniach.
- Wykrywane i automatycznie czyszczone są przeterminowane pliki lock (`transcriber.lock`), aby zapobiec trwałemu blokowaniu `process_recorder()` po awarii poprzedniego procesu.

### Testing
- Dodano testy jednostkowe zabezpieczające konfigurację fallbacku CPU i obsługę starych plików lock w `Transcriber`.

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

- **1.8.0** (2025-11-25) - LLM-based automatic tagging, tag indexing, retag script
- **1.7.1** (2025-11-25) - Process lock + rozszerzony fallback Metal → CPU
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

