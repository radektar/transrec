# Niewykonane testy manualne - v2.0.0

> **Data utworzenia:** 2025-12-26  
> **Status:** Oczekujące na wykonanie  
> **Wersja:** v2.0.0

---

## 📊 Status wykonanych testów

### ✅ Faza 2 - Wykonane
- ✅ **TEST M1:** Pierwsze uruchomienie - wszystkie zależności pobrane
- ✅ **TEST M2:** Brak internetu - komunikat błędu
- ✅ **TEST M3:** Przerwane pobieranie - resume download

### ⏳ Faza 2 - Niewykonane (opcjonalne)
- [ ] **TEST M4:** Brak miejsca na dysku
- [x] **TEST M5:** Uszkodzony plik - wykrycie i naprawa ✅ **PASS** (2025-12-26)
- [ ] **TEST M6:** Wolne połączenie - timeout handling

### ⏳ Faza 1 - Niewykonane (wymagane fizyczne urządzenia)
- [ ] **SCENARIUSZ 1:** Watch mode "auto" - wykrywanie urządzeń
- [ ] **SCENARIUSZ 2:** Watch mode "specific" - tylko wybrane volumeny
- [ ] **SCENARIUSZ 3:** Watch mode "manual" - brak auto-detekcji
- [ ] **SCENARIUSZ 4:** Wykrywanie różnych formatów audio
- [ ] **SCENARIUSZ 5:** Ignorowanie system volumes
- [ ] **SCENARIUSZ 6:** Migracja ze starej konfiguracji
- [ ] **SCENARIUSZ 7:** Głębokość skanowania (max_depth)

---

# FAZA 2: System pobierania zależności - Niewykonane testy

## TEST M4: Brak miejsca na dysku

**Faza:** 2  
**Priorytet:** Niski (opcjonalny)  
**Trudność:** ⚠️ Wysoka

**Cel:** Weryfikacja obsługi braku miejsca na dysku.

### Prerequisites

```bash
# Usuń wszystkie pobrane zależności
rm -rf ~/Library/Application\ Support/Transrec/

# UWAGA: Ten test wymaga symulacji braku miejsca
# Możesz użyć Disk Utility lub stworzyć duży plik
```

### Steps

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

### Expected Results

| Element | Oczekiwane zachowanie | Status |
|---------|----------------------|--------|
| Wykrycie braku miejsca | Przed rozpoczęciem pobierania | [ ] |
| Komunikat błędu | "Brak miejsca na dysku" | [ ] |
| Szczegóły | Pokazuje dostępne vs wymagane (np. "Dostępne: 123MB, Wymagane: 500MB") | [ ] |
| Przycisk "Zamknij" | Dostępny | [ ] |
| Status | "Status: Brak miejsca" | [ ] |
| Aplikacja nie crashuje | Działa normalnie, tylko nie pobiera | [ ] |

### Verification Commands

```bash
# Sprawdź dostępne miejsce
df -h ~/Library/Application\ Support/Transrec/

# Sprawdź logi błędów
grep -i "disk\|space\|miejsce" ~/Library/Logs/olympus_transcriber.log | tail -10
```

### Uwagi

- Test może być trudny do wykonania na prawdziwym systemie (wymaga wypełnienia dysku)
- Można użyć mockowania w testach automatycznych jako alternatywa
- Ważne: aplikacja nie powinna próbować pobierać jeśli brak miejsca

---

## TEST M5: Uszkodzony plik (symulacja) ✅ **WYKONANY**

**Faza:** 2  
**Priorytet:** Wysoki (ważny test)  
**Trudność:** ✅ Łatwa  
**Status:** ✅ PASS (2025-12-26)

**Cel:** Weryfikacja wykrywania i naprawy uszkodzonych plików.

**Wyniki:** Wszystkie elementy przeszły pomyślnie. Checksum verification działa, auto-repair działa automatycznie.  
**Raport:** Zobacz `test_results_m5.md`

### Prerequisites

```bash
# Najpierw pobierz pliki normalnie (TEST M1)
# Następnie uszkodź jeden z plików
```

### Steps

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
   # Porównaj z oczekiwanym checksum z checksums.py
   ```

### Expected Results

| Element | Oczekiwane zachowanie | Status |
|---------|----------------------|--------|
| Wykrycie błędnego checksum | Przy starcie aplikacji | [ ] |
| Usunięcie uszkodzonego pliku | Plik zostaje usunięty | [ ] |
| Ponowne pobieranie | Pobiera plik od nowa | [ ] |
| Weryfikacja | Po ponownym pobraniu checksum się zgadza | [ ] |
| Działanie | Aplikacja działa normalnie po naprawie | [ ] |

### Verification Commands

```bash
# Sprawdź checksum przed i po
shasum -a 256 ~/Library/Application\ Support/Transrec/bin/whisper-cli

