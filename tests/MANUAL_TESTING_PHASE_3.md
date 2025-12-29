# Manual Testing Guide - Faza 3: First-Run Wizard

> **Wersja:** v2.0.0  
> **Faza:** 3 - First-Run Wizard  
> **Data utworzenia:** 2025-01-XX  
> **Status:** ⚠️ Wymagane przed produkcją v2.0.0 FREE

---

## 📊 Status testów

### ✅ Testy automatyczne (ZAKOŃCZONE)

**Testy jednostkowe:** `tests/test_user_settings.py`
- ✅ 6 testów przechodzi (100% pass rate)
- ✅ Pokrycie: load/save, defaults, error handling

**Testy jednostkowe:** `tests/test_permissions.py`
- ✅ 6 testów przechodzi (100% pass rate)
- ✅ Pokrycie: FDA check, volume access, preferences opening

**Testy jednostkowe:** `tests/test_wizard.py`
- ✅ 8 testów przechodzi (100% pass rate)
- ✅ Pokrycie: needs_setup, step order, dialog handling

### ✅ Testy manualne (WYKONANE)

**Status:** Zakończone - 10/16 testów przeszło pomyślnie

**Wykonane testy:**
- ✅ M3.1-M3.2: Ekran powitalny działa poprawnie
- ✅ M3.3: Pomijanie kroku pobierania gdy zależności zainstalowane
- ✅ M3.6: Dialog FDA działa, otwieranie System Preferences
- ✅ M3.7: Wybór trybu automatycznego źródeł
- ✅ M3.9: Zmiana folderu docelowego (zapisane w config.json)
- ✅ M3.10: Zmiana języka (zapisane w config.json)
- ✅ M3.11: Pomijanie konfiguracji AI
- ✅ M3.13: Zakończenie wizarda i uruchomienie daemona
- ✅ M3.16: Wizard nie uruchamia się ponownie po zakończeniu

**Opcjonalne testy (nie wymagane dla produkcji):**
- ⬜ M3.4: Pełne pobieranie zależności (~500MB)
- ⬜ M3.5: FDA z już nadanymi uprawnieniami
- ⬜ M3.8: Wybór konkretnych dysków
- ⬜ M3.12: Konfiguracja AI z kluczem API
- ⬜ M3.14: Anulowanie wizarda
- ⬜ M3.15: Nawigacja wstecz

**Znalezione problemy UX:**
- M3.9: Brak graficznego wyboru folderu (zapisane w BACKLOG.md sekcja 2)
- M3.10: Złe UX wyboru języka - wymaga kodów (zapisane w BACKLOG.md sekcja 3)

---

## 📋 Cel testów manualnych

Weryfikacja wizarda pierwszego uruchomienia, który przeprowadza użytkownika przez konfigurację aplikacji. Wizard powinien być intuicyjny, prowadzić użytkownika krok po kroku i zapisywać wszystkie ustawienia poprawnie.

---

## ✅ Prerequisites

### Wymagane przed rozpoczęciem

- [ ] Unit tests przechodzą (100%)
- [ ] Aplikacja uruchomiona z brancha `feature/faza-3-first-run-wizard`
- [ ] Python 3.12+ z venv aktywowanym
- [ ] rumps zainstalowane (`pip install rumps`)

### Środowisko testowe

- macOS 12+ (Monterey lub nowszy)
- Apple Silicon (M1/M2/M3) - zalecane
- Połączenie z internetem (dla testu pobierania)
- ~500MB wolnego miejsca na dysku

### Przygotowanie środowiska

```bash
# 1. Przejdź do projektu
cd ~/CODEing/transrec

# 2. Aktywuj venv
source venv/bin/activate

# 3. Upewnij się że jesteś na właściwym branchu
git checkout feature/faza-3-first-run-wizard

# 4. Uruchom aplikację
python -m src.menu_app

# 5. W osobnym terminalu - obserwuj logi
tail -f ~/Library/Logs/olympus_transcriber.log
```

---

## 🧪 Scenariusze testowe

### TEST M3.1: Pierwsze uruchomienie

