# Manual Testing Guide - Faza 4: Pakowanie z py2app

> **Wersja:** v2.0.0  
> **Faza:** 4 - Pakowanie z py2app  
> **Data utworzenia:** 2025-12-29  
> **Status:** ⚠️ Wymagane przed produkcją v2.0.0 FREE

---

## 📊 Status testów

### ✅ Testy automatyczne (WYMAGANE)

**Testy jednostkowe:** `tests/test_build.py`
- [ ] Testy konfiguracji setup_app.py
- [ ] Testy skryptu budowania
- [ ] Testy struktury bundle (wymaga buildu)

### ⬜ Testy manualne (WYMAGANE)

**Status:** Do wykonania

**Wymagane testy:**
- [ ] M4.1: Build test
- [ ] M4.2: Launch test
- [ ] M4.3: Menu functionality
- [ ] M4.4: Wizard w bundle
- [ ] M4.5: Dependency download w bundle
- [ ] M4.6: Clean system test (opcjonalny - wymaga innego Maca)
- [ ] M4.7: Size verification

---

## 📋 Cel testów manualnych

Weryfikacja że `.app` bundle działa poprawnie po zbudowaniu z py2app. Bundle powinien działać na czystym macOS bez wymagania instalacji Python lub innych zależności.

---

## ✅ Prerequisites

### Wymagane przed rozpoczęciem

- [ ] Unit tests przechodzą (100%)
- [ ] Aplikacja na branchu `feature/faza-4-py2app`
- [ ] Python 3.12+ z venv aktywowanym
- [ ] py2app zainstalowane (`pip install py2app`)
- [ ] Ikona utworzona (`assets/icon.icns`)

### Środowisko testowe

- macOS 12+ (Monterey lub nowszy)
- Apple Silicon (M1/M2/M3) - wymagane dla buildu
- Połączenie z internetem (dla testu pobierania zależności)
- ~500MB wolnego miejsca na dysku (dla buildu i zależności)

### Przygotowanie środowiska

```bash
# 1. Przejdź do projektu
cd ~/CODEing/transrec

# 2. Aktywuj venv
source venv/bin/activate

# 3. Upewnij się że jesteś na właściwym branchu
git checkout feature/faza-4-py2app

# 4. Zainstaluj py2app jeśli nie zainstalowany
pip install py2app

# 5. Uruchom build
bash scripts/build_app.sh
```

---

## 🧪 Scenariusze testowe

### TEST M4.1: Build test

**Cel:** Sprawdzenie czy build kończy się sukcesem i bundle ma odpowiedni rozmiar.

**Kroki:**
1. Uruchom build script:
   ```bash
   bash scripts/build_app.sh
   ```

2. **SPRAWDŹ:**
   - Czy build kończy się bez błędów
   - Czy `dist/Transrec.app` istnieje
   - Czy rozmiar bundle jest wyświetlony
   - Czy rozmiar <20MB (bez modeli)

3. **SPRAWDŹ strukturę bundle:**
   ```bash
   ls -la dist/Transrec.app/Contents/
   ls -la dist/Transrec.app/Contents/MacOS/
   ls -la dist/Transrec.app/Contents/Resources/
   ```

4. **SPRAWDŹ Info.plist:**
   ```bash
   plutil -p dist/Transrec.app/Contents/Info.plist
   ```
   - Sprawdź czy `CFBundleIdentifier` to `com.transrec.app`
   - Sprawdź czy `LSUIElement` to `true`
   - Sprawdź czy `CFBundleVersion` to `2.0.0`

**Oczekiwany wynik:**
- ✅ Build kończy się sukcesem
- ✅ Bundle istnieje w `dist/Transrec.app`
- ✅ Rozmiar <20MB
- ✅ Wszystkie wymagane pliki istnieją

---

### TEST M4.2: Launch test

**Cel:** Sprawdzenie czy aplikacja uruchamia się z bundle.

**Kroki:**
1. Uruchom bundle:
   ```bash
   open dist/Transrec.app
   ```

2. **OBSERWUJ:**
   - Czy aplikacja się uruchamia (brak błędów w konsoli)
   - Czy ikona pojawia się w menu bar (góra ekranu)
   - Czy nie ma komunikatów o błędach

3. **SPRAWDŹ logi:**
   ```bash
   tail -f ~/Library/Logs/olympus_transcriber.log
   ```
   - Sprawdź czy są błędy importu modułów
   - Sprawdź czy aplikacja startuje poprawnie

