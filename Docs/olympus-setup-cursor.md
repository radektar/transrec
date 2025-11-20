# Olympus Transcriber - Cursor Project Setup Guide

## 📋 Spis treści
1. [Konfiguracja projektu w Cursor](#konfiguracja-projektu)
2. [Struktura folderu](#struktura-folderu)
3. [Pierwsze uruchomienie](#pierwsze-uruchomienie)
4. [Development workflow](#development-workflow)
5. [Debugowanie](#debugowanie)
6. [Deployment na LaunchAgent](#deployment)

---

## Konfiguracja projektu

### Krok 1: Stwórz folder projektu

```bash
mkdir ~/Projects/olympus-transcriber
cd ~/Projects/olympus-transcriber
```

### Krok 2: Otwórz w Cursor

```bash
# Jeśli masz cursor zainstalowany
cursor ~/Projects/olympus-transcriber

# Lub otwórz Cursor i użyj: File → Open → olympus-transcriber
```

---

## Struktura folderu

Przygotuj tę strukturę w Cursor (File → New Folder):

```
olympus-transcriber/
├── .cursor/                    # Cursor configuration
│   └── rules/
│       └── python-rules.mdc    # Python-specific rules
├── .vscode/                    # VS Code debug config
│   └── launch.json             # Debugger setup
├── .gitignore                  # Ignoruj venv, logs
├── venv/                       # Virtual environment (tworzysz poniżej)
├── src/
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   ├── transcriber.py          # Główna logika transkrypcji
│   ├── file_monitor.py         # FSEvents monitoring
│   ├── config.py               # Konfiguracja
│   └── logger.py               # Setup loggingu
├── tests/
│   ├── __init__.py
│   └── test_transcriber.py     # Testy
├── docs/
│   ├── API.md                  # Dokumentacja API
│   ├── DEVELOPMENT.md          # Development notes
│   └── ARCHITECTURE.md         # Architektura rozwiązania
├── requirements.txt            # Python dependencies
├── requirements-dev.txt        # Dev dependencies
├── README.md                   # Project readme
└── setup.sh                    # Instalacja z jednego polecenia
```

---

## Pierwsze uruchomienie

### Krok 1: Virtual Environment

W terminalu Cursor (Ctrl + `):

```bash
# Utwórz virtual environment
python3 -m venv venv

# Aktywuj (macOS/Linux)
source venv/bin/activate

# Powinno pokazać: (venv) before command prompt
```

### Krok 2: Instalacja zależności

```bash
# Upewnij się że venv jest aktywny
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Dla development/testing
```

### Krok 3: Weryfikacja

```bash
# Sprawdź Python version
python --version

# Sprawdź zainstalowane pakiety
pip list
```

---

## Development Workflow

### Struktura pliku `src/config.py`

```python
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Config:
    """Konfiguracja aplikacji"""
    RECORDER_NAMES = ["LS-P1", "OLYMPUS", "RECORDER"]
    TRANSCRIBE_DIR = Path.home() / "Documents" / "Transcriptions"
    STATE_FILE = Path.home() / ".olympus_transcriber_state.json"
    LOG_DIR = Path.home() / "Library" / "Logs"
    LOG_FILE = LOG_DIR / "olympus_transcriber.log"
    
    # MacWhisper paths
    MACWHISPER_PATHS = [
        "/Applications/MacWhisper.app/Contents/MacOS/MacWhisper",
        "/usr/local/bin/macwhisper",
        "/opt/homebrew/bin/macwhisper",
    ]
    
    # Timeouts (sekundy)
    TRANSCRIPTION_TIMEOUT = 1800  # 30 minut
    PERIODIC_CHECK_INTERVAL = 30   # Co 30 sekund
    MOUNT_MONITOR_DELAY = 1        # Czekaj 1s na full mount

config = Config()
```

### Struktura pliku `src/logger.py`

```python
import logging
from src.config import config

def setup_logger():
    """Setup centralized logging"""
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger("olympus_transcriber")
    logger.setLevel(logging.DEBUG)
    
    # File handler
    fh = logging.FileHandler(config.LOG_FILE)
    fh.setLevel(logging.INFO)
    
    # Console handler (для development)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger

logger = setup_logger()
```

### Struktura `src/file_monitor.py`

```python
import os
import threading
from pathlib import Path
from datetime import datetime, timedelta
from fsevents import Observer, Stream
from src.logger import logger
from src.config import config

class FileMonitor:
    """Monitor dla zmian w /Volumes (podłączenie recordera)"""
    
    def __init__(self, callback):
        self.callback = callback
        self.observer = None
        self.is_monitoring = False
    
    def start(self):
        """Uruchom monitoring"""
        self.observer = Observer()
        
        def on_change(event):
            for path in event.paths:
                if any(name in path for name in config.RECORDER_NAMES):
                    logger.info(f"📢 Detected recorder activity: {path}")
                    # Czekaj aby system miał czas na full mount
                    import time
                    time.sleep(config.MOUNT_MONITOR_DELAY)
                    self.callback()
        
        stream = Stream(on_change, "/Volumes", recursive=False)
        self.observer.schedule(stream)
        
        logger.info("✓ Mount monitor started")
        self.is_monitoring = True
        self.observer.start()
    
    def stop(self):
        """Zatrzymaj monitoring"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.is_monitoring = False
            logger.info("✓ Mount monitor stopped")
```

### Struktura `src/transcriber.py`

```python
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from src.config import config
from src.logger import logger

class Transcriber:
    """Główna logika transkrypcji"""
    
    def __init__(self):
        self.transcription_in_progress = {}
        self.macwhisper_path = self._find_macwhisper()
        self.recorder_monitoring = False
    
    def _find_macwhisper(self):
        """Znajdź ścieżkę do MacWhisper"""
        for path in config.MACWHISPER_PATHS:
            if Path(path).exists():
                logger.info(f"✓ Found MacWhisper at: {path}")
                return path
        logger.warning("⚠ MacWhisper not found")
        return None
    
    def find_recorder(self):
        """Szukaj podłączonego recordera"""
        volumes_path = Path("/Volumes")
        if not volumes_path.exists():
            return None
        
        for name in config.RECORDER_NAMES:
            recorder = volumes_path / name
            if recorder.exists() and recorder.is_dir():
                logger.info(f"✓ Recorder found: {recorder}")
                return recorder
        return None
    
    def get_last_sync_time(self):
        """Pobierz czas ostatniej synchronizacji"""
        if config.STATE_FILE.exists():
            try:
                with open(config.STATE_FILE, 'r') as f:
                    data = json.load(f)
                    last_sync_str = data.get("last_sync")
                    if last_sync_str:
                        return datetime.fromisoformat(last_sync_str)
            except Exception as e:
                logger.error(f"Error reading state: {e}")
        
        return datetime.now() - timedelta(days=7)
    
    def save_sync_time(self):
        """Zapisz czas tej synchronizacji"""
        try:
            with open(config.STATE_FILE, 'w') as f:
                json.dump({"last_sync": datetime.now().isoformat()}, f)
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    def find_audio_files(self, recorder_path, since):
        """Znajdź nowe pliki audio"""
        audio_extensions = {".mp3", ".wav", ".m4a", ".wma"}
        new_files = []
        
        try:
            for audio_file in recorder_path.rglob("*"):
                if audio_file.suffix.lower() in audio_extensions:
                    try:
                        mtime = datetime.fromtimestamp(audio_file.stat().st_mtime)
                        if mtime > since:
                            new_files.append(audio_file)
                    except OSError as e:
                        logger.warning(f"Could not access: {audio_file} - {e}")
                        continue
        except Exception as e:
            logger.error(f"Error scanning files: {e}")
            return []
        
        return sorted(new_files, key=lambda x: x.stat().st_mtime)
    
    def transcribe_file(self, audio_file):
        """Transkrybuj jeden plik"""
        if not self.macwhisper_path:
            logger.error("MacWhisper not available")
            return False
        
        output_file = config.TRANSCRIBE_DIR / f"{audio_file.stem}.txt"
        file_id = audio_file.stem
        
        if file_id in self.transcription_in_progress:
            logger.info(f"⏳ Already transcribing: {audio_file.name}")
            return False
        
        if output_file.exists():
            logger.info(f"✓ Already transcribed: {audio_file.name}")
            return True
        
        logger.info(f"🎙️  Starting transcription: {audio_file.name}")
        self.transcription_in_progress[file_id] = True
        
        try:
            config.TRANSCRIBE_DIR.mkdir(parents=True, exist_ok=True)
            
            result = subprocess.run(
                [self.macwhisper_path, str(audio_file), "-o", str(output_file)],
                capture_output=True,
                timeout=config.TRANSCRIPTION_TIMEOUT,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"✓ Transcription complete: {audio_file.name}")
                return True
            else:
                logger.error(f"✗ Transcription failed: {audio_file.name}")
                logger.error(f"  Error: {result.stderr}")
                return False
        
        except subprocess.TimeoutExpired:
            logger.error(f"✗ Timeout (30 min): {audio_file.name}")
            return False
        except Exception as e:
            logger.error(f"✗ Error: {audio_file.name}: {e}")
            return False
        finally:
            self.transcription_in_progress.pop(file_id, None)
    
    def process_recorder(self):
        """Główna funkcja przetwarzania"""
        logger.info("=" * 60)
        logger.info("🔍 Checking for recorder...")
        
        recorder = self.find_recorder()
        if not recorder:
            logger.info("❌ Recorder not found")
            self.recorder_monitoring = False
            return
        
        logger.info(f"✓ Recorder detected")
        self.recorder_monitoring = True
        
        last_sync = self.get_last_sync_time()
        logger.info(f"📅 Looking for files after: {last_sync}")
        
        new_files = self.find_audio_files(recorder, last_sync)
        logger.info(f"📁 Found {len(new_files)} files")
        
        if new_files:
            for audio_file in new_files:
                self.transcribe_file(audio_file)
                time.sleep(1)  # Delay między plikami
        else:
            logger.info("ℹ️  No new files")
        
        self.save_sync_time()
        logger.info("✓ Sync complete")
        logger.info("=" * 60)
```

### Struktura `src/main.py`

```python
import sys
import time
import threading
from src.transcriber import Transcriber
from src.file_monitor import FileMonitor
from src.logger import logger

def main():
    """Main entry point"""
    logger.info("🚀 Olympus Transcriber started")
    
    transcriber = Transcriber()
    monitor = FileMonitor(callback=transcriber.process_recorder)
    
    try:
        # Uruchom FSEvents monitor
        monitor.start()
        
        # Uruchom periodic check (fallback)
        def periodic_check():
            while True:
                try:
                    time.sleep(30)
                    if transcriber.find_recorder():
                        if not transcriber.recorder_monitoring:
                            transcriber.process_recorder()
                except Exception as e:
                    logger.error(f"Error in periodic check: {e}")
        
        checker_thread = threading.Thread(target=periodic_check, daemon=True)
        checker_thread.start()
        
        logger.info("✓ All monitors running. Waiting for recorder...")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("⏹ Shutting down...")
        monitor.stop()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## Debugowanie

### Krok 1: Ustaw breakpoint

W edytorze Cursor, otwórz dowolny plik `.py` i kliknij na lewą krawędź linii kodu, aby ustawić breakpoint (pojawi się czerwona kropka).

### Krok 2: Uruchom debugger

Stwórz `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Main",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/src/main.py",
            "console": "integratedTerminal",
            "justMyCode": true,
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Debug Tests",
            "type": "debugpy",
            "request": "launch",
            "program": "-m",
            "args": ["pytest", "tests/", "-v"],
            "console": "integratedTerminal"
        }
    ]
}
```

### Krok 3: Uruchom Debug

Ctrl + Shift + D, wybierz "Debug Main" i kliknij play.

---

## Deployment

### Krok 1: Przygotuj production build

```bash
# Deaktywuj venv (opcjonalnie)
# deactivate

# Utwórz standalone build
pip install pyinstaller
pyinstaller --onefile --name olympus-transcriber src/main.py
```

### Krok 2: Stwórz LaunchAgent

```bash
# Utwórz plik LaunchAgent
mkdir -p ~/Library/LaunchAgents
cat > ~/Library/LaunchAgents/com.user.olympus-transcriber.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.olympus-transcriber</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/USERNAME/.local/bin/olympus_transcriber.py</string>
    </array>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>/tmp/olympus-out.log</string>
    
    <key>StandardErrorPath</key>
    <string>/tmp/olympus-err.log</string>
</dict>
</plist>
EOF
```

Zamień `USERNAME` na swój login.

### Krok 3: Załaduj LaunchAgent

```bash
# Załaduj
launchctl load ~/Library/LaunchAgents/com.user.olympus-transcriber.plist

# Weryfikuj
launchctl list | grep olympus

# Logi
tail -f /tmp/olympus-out.log
```

---

## Cursor Rules

Stwórz `.cursor/rules/python-rules.mdc`:

```markdown
---
title: "Olympus Transcriber - Python Standards"
description: "Python coding standards for this project"
globs: "src/**/*.py"
alwaysApply: true
---

# Coding Standards

- Use type hints for all function parameters and returns
- Follow PEP 8 strictly
- Maximum line length: 88 characters (Black style)
- Use docstrings for all functions (Google style)
- All functions should be testable
- Use logging instead of print()
- Never use global variables (use classes)

# Project-specific

- Imports order: stdlib → third-party → local
- Use `from src.logger import logger` for logging
- Use `from src.config import config` for configuration
- All file I/O must handle exceptions
- All subprocess calls must have timeout

# Testing

- Write tests before implementation (TDD)
- Use pytest
- All public functions must have tests
- Use fixtures for common setup
```

---

## Pomocne polecenia

```bash
# Uruchom główny skrypt
source venv/bin/activate
python src/main.py

# Uruchom testy
pytest tests/ -v

# Sprawdź linting
flake8 src/

# Format kodu
black src/

# Sprawdź type hints
mypy src/
```

---

## Iteracyjny Development

1. **Plan** - Napisz test dla nowej funkcji
2. **Red** - Uruchom test (powinien failnąć)
3. **Green** - Napisz minimalny kod by test przeszedł
4. **Refactor** - Ulepsz kod w Cursor
5. **Commit** - Git commit zmian

Cursor będzie Ci pomagać na każdym kroku! 🚀
