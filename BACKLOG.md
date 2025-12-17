# Backlog projektu „Transrec"

> **Wersja:** v1.11.0 → v2.0.0
>
> **Powiązane dokumenty:**
> - [CHANGELOG.md](CHANGELOG.md) - Historia zmian
> - [Docs/PUBLIC-DISTRIBUTION-PLAN.md](Docs/PUBLIC-DISTRIBUTION-PLAN.md) - Szczegółowy plan

---

## 🚀 PRIORYTET: Dystrybucja Publiczna + Freemium

### Model biznesowy: Freemium

```
┌─────────────────────────────────────────────────────────────────┐
│  FREE (GitHub, open source)     │  PRO ($79 lifetime)          │
├─────────────────────────────────┼───────────────────────────────┤
│  ✅ Wykrywanie recorderów       │  ✅ Wszystko z FREE +         │
│  ✅ Transkrypcja lokalna        │  ⭐ AI Podsumowania           │
│  ✅ Export Markdown             │  ⭐ AI Tagi                   │
│  ✅ Podstawowe tagi             │  ⭐ Cloud sync (przyszłość)   │
│  ❌ AI features                 │  ⭐ Web dashboard (przyszłość)│
└─────────────────────────────────┴───────────────────────────────┘
```

### Roadmap

#### ✅ v1.11.0 Przygotowanie (DONE)
- [x] Cursor rules dla projektu (Git Flow, freemium, dokumentacja)
- [x] Reorganizacja dokumentacji (archiwum, cross-references)
- [x] Aktualizacja dokumentów dla v2.0.0

#### v2.0.0 FREE (~5 tygodni)
- [ ] **Faza 1:** Uniwersalne źródła nagrań (nie tylko Olympus LS-P1)
- [ ] **Faza 2:** System pobierania whisper.cpp/modeli on-demand
- [ ] **Faza 3:** First-run wizard z konfiguracją
- [ ] **Faza 4:** Pakowanie z py2app (zamiast PyInstaller)
- [ ] **Faza 5:** Code signing & notaryzacja ($99 Apple Developer)
- [ ] **Faza 6:** Profesjonalny DMG & GitHub Release
- [ ] **Faza 7:** GUI Settings & polish
- [ ] **Faza 8:** Infrastruktura Freemium (feature flags, placeholder PRO)

#### v2.1.0 PRO (~3 tygodnie po FREE)
- [ ] **Faza 9:** Backend PRO (Cloudflare Workers + LemonSqueezy)
- [ ] API: /v1/license, /v1/summarize, /v1/tags
- [ ] Integracja z aplikacją
- [ ] Strona transrec.app z zakupem

### Wymagane decyzje (przed Fazą 1)
- [x] ~~Zatwierdzenie planu~~ ✓
- [x] ~~Strategia Git~~ ✓ (Git Flow z feature branches)
- [ ] Rejestracja Apple Developer Program ($99)
- [ ] Wybór: tylko Apple Silicon vs obie architektury
- [ ] Model cenowy PRO: lifetime $79 vs subskrypcja

### Strategia Git (zatwierdzona)

```
Repozytoria:
├── transrec (PUBLIC)           ← Główna aplikacja FREE+PRO
├── transrec-backend (PRIVATE)  ← API dla PRO
└── transrec.app (PUBLIC)       ← Strona marketingowa (opcjonalnie)

Git Flow:
├── main                        ← Produkcja (tylko releases)
├── develop                     ← Integracja
└── feature/faza-X-nazwa        ← Feature branches

Wersjonowanie:
├── v1.11.0                     ← Przygotowanie (CURRENT)
├── v2.0.0-alpha.1, beta.1, rc.1
├── v2.0.0                      ← Release FREE
└── v2.1.0                      ← Release PRO
```

### Następne kroki

```bash
# 1. Commituj zmiany v1.11.0
git add -A
git commit -m "v1.11.0: Documentation v2.0.0, Cursor rules, Git Flow strategy"
git tag -a v1.11.0 -m "Preparation for v2.0.0 - docs, rules, Git strategy"
git push origin main --tags

# 2. Utwórz branch develop (jeśli nie istnieje)
git checkout -b develop
git push -u origin develop

# 3. Rozpocznij Fazę 1
git checkout develop
git checkout -b feature/faza-1-universal-sources
```

---

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