# Sprawdź logi wykrywania błędów
grep -i "checksum\|uszkodzony\|corrupted" ~/Library/Logs/olympus_transcriber.log | tail -10

# Test czy whisper-cli działa
~/Library/Application\ Support/Transrec/bin/whisper-cli -h
```

### Uwagi

- Checksum verification powinna działać przy każdym starcie aplikacji
- Jeśli checksum się nie zgadza, plik powinien być automatycznie pobrany ponownie
- Ważne: aplikacja nie powinna używać uszkodzonego pliku

---

## TEST M6: Wolne połączenie (timeout handling)

**Faza:** 2  
**Priorytet:** Średni (opcjonalny)  
**Trudność:** ⚠️ Średnia

**Cel:** Weryfikacja obsługi wolnego połączenia i timeoutów.

### Prerequisites

```bash
# Usuń wszystkie pobrane zależności
rm -rf ~/Library/Application\ Support/Transrec/

# Zainstaluj Network Link Conditioner (opcjonalnie)
# Lub użyj innego narzędzia do ograniczenia przepustowości
```

### Steps

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

### Expected Results

| Element | Oczekiwane zachowanie | Status |
|---------|----------------------|--------|
| Pobieranie działa | Wolno ale stabilnie, bez błędów | [ ] |
| Postęp się aktualizuje | Regularnie pokazuje aktualny procent | [ ] |
| Timeout nie występuje | Nie przerywa przedwcześnie (30min limit) | [ ] |
| Wszystkie pliki pobrane | whisper-cli, ffmpeg, model - wszystkie OK | [ ] |
| Checksums poprawne | Wszystkie pliki zweryfikowane | [ ] |

### Verification Commands

```bash
# Sprawdź logi timeoutów
grep -i "timeout\|slow\|wolno" ~/Library/Logs/olympus_transcriber.log | tail -10

# Sprawdź czy wszystkie pliki są kompletne
ls -lh ~/Library/Application\ Support/Transrec/bin/
ls -lh ~/Library/Application\ Support/Transrec/models/
```

### Uwagi

- Timeout per chunk: 30 sekund
- Timeout całkowity: 30 minut (dla dużego modelu)
- Przy bardzo wolnym połączeniu (< 50KB/s) może być problematyczne
- Ważne: aplikacja powinna być cierpliwa przy wolnych połączeniach

---

# FAZA 1: Uniwersalne źródła nagrań - Niewykonane testy

**Uwaga:** Wszystkie testy z Fazy 1 wymagają fizycznych urządzeń (USB/SD card) z plikami audio.

## SCENARIUSZ 1: Watch Mode "auto" - Automatyczne wykrywanie

**Faza:** 1  
**Priorytet:** Wysoki (podstawowy)  
**Trudność:** ⚠️ Wymaga urządzeń

**Cel:** Weryfikacja automatycznego wykrywania urządzeń z plikami audio.

### Wymagane urządzenia

| Urządzenie | Status | Uwagi |
|------------|--------|-------|
| Olympus LS-P1 | [ ] | Legacy recorder (backward compatibility) |
| Zoom H1/H6 | [ ] | Popularny recorder |
| Generic SD card | [ ] | Z plikami .mp3, .wav |
| USB flash drive | [ ] | Z plikami audio |
| iPhone (jako dysk) | [ ] | Opcjonalnie - DCIM folder |
| Empty USB drive | [ ] | **NIE powinien być wykryty** |

### Setup

```bash
# 1. Uruchom aplikację
cd ~/CODEing/transrec
source venv/bin/activate
python -m src.menu_app

# 2. Ustaw watch_mode na "auto" (jeśli nie jest domyślny)
python3 << EOF
from src.config.settings import UserSettings
settings = UserSettings.load()
settings.watch_mode = "auto"
settings.save()
print("Watch mode set to: auto")
EOF

