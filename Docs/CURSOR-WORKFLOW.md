# Workflow w Cursor - Step by Step

## 📋 Część 1: Inicjalizacja Projektu

### Krok 1.1: Utwórz folder projektu

```bash
mkdir -p ~/Projects/olympus-transcriber
cd ~/Projects/olympus-transcriber
```

### Krok 1.2: Inicjalizuj Git (opcjonalnie, ale rekomendowane)

```bash
git init
```

### Krok 1.3: Otwórz w Cursor

```bash
cursor ~/Projects/olympus-transcriber
```

Lub: Cursor → File → Open → olympus-transcriber

### Krok 1.4: Utwórz strukturę folderów w Cursor

W Cursor (left sidebar):
1. Prawy klik na root → New Folder → `src`
2. Prawy klik na root → New Folder → `tests`
3. Prawy klik na root → New Folder → `docs`
4. Prawy klik na root → New Folder → `.cursor`
5. W `.cursor` → New Folder → `rules`

Struktura powinna wyglądać:
```
olympus-transcriber/
├── src/
├── tests/
├── docs/
└── .cursor/
    └── rules/
```

---

## 📝 Część 2: Tworzenie Plików Bazowych

### Krok 2.1: Utwórz `.gitignore`

W Cursor:
1. Prawy klik na root
2. New File → `.gitignore`
3. Wklej zawartość z **pliku `.gitignore`** (patrz dokumentacja setup)

### Krok 2.2: Utwórz `requirements.txt`

1. New File → `requirements.txt`
2. Wklej zawartość (patrz dokumentacja setup)

### Krok 2.3: Utwórz `requirements-dev.txt`

1. New File → `requirements-dev.txt`
2. Wklej zawartość (patrz dokumentacja setup)

### Krok 2.4: Utwórz `README.md`

1. New File → `README.md`
2. Wklej zawartość (patrz dokumentacja setup)

---

## 🐍 Część 3: Virtual Environment i Setup

### Krok 3.1: Otwórz Terminal w Cursor

Keyboard Shortcut: **Ctrl + `` (backtick)**

Lub: Terminal → New Terminal

### Krok 3.2: Utwórz Virtual Environment

```bash
python3 -m venv venv
```

### Krok 3.3: Aktywuj Virtual Environment

```bash
source venv/bin/activate
```

Powinno pokazać:
```
(venv) user@machine olympus-transcriber %
```

### Krok 3.4: Zainstaluj Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Krok 3.5: Weryfikacja

```bash
python --version
pip list
```

---

## 📂 Część 4: Tworzenie Source Code

### Krok 4.1: Utwórz `src/__init__.py`

```bash
# W Cursor
New File → src/__init__.py
# (plik może być pusty)
```

### Krok 4.2: Utwórz `src/config.py`

1. New File → `src/config.py`
2. Wklej kod z **dokumentacji setup** (sekcja "Struktura pliku src/config.py")

**Quick Add w Cursor:**
- Użyj Cmd+K aby vygenerować kod
- Prompt: "Create Python config.py with dataclass for olympus transcriber paths and constants"

### Krok 4.3: Utwórz `src/logger.py`

1. New File → `src/logger.py`
2. Wklej kod z **dokumentacji setup** (sekcja "Struktura pliku src/logger.py")

### Krok 4.4: Utwórz `src/file_monitor.py`

1. New File → `src/file_monitor.py`
2. Wklej kod z **dokumentacji setup** (sekcja "Struktura src/file_monitor.py")

### Krok 4.5: Utwórz `src/transcriber.py`

1. New File → `src/transcriber.py`
2. Wklej kod z **dokumentacji setup** (sekcja "Struktura src/transcriber.py")

**Wskazówka:** Plik jest dużo, więc:
- Otwórz kod w jednym oknie
- Ctrl+P w Cursor → transcriber.py
- Wklej całą zawartość

### Krok 4.6: Utwórz `src/main.py`

1. New File → `src/main.py`
2. Wklej kod z **dokumentacji setup** (sekcja "Struktura src/main.py")

---

## 🧪 Część 5: Debugowanie i Testing Setup

### Krok 5.1: Utwórz `.vscode/launch.json`

1. New File → `.vscode/launch.json` (tworzy folder automatycznie)
2. Wklej:

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
        }
    ]
}
```

### Krok 5.2: Utwórz Cursor Rules

1. New File → `.cursor/rules/python-rules.mdc`
2. Wklej zawartość z **dokumentacji setup** (sekcja "Cursor Rules")

---

## ▶️ Część 6: Testowanie Lokalne

### Krok 6.1: Uruchom Main Script

W Terminal (Ctrl + `):

```bash
# Upewnij się że venv jest aktywny
source venv/bin/activate

# Uruchom
python src/main.py
```

