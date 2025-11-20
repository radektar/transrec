# API Documentation

Complete API reference for Olympus Transcriber modules.

## Table of Contents

- [config.py](#configpy)
- [logger.py](#loggerpy)
- [file_monitor.py](#file_monitorpy)
- [transcriber.py](#transcriberpy)
- [main.py](#mainpy)

---

## config.py

Configuration management module.

### Class: `Config`

Central configuration dataclass with all application settings.

#### Attributes

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `RECORDER_NAMES` | `List[str]` | `["LS-P1", "OLYMPUS", "RECORDER"]` | Volume names to detect as recorder |
| `TRANSCRIBE_DIR` | `Path` | `~/Documents/Transcriptions` | Output directory for transcriptions |
| `LOG_DIR` | `Path` | `~/Library/Logs` | Directory for log files |
| `STATE_FILE` | `Path` | `~/.olympus_transcriber_state.json` | State file path |
| `LOG_FILE` | `Path` | `~/Library/Logs/olympus_transcriber.log` | Main log file path |
| `MACWHISPER_PATHS` | `List[str]` | `["/Applications/MacWhisper.app/...", ...]` | Possible MacWhisper locations |
| `TRANSCRIPTION_TIMEOUT` | `int` | `1800` | Max transcription time (seconds) |
| `PERIODIC_CHECK_INTERVAL` | `int` | `30` | Fallback check interval (seconds) |
| `MOUNT_MONITOR_DELAY` | `int` | `1` | Wait after mount detection (seconds) |
| `AUDIO_EXTENSIONS` | `set` | `{".mp3", ".wav", ".m4a", ".wma"}` | Supported audio formats |

#### Methods

##### `ensure_directories() -> None`

Creates necessary directories if they don't exist.

**Example:**
```python
from src.config import config

config.ensure_directories()
```

### Global Instance

```python
from src.config import config

# Access configuration
print(config.TRANSCRIBE_DIR)
print(config.TRANSCRIPTION_TIMEOUT)
```

---

## logger.py

Centralized logging configuration.

### Function: `setup_logger`

```python
def setup_logger(
    name: str = "olympus_transcriber",
    level: int = logging.INFO,
    log_to_file: bool = True,
    log_to_console: bool = True,
) -> logging.Logger
```

Setup and return configured logger instance.

#### Parameters

- `name` (str): Logger name (default: "olympus_transcriber")
- `level` (int): Logging level (default: INFO)
- `log_to_file` (bool): Enable file handler (default: True)
- `log_to_console` (bool): Enable console handler (default: True)

#### Returns

- `logging.Logger`: Configured logger instance

#### Example

```python
from src.logger import logger

logger.info("Application started")
logger.debug("Debug information")
logger.warning("Warning message")
logger.error("Error occurred")
```

### Global Instance

```python
from src.logger import logger

# Use throughout application
logger.info("Message here")
```

---

## file_monitor.py

File system monitoring using FSEvents.

### Class: `FileMonitor`

Monitors `/Volumes` for recorder mount events.

#### Constructor

```python
def __init__(self, callback: Callable[[], None])
```

**Parameters:**
- `callback`: Function to call when recorder is detected

#### Attributes

| Name | Type | Description |
|------|------|-------------|
| `callback` | `Callable` | Function to trigger on detection |
| `observer` | `Optional[Observer]` | FSEvents observer instance |
| `is_monitoring` | `bool` | Flag if monitoring is active |

#### Methods

##### `start() -> None`

Start monitoring `/Volumes` for mount events.

**Example:**
```python
from src.file_monitor import FileMonitor

def on_recorder_detected():
    print("Recorder found!")

monitor = FileMonitor(callback=on_recorder_detected)
monitor.start()
```

**Behavior:**
- Creates FSEvents Observer
- Watches `/Volumes` directory
- Triggers callback when recorder name detected
- Includes 1-second delay for full mount
- Debounces rapid triggers (2 seconds)

##### `stop() -> None`

Stop monitoring and clean up resources.

**Example:**
```python
monitor.stop()
```

**Behavior:**
- Stops FSEvents observer
- Waits up to 5 seconds for clean shutdown
- Sets `is_monitoring` to False
- Logs stop event

---

## transcriber.py

Core transcription engine.

### Class: `Transcriber`

Handles recorder detection, file scanning, and transcription.

#### Constructor

```python
def __init__(self)
```

Initializes transcriber with MacWhisper detection.

#### Attributes

| Name | Type | Description |
|------|------|-------------|
| `transcription_in_progress` | `Dict[str, bool]` | Tracks files being transcribed |
| `macwhisper_path` | `Optional[str]` | Path to MacWhisper executable |
| `recorder_monitoring` | `bool` | Flag if recorder is connected |

#### Methods

##### `find_recorder() -> Optional[Path]`

Search for connected Olympus recorder.

**Returns:**
- `Path`: Recorder volume path if found
- `None`: If no recorder detected

**Example:**
```python
from src.transcriber import Transcriber

transcriber = Transcriber()
recorder = transcriber.find_recorder()

if recorder:
    print(f"Found at: {recorder}")
```

##### `get_last_sync_time() -> datetime`

Get timestamp of last synchronization.

**Returns:**
- `datetime`: Last sync time, or 7 days ago if no state

**Example:**
```python
last_sync = transcriber.get_last_sync_time()
print(f"Last sync: {last_sync}")
```

##### `save_sync_time() -> None`

Save current time as last sync timestamp.

**Example:**
```python
transcriber.save_sync_time()
```

##### `find_audio_files(recorder_path: Path, since: datetime) -> List[Path]`

Find new audio files modified after given datetime.

**Parameters:**
- `recorder_path`: Root path of recorder volume
- `since`: Only return files modified after this time

**Returns:**
- `List[Path]`: Audio files sorted by modification time

**Example:**
```python
from datetime import datetime, timedelta
from pathlib import Path

recorder = Path("/Volumes/LS-P1")
since = datetime.now() - timedelta(days=1)
files = transcriber.find_audio_files(recorder, since)

print(f"Found {len(files)} new files")
```

##### `transcribe_file(audio_file: Path) -> bool`

Transcribe a single audio file using MacWhisper.

**Parameters:**
- `audio_file`: Path to audio file

**Returns:**
- `True`: Transcription succeeded
- `False`: Transcription failed or skipped

**Example:**
```python
from pathlib import Path

audio = Path("/Volumes/LS-P1/recording.mp3")
success = transcriber.transcribe_file(audio)

if success:
    print("Transcription complete")
```

**Behavior:**
- Checks if MacWhisper is available
- Checks if already transcribed
- Tracks in-progress transcriptions
- Runs MacWhisper subprocess with timeout
- Saves output to `TRANSCRIBE_DIR`
- Logs all events

##### `process_recorder() -> None`

Main workflow: detect, scan, transcribe.

**Example:**
```python
transcriber.process_recorder()
```

**Workflow:**
1. Find recorder
2. Get last sync time
3. Find new audio files
4. Transcribe each file
5. Save sync time

**Behavior:**
- Logs detailed progress
- Handles errors gracefully
- Updates `recorder_monitoring` flag
- Reports success/failure counts

---

## main.py

Application orchestrator and entry point.

### Class: `OlympusTranscriber`

Main application coordinator.

#### Constructor

```python
def __init__(self)
```

Initializes application and signal handlers.

#### Attributes

| Name | Type | Description |
|------|------|-------------|
| `transcriber` | `Optional[Transcriber]` | Transcription engine |
| `monitor` | `Optional[FileMonitor]` | File system monitor |
| `periodic_thread` | `Optional[Thread]` | Background checker thread |
| `running` | `bool` | Application running flag |

#### Methods

##### `start() -> None`

Start the transcriber daemon.

**Example:**
```python
from src.main import OlympusTranscriber

app = OlympusTranscriber()
app.start()  # Blocks until stopped
```

**Behavior:**
1. Logs startup information
2. Initializes Transcriber
3. Initializes FileMonitor
4. Starts FSEvents monitoring
5. Starts periodic checker thread
6. Enters keep-alive loop

##### `stop() -> None`

Stop the daemon and cleanup.

**Example:**
```python
app.stop()
```

**Behavior:**
1. Sets running flag to False
2. Stops file monitor
3. Waits for threads to finish
4. Logs shutdown complete

### Function: `main()`

Main entry point for application.

**Example:**
```python
if __name__ == "__main__":
    from src.main import main
    main()
```

**Behavior:**
- Creates OlympusTranscriber instance
- Calls start()
- Handles exceptions
- Sets exit code

---

## Usage Examples

### Basic Usage

```python
from src.main import OlympusTranscriber

# Create and start application
app = OlympusTranscriber()
try:
    app.start()
except KeyboardInterrupt:
    app.stop()
```

### Custom Configuration

```python
from src.config import config
from pathlib import Path

# Override default paths
config.TRANSCRIBE_DIR = Path.home() / "My Transcriptions"
config.TRANSCRIPTION_TIMEOUT = 3600  # 1 hour

# Create directories
config.ensure_directories()
```

### Manual Transcription

```python
from src.transcriber import Transcriber
from pathlib import Path

transcriber = Transcriber()

# Transcribe single file
audio_file = Path("/path/to/audio.mp3")
success = transcriber.transcribe_file(audio_file)

if success:
    print("Done!")
```

### Custom Monitoring

```python
from src.file_monitor import FileMonitor
from src.transcriber import Transcriber

transcriber = Transcriber()

def custom_callback():
    print("Recorder detected!")
    transcriber.process_recorder()

monitor = FileMonitor(callback=custom_callback)
monitor.start()

# Keep alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    monitor.stop()
```

### State Management

```python
from src.transcriber import Transcriber
from datetime import datetime, timedelta

transcriber = Transcriber()

# Check last sync
last_sync = transcriber.get_last_sync_time()
print(f"Last sync: {last_sync}")

# Save current sync time
transcriber.save_sync_time()
```

### Logging

```python
from src.logger import logger

# Different log levels
logger.debug("Detailed debug info")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical failure")

# With exception info
try:
    risky_operation()
except Exception as e:
    logger.error("Operation failed", exc_info=True)
```

---

## Type Hints Reference

```python
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Callable, Dict

# Common types used throughout
PathLike = Path
Callback = Callable[[], None]
AudioFiles = List[Path]
StateDict = Dict[str, bool]
TimeStamp = datetime
```

---

## Constants

```python
# From config.py
DEFAULT_TIMEOUT = 1800  # 30 minutes
DEFAULT_CHECK_INTERVAL = 30  # 30 seconds
DEFAULT_MOUNT_DELAY = 1  # 1 second
DEBOUNCE_INTERVAL = 2  # 2 seconds

# Audio formats
SUPPORTED_FORMATS = {".mp3", ".wav", ".m4a", ".wma"}

# Recorder names
RECORDER_IDENTIFIERS = ["LS-P1", "OLYMPUS", "RECORDER"]
```

---

## Error Handling

All modules use comprehensive error handling:

```python
try:
    # Operation
    result = operation()
except SpecificError as e:
    logger.error(f"Specific error: {e}")
    # Handle specifically
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    # Handle generally
```

## Threading Safety

- `Transcriber.transcription_in_progress` is thread-safe (dict operations)
- `OlympusTranscriber.running` is used as flag for thread coordination
- All threads are daemon threads (won't block shutdown)
- 5-second timeout on thread joins during shutdown

---

For implementation details, see source code in `src/` directory.
For usage examples, see `README.md` and `DEVELOPMENT.md`.