4. **KLIKNIJ** ikonę w menu bar
   - Sprawdź czy menu się otwiera

**Oczekiwany wynik:**
- ✅ Aplikacja uruchamia się bez błędów
- ✅ Ikona pojawia się w menu bar
- ✅ Menu działa po kliknięciu
- ✅ Brak błędów w logach

---

### TEST M4.3: Menu functionality

**Cel:** Sprawdzenie czy wszystkie opcje menu działają.

**Kroki:**
1. Uruchom bundle (jeśli nie uruchomiony):
   ```bash
   open dist/Transrec.app
   ```

2. **SPRAWDŹ menu:**
   - Kliknij ikonę w menu bar
   - Sprawdź wszystkie opcje menu:
     - Start / Stop
     - Status
     - Otwórz logi
     - Reset memory
     - Ustawienia
     - Quit

3. **TEST każdej opcji:**
   - **Otwórz logi:** Sprawdź czy otwiera się log w domyślnym edytorze
   - **Reset memory:** Sprawdź czy dialog się pojawia i działa
   - **Ustawienia:** Sprawdź czy okno ustawień się otwiera (jeśli zaimplementowane)
   - **Quit:** Sprawdź czy aplikacja się zamyka

**Oczekiwany wynik:**
- ✅ Wszystkie opcje menu są widoczne
- ✅ Wszystkie opcje działają poprawnie
- ✅ Brak błędów przy klikaniu opcji

---

### TEST M4.4: Wizard w bundle

**Cel:** Sprawdzenie czy wizard działa w bundle.

**Kroki:**
1. **PRZYGOTOWANIE:** Usuń konfigurację (jeśli istnieje):
   ```bash
   rm -f ~/Library/Application\ Support/Transrec/config.json
   ```

2. Uruchom bundle:
   ```bash
   open dist/Transrec.app
   ```

3. **OBSERWUJ:**
   - Czy wizard się uruchamia automatycznie
   - Czy wszystkie kroki wizarda działają
   - Czy można przejść przez cały wizard

4. **PRZEJDŹ przez wizard:**
   - Krok 1: Powitanie
   - Krok 2: Pobieranie (powinno być pominięte jeśli zależności już są)
   - Krok 3: FDA (jeśli nie nadane)
   - Krok 4: Źródła nagrań
   - Krok 5: Folder docelowy
   - Krok 6: Język
   - Krok 7: AI (opcjonalnie)
   - Krok 8: Zakończenie

5. **SPRAWDŹ** czy konfiguracja została zapisana:
   ```bash
   cat ~/Library/Application\ Support/Transrec/config.json
   ```

**Oczekiwany wynik:**
- ✅ Wizard uruchamia się automatycznie
- ✅ Wszystkie kroki działają
- ✅ Konfiguracja jest zapisywana poprawnie
- ✅ Po zakończeniu wizarda aplikacja działa normalnie

---

### TEST M4.5: Dependency download w bundle

**Cel:** Sprawdzenie czy pobieranie zależności działa w bundle.

**Kroki:**
1. **PRZYGOTOWANIE:** Usuń zależności:
   ```bash
   rm -rf ~/Library/Application\ Support/Transrec/bin/
   rm -rf ~/Library/Application\ Support/Transrec/models/
   ```

2. Uruchom bundle:
   ```bash
   open dist/Transrec.app
   ```

3. **OBSERWUJ:**
   - Czy wizard wykrywa brak zależności
   - Czy krok pobierania się uruchamia
   - Czy progress callback działa (jeśli widoczny)
   - Czy pobieranie kończy się sukcesem

4. **SPRAWDŹ** czy zależności zostały pobrane:
   ```bash
   ls -la ~/Library/Application\ Support/Transrec/bin/
   ls -la ~/Library/Application\ Support/Transrec/models/
   ```

**Oczekiwany wynik:**
- ✅ Wizard wykrywa brak zależności
- ✅ Pobieranie działa poprawnie
- ✅ Zależności są pobierane do poprawnej lokalizacji
- ✅ Po pobraniu aplikacja działa normalnie

---

### TEST M4.6: Clean system test

**Cel:** Sprawdzenie czy bundle działa na czystym macOS bez Python.

**UWAGA:** Ten test wymaga innego Maca lub VM bez zainstalowanego Python.

