# System Architecture

## Overview

Olympus Transcriber to system automatycznie transkrybujący pliki audio z rekordera Olympus LS-P1.

```
┌─────────────────────────────────────────────────────────────┐
│                     macOS System                             │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  FSEvents Monitor (src/file_monitor.py)              │   │
│  │  - Watches /Volumes for mount events                 │   │
│  │  - Triggers on recorder connection                   │   │
│  └───────────────────┬──────────────────────────────────┘   │
│                      │ (onChange callback)                   │
│  ┌──────────────────┴──────────────────────────────────┐   │
│  │  Transcriber Engine (src/transcriber.py)            │   │
│  │  - Detects recorder path (/Volumes/LS-P1)           │   │
│  │  - Scans for new audio files                        │   │
│  │  - Manages transcription queue                      │   │
│  └───────────────────┬──────────────────────────────────┘   │
│                      │                                       │
│  ┌──────────────────┴──────────────────────────────────┐   │
│  │  MacWhisper Bridge                                  │   │
│  │  - Spawns MacWhisper subprocess                     │   │
│  │  - Monitors progress & timeout                      │   │
│  │  - Handles errors                                   │   │
│  └───────────────────┬──────────────────────────────────┘   │
│                      │                                       │
│                      ▼                                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Output: ~/Documents/Transcriptions/                │   │
│  │  - audio_file_1.txt                                 │   │
│  │  - audio_file_2.txt                                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  State Management (~/.olympus_transcriber_state.json) │   │
│  │  - Tracks last sync time                            │   │
│  │  - Prevents duplicate transcriptions                │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Logging (~/Library/Logs/olympus_transcriber.log)    │   │
│  │  - All events logged with timestamps                │   │
│  │  - Debug during development                         │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. FSEvents Monitor (`src/file_monitor.py`)

**Odpowiedzialność:** Detektowanie połączenia recordera

```python
FileMonitor
├── start()           # Uruchom monitoring
├── stop()            # Zatrzymaj monitoring
└── on_change()       # Callback na zmianę w /Volumes
```

**Mechanizm:**
- MacFSEvents śledzi `/Volumes`
- Na zmianę → callback
- Czeka 1 sekundę na pełny mount
- Uruchamia `Transcriber.process_recorder()`

**Zalety:**
- ✅ Natychmiastowa reaktywność
- ✅ Minimalne zużycie zasobów
- ✅ Zero pollingu

### 2. Transcriber Engine (`src/transcriber.py`)

**Odpowiedzialność:** Zarządzanie procesem transkrypcji

```python
Transcriber
├── find_recorder()             # Znaleź /Volumes/LS-P1
├── find_audio_files()          # Znaleź nowe .mp3/.wav
├── _stage_audio_file()         # Skopiuj plik do lokalnego stagingu
├── get_last_sync_time()        # Pobierz czas ostatniego sync
├── save_sync_time()            # Zapisz czas sync
├── transcribe_file()           # Transkrybuj jeden plik (na staged copy)
└── process_recorder()          # Główny workflow
```

**Staging Workflow:**
- Pliki z recordera są kopiowane do `LOCAL_RECORDINGS_DIR` przed transkrypcją
- To zapewnia stabilność nawet gdy recorder się odmontowuje podczas przetwarzania
- Pliki na rejestratorze pozostają nietknięte (nie są kasowane ani przenoszone)
- Jeśli staging się nie powiedzie (np. recorder odmontowany), plik jest pomijany i `last_sync` nie jest aktualizowany

**Workflow:**
```
process_recorder() 
  ├─ find_recorder()
  ├─ get_last_sync_time()
  ├─ find_audio_files(since=last_sync)
  └─ for each file:
      ├─ _stage_audio_file()  # Copy to local staging directory
      │   └─ shutil.copy2() preserves mtime and metadata
      └─ transcribe_file(staged_file)
          ├─ check if already done (state file)
          ├─ run whisper.cpp subprocess (on local copy)
          ├─ handle timeout/errors
          └─ save to TRANSCRIBE_DIR/
  └─ save_sync_time()  # Only if ALL files succeeded
```

### 3. Main Process (`src/main.py`)

**Odpowiedzialność:** Orchestration i background daemon

```
main()
├─ setup logger
├─ create Transcriber instance
├─ create FileMonitor instance
├─ start FileMonitor (FSEvents thread)
├─ start Periodic Check (fallback thread)
└─ keep main thread alive
```

**Dwa wątki:**
1. **FSEvents Monitor** - natychmiastowe odpowiadanie
2. **Periodic Checker** - fallback co 30 sekund

## State Management

### State File: `~/.olympus_transcriber_state.json`

```json
{
  "last_sync": "2025-11-19T10:35:00.123456"
}
```

**Cel:**
- Śledź czas ostatniego podłączenia
- Znajdź NOWE pliki (mtime > last_sync)
- Unikaj duplikatów

### Transcription Cache

Wyniki transkrypcji w `~/Documents/Transcriptions/`:
- `audio_1.txt` - audio_1.mp3 → transkrypcja
- `audio_2.txt` - audio_2.wav → transkrypcja

**Cel:**
- Szybkie sprawdzenie czy już transkrybowany
- Fallback jeśli state file zginie

## Configuration (`src/config.py`)

Centralizowana konfiguracja:

```python
Config:
  RECORDER_NAMES          # Nazwy możliwych voluminów
  TRANSCRIBE_DIR          # Gdzie zapisywać transkrypcje
  LOCAL_RECORDINGS_DIR    # Lokalny staging dla kopii plików z recordera
  STATE_FILE              # Gdzie śledzić sync state
  WHISPER_CPP_PATH        # Ścieżka do whisper.cpp binary
  TRANSCRIPTION_TIMEOUT   # Maksymalny czas transkrypcji
