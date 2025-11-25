# Development Guide

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd ~/CODE/Olympus_transcription
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Run Locally

```bash
python src/main.py
```

### 3. Run Tests

```bash
pytest tests/ -v
```

## 📁 Project Structure

```
Olympus_transcription/
├── src/
│   ├── __init__.py         # Package definition
│   ├── config.py           # Configuration management
│   ├── logger.py           # Logging setup
│   ├── file_monitor.py     # FSEvents monitoring
│   ├── transcriber.py      # Transcription engine
│   └── main.py            # Application entry point
├── tests/
│   ├── test_config.py      # Config tests
│   ├── test_transcriber.py # Transcriber tests
│   └── test_file_monitor.py # Monitor tests
├── Docs/
│   ├── ARCHITECTURE.md     # System architecture
│   ├── DEVELOPMENT.md      # This file
│   ├── INSTALLATION-GUIDE  # Installation instructions
│   └── CURSOR-WORKFLOW.md  # Cursor IDE workflow
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── setup.sh               # LaunchAgent installer
└── README.md              # Project overview
```

## 🔧 Development Workflow

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

# Run with verbose output
pytest tests/ -v -s
```

### Debugging

#### VS Code / Cursor

1. Set breakpoints by clicking left margin
2. Press F5 or use Debug panel
3. Select "Debug Main" configuration
4. Step through code with F10 (step over) or F11 (step into)

#### Logging

```bash
# Watch application logs
tail -f ~/Library/Logs/olympus_transcriber.log

# Watch LaunchAgent logs
tail -f /tmp/olympus-transcriber-out.log
tail -f /tmp/olympus-transcriber-err.log
```

## 🧪 Testing Strategy

### Unit Tests

Each module has corresponding unit tests:

- `test_config.py` - Configuration validation
- `test_transcriber.py` - Core transcription logic
- `test_file_monitor.py` - FSEvents monitoring

### Test Fixtures

Common fixtures in `tests/conftest.py`:

- `tmp_path` - Temporary directory (pytest built-in)
- `mock_callback` - Mock function for callbacks
- `transcriber` - Transcriber instance with mocked logger

### Mocking

Use `unittest.mock` for external dependencies:

```python
from unittest.mock import Mock, patch

@patch('src.transcriber.subprocess.run')
def test_transcribe(mock_run):
    mock_run.return_value.returncode = 0
    # Test code here
```

## 📋 Staging Workflow

### Overview

The transcription system uses a **staging workflow** to ensure reliability when working with external recorder devices that may unmount during processing.

### How It Works

1. **File Discovery**: `find_audio_files()` scans the recorder for new files
2. **Staging**: `_stage_audio_file()` copies each file to `LOCAL_RECORDINGS_DIR` (default: `~/.olympus_transcriber/recordings`)
3. **Transcription**: `transcribe_file()` processes the staged copy (not the original)
4. **State Management**: `last_sync` is only updated if ALL files in batch succeeded

### Key Benefits

- **Stability**: Transcription continues even if recorder unmounts mid-process
- **Data Safety**: Original files on recorder are never modified or deleted
- **Error Recovery**: Failed files remain in queue (not lost) if staging fails

### Configuration

Staging directory is configured in `src/config.py`:

```python
LOCAL_RECORDINGS_DIR: Path = None  # Defaults to ~/.olympus_transcriber/recordings
```

#### Multi-Computer Setup: TRANSCRIBE_DIR Configuration

When running the application on multiple Macs with different usernames, you need to ensure all instances point to the **same synchronized vault directory** to prevent duplicate transcriptions.

**Problem:**
- Default `TRANSCRIBE_DIR` uses `Path.home()`, which resolves to different paths on different computers
- Each computer would have its own local state file, potentially causing duplicate transcriptions

**Solution:**
Set the `OLYMPUS_TRANSCRIBE_DIR` environment variable on each computer to point to the same synchronized Obsidian vault directory.

**On each computer:**

1. **Option A: Using `.env` file** (recommended for development)
   
   Create or edit `.env` in the project root:
   ```bash
   OLYMPUS_TRANSCRIBE_DIR="/Users/your_username/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian/11-Transcripts"
   ```

2. **Option B: Using shell environment** (recommended for production)
   
   Add to `~/.zshrc` (or `~/.bash_profile`):
   ```bash
   export OLYMPUS_TRANSCRIBE_DIR="/Users/your_username/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian/11-Transcripts"
   ```
   
   Then reload:
   ```bash
   source ~/.zshrc
   ```

**Important:**
- All computers must point to the **exact same directory** (same vault, same folder)
- The application checks for existing transcriptions by looking for markdown files with matching `source: <audio_file>` in YAML frontmatter
- As long as all instances use the same `TRANSCRIBE_DIR`, duplicate transcriptions are automatically prevented

**Verification:**
When the application starts, it logs the transcription directory being used:
```
✓ TRANSCRIBE_DIR set from OLYMPUS_TRANSCRIBE_DIR: /path/to/vault
```
or
```
ℹ️  TRANSCRIBE_DIR using default path (set OLYMPUS_TRANSCRIBE_DIR to override)
```

**Warning:**
If the directory doesn't appear to be in a synced location (iCloud/Obsidian), the application will log a warning reminding you to use a synchronized vault for multi-computer setups.

### Testing Staging

```bash
# Test staging functionality
pytest tests/test_transcriber.py::test_stage_audio_file_success -v

