# Development Guide

> **Wersja:** v2.0.0 (w przygotowaniu)
>
> **Powiązane dokumenty:**
> - [README.md](../README.md) - Przegląd projektu
> - [ARCHITECTURE.md](ARCHITECTURE.md) - Architektura systemu
> - [API.md](API.md) - Dokumentacja API modułów
> - [TESTING-GUIDE.md](TESTING-GUIDE.md) - Przewodnik testowania
> - [PUBLIC-DISTRIBUTION-PLAN.md](PUBLIC-DISTRIBUTION-PLAN.md) - Plan dystrybucji

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/transrec.git
cd transrec
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Install whisper.cpp

```bash
bash scripts/install_whisper_cpp.sh
```

### 3. Run Locally

```bash
# Menu bar app (recommended)
python -m src.menu_app

# CLI mode
python -m src.main
```

### 4. Run Tests

```bash
pytest tests/ -v
```

## 📁 Project Structure

```
transrec/
├── src/
│   ├── __init__.py           # Package definition
│   ├── config.py             # Configuration management
│   ├── logger.py             # Logging setup
│   ├── file_monitor.py       # FSEvents monitoring
│   ├── transcriber.py        # Transcription engine
│   ├── markdown_generator.py # MD file generation
│   ├── state_manager.py      # State persistence
│   ├── menu_app.py           # Menu bar application
│   ├── app_core.py           # Core daemon logic
│   ├── summarizer.py         # AI summaries (PRO)
│   └── tagger.py             # Auto-tagging (PRO)
├── tests/
│   ├── test_config.py
│   ├── test_transcriber.py
│   ├── test_file_monitor.py
│   ├── test_state_manager.py
│   └── ...
├── Docs/
│   ├── ARCHITECTURE.md       # System architecture
│   ├── API.md                # API documentation
│   ├── DEVELOPMENT.md        # This file
│   └── ...
├── scripts/
│   ├── install_whisper_cpp.sh
│   └── ...
├── .cursor/rules/            # Cursor IDE rules
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Development dependencies
└── README.md                 # Project overview
```

## 🔧 Development Workflow

### Git Flow

Projekt używa Git Flow. Szczegóły w `.cursor/rules/git-workflow.mdc`.

```bash
# Nowa funkcja
git checkout develop
git pull origin develop
git checkout -b feature/nazwa-funkcji

# Po zakończeniu
git checkout develop
git merge feature/nazwa-funkcji
git push origin develop
```

### Commit Messages

Format: `v2.0.0: Opis zmiany`

```bash
git commit -m "v2.0.0: Add universal volume detection"
git commit -m "v2.0.0: Fix FSEvents callback race condition"
```

### Code Quality

#### Formatting

```bash
# Format code with Black
black src/

# Sort imports
isort src/
```

#### Linting

```bash
# Check code style
flake8 src/

# Type checking
mypy src/
```

#### Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_transcriber.py -v

# Open coverage report
open htmlcov/index.html
```

## 🧪 Testing Strategy

### Unit Tests

Każdy moduł ma odpowiadające testy:

- `test_config.py` - Configuration validation
- `test_transcriber.py` - Core transcription logic
- `test_file_monitor.py` - FSEvents monitoring
- `test_state_manager.py` - State persistence
- `test_markdown_generator.py` - MD generation

### Test Fixtures

Common fixtures w `tests/conftest.py`:

```python
@pytest.fixture
def mock_volume(tmp_path):
    """Create mock volume with audio files."""
    volume = tmp_path / "RECORDER"
    volume.mkdir()
    (volume / "recording.mp3").touch()
    return volume

@pytest.fixture
def transcriber():
    """Transcriber instance with mocked dependencies."""
    return Transcriber()
```

### Mocking

```python
from unittest.mock import Mock, patch

@patch('src.transcriber.subprocess.run')
def test_transcribe(mock_run):
    mock_run.return_value.returncode = 0
    # Test code here
```

Szczegóły: **[TESTING-GUIDE.md](TESTING-GUIDE.md)**

## 📋 Staging Workflow

### Overview

System używa **staging workflow** dla stabilności:

1. **File Discovery**: Skanuj dysk zewnętrzny
2. **Staging**: Kopiuj do `~/.transrec/recordings/`
3. **Transcription**: Przetwarzaj lokalną kopię
4. **State Update**: Aktualizuj stan tylko jeśli wszystko succeeded

### Benefits

- **Stability**: Transkrypcja kontynuuje nawet gdy dysk odmontowany
- **Data Safety**: Oryginalne pliki nietknięte
- **Error Recovery**: Failed files pozostają w kolejce

### Testing Staging

```bash
pytest tests/test_transcriber.py::test_stage_audio_file_success -v
```

## 🔄 Development Cycle

### 1. Create Feature Branch

```bash
git checkout develop
git checkout -b feature/faza-X-nazwa
```

### 2. Write Tests (TDD)

```python
# tests/test_new_feature.py
def test_new_feature():
    result = new_feature()
    assert result == expected
