# Manual Testing Guide - Faza 2: System pobierania zależności

> **Wersja:** v2.0.0  
> **Faza:** 2 - Dependency Downloader  
> **Data utworzenia:** 2025-12-26  
> **Status:** ⚠️ Wymagane przed produkcją v2.0.0 FREE

---

## 📊 Status testów

### ✅ Testy automatyczne (ZAKOŃCZONE)

**Testy jednostkowe:** `tests/test_downloader.py`
- ✅ 20 testów przechodzi (100% pass rate)
- ✅ Pokrycie scenariuszy: sprawdzanie, checksum, network, disk space, pobieranie, retry, progress callback
- ✅ Coverage: 62% (poniżej wymaganego 80%, ale podstawowe funkcje pokryte)

**Testy integracyjne:** `tests/test_downloader_integration.py`
- ⚠️ Wymagają GitHub Release z binaries (obecnie zakomentowane)

### ⚠️ Testy manualne (WYMAGANE PRZED PRODUKCJĄ)

**Status:** Oczekujące na wykonanie

**Uwaga:** Testy manualne są **niezbędne** przed wydaniem v2.0.0 FREE, aby zweryfikować:
- Rzeczywiste pobieranie z GitHub Releases
- Pobieranie dużych plików (model ~466MB)
- Resume download po przerwaniu
- Obsługę błędów w rzeczywistych warunkach
- UX dla użytkownika końcowego

---

## 📋 Cel testów manualnych

Weryfikacja automatycznego pobierania whisper.cpp, ffmpeg i modeli przy pierwszym uruchomieniu aplikacji. Użytkownik nie powinien musieć nic instalować ręcznie.

---

## ✅ Prerequisites

### Wymagane przed rozpoczęciem

- [ ] **GitHub Release utworzony** z binaries (whisper-cli-arm64, ffmpeg-arm64)
- [ ] **Checksums zaktualizowane** w `src/setup/checksums.py`
- [ ] **URLs zaktualizowane** w `src/setup/checksums.py` (wskazują na prawdziwe Release)
- [ ] Unit tests przechodzą (100%)
- [ ] Aplikacja uruchomiona z brancha `feature/faza-2-dependency-downloader`

### Środowisko testowe

- macOS 12+ (Monterey lub nowszy)
- Apple Silicon (M1/M2/M3) - wymagane dla ARM64 binaries
- Python 3.12+ z venv aktywowanym
- Połączenie z internetem (dla większości testów)
- ~500MB wolnego miejsca na dysku

### Przygotowanie środowiska

```bash
# 1. Przejdź do projektu
cd ~/CODEing/transrec

# 2. Aktywuj venv
source venv/bin/activate

# 3. Upewnij się że jesteś na właściwym branchu
git checkout feature/faza-2-dependency-downloader

# 4. Uruchom aplikację
python -m src.menu_app

# 5. W osobnym terminalu - obserwuj logi
tail -f ~/Library/Logs/olympus_transcriber.log
```

---

## 🧪 Scenariusze testowe

### TEST M1: Pierwsze uruchomienie (czysta instalacja)

**Cel:** Weryfikacja pełnego flow pobierania wszystkich zależności od zera.

#### Prerequisites

```bash
# Usuń wszystkie pobrane zależności
rm -rf ~/Library/Application\ Support/Transrec/
```

#### Steps

1. **Uruchom aplikację**
   ```bash
   python -m src.menu_app
   ```

2. **Obserwuj zachowanie aplikacji:**
   - Czy pojawia się dialog pobierania?
   - Czy status w menu bar pokazuje postęp?
   - Czy logi pokazują informacje o pobieraniu?

3. **Poczekaj na zakończenie pobierania:**
   - whisper-cli (~10MB) - powinno zająć ~10-30 sekund
   - ffmpeg (~15MB) - powinno zająć ~15-30 sekund
   - Model small (~466MB) - powinno zająć ~3-10 minut (zależy od prędkości internetu)

4. **Sprawdź czy pliki zostały pobrane:**
   ```bash
   ls -lh ~/Library/Application\ Support/Transrec/bin/
   ls -lh ~/Library/Application\ Support/Transrec/models/
   ```

