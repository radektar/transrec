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
- [x] **Faza 1:** Uniwersalne źródła nagrań (nie tylko Olympus LS-P1) ✅ *COMPLETED*
- [x] **Faza 2:** System pobierania whisper.cpp/modeli on-demand ✅ *COMPLETED - GitHub Release deps-v1.0.0 działa*
- [x] **Faza 3:** First-run wizard z konfiguracją ✅ *COMPLETED - testy manualne zakończone*
- [x] **Faza 4:** Pakowanie z py2app (zamiast PyInstaller) ✅ *COMPLETED - bundle działa, wymaga optymalizacji rozmiaru (43MB > 20MB)*
- [ ] **Faza 5:** Code signing & notaryzacja ($99 Apple Developer)
- [ ] **Faza 6:** Profesjonalny DMG & GitHub Release
- [x] **Faza 7:** GUI Settings & polish ✅ *COMPLETED - testy automatyczne przechodzą, testy manualne wymagane*
  - [x] Date picker dla "Resetuj pamięć od..." (7 dni / 30 dni / custom) ✅
  - [x] Graficzny wybór folderu w wizardzie (NSOpenPanel) ✅
  - [x] Dialog "O aplikacji" w menu ✅
  - [x] Moduł UI (`src/ui/`) przygotowany na redesign ✅
  - [x] **KRYTYCZNE:** Naprawa blokowania UI podczas pobierania zależności ✅ *Naprawione w Fazie 4*
  - [x] Okno ustawień aplikacji (zmiana folderu, języka po instalacji) ✅ *COMPLETED - zobacz BACKLOG sekcja 3*
  - [x] Możliwość zamknięcia wizarda w każdym kroku ✅ *COMPLETED - zobacz BACKLOG sekcja 4*
  - [x] Dropdown wyboru języka w wizardzie ✅ *COMPLETED - zobacz BACKLOG sekcja 5*
- [ ] **Faza 8:** Infrastruktura Freemium (feature flags, placeholder PRO)
- [ ] **Faza 9:** Pełny redesign UI (nowy instalator, menu, ikony, kolory) - *przed dystrybucją*

#### v2.1.0 PRO (~3 tygodnie po FREE)
- [ ] **Faza 10:** Backend PRO (Cloudflare Workers + LemonSqueezy)
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

## 2. Poprawka UX: Graficzny wybór folderu w wizardzie

### 2.1. Problem
W kroku wyboru folderu docelowego (TEST M3.9) użytkownik może tylko wpisać ścieżkę ręcznie. Brak natywnego dialogu wyboru folderu to złe UX.

### 2.2. Rozwiązanie
Dodać przycisk "Wybierz folder..." który otworzy natywny dialog macOS (`NSOpenPanel` przez PyObjC).

**Plik:** `src/setup/wizard.py` - metoda `_show_output_config()`

```python
from AppKit import NSOpenPanel, NSURL

def _show_output_config(self) -> str:
    """Konfiguracja folderu docelowego."""
    # Najpierw pokaż dialog z opcją wyboru
    response = rumps.alert(
        title="📂 Folder na transkrypcje",
        message=(
            "Gdzie zapisywać pliki z transkrypcjami?\n\n"
            "Domyślnie: folder Obsidian w iCloud"
        ),
        ok="Wybierz folder...",
        cancel="Użyj domyślnego",
    )
    
    if response == 1:  # Wybierz folder
        folder_path = self._choose_folder_dialog()
        if folder_path:
            self.settings.output_dir = folder_path
            return "next"
        else:
            return "back"  # Anulowano wybór
    
    # Użyj domyślnego lub pozwól edytować
    window = rumps.Window(...)
    # ... reszta kodu

def _choose_folder_dialog(self) -> Optional[str]:
    """Otwórz natywny dialog wyboru folderu."""
    panel = NSOpenPanel.openPanel()
    panel.setCanChooseFiles_(False)
    panel.setCanChooseDirectories_(True)
    panel.setAllowsMultipleSelection_(False)
    panel.setTitle_("Wybierz folder na transkrypcje")
    
    if panel.runModal() == 1:  # NSModalResponseOK
        url = panel.URLs()[0]
        return url.path()
    return None
```

### 2.3. Zadania
- [x] Dodać metodę `_choose_folder_dialog()` używającą NSOpenPanel ✅ *COMPLETED*
- [x] Zaktualizować `_show_output_config()` z opcją "Wybierz folder..." ✅ *COMPLETED*
- [x] Przetestować na macOS 12+ ✅ *COMPLETED*

---

## 3. UX: Okno ustawień aplikacji

