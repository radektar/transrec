# Testowanie Daemona Olympus Transcriber

## ✅ Daemon jest uruchomiony!

Daemon został właśnie uruchomiony i działa w tle.

## 🧪 Jak przetestować

### 1. Sprawdź status daemona

```bash
cd ~/CODE/Olympus_transcription
launchctl list | grep olympus-transcriber
```

Powinieneś zobaczyć:
```
3382	0	com.user.olympus-transcriber
```

Gdzie:
- Pierwsza liczba to **PID** (Process ID)
- `0` oznacza że proces działa bez błędów

### 2. Monitoruj logi w czasie rzeczywistym

Otwórz terminal i uruchom:

```bash
tail -f ~/Library/Logs/olympus_transcriber.log
```

Logi powinny pokazywać:
```
✓ All monitors running
⏳ Waiting for recorder connection...
```

### 3. Podłącz recorder Olympus LS-P1

**Co się stanie:**

1. **Powiadomienie macOS** (Notification Center):
   - "Olympus Transcriber"
   - "Recorder wykryty"
   - "Podłączono: LS-P1"

2. **W logach zobaczysz:**
   ```
   🔍 Checking for recorder...
   ✓ Recorder detected: /Volumes/LS-P1
   📅 Looking for files modified after: 2025-11-18 ...
   📁 Found X new audio file(s)
   ```

3. **Jeśli są nowe pliki:**
   - **Kolejne powiadomienie**: "Znaleziono X nowych nagrań"
   - **W logach**: Postęp transkrypcji każdego pliku
   - **Po zakończeniu**: Powiadomienie "Przetworzono: X/Y plików"

### 4. Sprawdź wyniki

Po zakończeniu transkrypcji, sprawdź folder:

```bash
# Dla Obsidian
open ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/Obsidian/11-Transcripts/

# Lub dla standardowego folderu
open ~/Documents/Transcriptions/
```

Pliki będą nazwane: `YYYY-MM-DD_Tytul.md` z pełnym YAML frontmatter.

## 🔧 Zarządzanie Daemonem

### Restart daemona

```bash
cd ~/CODE/Olympus_transcription
bash scripts/restart_daemon.sh
```

lub:

```bash
make reload-daemon
```

### Stop daemona

```bash
make stop-daemon
```

### Start daemona

```bash
launchctl load ~/Library/LaunchAgents/com.user.olympus-transcriber.plist
```

### Status

```bash
make status
```

## 📋 Logi

### Logi aplikacji (główne)
```bash
tail -f ~/Library/Logs/olympus_transcriber.log
```

### Logi LaunchAgent (stdout)
```bash
tail -f /tmp/olympus-transcriber-out.log
```

### Logi błędów
```bash
tail -f /tmp/olympus-transcriber-err.log
```

## 🔔 Konfiguracja Powiadomień

Aby powiadomienia działały poprawnie:

1. Otwórz **System Settings** → **Notifications**
2. Znajdź **Terminal** lub **Script Editor** na liście
3. Upewnij się że są włączone:
   - ✅ Allow notifications
   - ✅ Show in Notification Center
   - ✅ Show on lock screen (opcjonalnie)

## 🐛 Troubleshooting

### Powiadomienia się nie pokazują

1. Sprawdź ustawienia w System Settings → Notifications
2. Sprawdź czy daemon działa: `launchctl list | grep olympus`
3. Zobacz logi: `tail -30 ~/Library/Logs/olympus_transcriber.log`

### Daemon nie działa po restarcie Mac

Daemon powinien uruchomić się automatycznie (ma `RunAtLoad = true`).

Jeśli nie:
```bash
cd ~/CODE/Olympus_transcription
bash scripts/restart_daemon.sh
```

### Recorder nie jest wykrywany

1. Sprawdź czy dyktafon jest zamontowany:
   ```bash
   ls /Volumes/
   ```
   
   Powinien być `/Volumes/LS-P1` lub `/Volumes/OLYMPUS`

2. Sprawdź logi - powinna być linijka:
   ```
   📢 Detected change in /Volumes/...
   ```

### Transkrypcja nie działa

Sprawdź czy whisper.cpp jest zainstalowany:
```bash
ls -la ~/whisper.cpp/main
~/whisper.cpp/main -h
```

Jeśli nie ma, zainstaluj:
```bash
bash scripts/install_whisper_cpp.sh
```

## ✨ Sukces!

Jeśli widzisz:
- ✅ Daemon działa (`launchctl list | grep olympus`)
- ✅ Logi pokazują "Waiting for recorder connection..."
- ✅ Po podłączeniu recordera widzisz powiadomienie
- ✅ Transkrypcje pojawiają się w folderze wyjściowym

**To znaczy że wszystko działa poprawnie!** 🎉

Daemon będzie teraz działał w tle automatycznie i przetwarzał nowe nagrania za każdym razem gdy podłączysz recorder.