5. **Sprawdź czy aplikacja działa normalnie:**
   - Czy status zmienił się na "Gotowe"?
   - Czy można uruchomić transkrypcję?

#### Expected Results

| Element | Oczekiwane zachowanie | Status |
|---------|----------------------|--------|
| Dialog pobierania | Pojawia się automatycznie przy starcie | [ ] |
| Postęp w status | Pokazuje "Pobieranie whisper-cli... X%" | [ ] |
| whisper-cli | Pobrany do `bin/whisper-cli`, chmod 755 | [ ] |
| ffmpeg | Pobrany do `bin/ffmpeg`, chmod 755 | [ ] |
| Model | Pobrany do `models/ggml-small.bin` | [ ] |
| Checksum verification | Wszystkie pliki zweryfikowane (SHA256) | [ ] |
| Status końcowy | "Status: Gotowe" | [ ] |
| Aplikacja działa | Można uruchomić transkrypcję | [ ] |

#### Verification Commands

```bash
# Sprawdź czy pliki istnieją i mają właściwe uprawnienia
ls -lh ~/Library/Application\ Support/Transrec/bin/whisper-cli
ls -lh ~/Library/Application\ Support/Transrec/bin/ffmpeg
ls -lh ~/Library/Application\ Support/Transrec/models/ggml-small.bin

# Sprawdź uprawnienia
file ~/Library/Application\ Support/Transrec/bin/whisper-cli
file ~/Library/Application\ Support/Transrec/bin/ffmpeg

# Sprawdź logi pobierania
grep -i "pobieranie\|download\|checksum" ~/Library/Logs/olympus_transcriber.log | tail -20

# Test czy whisper-cli działa
~/Library/Application\ Support/Transrec/bin/whisper-cli -h

# Test czy ffmpeg działa
~/Library/Application\ Support/Transrec/bin/ffmpeg -version
```

#### Uwagi

- Jeśli pobieranie się nie rozpoczyna automatycznie, sprawdź logi czy są jakieś błędy
- Jeśli checksum się nie zgadza, sprawdź czy GitHub Release ma poprawne checksums
- Jeśli timeout, sprawdź prędkość internetu (model może wymagać więcej czasu)

---

### TEST M2: Brak internetu

**Cel:** Weryfikacja obsługi braku połączenia z internetem.

#### Prerequisites

```bash
# Usuń wszystkie pobrane zależności
rm -rf ~/Library/Application\ Support/Transrec/
```

#### Steps

1. **Wyłącz połączenie z internetem:**
   - System Preferences → Network → WiFi: Off
   - Lub: Odłącz kabel Ethernet
   - Lub: Użyj Network Link Conditioner (jeśli zainstalowany)

2. **Uruchom aplikację:**
   ```bash
   python -m src.menu_app
   ```

3. **Obserwuj zachowanie:**
   - Czy pojawia się komunikat o braku internetu?
   - Czy są przyciski "Spróbuj ponownie" i "Zamknij"?
   - Czy status pokazuje odpowiedni komunikat?

4. **Włącz internet ponownie**

5. **Kliknij "Spróbuj ponownie"** (jeśli dostępne) lub uruchom aplikację ponownie

6. **Sprawdź czy pobieranie działa po włączeniu internetu**

#### Expected Results

| Element | Oczekiwane zachowanie | Status |
|---------|----------------------|--------|
| Wykrycie braku internetu | Komunikat "Brak połączenia z internetem" | [ ] |
| Dialog błędu | Pokazuje szczegóły błędu | [ ] |
| Przycisk "Spróbuj ponownie" | Dostępny (jeśli zaimplementowany) | [ ] |
| Przycisk "Zamknij" | Dostępny | [ ] |
| Status | "Status: Brak połączenia" | [ ] |
| Po włączeniu internetu | Pobieranie działa normalnie | [ ] |

#### Verification Commands