### 3.1. Problem
Użytkownik nie może zmienić folderu docelowego ani innych ustawień po pierwszej konfiguracji (wizard). Obecnie jedyną opcją jest usunięcie `config.json` i ponowne uruchomienie wizarda, co jest złe UX.

### 3.2. Rozwiązanie
Dodać okno ustawień dostępne z menu bar app, które pozwoli na zmianę:
- Folderu docelowego (z graficznym wyborem przez NSOpenPanel)
- Języka transkrypcji
- Innych ustawień konfiguracyjnych

**Plik:** `src/menu_app.py` - dodać menu item "Ustawienia..."
**Nowy plik:** `src/ui/settings_window.py` - okno ustawień (tkinter lub AppKit)

### 3.3. Zadania
- [x] Dodać menu item "Ustawienia..." w `menu_app.py` ✅ *COMPLETED*
- [x] Stworzyć okno ustawień z możliwością zmiany folderu docelowego ✅ *COMPLETED*
- [x] Dodać graficzny wybór folderu (reuse `choose_folder_dialog()`) ✅ *COMPLETED*
- [x] Dodać możliwość zmiany języka transkrypcji ✅ *COMPLETED*
- [x] Dodać możliwość zmiany modelu Whisper ✅ *COMPLETED*
- [x] Zapis zmian do `config.json` ✅ *COMPLETED*
- [ ] Przetestować zmiany ustawień - *wymagane testy manualne*

---

## 4. UX: Możliwość zamknięcia wizarda w każdym kroku

### 4.1. Problem
Użytkownik nie może zamknąć wizarda po pierwszym kroku (welcome). W innych krokach nie ma opcji "Anuluj" lub "Zakończ" - tylko "Wstecz" lub "Pomiń". Jeśli użytkownik chce przerwać konfigurację, musi zamknąć całą aplikację, co jest złe UX.

### 4.2. Rozwiązanie
Dodać opcję "Anuluj" lub "Zakończ" w każdym kroku wizarda (oprócz kroku pobierania, gdzie nie można przerwać).

**Plik:** `src/setup/wizard.py` - wszystkie metody `_show_*()`

### 4.3. Zadania
- [x] Dodać opcję "Anuluj" w każdym kroku wizarda (ok/cancel w rumps.alert) ✅ *COMPLETED*
- [x] Obsłużyć "cancel" w każdym kroku (zwrócić "cancel") ✅ *COMPLETED*
- [x] Dodać możliwość zamknięcia aplikacji po anulowaniu wizarda ✅ *COMPLETED*
- [ ] Przetestować zamknięcie wizarda z różnych kroków - *wymagane testy manualne*

---

## 5. Poprawka UX: Wybór języka w wizardzie

### 5.1. Problem
W kroku wyboru języka (TEST M3.10) użytkownik musi wpisać kod języka ręcznie (pl/en/auto). To złe UX:
- Wymaga znajomości kodów ISO
- Brak dropdown/select - lista jest tylko tekstowa w message
- Nie jest jasne że to język domyślny (można zmienić później)
- Whisper.cpp obsługuje tylko jeden język na raz, ale nie jest to wyjaśnione

### 5.2. Rozwiązanie
Użyć `NSPopUpButton` (dropdown) przez PyObjC z pełnymi nazwami języków.

**Plik:** `src/setup/wizard.py` - metoda `_show_language()`

```python
from AppKit import NSAlert, NSPopUpButton, NSView, NSRect

def _show_language(self) -> str:
    """Konfiguracja języka transkrypcji z dropdown."""
    alert = NSAlert.alloc().init()
    alert.setMessageText_("🗣️ Język transkrypcji")
    alert.setInformativeText_(
        "Wybierz domyślny język dla wszystkich nagrań.\n\n"
        "Możesz zmienić to później w Ustawieniach."
    )
    
    # Utwórz dropdown
    popup = NSPopUpButton.alloc().initWithFrame_(NSRect((0, 0), (200, 24)))
    for code, name in SUPPORTED_LANGUAGES.items():
        popup.addItemWithTitle_(f"{name} ({code})")
    
    # Ustaw aktualną wartość
    current_idx = list(SUPPORTED_LANGUAGES.keys()).index(self.settings.language)
    popup.selectItemAtIndex_(current_idx)
    
    # Dodaj do alertu
    alert.setAccessoryView_(popup)
    alert.addButtonWithTitle_("OK")
    alert.addButtonWithTitle_("Wstecz")
    
    response = alert.runModal()
    if response == 1000:  # OK
        selected_idx = popup.indexOfSelectedItem()
        selected_code = list(SUPPORTED_LANGUAGES.keys())[selected_idx]
        self.settings.language = selected_code
        return "next"
    else:
        return "back"
```