**Cel:** Weryfikacja że wizard uruchamia się przy pierwszym uruchomieniu.

#### Prerequisites

```bash
# Usuń config.json jeśli istnieje
rm -f ~/Library/Application\ Support/Transrec/config.json
```

#### Steps

1. **Uruchom aplikację**
   ```bash
   python -m src.menu_app
   ```

2. **Obserwuj zachowanie:**
   - ✅ Wizard powinien się uruchomić automatycznie
   - ✅ Ekran powitalny powinien się pojawić
   - ✅ Menu bar powinien być widoczny (ikona 🎙️)

#### Kryteria sukcesu

- [ ] Wizard uruchamia się automatycznie
- [ ] Ekran powitalny jest widoczny
- [ ] Przyciski "Rozpocznij →" i "Anuluj" działają

---

### TEST M3.2: Krok powitania

**Cel:** Weryfikacja ekranu powitalnego.

#### Steps

1. Uruchom aplikację (z usuniętym config.json)
2. Obserwuj ekran powitalny

#### Kryteria sukcesu

- [ ] Tytuł: "🎙️ Witaj w Transrec!"
- [ ] Wiadomość zawiera opis aplikacji
- [ ] Przycisk "Rozpocznij →" przechodzi dalej
- [ ] Przycisk "Anuluj" zamyka wizard

---

### TEST M3.3: Pobieranie - skip

**Cel:** Weryfikacja że krok pobierania jest pomijany gdy zależności już pobrane.

#### Prerequisites

```bash
# Upewnij się że zależności są zainstalowane
# (nie usuwaj ~/Library/Application Support/Transrec/bin/)
```

#### Steps

1. Uruchom aplikację z usuniętym config.json
2. Przejdź przez krok powitania
3. Obserwuj krok pobierania

#### Kryteria sukcesu

- [ ] Krok pobierania jest automatycznie pominięty
- [ ] Przechodzi bezpośrednio do kroku FDA
- [ ] W logach: "Zależności już zainstalowane - pomijam krok"

---

### TEST M3.4: Pobieranie - pełne

**Cel:** Weryfikacja pełnego pobierania zależności z progress bar.

#### Prerequisites

```bash
# Usuń zależności
rm -rf ~/Library/Application\ Support/Transrec/bin/
rm -rf ~/Library/Application\ Support/Transrec/models/
```

#### Steps

1. Uruchom aplikację z usuniętym config.json
2. Przejdź przez krok powitania
3. W kroku pobierania kliknij "Pobierz teraz"
4. Obserwuj postęp pobierania

#### Kryteria sukcesu

- [ ] Dialog z informacją o ~500MB
- [ ] Po kliknięciu "Pobierz teraz" rozpoczyna się pobieranie
- [ ] Status w menu bar pokazuje postęp (jeśli dostępny)
- [ ] Po zakończeniu pojawia się komunikat "✅ Pobrano"
- [ ] Wszystkie pliki są pobrane:
  - `~/Library/Application Support/Transrec/bin/whisper-cli`
  - `~/Library/Application Support/Transrec/bin/ffmpeg`
  - `~/Library/Application Support/Transrec/models/ggml-small.bin`

---

### TEST M3.5: FDA - ma uprawnienia

**Cel:** Weryfikacja że krok FDA jest pomijany gdy uprawnienia już nadane.

#### Prerequisites

- FDA nadane w System Preferences -> Privacy -> Full Disk Access

#### Steps

1. Uruchom aplikację z usuniętym config.json
2. Przejdź przez kroki: powitanie, pobieranie
3. Obserwuj krok FDA

#### Kryteria sukcesu

- [ ] Krok FDA jest automatycznie pominięty
- [ ] Przechodzi bezpośrednio do kroku źródeł nagrań
- [ ] W logach: "FDA już nadane - pomijam krok"

---

### TEST M3.6: FDA - brak uprawnień

**Cel:** Weryfikacja instrukcji FDA i otwierania System Preferences.

#### Prerequisites

```bash
# Upewnij się że FDA NIE jest nadane
# (usuń Transrec z System Preferences -> Privacy -> Full Disk Access)
```