```bash
# Sprawdź logi błędów
grep -i "network\|internet\|connection" ~/Library/Logs/olympus_transcriber.log | tail -10

# Sprawdź czy aplikacja nie crashuje
ps aux | grep -i "menu_app\|python.*src.menu_app"
```

#### Uwagi

- Aplikacja nie powinna crashować przy braku internetu
- Komunikat powinien być czytelny dla użytkownika nietechnicznego
- Po włączeniu internetu aplikacja powinna móc kontynuować normalnie

---

### TEST M3: Przerwane pobieranie (resume download)

**Cel:** Weryfikacja wznowienia pobierania po przerwaniu.

#### Prerequisites

```bash
# Usuń wszystkie pobrane zależności
rm -rf ~/Library/Application\ Support/Transrec/
```

#### Steps

1. **Uruchom aplikację i rozpocznij pobieranie:**
   ```bash
   python -m src.menu_app
   ```

2. **Poczekaj aż rozpocznie się pobieranie modelu** (~466MB - najdłuższe)

3. **W trakcie pobierania (np. przy 30-50%) zamknij aplikację:**
   - Cmd+Q lub kliknij "Zakończ" w menu

4. **Sprawdź czy plik tymczasowy istnieje:**
   ```bash
   ls -lh ~/Library/Application\ Support/Transrec/downloads/*.tmp
   ```

5. **Uruchom aplikację ponownie:**
   ```bash
   python -m src.menu_app
   ```

6. **Obserwuj czy pobieranie wznawia się:**
   - Czy zaczyna od początku czy od miejsca przerwania?
   - Czy postęp pokazuje poprawny procent?

7. **Poczekaj na zakończenie**

8. **Sprawdź czy końcowy plik jest poprawny:**
   ```bash
   # Sprawdź checksum
   shasum -a 256 ~/Library/Application\ Support/Transrec/models/ggml-small.bin
   # Porównaj z oczekiwanym checksum z checksums.py
   ```

#### Expected Results

| Element | Oczekiwane zachowanie | Status |
|---------|----------------------|--------|
| Plik tymczasowy | Zostaje w `downloads/` po przerwaniu | [ ] |
| Resume download | Wznawia od miejsca przerwania (Range header) | [ ] |
| Nie zaczyna od nowa | Nie pobiera ponownie już pobranych bajtów | [ ] |
| Postęp | Pokazuje poprawny procent (nie zaczyna od 0%) | [ ] |
| Końcowy plik | Ma poprawny checksum | [ ] |
| Pliki .tmp | Usunięte po sukcesie | [ ] |

#### Verification Commands

```bash
# Sprawdź rozmiar pliku tymczasowego przed wznowieniem
ls -lh ~/Library/Application\ Support/Transrec/downloads/*.tmp

# Sprawdź logi resume
grep -i "resume\|wznawianie\|range" ~/Library/Logs/olympus_transcriber.log | tail -10

# Sprawdź czy plik końcowy jest kompletny
ls -lh ~/Library/Application\ Support/Transrec/models/ggml-small.bin
# Powinien mieć ~466MB

# Sprawdź checksum
python3 << EOF
from src.setup.downloader import DependencyDownloader
from src.setup.checksums import CHECKSUMS
downloader = DependencyDownloader()
model_path = downloader.models_dir / "ggml-small.bin"
expected = CHECKSUMS.get("ggml-small.bin", "")
if expected:
    result = downloader.verify_checksum(model_path, expected)
    print(f"Checksum valid: {result}")
else:
    print("No checksum available for verification")
EOF
```

#### Uwagi

- Resume download wymaga wsparcia Range header przez serwer
- GitHub Releases i HuggingFace wspierają Range header
- Jeśli resume nie działa, sprawdź logi czy Range header jest używany

---

### TEST M4: Brak miejsca na dysku

**Cel:** Weryfikacja obsługi braku miejsca na dysku.

#### Prerequisites

```bash
# Usuń wszystkie pobrane zależności
rm -rf ~/Library/Application\ Support/Transrec/

# UWAGA: Ten test wymaga symulacji braku miejsca
# Możesz użyć Disk Utility lub stworzyć duży plik
```

#### Steps

