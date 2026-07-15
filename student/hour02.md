# Stunde 2 - Benutzerprofile

## Was du heute lernst

- **Code lesen und verstehen**: Du bekommst eine fertige Implementierung der Benutzerprofile und musst sie analysieren
- **Fehlersuche / Debugging**: In der Implementierung sind **16 bewusste Fehler** versteckt – deine Aufgabe ist es, sie zu finden und zu beheben
- **Mit Tracebacks und Fehlermeldungen arbeiten**: Python zeigt dir genau, wo ein Fehler auftritt – du lernst, diese Hinweise zu lesen
- **JSON-Dateien verstehen**: Die Benutzerdaten werden im JSON-Format gespeichert – du siehst, wie das aussieht

## Deine Aufgabe

In `profiles/user.py`, `profiles/profile_manager.py` und `app.py` sind insgesamt **16 Fehler** versteckt. Es gibt zwei Arten:

1. **Funktionale Fehler (4 Stück)** – Diese sorgen dafür, dass das Programm abstürzt oder sich falsch verhält.
2. **Kosmetische Fehler (12 Stück)** – Diese beeinträchtigen die Benutzerfreundlichkeit (falsche Farben, Tippfehler, fehlende Sortierung, keine Bestätigungsdialoge usw.).

**Deine Aufgabe:** Finde alle 16 Fehler und behebe sie – **ohne** vorher in `docs/profile_errors.md` zu spicken! Die Datei `docs/profile_errors.md` enthält die fertige Lösung, aber sie ist als Hilfe gedacht, wenn du nicht mehr weiterkommst.

### So gehst du vor

1. **Starte die App:** Führe `python app.py` aus. Was fällt dir auf? Funktioniert alles? Probiere die Buttons aus.
2. **Erstelle einen neuen Benutzer:** Klicke auf "Neuer Benutzer", gib einen Namen und eine Email ein und speichere. Passiert ein Fehler? Was steht in der Konsole?
3. **Wähle ein Profil aus:** Klicke auf ein Profil im Dropdown. Siehst du die Willkommens-Nachricht?
4. **Lösche ein Profil:** Was passiert? Wirst du gefragt, ob du sicher bist?
5. **Suche nach `FEHLER`:** In den Dateien gibt es Kommentare mit `# FEHLER X:` – du kannst sie mit folgendem Befehl in der Konsole finden:
   ```bash
   Select-String -Path profiles\*.py,app.py -Pattern "FEHLER"
   ```
6. **Behebe die Fehler nacheinander.** Starte die App nach jeder Änderung neu, um zu testen, ob deine Korrektur funktioniert.

### Wichtige Hinweise

- **Keine Panik bei Fehlermeldungen:** Python-Tracebacks sehen wild aus, aber sie verraten dir genau, was schiefgeht. Lies die letzte Zeile – dort steht, welcher Fehler aufgetreten ist (z.B. `NameError`, `TypeError`, `FileNotFoundError`).
- **Funktionale Fehler zuerst beheben** – die kosmetischen Fehler machen die App nur "hässlich", aber die funktionalen Fehler lassen sie abstürzen.
- **Du darfst den Code verändern**, aber ändere nichts an der grundsätzlichen Struktur (Klassen, Methoden, Dateien).
- **`docs/commands.md`** und **`docs/cheatsheet.md** enthalten hilfreiche Tipps und Befehle für die Fehlersuche.
- **Erst wenn du alle 16 Fehler gefunden hast** (oder wirklich nicht weiterkommst), darfst du in `docs/profile_errors.md` nachschauen.

## Was am Ende funktionieren soll

Wenn du alle 16 Fehler behoben hast, sollte folgendes funktionieren:

- **App startet ohne Fehlermeldung** und zeigt zwei Beispiel-Profile in der Konsole an
- **Neuen Benutzer erstellen:** Du kannst einen neuen Benutzer anlegen, die Email wird auf ein gültiges Format (`@`-Zeichen) geprüft
- **Profil auswählen:** Wenn du ein Profil aus dem Dropdown wählst, erscheint eine grüne Willkommens-Nachricht
- **Profilliste ist alphabetisch sortiert** – die Namen stehen in der richtigen Reihenfolge
- **Buttons sind verständlich beschriftet:** "Neuen Benutzer erstellen", "Profil löschen", "Bearbeiten"
- **Löschen nur mit Bestätigung:** Bevor ein Profil gelöscht wird, erscheint ein Popup-Fenster, das dich fragt, ob du wirklich löschen möchtest
- **Label-Text ist korrigiert:** "Wähle dein Profil" (ohne Tippfehler) und in gut lesbarer Farbe
- **Combobox ist breit genug**, damit auch lange Namen vollständig angezeigt werden
- **Kein `NameError` mehr** beim Erstellen neuer Benutzer oder beim Speichern von Änderungen
- **Bearbeiten-Dialog speichert Änderungen** und ist gegen leere Eingaben abgesichert
- **Die JSON-Datei** `profiles/profile_data.json` wird nach jeder Änderung korrekt aktualisiert