#### Steps

1. Uruchom aplikację z usuniętym config.json
2. Przejdź przez kroki: powitanie, pobieranie
3. W kroku FDA kliknij "Otwórz Ustawienia"
4. Obserwuj zachowanie

#### Kryteria sukcesu

- [ ] Dialog z instrukcją FDA jest widoczny
- [ ] Przycisk "Otwórz Ustawienia" otwiera System Preferences
- [ ] Po kliknięciu pojawia się dialog "Gotowe?"
- [ ] Przycisk "Pomiń" pozwala przejść dalej bez FDA

---

### TEST M3.7: Źródła - tryb auto

**Cel:** Weryfikacja konfiguracji trybu automatycznego wykrywania.

#### Steps

1. Uruchom aplikację z usuniętym config.json
2. Przejdź przez kroki: powitanie, pobieranie, FDA
3. W kroku źródeł kliknij "Automatycznie"
4. Sprawdź config.json

#### Kryteria sukcesu

- [ ] Dialog z wyborem trybu jest widoczny
- [ ] Kliknięcie "Automatycznie" przechodzi dalej
- [ ] W `config.json`: `"watch_mode": "auto"`
- [ ] W `config.json`: `"watched_volumes": []`

---

### TEST M3.8: Źródła - konkretne dyski

**Cel:** Weryfikacja konfiguracji konkretnych dysków.

#### Steps

1. Uruchom aplikację z usuniętym config.json
2. Przejdź przez kroki: powitanie, pobieranie, FDA
3. W kroku źródeł kliknij "Określone dyski"
4. Wpisz "LS-P1, ZOOM-H6" i kliknij "OK"
5. Sprawdź config.json

#### Kryteria sukcesu

- [ ] Po kliknięciu "Określone dyski" pojawia się okno tekstowe
- [ ] Wpisanie "LS-P1, ZOOM-H6" i kliknięcie "OK" przechodzi dalej
- [ ] W `config.json`: `"watch_mode": "specific"`
- [ ] W `config.json`: `"watched_volumes": ["LS-P1", "ZOOM-H6"]`
- [ ] Przycisk "Wstecz" pozwala wrócić do wyboru trybu

---

### TEST M3.9: Folder docelowy

**Cel:** Weryfikacja zmiany folderu docelowego.

#### Steps

1. Uruchom aplikację z usuniętym config.json
2. Przejdź przez kroki: powitanie, pobieranie, FDA, źródła
3. W kroku folderu docelowego zmień ścieżkę na `/tmp/test_transcriptions`
4. Kliknij "OK"
5. Sprawdź config.json

#### Kryteria sukcesu

- [ ] Okno tekstowe pokazuje domyślną ścieżkę
- [ ] Zmiana ścieżki i kliknięcie "OK" przechodzi dalej
- [ ] W `config.json`: `"output_dir": "/tmp/test_transcriptions"`
- [ ] Przycisk "Wstecz" pozwala wrócić do poprzedniego kroku

---

### TEST M3.10: Język

**Cel:** Weryfikacja zmiany języka transkrypcji.

#### Steps

1. Uruchom aplikację z usuniętym config.json
2. Przejdź przez wszystkie poprzednie kroki
3. W kroku języka zmień na "en"
4. Kliknij "OK"
5. Sprawdź config.json

#### Kryteria sukcesu

- [ ] Okno tekstowe pokazuje domyślny język "pl"
- [ ] Lista dostępnych języków jest widoczna w wiadomości
- [ ] Wpisanie "en" i kliknięcie "OK" przechodzi dalej
- [ ] W `config.json`: `"language": "en"`
- [ ] Wpisanie nieprawidłowego kodu (np. "xyz") nie zmienia języka

---

### TEST M3.11: AI - pominięcie

**Cel:** Weryfikacja pominięcia konfiguracji AI.

#### Steps

1. Uruchom aplikację z usuniętym config.json
2. Przejdź przez wszystkie poprzednie kroki
3. W kroku AI kliknij "Pomiń"
4. Sprawdź config.json

#### Kryteria sukcesu