1. **Symuluj brak miejsca na dysku:**
   ```bash
   # Opcja 1: Stwórz duży plik (ostrożnie!)
   # dd if=/dev/zero of=~/test_fill.dd bs=1m count=10000
   # (To wypełni ~10GB - użyj ostrożnie!)
   
   # Opcja 2: Użyj Disk Utility do zmniejszenia wolnego miejsca
   # (Wymaga uprawnień administratora)
   
   # Opcja 3: Zmodyfikuj kod testowy aby mockować disk_usage
   ```

2. **Sprawdź dostępne miejsce:**
   ```bash
   df -h ~/Library/Application\ Support/Transrec/
   # Powinno być < 500MB wolnego
   ```

3. **Uruchom aplikację:**
   ```bash
   python -m src.menu_app
   ```

4. **Obserwuj zachowanie:**
   - Czy pojawia się komunikat o braku miejsca?
   - Czy pokazuje ile jest dostępne vs wymagane?
   - Czy aplikacja nie crashuje?

#### Expected Results

| Element | Oczekiwane zachowanie | Status |
|---------|----------------------|--------|
| Wykrycie braku miejsca | Przed rozpoczęciem pobierania | [ ] |
| Komunikat błędu | "Brak miejsca na dysku" | [ ] |
| Szczegóły | Pokazuje dostępne vs wymagane (np. "Dostępne: 123MB, Wymagane: 500MB") | [ ] |
| Przycisk "Zamknij" | Dostępny | [ ] |
| Status | "Status: Brak miejsca" | [ ] |
| Aplikacja nie crashuje | Działa normalnie, tylko nie pobiera | [ ] |

#### Verification Commands

```bash
# Sprawdź dostępne miejsce
df -h ~/Library/Application\ Support/Transrec/

# Sprawdź logi błędów
grep -i "disk\|space\|miejsce" ~/Library/Logs/olympus_transcriber.log | tail -10
```

#### Uwagi

- Test może być trudny do wykonania na prawdziwym systemie (wymaga wypełnienia dysku)
- Można użyć mockowania w testach automatycznych jako alternatywa
- Ważne: aplikacja nie powinna próbować pobierać jeśli brak miejsca

---

### TEST M5: Uszkodzony plik (symulacja)

**Cel:** Weryfikacja wykrywania i naprawy uszkodzonych plików.

#### Prerequisites

```bash
# Najpierw pobierz pliki normalnie (TEST M1)
# Następnie uszkodź jeden z plików
```

#### Steps

1. **Pobierz zależności normalnie** (wykonaj TEST M1)

2. **Uszkodź plik whisper-cli:**
   ```bash
   # Dodaj losowe dane do pliku
   echo "corrupted data" >> ~/Library/Application\ Support/Transrec/bin/whisper-cli
   
   # Lub: Usuń część pliku
   # truncate -s -1000 ~/Library/Application\ Support/Transrec/bin/whisper-cli
   ```

3. **Uruchom aplikację ponownie:**
   ```bash
   python -m src.menu_app
   ```

4. **Obserwuj zachowanie:**
   - Czy aplikacja wykrywa błędny checksum?
   - Czy pobiera plik ponownie?
   - Czy po ponownym pobraniu działa?

5. **Sprawdź czy plik został naprawiony:**
   ```bash
   # Sprawdź checksum
   shasum -a 256 ~/Library/Application\ Support/Transrec/bin/whisper-cli
   # Porównaj z oczekiwanym checksum
   ```

#### Expected Results

| Element | Oczekiwane zachowanie | Status |
|---------|----------------------|--------|
| Wykrycie błędnego checksum | Przy starcie aplikacji | [ ] |
| Usunięcie uszkodzonego pliku | Plik zostaje usunięty | [ ] |
| Ponowne pobieranie | Pobiera plik od nowa | [ ] |
| Weryfikacja | Po ponownym pobraniu checksum się zgadza | [ ] |
| Działanie | Aplikacja działa normalnie po naprawie | [ ] |

#### Verification Commands