**Uwagi:**
- Whisper.cpp obsługuje tylko jeden język na raz (flaga `-l`)
- Opcja "auto" (automatyczne wykrywanie) jest najlepsza dla większości użytkowników
- To język domyślny - można zmienić później w ustawieniach

### 5.3. Zadania
- [x] Zaimplementować `_show_language()` z NSPopUpButton ✅ *COMPLETED*
- [x] Dodać wyjaśnienie że to język domyślny ✅ *COMPLETED*
- [x] Dodać opcję "Anuluj" w dialogu języka ✅ *COMPLETED*
- [ ] Przetestować na macOS 12+ - *wymagane testy manualne*
- [ ] Zaktualizować TEST M3.10 w dokumentacji - *opcjonalne*

---

## 4. Optymalizacja rozmiaru bundle py2app

### 4.1. Problem

Po Fazie 4 bundle `.app` ma rozmiar **43MB**, podczas gdy cel to **<20MB** (bez modeli whisper). Większy rozmiar wydłuża czas pobierania i zajmuje więcej miejsca na dysku użytkownika.

### 4.2. Analiza rozmiaru

**Obecny stan:**
- Bundle: 43MB
- Cel: <20MB
- Różnica: +23MB do zoptymalizowania

**Główne komponenty bundle:**
- Python runtime (~15-20MB)
- Pakiety Python (rumps, anthropic, mutagen, httpx, etc.)
- PyObjC frameworks (Cocoa, FSEvents)
- MacFSEvents wrapper

### 4.3. Strategia optymalizacji

**Opcje do rozważenia:**

1. **Agresywniejsze excludes:**
   - Sprawdzić które pakiety są faktycznie importowane
   - Usunąć nieużywane moduły z PyObjC
   - Wykluczyć niepotrzebne części bibliotek

2. **Użycie `--optimize=2` w py2app:**
   - Bytecode optimization (już włączone)
   - Możliwe dalsze optymalizacje

3. **Analiza zależności:**
   - Sprawdzić które moduły są faktycznie używane
   - Użyć `py2app` z opcją `--analyze` do analizy importów
   - Usunąć nieużywane zależności z `requirements.txt` jeśli możliwe

4. **Alternatywne podejście:**
   - Rozważyć użycie `pyinstaller` zamiast `py2app` (może być mniejsze)
   - Lub użycie `cx_Freeze` (mniej popularne, ale może być lżejsze)

### 4.4. Zadania

- [ ] Przeanalizować rozmiar komponentów bundle (`du -sh dist/Transrec.app/Contents/Resources/*`)
- [ ] Zidentyfikować największe pakiety
- [ ] Sprawdzić które moduły PyObjC są faktycznie używane
- [ ] Dodać agresywniejsze excludes w `setup_app.py`
- [ ] Przetestować build po optymalizacji
- [ ] Sprawdzić czy wszystkie funkcje działają po optymalizacji
- [ ] Cel: zmniejszyć rozmiar do <20MB

### 4.5. Priorytet

**Średni** - Bundle działa poprawnie, optymalizacja może być wykonana przed Fazą 6 (DMG Release) lub później jako poprawka.

---

## 5. Stabilizacja lub wyłączenie Core ML

### 4.1. Konfigurowalny tryb Core ML / CPU

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

### 4.2. Automatyczne wykrywanie niestabilności Core ML

- **Cel**: Automatyczne przełączenie na CPU, gdy Core ML jest niestabilne.
- **Zakres**:
  - Zliczanie liczby błędów zawierających wzorce typu:
    - `Core ML`, `ggml_metal`, `MTLLibrar`, `tensor API disabled` itp.
  - Prosty mechanizm heurystyczny:
    - jeśli w ostatnich `N` próbach (np. 5) Core ML zawodzi więcej niż `K` razy (np. 3),
      to automatycznie przełącz `WHISPER_COREML_MODE` na `off` (tylko CPU) do czasu restartu.
  - Wyraźny wpis w logu i (opcjonalnie) notyfikacja systemowa o przełączeniu trybu.

### 4.3. Dokumentacja i domyślne ustawienia

- **Zakres**:
  - Zaktualizować:
    - `QUICKSTART.md` – sekcja „Core ML vs CPU (wydajność vs stabilność)”.
    - `Docs/INSTALLATION-GUIDE` – opis konfiguracji `WHISPER_COREML_MODE`.
  - Zaproponować bezpieczny domyślny tryb:
    - `auto` z działającym fallbackiem, ale z jasną instrukcją jak wymusić `off`.