**Kroki:**
1. **PRZYGOTOWANIE:**
   - Skopiuj `dist/Transrec.app` na inny Mac (lub VM)
   - Upewnij się że Python nie jest zainstalowany systemowo

2. Uruchom bundle:
   ```bash
   open Transrec.app
   ```

3. **SPRAWDŹ:**
   - Czy aplikacja się uruchamia
   - Czy wszystkie funkcje działają
   - Czy transkrypcja działa (jeśli recorder podłączony)
   - Czy wizard działa
   - Czy pobieranie zależności działa

**Oczekiwany wynik:**
- ✅ Aplikacja działa bez Python
- ✅ Wszystkie funkcje działają
- ✅ Transkrypcja działa
- ✅ Wizard działa
- ✅ Pobieranie zależności działa

**UWAGA:** Jeśli nie masz dostępu do innego Maca, możesz oznaczyć ten test jako opcjonalny.

---

### TEST M4.7: Size verification

**Cel:** Sprawdzenie rozmiaru bundle i jego komponentów.

**Kroki:**
1. **SPRAWDŹ całkowity rozmiar:**
   ```bash
   du -sh dist/Transrec.app
   ```

2. **SPRAWDŹ rozmiar komponentów:**
   ```bash
   du -sh dist/Transrec.app/Contents/Resources/*
   ```

3. **SPRAWDŹ** czy rozmiar <20MB (bez modeli)

4. **SPRAWDŹ** które komponenty zajmują najwięcej miejsca:
   ```bash
   du -sh dist/Transrec.app/Contents/Resources/* | sort -h
   ```

**Oczekiwany wynik:**
- ✅ Całkowity rozmiar <20MB
- ✅ Python runtime i pakiety są w bundle
- ✅ Brak niepotrzebnych modułów (tkinter, matplotlib, etc.)

---

## 📝 Notatki z testów

### Data wykonania: ___________

### Tester: ___________

### Środowisko:
- macOS wersja: ___________
- Architektura: ___________
- Python wersja: ___________

### Wyniki:

| Test ID | Status | Uwagi |
|---------|--------|-------|
| M4.1 | ⬜ | |
| M4.2 | ⬜ | |
| M4.3 | ⬜ | |
| M4.4 | ⬜ | |
| M4.5 | ⬜ | |
| M4.6 | ⬜ | Opcjonalny |
| M4.7 | ⬜ | |

### Znalezione problemy:

- 

---

## ✅ Checklist przed zakończeniem Fazy 4

- [ ] Build script kończy się sukcesem
- [ ] `.app` uruchamia się bez błędów
- [ ] `.app` rozmiar <20MB
- [ ] Testy automatyczne przechodzą (100% pass)
- [ ] Testy manualne wykonane i udokumentowane
- [ ] Test na czystym macOS (VM lub inny Mac) - opcjonalny
- [ ] Wszystkie funkcje działają z bundled app
- [ ] Wizard działa w bundle
- [ ] Pobieranie zależności działa w bundle
- [ ] Menu działa poprawnie

---

## 🔍 Troubleshooting

### Problem: Build fails with import errors

**Rozwiązanie:**
- Sprawdź czy wszystkie wymagane pakiety są w `packages` w `setup_app.py`
- Sprawdź czy moduły są w `includes` jeśli są importowane dynamicznie

### Problem: Bundle nie uruchamia się

**Rozwiązanie:**
- Sprawdź logi: `~/Library/Logs/olympus_transcriber.log`
- Sprawdź Console.app dla błędów systemowych
- Sprawdź czy wszystkie zależności są w bundle

### Problem: Bundle jest za duży (>20MB)

**Rozwiązanie:**
- Sprawdź `excludes` w `setup_app.py`
- Użyj `--optimize=2` w py2app
- Sprawdź które pakiety zajmują najwięcej miejsca

### Problem: Wizard nie działa w bundle

**Rozwiązanie:**
- Sprawdź czy `src.setup` jest w `includes`
- Sprawdź czy wszystkie moduły wizarda są importowane poprawnie

---

**Powiązane dokumenty:**
- [PUBLIC-DISTRIBUTION-PLAN.md](../Docs/PUBLIC-DISTRIBUTION-PLAN.md) - Szczegółowy plan Fazy 4
- [MANUAL_TESTING_PHASE_3.md](MANUAL_TESTING_PHASE_3.md) - Testy manualne Fazy 3 (wzór)