```

### 3. Implement Feature

```python
# src/new_module.py
def new_feature():
    # Implementation
    return result
```

### 4. Run Tests

```bash
pytest tests/test_new_feature.py -v
```

### 5. Format and Lint

```bash
black src/
isort src/
flake8 src/
mypy src/
```

### 6. Commit

```bash
git add -A
git commit -m "v2.0.0: Add new feature"
```

### 7. Merge to develop

```bash
git checkout develop
git merge feature/faza-X-nazwa
git push origin develop
```

## 🐛 Debugging

### VS Code / Cursor

1. Set breakpoints
2. Press F5 or use Debug panel
3. Select configuration
4. Step through code

### Logging

```bash
# Watch application logs
tail -f ~/Library/Logs/transrec.log

# Watch with grep
tail -f ~/Library/Logs/transrec.log | grep -i error
```

### Common Issues

#### FSEvents Not Working

```bash
# Check if FSEvents is installed
pip list | grep MacFSEvents

# Verify /Volumes is accessible
ls -la /Volumes
```

#### whisper.cpp Not Found

```bash
# Reinstall
bash scripts/install_whisper_cpp.sh

# Verify path
ls -la ~/whisper.cpp/main
```

#### Import Errors

```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## 📚 Code Style Guide

### Python Standards

- Follow PEP 8
- Use type hints for all functions
- Maximum line length: 88 characters (Black default)
- Use docstrings (Google style)

### Example Function

```python
from pathlib import Path
from typing import Optional

def find_audio_files(directory: Path, since: datetime) -> list[Path]:
    """Find audio files modified after given datetime.
    
    Args:
        directory: Directory to search in
        since: Only return files modified after this time
        
    Returns:
        List of audio file paths sorted by modification time
        
    Raises:
        ValueError: If directory doesn't exist
    """
    if not directory.exists():
        raise ValueError(f"Directory not found: {directory}")
    
    return sorted(
        [f for f in directory.rglob("*") if f.suffix in AUDIO_EXTENSIONS],
        key=lambda f: f.stat().st_mtime
    )
```

### Logging

Always use logger, never print():

```python
from src.logger import logger

# Good
logger.info("Processing file")
logger.error(f"Failed: {error}")

# Bad
print("Processing file")
```

### Error Handling

```python
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    return None
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise
```

## 🔐 Security

- No credentials in code
- API keys via environment variables only
- State file is local only
- whisper.cpp runs locally
- PRO features use secure backend API

## 🚀 Performance Tips

### FSEvents vs Polling

FSEvents is much more efficient:
- Zero CPU when idle
- Instant notification on changes
- No battery impact

### Transcription

- Set appropriate timeout (default 1 hour)
- Process files sequentially
- Use state file to avoid re-processing

## 📊 Monitoring

### Health Checks

```bash
# Is app running?
pgrep -f "menu_app"

# Recent activity?
tail -20 ~/Library/Logs/transrec.log

# State file status?
cat ~/.transrec_state.json | python -m json.tool
```

## 🤝 Contributing

### Pull Request Process

1. Fork the repository
2. Create feature branch from `develop`
3. Write tests for new features
4. Ensure all tests pass
5. Update documentation
6. Submit PR to `develop`

### Commit Message Format

```
v2.0.0: <subject>
```

Examples:
```
v2.0.0: Add universal volume detection
v2.0.0: Fix race condition in FSEvents callback
v2.0.0: Update API documentation
```

## 📞 Getting Help

- Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Check [API.md](API.md) for module documentation
- Check [README.md](../README.md) for usage guide
- Check logs for errors
- Open an issue on GitHub

---

> **Powiązane dokumenty:**
> - [README.md](../README.md) - Przegląd projektu
> - [ARCHITECTURE.md](ARCHITECTURE.md) - Architektura systemu
> - [API.md](API.md) - Dokumentacja API modułów
> - [TESTING-GUIDE.md](TESTING-GUIDE.md) - Przewodnik testowania
> - [PUBLIC-DISTRIBUTION-PLAN.md](PUBLIC-DISTRIBUTION-PLAN.md) - Plan dystrybucji v2.0.0