```bash
# Sprawdź checksum przed i po
shasum -a 256 ~/Library/Application\ Support/Transrec/bin/whisper-cli

# Sprawdź logi wykrywania błędów
grep -i "checksum\|uszkodzony\|corrupted" ~/Library/Logs/olympus_transcriber.log | tail -10

# Test czy whisper-cli działa
~/Library/Application\ Support/Transrec/bin/whisper-cli -h
```

#### Uwagi

- Checksum verification powinna działać przy każdym starcie aplikacji
- Jeśli checksum się nie zgadza, plik powinien być automatycznie pobrany ponownie
- Ważne: aplikacja nie powinna używać uszkodzonego pliku

---

### TEST M6: Wolne połączenie (timeout handling)

**Cel:** Weryfikacja obsługi wolnego połączenia i timeoutów.

#### Prerequisites

```bash
# Usuń wszystkie pobrane zależności
rm -rf ~/Library/Application\ Support/Transrec/

# Zainstaluj Network Link Conditioner (opcjonalnie)
# Lub użyj innego narzędzia do ograniczenia przepustowości
```

#### Steps

1. **Ogranicz przepustowość internetu:**
   ```bash
   # Opcja 1: Network Link Conditioner (jeśli zainstalowany)
   # Ustaw: 100KB/s download
   
   # Opcja 2: Użyj innego narzędzia do throttlingu
   # Lub: Użyj wolnego WiFi hotspot
   ```

2. **Uruchom aplikację:**
   ```bash
   python -m src.menu_app
   ```

3. **Obserwuj pobieranie:**
   - Czy postęp się aktualizuje regularnie?
   - Czy timeout nie występuje przedwcześnie?
   - Czy pobieranie działa stabilnie (wolno ale bez błędów)?

4. **Poczekaj na zakończenie** (może zająć znacznie więcej czasu)

5. **Sprawdź czy wszystkie pliki zostały pobrane poprawnie**

#### Expected Results

| Element | Oczekiwane zachowanie | Status |
|---------|----------------------|--------|
| Pobieranie działa | Wolno ale stabilnie, bez błędów | [ ] |
| Postęp się aktualizuje | Regularnie pokazuje aktualny procent | [ ] |
| Timeout nie występuje | Nie przerywa przedwcześnie (30min limit) | [ ] |
| Wszystkie pliki pobrane | whisper-cli, ffmpeg, model - wszystkie OK | [ ] |
| Checksums poprawne | Wszystkie pliki zweryfikowane | [ ] |

#### Verification Commands

```bash
# Sprawdź logi timeoutów
grep -i "timeout\|slow\|wolno" ~/Library/Logs/olympus_transcriber.log | tail -10

# Sprawdź czy wszystkie pliki są kompletne
ls -lh ~/Library/Application\ Support/Transrec/bin/
ls -lh ~/Library/Application\ Support/Transrec/models/
```

#### Uwagi

- Timeout per chunk: 30 sekund
- Timeout całkowity: 30 minut (dla dużego modelu)
- Przy bardzo wolnym połączeniu (< 50KB/s) może być problematyczne
- Ważne: aplikacja powinna być cierpliwa przy wolnych połączeniach

---

## 📊 Checklist testów manualnych

### Przed rozpoczęciem

- [ ] GitHub Release utworzony z binaries
- [ ] Checksums zaktualizowane w `checksums.py`
- [ ] URLs zaktualizowane w `checksums.py`
- [ ] Unit tests przechodzą (100%)
- [ ] Aplikacja uruchomiona z właściwego brancha
- [ ] Logi włączone (`tail -f`)

### Testy podstawowe (OBOWIĄZKOWE)

- [ ] **TEST M1:** Pierwsze uruchomienie - wszystkie zależności pobrane
- [ ] **TEST M2:** Brak internetu - komunikat błędu
- [ ] **TEST M3:** Przerwane pobieranie - resume download

### Testy zaawansowane (OPCJONALNE)

- [ ] **TEST M4:** Brak miejsca na dysku - komunikat błędu
- [ ] **TEST M5:** Uszkodzony plik - wykrycie i naprawa
- [ ] **TEST M6:** Wolne połączenie - timeout handling