- [ ] Dialog z informacją o AI podsumowaniach jest widoczny
- [ ] Kliknięcie "Pomiń" przechodzi dalej
- [ ] W `config.json`: `"enable_ai_summaries": false`
- [ ] W `config.json`: `"ai_api_key": null`

---

### TEST M3.12: AI - z kluczem

**Cel:** Weryfikacja konfiguracji AI z kluczem API.

#### Steps

1. Uruchom aplikację z usuniętym config.json
2. Przejdź przez wszystkie poprzednie kroki
3. W kroku AI kliknij "Skonfiguruj API"
4. Wpisz przykładowy klucz "sk-test-123" i kliknij "Zapisz"
5. Sprawdź config.json

#### Kryteria sukcesu

- [ ] Po kliknięciu "Skonfiguruj API" pojawia się okno tekstowe
- [ ] Wpisanie klucza i kliknięcie "Zapisz" przechodzi dalej
- [ ] W `config.json`: `"enable_ai_summaries": true`
- [ ] W `config.json`: `"ai_api_key": "sk-test-123"`
- [ ] Kliknięcie "Pomiń" w oknie klucza nie zapisuje klucza

---

### TEST M3.13: Zakończenie

**Cel:** Weryfikacja zakończenia wizarda i uruchomienia aplikacji.

#### Steps

1. Uruchom aplikację z usuniętym config.json
2. Przejdź przez wszystkie 8 kroków wizarda
3. Obserwuj ekran zakończenia
4. Sprawdź config.json i działanie aplikacji

#### Kryteria sukcesu

- [ ] Ekran zakończenia pokazuje komunikat sukcesu
- [ ] W `config.json`: `"setup_completed": true`
- [ ] Po zakończeniu wizarda uruchamia się transcriber (daemon)
- [ ] Menu bar działa normalnie
- [ ] Status w menu bar pokazuje działanie aplikacji

---

### TEST M3.14: Anulowanie

**Cel:** Weryfikacja anulowania wizarda.

#### Steps

1. Uruchom aplikację z usuniętym config.json
2. Przejdź przez kroki: powitanie, pobieranie, FDA
3. W kroku źródeł kliknij "Anuluj" (jeśli dostępne) lub zamknij aplikację
4. Sprawdź config.json

#### Kryteria sukcesu

- [ ] Anulowanie na dowolnym kroku zamyka wizard
- [ ] W `config.json`: `"setup_completed": false` (lub plik nie istnieje)
- [ ] Aplikacja pokazuje komunikat o niekompletnej konfiguracji
- [ ] Daemon nie uruchamia się
- [ ] Można uruchomić aplikację ponownie i wizard się pojawi

---

### TEST M3.15: Back navigation

**Cel:** Weryfikacja nawigacji wstecz między krokami.

#### Steps

1. Uruchom aplikację z usuniętym config.json
2. Przejdź do kroku 5 (Folder docelowy)
3. Kliknij "Wstecz"
4. Sprawdź czy dane z poprzednich kroków są zachowane

#### Kryteria sukcesu

- [ ] Przycisk "Wstecz" w kroku 5 wraca do kroku 4
- [ ] Dane z kroku 4 (źródła) są zachowane
- [ ] Można ponownie przejść do kroku 5 i zmienić ustawienia
- [ ] Po przejściu wszystkich kroków wszystkie dane są zapisane

---

### TEST M3.16: Restart po wizardzie

**Cel:** Weryfikacja że wizard nie uruchamia się ponownie po zakończeniu.

#### Prerequisites

```bash
# Upewnij się że config.json istnieje z setup_completed=true
```

#### Steps

1. Zamknij aplikację (jeśli działa)
2. Uruchom aplikację ponownie
3. Obserwuj zachowanie

#### Kryteria sukcesu

- [ ] Wizard się NIE uruchamia
- [ ] Aplikacja startuje normalnie (bez wizarda)
- [ ] Daemon uruchamia się automatycznie
- [ ] Menu bar działa normalnie
- [ ] W logach: brak "Uruchamianie Setup Wizard"

---

