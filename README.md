# Transrec

> **Wersja:** v1.10.0 (development) → v2.0.0 (w przygotowaniu)

Automatyczny system transkrypcji plików audio z dowolnego dyktafonu lub karty SD na macOS.

## 🎯 Funkcje

### FREE (v2.0.0)
- **Automatyczna detekcja** - wykrywa podłączenie dowolnego dysku zewnętrznego z plikami audio
- **Inteligentne skanowanie** - znajduje tylko nowe pliki audio od ostatniej synchronizacji
- **Automatyczna transkrypcja** - używa whisper.cpp z Core ML dla maksymalnej wydajności
- **Markdown Output** - transkrypcje zapisywane jako pliki `.md` z YAML frontmatter
- **Menu bar app** - natywna aplikacja macOS z interfejsem w pasku menu
- **Settings UI** - graficzne okno ustawień

### PRO (v2.1.0 - planowane)
- 🔒 **AI Podsumowania** - automatyczne generowanie podsumowań używając Claude API
- 🔒 **Auto-tagging** - inteligentne tagowanie transkrypcji
- 🔒 **Auto-title** - nazwy plików generowane z podsumowania
- 🔒 **Cloud sync** - synchronizacja z Obsidian/iCloud

## 📋 Wymagania

- macOS 12+ (Apple Silicon zalecane dla Core ML)
- Python 3.12+
- ffmpeg (instalowany automatycznie)
- whisper.cpp (instalowany automatycznie przy pierwszym uruchomieniu)

## 🚀 Szybki Start

Szczegółowa instrukcja: **[QUICKSTART.md](QUICKSTART.md)**

```bash
# 1. Sklonuj repozytorium
git clone https://github.com/yourusername/transrec.git
cd transrec

# 2. Utwórz virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Zainstaluj zależności
pip install -r requirements.txt

# 4. Zainstaluj whisper.cpp
bash scripts/install_whisper_cpp.sh

# 5. Uruchom aplikację
python -m src.menu_app
```

## 📂 Struktura Projektu

```
transrec/
├── src/                      # Kod źródłowy
│   ├── main.py              # Entry point (CLI)
│   ├── menu_app.py          # Menu bar application (GUI)
│   ├── app_core.py          # Core daemon logic
│   ├── config.py            # Konfiguracja
│   ├── file_monitor.py      # FSEvents monitoring
│   ├── transcriber.py       # Logika transkrypcji
│   ├── markdown_generator.py # Generowanie plików MD
│   ├── summarizer.py        # AI podsumowania (PRO)
│   └── tagger.py            # Auto-tagging (PRO)
├── tests/                    # Testy
├── Docs/                     # Dokumentacja
│   ├── PUBLIC-DISTRIBUTION-PLAN.md  # Plan v2.0.0
│   ├── ARCHITECTURE.md      # Architektura systemu
│   ├── API.md               # Dokumentacja API
│   └── ...
├── scripts/                  # Skrypty pomocnicze
├── requirements.txt          # Dependencies
└── README.md                 # Ten plik
```

## 📝 Użycie

### Menu Bar App (Zalecane)

```bash
python -m src.menu_app
```

Aplikacja pojawi się w pasku menu z opcjami:
- Status w czasie rzeczywistym
- Otwieranie logów
- Reset pamięci
- Ustawienia

### CLI Mode

```bash
python -m src.main
```

## 🔧 Konfiguracja

Konfiguracja w `src/config.py` lub przez zmienne środowiskowe:

| Zmienna | Opis | Domyślnie |
|---------|------|-----------|
| `OLYMPUS_TRANSCRIBE_DIR` | Folder na transkrypcje | `~/Documents/Transcriptions` |
| `WHISPER_MODEL` | Model whisper | `small` |
| `WHISPER_LANGUAGE` | Język transkrypcji | `pl` |

Szczegóły: **[Docs/API.md](Docs/API.md#configpy)**

## 📚 Dokumentacja

| Dokument | Opis |
|----------|------|
| **[QUICKSTART.md](QUICKSTART.md)** | Szybki start dla developerów |
| **[CHANGELOG.md](CHANGELOG.md)** | Historia zmian |
| **[BACKLOG.md](BACKLOG.md)** | Zaplanowane funkcje |
| **[Docs/ARCHITECTURE.md](Docs/ARCHITECTURE.md)** | Architektura systemu |
| **[Docs/API.md](Docs/API.md)** | Dokumentacja API modułów |
| **[Docs/DEVELOPMENT.md](Docs/DEVELOPMENT.md)** | Przewodnik deweloperski |
| **[Docs/FULL_DISK_ACCESS_SETUP.md](Docs/FULL_DISK_ACCESS_SETUP.md)** | Konfiguracja FDA |
| **[Docs/PUBLIC-DISTRIBUTION-PLAN.md](Docs/PUBLIC-DISTRIBUTION-PLAN.md)** | Plan dystrybucji v2.0.0 |

## 🧪 Development

```bash
# Testy
pytest tests/ -v

# Formatowanie
black src/
isort src/

# Linting
flake8 src/
mypy src/
```

Szczegóły: **[Docs/DEVELOPMENT.md](Docs/DEVELOPMENT.md)**

## 🗺️ Roadmap

### v2.0.0 FREE (Q1 2025)
- [ ] Universal recorder support
- [ ] First-run wizard
- [ ] py2app packaging
- [ ] Code signing & notarization
- [ ] DMG release

### v2.1.0 PRO (Q2 2025)
- [ ] AI summaries
- [ ] Auto-tagging
- [ ] Cloud sync
- [ ] License management

Szczegóły: **[Docs/PUBLIC-DISTRIBUTION-PLAN.md](Docs/PUBLIC-DISTRIBUTION-PLAN.md)**

## 🐛 Troubleshooting

### Aplikacja nie wykrywa dysku

1. Sprawdź czy dysk jest zamontowany: `ls /Volumes/`
2. Sprawdź logi: `tail -f ~/Library/Logs/olympus_transcriber.log`
3. Upewnij się, że aplikacja ma **Full Disk Access**: **[Docs/FULL_DISK_ACCESS_SETUP.md](Docs/FULL_DISK_ACCESS_SETUP.md)**

### whisper.cpp nie znaleziony

```bash
bash scripts/install_whisper_cpp.sh
```

## 📄 Licencja

MIT License

## 🤝 Contributing

1. Fork repozytorium
2. Utwórz feature branch: `git checkout -b feature/nazwa`
3. Commit: `git commit -m "v2.0.0: Opis zmiany"`
4. Push i Pull Request do `develop`

Szczegóły workflow: **[Docs/DEVELOPMENT.md](Docs/DEVELOPMENT.md)**

---

> **Powiązane dokumenty:**
> - Architektura: [Docs/ARCHITECTURE.md](Docs/ARCHITECTURE.md)
> - API: [Docs/API.md](Docs/API.md)
> - Development: [Docs/DEVELOPMENT.md](Docs/DEVELOPMENT.md)
> - Plan v2.0.0: [Docs/PUBLIC-DISTRIBUTION-PLAN.md](Docs/PUBLIC-DISTRIBUTION-PLAN.md)