### Po testach

- [ ] Wszystkie logi zapisane
- [ ] Screenshots problemów (jeśli były)
- [ ] Raport utworzony (poniżej)

---

## 📝 Template raportu testowego

```markdown
# Raport testów manualnych - Faza 2

**Data:** YYYY-MM-DD
**Tester:** [Imię]
**Wersja:** feature/faza-2-dependency-downloader
**macOS:** [wersja, np. macOS 14.2.1]
**Architektura:** [arm64 / x86_64]

## Prerequisites

- [ ] GitHub Release utworzony: TAK/NIE
- [ ] Checksums zaktualizowane: TAK/NIE
- [ ] URLs zaktualizowane: TAK/NIE
- [ ] Unit tests: PASS/FAIL

## Wyniki testów

### TEST M1: Pierwsze uruchomienie

| Element | Status | Uwagi |
|---------|--------|-------|
| Dialog pobierania | PASS/FAIL | |
| Postęp w status | PASS/FAIL | |
| whisper-cli pobrany | PASS/FAIL | |
| ffmpeg pobrany | PASS/FAIL | |
| Model pobrany | PASS/FAIL | |
| Checksum verification | PASS/FAIL | |
| Aplikacja działa | PASS/FAIL | |

**Czas pobierania:**
- whisper-cli: [X] sekund
- ffmpeg: [X] sekund
- Model: [X] minut

**Uwagi:** [opcjonalne]

### TEST M2: Brak internetu

| Element | Status | Uwagi |
|---------|--------|-------|
| Wykrycie braku internetu | PASS/FAIL | |
| Komunikat błędu | PASS/FAIL | |
| Przycisk "Spróbuj ponownie" | PASS/FAIL | |
| Po włączeniu internetu | PASS/FAIL | |

**Uwagi:** [opcjonalne]

### TEST M3: Przerwane pobieranie

| Element | Status | Uwagi |
|---------|--------|-------|
| Plik tymczasowy zachowany | PASS/FAIL | |
| Resume download | PASS/FAIL | |
| Nie zaczyna od nowa | PASS/FAIL | |
| Końcowy plik poprawny | PASS/FAIL | |

**Rozmiar przed przerwaniem:** [X] MB
**Rozmiar po wznowieniu:** [X] MB
**Czy zaczęło od nowa:** TAK/NIE

**Uwagi:** [opcjonalne]

### TEST M4: Brak miejsca (opcjonalny)

| Element | Status | Uwagi |
|---------|--------|-------|
| Wykrycie braku miejsca | PASS/FAIL/SKIP | |
| Komunikat błędu | PASS/FAIL/SKIP | |
| Szczegóły (dostępne/wymagane) | PASS/FAIL/SKIP | |

**Uwagi:** [opcjonalne]

### TEST M5: Uszkodzony plik (opcjonalny)

| Element | Status | Uwagi |
|---------|--------|-------|
| Wykrycie błędnego checksum | PASS/FAIL/SKIP | |
| Ponowne pobieranie | PASS/FAIL/SKIP | |
| Naprawa działa | PASS/FAIL/SKIP | |

**Uwagi:** [opcjonalne]

### TEST M6: Wolne połączenie (opcjonalny)

| Element | Status | Uwagi |
|---------|--------|-------|
| Pobieranie działa | PASS/FAIL/SKIP | |
| Postęp się aktualizuje | PASS/FAIL/SKIP | |
| Timeout nie występuje | PASS/FAIL/SKIP | |

**Przepustowość:** [X] KB/s
**Czas pobierania modelu:** [X] minut

**Uwagi:** [opcjonalne]

## Znalezione problemy

### Problem 1: [Tytuł]

**Severity:** Critical/High/Medium/Low

**Steps to reproduce:**
1. [Krok 1]
2. [Krok 2]
3. [Krok 3]

**Expected:** [Oczekiwane zachowanie]

**Actual:** [Rzeczywiste zachowanie]

**Logi:**
```
[Wklej relevant logi]
```

**Screenshots:** [Jeśli dostępne]

---

### Problem 2: [Tytuł]

[Opisz kolejny problem]

---

## Podsumowanie

- **Testy przeszły:** X/6 (M1, M2, M3 obowiązkowe)
- **Krytyczne problemy:** 0
- **Wysokie problemy:** 0
- **Średnie problemy:** 0
- **Niskie problemy:** 0

**Gotowe do merge:** TAK/NIE

**Uwagi końcowe:**
[Opisz ogólne wrażenia, sugestie, etc.]
```

