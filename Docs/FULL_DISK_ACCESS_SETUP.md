# Konfiguracja Full Disk Access dla Transrec

> **Wersja:** v2.0.0
>
> **Powiązane dokumenty:**
> - [README.md](../README.md) - Przegląd projektu
> - [ARCHITECTURE.md](ARCHITECTURE.md) - Architektura systemu

## Problem

Aplikacja uruchomiona przez `launchd` lub jako `.app` nie ma dostępu do plików na zewnętrznych dyskach (rekordera, karty SD, pendrive) z powodu ograniczeń macOS TCC (Transparency, Consent, and Control).

## Rozwiązanie

Aplikacja `Transrec.app` musi być dodana do **Full Disk Access** w ustawieniach systemowych.

## Instrukcja krok po kroku

### 1. Otwórz ustawienia Full Disk Access

**Opcja A - Przez System Settings:**
- System Settings → Privacy & Security → Full Disk Access

**Opcja B - Skrót:**
```bash
open "x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles"
```

### 2. Dodaj aplikację

1. Kliknij przycisk **"+"** (plus) na dole listy
2. W oknie wyboru pliku:
   - Naciśnij **Cmd + Shift + G** (Go to Folder)
   - Wklej: `~/Applications` lub `/Applications`
   - Naciśnij **Enter**
3. Wybierz **Transrec.app**
4. Kliknij **Open**

### 3. Włącz dostęp

- Upewnij się, że checkbox obok **Transrec.app** jest **zaznaczony**
- Jeśli nie jest, kliknij go aby włączyć

### 4. Zrestartuj aplikację

Po dodaniu do Full Disk Access, aplikacja musi być zrestartowana:

```bash
# Zatrzymaj obecną instancję
pkill -f "Transrec"

# Uruchom ponownie
open ~/Applications/Transrec.app
# lub
open /Applications/Transrec.app
```

### 5. Weryfikacja

Sprawdź logi aby potwierdzić dostęp:

```bash
tail -f ~/Library/Logs/transrec.log
```

Po podłączeniu dysku zewnętrznego z plikami audio powinieneś zobaczyć:
```
✓ Volume detected: /Volumes/NAZWA_DYSKU
📁 Found X new audio file(s)
```

## Troubleshooting

### "Found 0 new audio files" mimo że są nowe pliki

Sprawdź:
1. Czy aplikacja została zrestartowana po dodaniu do Full Disk Access
2. Czy checkbox w Full Disk Access jest zaznaczony
3. Czy dysk jest widoczny w Finderze: `ls /Volumes/`

### Aplikacja nie pojawia się na liście Full Disk Access

1. Znajdź lokalizację aplikacji:
   ```bash
   mdfind -name "Transrec.app"
   ```
2. Dodaj ręcznie przez przycisk "+"

### First-Run Wizard (v2.0.0)

W wersji 2.0.0 aplikacja automatycznie:
1. Wykrywa brak Full Disk Access
2. Wyświetla instrukcję z przyciskiem do System Settings
3. Weryfikuje dostęp po powrocie do aplikacji

## Alternatywa: Uruchamianie z Terminala (Development)

Jeśli nie możesz dodać aplikacji do Full Disk Access, możesz uruchomić z Terminala (który dziedziczy uprawnienia użytkownika):

```bash
cd ~/CODEing/transrec
source venv/bin/activate
python -m src.menu_app
```

**Uwaga:** Ta metoda jest zalecana tylko do development/testowania. Dla normalnego użycia aplikacja powinna działać jako `.app` z Full Disk Access.

## Dlaczego Full Disk Access jest wymagany?

macOS od wersji 10.14 (Mojave) wprowadził TCC - system kontroli dostępu do prywatnych danych użytkownika. Zewnętrzne dyski są traktowane jako "prywatne lokalizacje", więc aplikacje muszą mieć jawną zgodę użytkownika na dostęp.

### Co się stanie bez FDA?

- Aplikacja wykryje podłączenie dysku
- Ale `os.listdir()` zwróci pustą listę plików
- Transkrypcja nie będzie możliwa

---

> **Powiązane dokumenty:**
> - [README.md](../README.md) - Przegląd projektu
> - [ARCHITECTURE.md](ARCHITECTURE.md) - Architektura systemu
> - [PUBLIC-DISTRIBUTION-PLAN.md](PUBLIC-DISTRIBUTION-PLAN.md) - Plan dystrybucji v2.0.0
