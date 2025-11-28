# Backlog projektu „Transrec”

## 1. Alternatywny wrapper z GUI w pasku menu

### 1.1. Menu bar app (ikona w pasku)

- **Cel**: Wygodna kontrola daemona z paska menu macOS.
- **Zakres**:
  - Ikona w pasku menu z prostym menu:
    - Start / Stop transkrybera.
    - Status: Idle / Scanning / Transcribing / Error.
    - Nazwa ostatnio przetworzonego pliku.
    - Szybkie linki: otwórz log, otwórz katalog transkryptów.
  - Integracja ze stanem aplikacji (`AppStatus`, `state_manager`).
- **Uwagi techniczne**:
  - Osobna aplikacja `.app` (np. Python + pyobjc / Swift), która uruchamia istniejący daemon (`python -m src.main`) lub komunikuje się z już działającym procesem.
  - Jedno źródło prawdy dla stanu (plik JSON / prosty socket / mechanizm IPC).

### 1.2. Natywny wrapper zamiast Automatora

- **Cel**: Usunięcie zależności od Automatora i powiadomień „0% completed (Run Shell Script)”.
- **Zakres**:
  - Mały natywny launcher (np. zbudowany w Swift lub jako mały binarny wrapper), który:
    - ustawia środowisko (`PATH`, `PYTHONPATH`, zmienne środowiskowe),
    - uruchamia `venv/bin/python -m src.main` jako proces w tle,
    - sam kończy działanie po starcie daemona.
  - Możliwość wspólnego użycia przez:
    - Login Items,
    - (opcjonalnie) LaunchAgenta.
- **Kryteria akceptacji**:
  - `open Transrec.app` nie pokazuje komunikatu o niekończącym się zadaniu Automatora.
  - Start z Login Items zachowuje się identycznie jak obecnie (transkrypcje działają).

## 2. Stabilizacja lub wyłączenie Core ML

### 2.1. Konfigurowalny tryb Core ML / CPU

- **Cel**: Mieć pełną kontrolę nad użyciem Core ML i możliwość jego wyłączenia.
- **Zakres**:
  - Nowa opcja w konfiguracji (`config.py` + `.env`), np.:
    - `WHISPER_COREML_MODE = "auto" | "off" | "force"`.
  - Zachowanie:
    - `auto` – aktualne: próbuj Core ML, w razie problemów fallback na CPU.
    - `off` – pomijaj Core ML, od razu używaj trybu CPU.
    - `force` – próba tylko z Core ML (do testów / debugowania); błąd, jeśli Core ML się wyłoży.
- **Kryteria akceptacji**:
  - Zmiana trybu nie wymaga zmian w kodzie – tylko konfiguracja.
  - Log jasno informuje, w jakim trybie działa transkrypcja.

### 2.2. Automatyczne wykrywanie niestabilności Core ML

- **Cel**: Automatyczne przełączenie na CPU, gdy Core ML jest niestabilne.
- **Zakres**:
  - Zliczanie liczby błędów zawierających wzorce typu:
    - `Core ML`, `ggml_metal`, `MTLLibrar`, `tensor API disabled` itp.
  - Prosty mechanizm heurystyczny:
    - jeśli w ostatnich `N` próbach (np. 5) Core ML zawodzi więcej niż `K` razy (np. 3),
      to automatycznie przełącz `WHISPER_COREML_MODE` na `off` (tylko CPU) do czasu restartu.
  - Wyraźny wpis w logu i (opcjonalnie) notyfikacja systemowa o przełączeniu trybu.

### 2.3. Dokumentacja i domyślne ustawienia

- **Zakres**:
  - Zaktualizować:
    - `QUICKSTART.md` – sekcja „Core ML vs CPU (wydajność vs stabilność)”.
    - `Docs/INSTALLATION-GUIDE` – opis konfiguracji `WHISPER_COREML_MODE`.
  - Zaproponować bezpieczny domyślny tryb:
    - `auto` z działającym fallbackiem, ale z jasną instrukcją jak wymusić `off`.