---

## 🐛 Troubleshooting

### Problem: Pobieranie się nie rozpoczyna

**Debug:**
```bash
# Sprawdź logi
grep -i "download\|pobieranie\|check_all" ~/Library/Logs/olympus_transcriber.log | tail -20

# Sprawdź czy check_all() zwraca False
python3 << EOF
from src.setup.downloader import DependencyDownloader
downloader = DependencyDownloader()
print(f"check_all(): {downloader.check_all()}")
print(f"whisper: {downloader.is_whisper_installed()}")
print(f"ffmpeg: {downloader.is_ffmpeg_installed()}")
print(f"model: {downloader.is_model_installed()}")
EOF
```

**Możliwe przyczyny:**
- Zależności już zainstalowane (check_all() zwraca True)
- Błąd w check_network() - brak internetu
- Błąd w check_disk_space() - brak miejsca
- Błąd w kodzie - sprawdź logi

### Problem: Checksum się nie zgadza

**Debug:**
```bash
# Sprawdź checksum pliku
shasum -a 256 ~/Library/Application\ Support/Transrec/bin/whisper-cli

# Porównaj z oczekiwanym w checksums.py
python3 << EOF
from src.setup.checksums import CHECKSUMS
print("Expected checksum:", CHECKSUMS.get("whisper-cli-arm64", "BRAK"))
EOF
```

**Możliwe przyczyny:**
- Błędny checksum w `checksums.py` (nie zaktualizowany po build)
- Uszkodzony plik podczas pobierania
- Błąd w verify_checksum()

### Problem: Resume download nie działa

**Debug:**
```bash
# Sprawdź czy plik .tmp istnieje
ls -lh ~/Library/Application\ Support/Transrec/downloads/*.tmp

# Sprawdź logi resume
grep -i "resume\|range\|wznawianie" ~/Library/Logs/olympus_transcriber.log | tail -20
```

**Możliwe przyczyny:**
- Serwer nie wspiera Range header (GitHub Releases wspiera)
- Plik .tmp został usunięty
- Błąd w logice resume

### Problem: Timeout podczas pobierania

**Debug:**
```bash
# Sprawdź logi timeoutów
grep -i "timeout\|slow\|wolno" ~/Library/Logs/olympus_transcriber.log | tail -20

# Sprawdź prędkość internetu
# (użyj speedtest.net lub innego narzędzia)
```

**Możliwe przyczyny:**
- Zbyt wolne połączenie (< 50KB/s)
- Timeout per chunk (30s) za krótki
- Problem z serwerem

---

## ✅ Kryteria akceptacji

Testy manualne są **PASS** jeśli:

- ✅ TEST M1: Wszystkie zależności pobrane poprawnie
- ✅ TEST M2: Brak internetu obsłużony gracefully
- ✅ TEST M3: Resume download działa poprawnie
- ✅ Brak crashy podczas testów
- ✅ Logi są czytelne i informatywne
- ✅ UX jest zrozumiały dla użytkownika nietechnicznego

**Minimum przed merge:** M1, M2, M3 - wszystkie PASS

---

**Powiązane dokumenty:**
- [PUBLIC-DISTRIBUTION-PLAN.md](../Docs/PUBLIC-DISTRIBUTION-PLAN.md) - Sekcja 5.2 (FAZA 2)
- [TESTING-GUIDE.md](../Docs/TESTING-GUIDE.md) - Ogólny przewodnik testowania
- [Plan Fazy 2](../../.cursor/plans/faza_2_-_dependency_downloader_591ac1ca.plan.md) - Szczegółowy plan implementacji