# Test batch failure handling
pytest tests/test_transcriber.py::test_process_recorder_batch_failure_handling -v
```

### Debugging Staging Issues

**Check staging directory:**
```bash
ls -la ~/.olympus_transcriber/recordings/
```

**Monitor staging in logs:**
```bash
tail -f ~/Library/Logs/olympus_transcriber.log | grep -i stage
```

**Common Issues:**
- Staging fails → Check disk space and permissions
- Files not reused → Verify mtime preservation with `shutil.copy2()`
- Batch failures → Check logs for specific error messages

## 🔄 Development Cycle

### 1. Create Feature Branch

```bash
git checkout -b feature/new-feature
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
git commit -m "feat: add new feature"
```

## 🐛 Debugging Common Issues

### FSEvents Not Working

**Symptom:** Monitor doesn't detect recorder

**Solutions:**
1. Check if FSEvents is installed:
   ```bash
   pip list | grep MacFSEvents
   ```
2. Verify /Volumes is accessible:
   ```bash
   ls -la /Volumes
   ```
3. Check logs for errors:
   ```bash
   tail -f ~/Library/Logs/olympus_transcriber.log
   ```

### MacWhisper Not Found

**Symptom:** "MacWhisper not found" warning

**Solutions:**
1. Install MacWhisper from official source
2. Update `MACWHISPER_PATHS` in `src/config.py`
3. Verify path exists:
   ```bash
   ls -la /Applications/MacWhisper.app/Contents/MacOS/MacWhisper
   ```

### LaunchAgent Won't Start

**Symptom:** Agent loads but doesn't run

**Solutions:**
1. Check status:
   ```bash
   launchctl list | grep olympus-transcriber
   ```
2. View errors:
   ```bash
   cat /tmp/olympus-transcriber-err.log
   ```
3. Verify Python path in plist:
   ```bash
   cat ~/Library/LaunchAgents/com.user.olympus-transcriber.plist
   ```
4. Reload agent:
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.user.olympus-transcriber.plist
   launchctl load ~/Library/LaunchAgents/com.user.olympus-transcriber.plist
   ```

### Import Errors

**Symptom:** `ModuleNotFoundError` when running

**Solutions:**
1. Ensure virtual environment is activated:
   ```bash
   source venv/bin/activate
   ```
2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Check PYTHONPATH includes project root

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

def find_file(name: str, directory: Path) -> Optional[Path]:
    """Find a file by name in directory.
    
    Args:
        name: Filename to search for
        directory: Directory to search in
        
    Returns:
        Path to file if found, None otherwise
        
    Raises:
        ValueError: If directory doesn't exist
    """
    if not directory.exists():
        raise ValueError(f"Directory not found: {directory}")
    
    for item in directory.rglob(name):
        if item.is_file():
            return item
    
    return None
```

### Logging

Always use the logger, never print():

```python
from src.logger import logger

# Good
logger.info("Processing file")
logger.error(f"Failed: {error}")

# Bad
print("Processing file")
```

### Error Handling

Handle errors gracefully:

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

## 🔐 Security Considerations

- No credentials in code
- State file is local only
- Logs may contain file paths (not sensitive)
- MacWhisper runs locally (no cloud)
- LaunchAgent runs as user (not root)

## 🚀 Performance Tips

### FSEvents vs Polling

FSEvents is much more efficient than polling:
- Zero CPU when idle
- Instant notification on changes
- No battery impact

### Transcription Optimization

- Set appropriate timeout (default 30 min)
- Process files sequentially to avoid resource contention
- Use state file to avoid re-transcribing

## 📊 Monitoring

### Health Checks

```bash
# Is daemon running?
launchctl list | grep olympus-transcriber

# Recent activity?
tail -20 ~/Library/Logs/olympus_transcriber.log

# Disk space for transcriptions?
df -h ~/Documents/Transcriptions/

# State file status?
cat ~/.olympus_transcriber_state.json
```

### Performance Metrics

```bash
# CPU usage
ps aux | grep olympus_transcriber

# Memory usage
top -l 1 | grep -A 5 python

# File count
ls -l ~/Documents/Transcriptions/ | wc -l
```

## 🤝 Contributing

### Pull Request Process

1. Fork the repository
2. Create feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Update documentation
6. Submit pull request

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Tests
- `chore`: Maintenance

Example:
```
feat: add support for FLAC audio files

- Add .flac to AUDIO_EXTENSIONS
- Update transcriber to handle FLAC
- Add tests for FLAC transcription

Closes #123
```

## 📞 Getting Help

- Check `Docs/ARCHITECTURE.md` for system design
- Check `README.md` for usage guide
- Check logs for errors
- Open an issue on GitHub





