# Olympus Transcriber

Automatyczny system transkrypcji plików audio z dyktafonu Olympus LS-P1 na macOS.

## 🎯 Funkcje

- **Automatyczna detekcja** - wykrywa moment podłączenia dyktafonu Olympus LS-P1
- **Inteligentne skanowanie** - znajduje tylko nowe pliki audio od ostatniej synchronizacji
- **Automatyczna transkrypcja** - używa whisper.cpp z Core ML dla maksymalnej wydajności
- **AI Podsumowania** - automatyczne generowanie podsumowań i tytułów używając Claude API
- **Markdown Output** - transkrypcje zapisywane jako pliki `.md` z YAML frontmatter (gotowe dla Obsidian)
- **Inteligentne nazewnictwo** - nazwy plików generowane z podsumowania: `YYYY-MM-DD_Tytul.md`
- **Metadane audio** - automatyczne wyciąganie daty nagrania i czasu trwania
- **Daemon w tle** - działa jako LaunchAgent, uruchamia się automatycznie przy starcie systemu
- **Tracking historii** - pamięta które pliki zostały już przetranksrybowane
- **Akceleracja GPU** - Core ML na Apple Silicon dla 10x szybszej transkrypcji

## 📋 Wymagania

- macOS (Silicon zalecane dla Core ML)
- Python 3.8+
- ffmpeg (instalowany automatycznie przez skrypt)
- whisper.cpp (instalowany automatycznie przez skrypt)
- Olympus LS-P1 recorder
- **Opcjonalnie:** Anthropic API key dla podsumowań (ustaw `ANTHROPIC_API_KEY` env var)

## 🚀 Instalacja

### 1. Sklonuj repozytorium

```bash
cd ~/CODE
git clone <repository-url> Olympus_transcription
cd Olympus_transcription
```

### 2. Utwórz i aktywuj virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Zainstaluj zależności

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Dla development
```

### 3.5. (Opcjonalnie) Skonfiguruj Claude API dla podsumowań

**Opcja 1: Plik .env (zalecane)**

```bash
# Skopiuj przykładowy plik
cp .env.example .env

# Edytuj .env i dodaj swój klucz API
nano .env  # lub użyj swojego edytora
```

W pliku `.env` dodaj:
```bash
ANTHROPIC_API_KEY=sk-ant-...
```

**Opcja 2: Zmienne środowiskowe systemu**

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Lub dodaj do `~/.zshrc` / `~/.bash_profile`:
```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.zshrc
source ~/.zshrc
```

**Bez API key:** System będzie działał, ale bez podsumowań AI (użyje prostych tytułów z nazwy pliku).

**Gdzie zdobyć klucz API:** https://console.anthropic.com/

### 4. Zainstaluj whisper.cpp

```bash
bash scripts/install_whisper_cpp.sh
```

Ten skrypt automatycznie:
- Klonuje i kompiluje whisper.cpp z obsługą Core ML
- Pobiera model "small" (optymalna równowaga szybkość/jakość)
- Generuje model Core ML dla Apple Silicon (jeśli dostępny)
- Instaluje ffmpeg jeśli potrzebny

### 5. Test lokalny

```bash
python src/main.py
```

### 6. Instalacja jako LaunchAgent

```bash
chmod +x setup.sh
./setup.sh
```

## 📂 Struktura Projektu

```
Olympus_transcription/
├── src/                    # Kod źródłowy
│   ├── __init__.py
│   ├── main.py            # Entry point
│   ├── config.py          # Konfiguracja
│   ├── logger.py          # Logging
│   ├── file_monitor.py    # FSEvents monitoring
│   ├── transcriber.py     # Logika transkrypcji
│   ├── summarizer.py      # AI podsumowania (Claude)
│   └── markdown_generator.py  # Generowanie plików MD
├── tests/                 # Testy
├── Docs/                  # Dokumentacja
├── requirements.txt       # Dependencies
└── setup.sh              # Instalacja LaunchAgent
```

## 🔧 Konfiguracja

Konfiguracja znajduje się w `src/config.py`:

- **RECORDER_NAMES** - nazwy voluminów do wykrywania
- **TRANSCRIBE_DIR** - folder na transkrypcje (domyślnie: Obsidian vault `11-Transcripts`)
- **STATE_FILE** - plik stanu (domyślnie: `~/.olympus_transcriber_state.json`)
- **WHISPER_MODEL** - rozmiar modelu: tiny, base, small (domyślny), medium, large
- **WHISPER_LANGUAGE** - język transkrypcji (domyślnie: "pl")
- **WHISPER_CPP_PATH** - ścieżka do binarki whisper.cpp (domyślnie: `~/whisper.cpp/main`)
- **WHISPER_CPP_MODELS_DIR** - folder z modelami (domyślnie: `~/whisper.cpp/models`)
- **TRANSCRIPTION_TIMEOUT** - maksymalny czas transkrypcji (60 minut)
- **ENABLE_SUMMARIZATION** - włącz/wyłącz podsumowania AI (domyślnie: True)
- **LLM_PROVIDER** - provider LLM (domyślnie: "claude")
- **LLM_MODEL** - model Claude (domyślnie: "claude-3-haiku-20240307")
- **SUMMARY_MAX_WORDS** - maksymalna liczba słów w podsumowaniu (200)
- **TITLE_MAX_LENGTH** - maksymalna długość tytułu (60 znaków)
- **DELETE_TEMP_TXT** - usuń pliki TXT po utworzeniu MD (domyślnie: True)

## 📝 Użycie

### Automatyczny tryb (LaunchAgent)

Po instalacji przez `setup.sh`, aplikacja działa w tle automatycznie:

1. Podłącz Olympus LS-P1 do Mac
2. System automatycznie wykryje nowe pliki audio
3. Transkrypcje pojawią się bezpośrednio w Obsidian vault (`11-Transcripts`)

### Manualny tryb (development)

```bash
source venv/bin/activate
python src/main.py
```

### Reset pamięci systemu

System śledzi ostatnio przetworzone pliki, aby unikać duplikatów. Jeśli chcesz przetworzyć pliki ponownie lub zmienić datę od której system ma wykrywać pliki:

**Opcja 1: Reset z zachowaniem bieżącej sesji**
```bash
bash scripts/reset_recorder_memory.sh
# Lub z własną datą:
bash scripts/reset_recorder_memory.sh 2025-11-15
```

**Opcja 2: Uruchomienie ze świeżą pamięcią (all-in-one)**
```bash
# Automatycznie resetuje pamięć do 18 listopada i uruchamia system
bash scripts/run_with_fresh_memory.sh