**Oczekiwane output:**
```
2025-11-19 10:35:00 - olympus_transcriber - INFO - 🚀 Olympus Transcriber started
2025-11-19 10:35:00 - olympus_transcriber - INFO - 📂 Transcription directory: /Users/USERNAME/Documents/Transcriptions
2025-11-19 10:35:00 - olympus_transcriber - INFO - 📄 State file: /Users/USERNAME/.olympus_transcriber_state.json
2025-11-19 10:35:00 - olympus_transcriber - INFO - ✓ All monitors running. Waiting for recorder...
```

### Krok 6.2: Test - Podłącz Recorder

1. Spraw by skrypt działał (linia wyżej)
2. W drugim oknie Terminal (Cmd+N):
   ```bash
   # Uruchom tailing na log file
   tail -f ~/Library/Logs/olympus_transcriber.log
   ```
3. Podłącz Olympus LS-P1 do USB
4. Obserwuj logi - powinno się pojawić:
   ```
   📢 Detected recorder activity: /Volumes/LS-P1
   🔍 Checking for recorder...
   ✓ Recorder detected
   ```

### Krok 6.3: Stop Skryptu

W Terminal gdzie runs `python src/main.py`:
- **Ctrl + C**

Powinno pokazać:
```
⏹ Shutting down...
```

---

## 🔧 Część 7: Iteracyjny Development w Cursor

### Workflow: Red-Green-Refactor

#### 1. **RED: Napisz test (TDD)**

Otwórz `tests/test_transcriber.py`:

```python
import pytest
from src.transcriber import Transcriber

def test_find_macwhisper():
    """Test znalezienia MacWhisper"""
    transcriber = Transcriber()
    result = transcriber._find_macwhisper()
    assert result is not None or result is None  # Test że działa
```

Uruchom:
```bash
pytest tests/test_transcriber.py -v
```

**Powinno failnąć** (bo test nie da się przejść bez kodu).

#### 2. **GREEN: Napisz minimalny kod**

W `src/transcriber.py`, dodaj test-specific codepath jeśli potrzeba.

Uruchom test znowu - powinno PASS.

#### 3. **REFACTOR: Popraw w Cursor**

Cursor AI Commands:
- **Cmd+K**: "Refactor this function to use better error handling"
- **Cmd+L**: "Add type hints to this function"
- **Cmd+Shift+K**: "Generate docstring for this function"

#### 4. **COMMIT: Zapisz w Git**

```bash
git add -A
git commit -m "feat: add macwhisper discovery"
```

### Cursor AI Features

**Cmd+K** - Generate Code:
```
"Dodaj funkcję aby znaleźć wszystkie nowe pliki MP3 od ostatniego sync"
```

**Cmd+L** (Composer Agent) - Multi-step refactor:
```
"Refactor config.py to:
1. Use Pydantic instead of dataclass
2. Add validation for paths
3. Add environment variable support"
```

**Cmd+I** - Edit/Transform:
- Zaznacz kod
- Cmd+I
- "Convert this to async"

---

## 📦 Część 8: Deployment

### Krok 8.1: Zrób setup.sh executable

```bash
chmod +x setup.sh
```

### Krok 8.2: Uruchom setup

```bash
bash setup.sh
```

**Co robi:**
1. Tworzy directories
2. Tworzy LaunchAgent .plist
3. Ładuje go do launchctl

### Krok 8.3: Weryfikacja Production

```bash
# Sprawdź czy daemon runs
launchctl list | grep olympus-transcriber

# Tail production logs
tail -f ~/Library/Logs/olympus_transcriber.log
```

---

## 📊 Część 9: Debugging w Cursor

### Breakpoint Debugging

1. W `src/transcriber.py`, kliknij na lewą krawędź przy linii:
   ```python
   recorder = self.find_recorder()  # ← kliknij tutaj
   ```
   Pojawi się **czerwona kropka** (breakpoint).

2. Ctrl+Shift+D → "Debug Main" → ▶️ Play

3. Skrypt uruchomi się i zatrzyma na breakpoint

4. Watch Variables:
   - Hover nad zmienną aby zobaczyć wartość
   - Bottom panel: Variables, Stack, Breakpoints

### Console Commands

W debugger console:

```python
# Sprawdź wartość zmiennej
recorder
>>> PosixPath('/Volumes/LS-P1')

# Zmień wartość (if needed)
transcriber.recorder_monitoring = True
```

---

## 🚀 Gotowe! Kolejne kroki

### Dla Szybkiego Development
1. Pracuj w Cursor
2. Testuj lokalnie (`python src/main.py`)
3. Piszej testy (`pytest`)
4. Commituj do Git

### Dla Integracji (przyszłość)
1. Dodaj Obsidian integration
2. Dodaj N8N webhook
3. Dodaj Web UI
4. Każdy feature = nowy branch w Git

### Dokumentacja
- Aktualizuj `docs/DEVELOPMENT.md` gdy zmienisz setup
- Aktualizuj `docs/ARCHITECTURE.md` gdy zmienisz design
- Commituj docs wraz z kodem
