# Manual Testing - Faza 7: GUI Settings & Polish

**Data:** 2025-01-XX  
**Wersja:** v2.0.0  
**Tester:** [Nazwa testera]

---

## Checklist testów manualnych

| ID | Test | Kryteria akceptacji | Status | Uwagi |
|----|------|---------------------|--------|-------|
| M7.1 | Date picker - 7 dni | Reset do 7 dni działa | [ ] | |
| M7.2 | Date picker - 30 dni | Reset do 30 dni działa | [ ] | |
| M7.3 | Date picker - custom | Input YYYY-MM-DD działa | [ ] | |
| M7.4 | Date picker - błędna data | Pokazuje komunikat błędu | [ ] | |
| M7.5 | Folder picker - NSOpenPanel | Otwiera dialog systemowy | [ ] | |
| M7.6 | Folder picker - wybór | Zapisuje wybraną ścieżkę | [ ] | |
| M7.7 | Folder picker - anuluj | Wraca do poprzedniego kroku | [ ] | |
| M7.8 | About dialog | Pokazuje wersję i linki | [ ] | |
| M7.9 | About dialog - zamknięcie | OK zamyka dialog | [ ] | |

---

## Procedura testów

### Przygotowanie

1. Zbuduj bundle:
   ```bash
   python setup_app.py py2app
   ```

2. Uruchom aplikację:
   ```bash
   open dist/Transrec.app
   ```

---

### M7.1: Date picker - 7 dni

**Kroki:**
1. Kliknij ikonę Transrec w pasku menu
2. Wybierz "Resetuj pamięć od..."
3. W dialogu wybierz opcję "7 dni"

**Oczekiwany wynik:**
- Pamięć zostaje zresetowana do daty sprzed 7 dni
- Pojawia się notyfikacja z potwierdzeniem

**Status:** [ ] PASS / [ ] FAIL

---

### M7.2: Date picker - 30 dni

**Kroki:**
1. Kliknij ikonę Transrec w pasku menu
2. Wybierz "Resetuj pamięć od..."
3. W dialogu wybierz opcję "30 dni"

**Oczekiwany wynik:**
- Pamięć zostaje zresetowana do daty sprzed 30 dni
- Pojawia się notyfikacja z potwierdzeniem

**Status:** [ ] PASS / [ ] FAIL

---

### M7.3: Date picker - custom data

**Kroki:**
1. Kliknij ikonę Transrec w pasku menu
2. Wybierz "Resetuj pamięć od..."
3. W dialogu wybierz "Inna data..."
4. Wpisz datę w formacie YYYY-MM-DD (np. 2025-12-01)
5. Kliknij OK

**Oczekiwany wynik:**
- Pamięć zostaje zresetowana do podanej daty
- Pojawia się notyfikacja z potwierdzeniem

**Status:** [ ] PASS / [ ] FAIL

---

### M7.4: Date picker - błędna data

**Kroki:**
1. Kliknij ikonę Transrec w pasku menu
2. Wybierz "Resetuj pamięć od..."
3. W dialogu wybierz "Inna data..."
4. Wpisz nieprawidłową datę (np. "invalid-date" lub "2025-13-45")
5. Kliknij OK

**Oczekiwany wynik:**
- Pojawia się komunikat błędu o nieprawidłowym formacie daty
- Pamięć nie zostaje zresetowana

**Status:** [ ] PASS / [ ] FAIL

---

### M7.5: Folder picker - NSOpenPanel

**Kroki:**
1. Uruchom wizard (jeśli nie był uruchomiony, usuń `~/Library/Application Support/Transrec/config.json`)
2. Przejdź do kroku "Folder na transkrypcje"
3. Kliknij "Wybierz folder..."

**Oczekiwany wynik:**
- Otwiera się natywny dialog macOS do wyboru folderu
- Dialog pozwala na przeglądanie folderów

**Status:** [ ] PASS / [ ] FAIL

---

### M7.6: Folder picker - wybór

**Kroki:**
1. W dialogu wyboru folderu (M7.5) wybierz dowolny folder
2. Kliknij "Wybierz"

**Oczekiwany wynik:**
- Wybrana ścieżka zostaje zapisana w ustawieniach
- Wizard przechodzi do następnego kroku

**Status:** [ ] PASS / [ ] FAIL

---

### M7.7: Folder picker - anuluj

**Kroki:**
1. W dialogu wyboru folderu (M7.5) kliknij "Anuluj" lub zamknij dialog
2. Następnie kliknij "Wstecz" w głównym dialogu

**Oczekiwany wynik:**
- Wizard wraca do poprzedniego kroku
- Ustawienia nie zostają zmienione

**Status:** [ ] PASS / [ ] FAIL

---

### M7.8: About dialog

**Kroki:**
1. Kliknij ikonę Transrec w pasku menu
2. Wybierz "O aplikacji..."

**Oczekiwany wynik:**
- Dialog pokazuje:
  - Nazwę aplikacji: "Transrec"
  - Wersję: "v2.0.0"
  - Link do strony: https://transrec.app
  - Link do GitHub: https://github.com/radektar/transrec
  - Informację o licencji: "Open Source (MIT)"

**Status:** [ ] PASS / [ ] FAIL

---

### M7.9: About dialog - zamknięcie

**Kroki:**
1. Otwórz dialog "O aplikacji" (M7.8)
2. Kliknij "OK"

**Oczekiwany wynik:**
- Dialog zamyka się
- Aplikacja działa normalnie

**Status:** [ ] PASS / [ ] FAIL

---

## Podsumowanie

- **Testy wykonane:** 0/9
- **Testy przechodzące:** 0/9
- **Testy nieprzechodzące:** 0/9

## Uwagi ogólne

[Dodaj tutaj wszelkie uwagi dotyczące UX, błędów, sugestii poprawy]

---

## Następne kroki

- [ ] Wszystkie testy przechodzą
- [ ] Zgłoszone błędy naprawione
- [ ] Dokumentacja zaktualizowana