```

**Wyjaśnienie:**
- Łatwo zmienić bez edycji innych plików
- `config = Config()` w każdym module
- Dla przyszłych integracji: możesz dodać `.env` support

## Logging (`src/logger.py`)

Centralizowany logger:

```python
logger = logging.getLogger("olympus_transcriber")
├─ FileHandler  → ~/Library/Logs/olympus_transcriber.log
├─ StreamHandler → Console (development)
└─ formatter    → timestamp, module, level, message
```

**Logi systemowe (LaunchAgent):**
- `/tmp/olympus-transcriber-out.log` - stdout
- `/tmp/olympus-transcriber-err.log` - stderr

## Error Handling

### Graceful Degradation

1. **MacWhisper nie znaleziony** → Log warning, czekaj na kolejny recorder
2. **Timeout transkrypcji** → Log error, pomiń plik, kontynuuj
3. **State file corrupted** → Reset to 1 week ago
4. **FSEvents fails** → Fallback na periodic checking (co 30s)

### Retry Strategy

Brak built-in retry - każde podłączenie recordera:
- Szuka NOWYCH plików (od last_sync)
- Jeśli transkrypcja failnęła poprzednio, spróbuje znowu
- Jeśli succeedła, zostaje w Documents/

## UI Layer (Menu Bar App)

### Menu App Architecture

Since version 1.5.0, the application includes a macOS menu bar interface:

```
┌─────────────────────────────────────────────────────────────┐
│  macOS Menu Bar                                             │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  OlympusMenuApp (src/menu_app.py)                   │  │
│  │  - rumps-based menu bar interface                    │  │
│  │  - Status display                                    │  │
│  │  - Menu actions (logs, reset, quit)                 │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                       │
│  ┌──────────────────┴──────────────────────────────────┐  │
│  │  OlympusTranscriber (src/app_core.py)                │  │
│  │  - Core daemon logic                                  │  │
│  │  - Thread-safe state management                       │  │
│  │  - FSEvents + Periodic monitoring                     │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                       │
│  ┌──────────────────┴──────────────────────────────────┐  │
│  │  Transcriber (src/transcriber.py)                     │  │
│  │  - Transcription workflow                              │  │
│  │  - State updates via callback                          │  │
│  └──────────────────────────────────────────────────────┘  │
```

**Key Components:**

1. **AppState** (`src/app_core.py`)
   - Thread-safe state container
   - Status: IDLE, SCANNING, TRANSCRIBING, ERROR
   - Current file tracking
   - Error message storage

2. **State Manager** (`src/state_manager.py`)
   - Python API for state file management
   - `reset_state()` - Reset last_sync date
   - `get_last_sync_time()` - Read state
   - `save_sync_time()` - Write state

3. **Menu App** (`src/menu_app.py`)
   - rumps-based macOS menu bar app
   - Runs `OlympusTranscriber` in background thread
   - Updates status every 2 seconds
   - Provides GUI for common operations

**Usage:**
- CLI mode: `python src/main.py` (original daemon)
- Tray app: `python src/menu_app.py` (with GUI)

## Future Extensions

### Planned Improvements

1. **Obsidian Integration**
   ```python
   # Automatycznie tworzyć note w Obsidian vault
   ObsidianBridge
   ├── create_note()
   ├── add_front_matter()
   └── link_files()
   ```

2. **N8N Webhook**
   ```python
   # Powiadamiać N8N o nowych transkrypcjach
   N8NNotifier
   ├── send_webhook()
   └── track_status()
   ```

3. **Web UI**
   ```python
   # Flask app dla management
   FlaskAPI
   ├── GET /status
   ├── POST /transcribe
   └── GET /history
   ```

4. **Database**
   ```python
   # SQLite dla historii
   Database
   ├── store_transcription()
   ├── query_by_date()
   └── export_report()
   ```

## Performance Considerations

### Resources
- **RAM:** ~50-100 MB (main process) + MacWhisper (~2GB)
- **CPU:** Minimal during idle, ~80-100% during transcription
- **Disk:** Depends on MacWhisper model + transcription output

### Optimization
- FSEvents = zero-polling overhead
- Single recorder at a time assumption
- Async could be future improvement

## Security Notes

- No credentials stored in code
- State file is local (~/.olympus_...)
- Logs contain file paths (not sensitive)
- MacWhisper runs locally (no cloud)