# Lub z własną datą:
bash scripts/run_with_fresh_memory.sh 2025-11-15
```

Po resecie system będzie przetwarzał wszystkie pliki audio utworzone po określonej dacie.

### Monitoring logów

```bash
# Logi aplikacji
tail -f ~/Library/Logs/olympus_transcriber.log

# LaunchAgent logi
tail -f /tmp/olympus-transcriber-out.log
tail -f /tmp/olympus-transcriber-err.log
```

### Zarządzanie LaunchAgent

```bash
# Status
launchctl list | grep olympus-transcriber

# Stop
launchctl unload ~/Library/LaunchAgents/com.user.olympus-transcriber.plist

# Start
launchctl load ~/Library/LaunchAgents/com.user.olympus-transcriber.plist
```

## 🧪 Development

### Uruchom testy

```bash
pytest tests/ -v
```

### Formatowanie kodu

```bash
black src/
isort src/
```

### Linting

```bash
flake8 src/
mypy src/
```

## 📊 Architektura

System składa się z 5 głównych modułów:

1. **config.py** - centralna konfiguracja
2. **logger.py** - system logowania
3. **file_monitor.py** - monitoring FSEvents dla `/Volumes`
4. **transcriber.py** - logika transkrypcji i zarządzanie stanem
5. **main.py** - orchestration i threading

Więcej szczegółów w `Docs/ARCHITECTURE.md`.

## 🐛 Troubleshooting

### Aplikacja nie wykrywa recordera

- Sprawdź czy dyktafon jest zamontowany: `ls /Volumes/`
- Sprawdź logi: `tail -f ~/Library/Logs/olympus_transcriber.log`

### whisper.cpp nie znaleziony

- Uruchom: `bash scripts/install_whisper_cpp.sh`
- Sprawdź ścieżkę w `src/config.py` → `WHISPER_CPP_PATH`
- Upewnij się że kompilacja się powiodła: `~/whisper.cpp/main -h`

### LaunchAgent nie działa

```bash
# Sprawdź status
launchctl list | grep olympus

# Sprawdź logi błędów
cat /tmp/olympus-transcriber-err.log
```

## 📄 Licencja

MIT License

## 🤝 Contributing

Pull requests są mile widziane. Dla większych zmian, proszę najpierw otworzyć issue.

## 📧 Kontakt

Dla pytań i wsparcia, sprawdź dokumentację w folderze `Docs/`.

