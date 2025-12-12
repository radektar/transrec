# Konfiguracja Full Disk Access dla Olympus Transcriber

## Problem
Daemon uruchomiony przez `launchd` nie ma dostępu do plików na zewnętrznych dyskach (np. rekorder Olympus) z powodu ograniczeń macOS TCC (Transparency, Consent, and Control).

## Rozwiązanie
Aplikacja `Transrec.app` musi być dodana do **Full Disk Access** w ustawieniach systemowych.

## Instrukcja krok po kroku

### 1. Otwórz ustawienia Full Disk Access
- System Settings → Privacy & Security → Full Disk Access
- Lub użyj skrótu: `open "x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles"`

### 2. Dodaj aplikację
- Kliknij przycisk **"+"** (plus) na dole listy
- W oknie wyboru pliku:
  - Naciśnij **Cmd + Shift + G** (Go to Folder)
  - Wklej: `~/Applications`
  - Naciśnij **Enter**
- Wybierz **Transrec.app**
- Kliknij **Open**

### 3. Włącz dostęp
- Upewnij się, że checkbox obok **Transrec.app** jest **zaznaczony**
- Jeśli nie jest, kliknij go aby włączyć

### 4. Zrestartuj aplikację
Po dodaniu do Full Disk Access, aplikacja musi być zrestartowana aby uzyskać nowe uprawnienia:

```bash
# Zatrzymaj obecną instancję (jeśli działa)
pkill -f "Transrec\|python.*src.main"

# Uruchom ponownie
open ~/Applications/Transrec.app
```

### 5. Weryfikacja
Sprawdź logi aby potwierdzić, że aplikacja ma dostęp do rekordera:

```bash
tail -f ~/Library/Logs/olympus_transcriber.log
```

Po podłączeniu rekordera powinieneś zobaczyć:
- `✓ Recorder detected: /Volumes/LS-P1`
- `📁 Found X new audio file(s)` (gdzie X > 0 jeśli są nowe pliki)

Jeśli nadal widzisz `Found 0 new audio file(s)` mimo że są nowe pliki, sprawdź:
- Czy aplikacja została zrestartowana po dodaniu do Full Disk Access
- Czy checkbox w Full Disk Access jest zaznaczony
- Czy rekorder jest podłączony i widoczny w Finderze

## Alternatywa: Uruchamianie z Terminala
Jeśli nie możesz dodać aplikacji do Full Disk Access, możesz uruchomić daemon ręcznie z Terminala (który ma już pełny dostęp):

```bash
cd ~/CODE/Olympus_transcription
venv/bin/python -m src.main
```

Terminal dziedziczy uprawnienia użytkownika, więc nie wymaga dodatkowej konfiguracji TCC.