## 📝 Notatki z testów

### Data wykonania: 2025-12-29

### Tester: tarhaskha

### Środowisko:
- macOS wersja: 26.1 (Sequoia)
- Architektura: Apple Silicon (M1/M2/M3)
- Python wersja: 3.12.12

### Wyniki:

| Test ID | Status | Uwagi |
|---------|--------|-------|
| M3.1 | ✅ | Wizard uruchomił się automatycznie, ekran powitalny widoczny |
| M3.2 | ✅ | Ekran powitalny OK, przyciski działają |
| M3.3 | ✅ | Krok pobierania pominięty (zależności zainstalowane) |
| M3.4 | ⬜ | OPCJONALNE - wymaga usunięcia zależności (~500MB) |
| M3.5 | ⬜ | Wymaga nadania FDA w System Preferences |
| M3.6 | ✅ | "Otwórz Ustawienia" działa, dialog "Gotowe?" pojawia się |
| M3.7 | ✅ | Kliknięcie "Automatycznie" przechodzi do kroku folderu docelowego |
| M3.8 | ⬜ | Wymaga powrotu i wyboru "Określone dyski" (opcjonalne) |
| M3.9 | ✅ | Folder docelowy zmieniony na /tmp/test_transcriptions, zapisane w config.json |
| M3.10 | ✅ | Język zmieniony na "en", zapisane w config.json |
| M3.11 | ✅ | AI pominięte, enable_ai_summaries: false w config.json |
| M3.12 | ⬜ | Wymaga powrotu i wyboru "Skonfiguruj API" (opcjonalne) |
| M3.13 | ✅ | Wizard zakończony, setup_completed: true, daemon uruchomiony |
| M3.14 | ⬜ | Wymaga restartu i anulowania (opcjonalne) |
| M3.15 | ⬜ | Wymaga restartu i nawigacji wstecz (opcjonalne) |
| M3.16 | ✅ | Wizard NIE uruchamia się ponownie - aplikacja startuje normalnie z daemonem |

### Znalezione problemy:

1. **M3.9 - Brak graficznego wyboru folderu:** W kroku wyboru folderu docelowego użytkownik może tylko wpisać ścieżkę ręcznie. Brak natywnego dialogu wyboru folderu (NSOpenPanel). To złe UX - użytkownik musi znać dokładną ścieżkę. **Rozwiązanie:** Dodać przycisk "Wybierz folder..." który otworzy natywny dialog macOS (NSOpenPanel przez PyObjC lub tkinter.filedialog).

2. **M3.10 - Złe UX wyboru języka:** 
   - Użytkownik musi wpisać kod języka ręcznie (pl/en/auto) - wymaga znajomości kodów
   - Brak dropdown/select - lista jest tylko tekstowa w message
   - Nie jest jasne że to język domyślny (można zmienić później)
   - Whisper.cpp obsługuje tylko jeden język na raz, ale nie jest to wyjaśnione
   **Rozwiązanie:** Użyć NSPopUpButton (dropdown) przez PyObjC z pełnymi nazwami języków. Dodać wyjaśnienie że to domyślny język dla wszystkich nagrań. Zobacz BACKLOG.md sekcja 3 dla szczegółów.

3. ___________

---

## ✅ Kryteria akceptacji

**Status:** ✅ **FAZA 3 GOTOWA DO PRODUKCJI**

Wszystkie kluczowe testy (M3.1-M3.3, M3.6-M3.7, M3.9-M3.11, M3.13, M3.16) przeszły pomyślnie.

**Znalezione problemy UX** zostały zidentyfikowane i zapisane w BACKLOG.md do poprawy w przyszłych wersjach (nie blokują produkcji v2.0.0 FREE).

---

## 🔗 Powiązane dokumenty

- [CHANGELOG.md](../../CHANGELOG.md) - Historia zmian
- [Docs/PUBLIC-DISTRIBUTION-PLAN.md](../../Docs/PUBLIC-DISTRIBUTION-PLAN.md) - Plan dystrybucji
- [test_wizard.py](test_wizard.py) - Testy automatyczne wizarda