# 3. Otwórz logi w osobnym terminalu
tail -f ~/Library/Logs/olympus_transcriber.log
```

### Test Steps

Dla każdego urządzenia z plikami audio:

1. **Podłącz urządzenie** (USB/SD card)
2. **Obserwuj logi** - powinno pojawić się:
   ```
   📢 Detected volume activity: /Volumes/[DEVICE_NAME]/...
   ```
3. **Sprawdź czy transkrypcja startuje** - powinien pojawić się proces transkrypcji
4. **Odłącz urządzenie**
5. **Podłącz ponownie** - sprawdź czy nie duplikuje przetwarzania (debouncing)

### Expected Results

| Urządzenie | Wykryte? | Transkrypcja startuje? | Uwagi |
|------------|----------|------------------------|-------|
| Olympus LS-P1 z audio | ✅ | ✅ | Legacy support |
| Zoom H1/H6 z audio | ✅ | ✅ | Nowy recorder |
| SD card z .mp3 | ✅ | ✅ | Generic device |
| USB drive z .wav | ✅ | ✅ | Generic device |
| USB drive BEZ audio | ❌ | ❌ | Powinien być ignorowany |
| iPhone (DCIM) | ⚠️ | ⚠️ | Zależy od zawartości |

### Verification Commands

```bash
# Sprawdź logi wykrywania
grep "Detected volume activity" ~/Library/Logs/olympus_transcriber.log | tail -10

# Sprawdź czy pliki zostały przetworzone
ls -la ~/Documents/Transcriptions/  # lub inny output_dir

# Sprawdź konfigurację
cat ~/Library/Application\ Support/Transrec/config.json | python3 -m json.tool
```

---

## SCENARIUSZ 2: Watch Mode "specific" - Tylko wybrane volumeny

**Faza:** 1  
**Priorytet:** Wysoki  
**Trudność:** ⚠️ Wymaga urządzeń

**Cel:** Weryfikacja przetwarzania tylko określonych urządzeń z listy.

### Setup

```bash
# Ustaw watch_mode na "specific" i dodaj urządzenia do listy
python3 << EOF
from src.config.settings import UserSettings
settings = UserSettings.load()
settings.watch_mode = "specific"
settings.watched_volumes = ["SD_CARD", "USB_DRIVE"]  # Zastąp rzeczywistymi nazwami
settings.save()
print(f"Watch mode: {settings.watch_mode}")
print(f"Watched volumes: {settings.watched_volumes}")
EOF
```

### Test Steps

1. **Podłącz urządzenie Z LISTY** (np. "SD_CARD")
   - ✅ Powinno być wykryte i przetworzone
   
2. **Podłącz urządzenie POZA LISTĄ** (np. "OTHER_DEVICE")
   - ❌ Powinno być zignorowane (brak logów wykrywania)

3. **Dodaj nowe urządzenie do listy** (bez restartu aplikacji)
   ```bash
   # Zmień config i podłącz urządzenie
   # Aplikacja powinna załadować nową konfigurację przy następnym wykryciu
   ```

### Expected Results

| Urządzenie | Na liście? | Wykryte? | Przetworzone? |
|------------|------------|----------|---------------|
| SD_CARD | ✅ | ✅ | ✅ |
| USB_DRIVE | ✅ | ✅ | ✅ |
| OTHER_DEVICE | ❌ | ❌ | ❌ |

---

## SCENARIUSZ 3: Watch Mode "manual" - Brak auto-detekcji

**Faza:** 1  
**Priorytet:** Wysoki  
**Trudność:** ⚠️ Wymaga urządzeń

**Cel:** Weryfikacja że tryb manual nie przetwarza automatycznie.

### Setup

```bash
python3 << EOF
from src.config.settings import UserSettings
settings = UserSettings.load()
settings.watch_mode = "manual"
settings.save()
print("Watch mode set to: manual")
EOF
```

### Test Steps

1. **Podłącz urządzenie z plikami audio**
2. **Obserwuj logi** - NIE powinno być żadnych logów wykrywania
3. **Sprawdź czy transkrypcja NIE startuje automatycznie**

### Expected Results

- ❌ Brak logów "Detected volume activity"
- ❌ Brak automatycznej transkrypcji
- ✅ Aplikacja działa normalnie (menu bar visible)

---

## SCENARIUSZ 4: Wykrywanie różnych formatów audio

**Faza:** 1  
**Priorytet:** Wysoki  
**Trudność:** ⚠️ Wymaga urządzeń

**Cel:** Weryfikacja wykrywania wszystkich obsługiwanych formatów.

### Setup

Przygotuj USB drive z plikami:
- `test.mp3`
- `test.wav`
- `test.m4a`
- `test.flac`
- `test.aac`
- `test.ogg`
- `test.txt` (nie-audio, powinien być ignorowany)

### Test Steps

1. **Podłącz USB drive** (watch_mode = "auto")
2. **Sprawdź logi** - powinny być wykryte wszystkie formaty audio
3. **Sprawdź czy .txt jest ignorowany**

### Expected Results

| Format | Wykryty? | Przetworzony? |
|--------|----------|---------------|
| .mp3 | ✅ | ✅ |
| .wav | ✅ | ✅ |
| .m4a | ✅ | ✅ |
| .flac | ✅ | ✅ |
| .aac | ✅ | ✅ |
| .ogg | ✅ | ✅ |
| .txt | ❌ | ❌ |

---

## SCENARIUSZ 5: Ignorowanie system volumes

**Faza:** 1  
**Priorytet:** Średni  
**Trudność:** ✅ Łatwa

**Cel:** Weryfikacja że systemowe volumeny są ignorowane.

### Test Steps

1. **Sprawdź czy "Macintosh HD" jest ignorowany**
   - Nawet jeśli zawiera pliki audio, nie powinien być przetwarzany

2. **Sprawdź inne system volumes:**
   - Recovery
   - Preboot
   - VM
   - Data

### Expected Results

- ❌ System volumes NIE są wykrywane
- ✅ Logi nie pokazują aktywności dla system volumes

---

## SCENARIUSZ 6: Migracja ze starej konfiguracji

**Faza:** 1  
**Priorytet:** Średni  
**Trudność:** ✅ Łatwa

**Cel:** Weryfikacja migracji z `~/.olympus_transcriber_state.json`.

### Setup

```bash
# 1. Utwórz stary state file
cat > ~/.olympus_transcriber_state.json << EOF
{
  "last_sync": "2024-01-01T12:00:00",
  "transcribe_dir": "$HOME/Documents/OldTranscriptions",
  "language": "en",
  "whisper_model": "medium",
  "recorder_names": ["LS-P1", "OLYMPUS"]
}
EOF

# 2. Usuń nowy config (jeśli istnieje)
rm -f ~/Library/Application\ Support/Transrec/config.json

# 3. Uruchom aplikację - powinna wykonać migrację
```

### Test Steps

1. **Uruchom aplikację**
2. **Sprawdź logi** - powinna być informacja o migracji:
   ```
   INFO - Old configuration detected, performing migration...
   INFO - Migrated output_dir from old config: ...
   INFO - Migrated watched volumes: ['LS-P1', 'OLYMPUS']
   INFO - ✓ Migration completed successfully
   ```

3. **Sprawdź nowy config:**
   ```bash
   cat ~/Library/Application\ Support/Transrec/config.json | python3 -m json.tool
   ```

### Expected Results

- ✅ Migracja wykonana automatycznie
- ✅ `watch_mode` = "specific" (z migrated volumes)
- ✅ `watched_volumes` = ["LS-P1", "OLYMPUS"]
- ✅ `output_dir` = migrated path
- ✅ `setup_completed` = true
- ✅ Nowy config.json utworzony

---

## SCENARIUSZ 7: Głębokość skanowania (max_depth)

**Faza:** 1  
**Priorytet:** Średni  
**Trudność:** ⚠️ Wymaga urządzeń

**Cel:** Weryfikacja że skanowanie jest ograniczone do rozsądnej głębokości.

### Setup

Utwórz strukturę katalogów na USB drive:
```
USB_DRIVE/
├── level1/
│   ├── level2/
│   │   ├── level3/
│   │   │   └── audio.mp3  ✅ Powinien być wykryty (depth 3)
│   │   └── level4/
│   │       └── audio.mp3  ❌ Powinien być ignorowany (depth 4)
```

### Test Steps

1. **Podłącz USB drive**
2. **Sprawdź logi** - tylko pliki do depth 3 powinny być wykryte

### Expected Results

- ✅ Pliki na głębokości ≤ 3 są wykryte
- ❌ Pliki na głębokości > 3 są ignorowane

---

## 📝 Podsumowanie

### Faza 2 - Niewykonane testy opcjonalne
- **TEST M4:** Brak miejsca na dysku (trudny, można pominąć)
- **TEST M5:** Uszkodzony plik (łatwy, **WAŻNY** - rekomendowany)
- **TEST M6:** Wolne połączenie (średni, wymaga narzędzi)

### Faza 1 - Niewykonane testy (wymagane urządzenia)
- **SCENARIUSZ 1-3:** Watch modes (podstawowe)
- **SCENARIUSZ 4:** Formaty audio (podstawowy)
- **SCENARIUSZ 5:** System volumes (łatwy)
- **SCENARIUSZ 6:** Migracja (łatwy)
- **SCENARIUSZ 7:** Max depth (średni)

**Rekomendacja:** Zacząć od TEST M5 (Faza 2) i SCENARIUSZ 5, 6 (Faza 1) - są łatwe i nie wymagają urządzeń.

---

**Powiązane dokumenty:**
- [MANUAL_TESTING_PHASE_1.md](MANUAL_TESTING_PHASE_1.md) - Pełny przewodnik Fazy 1
- [MANUAL_TESTING_PHASE_2.md](MANUAL_TESTING_PHASE_2.md) - Pełny przewodnik Fazy 2

