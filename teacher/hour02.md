# Stunde 2 - Benutzerprofile (Lehrerversion)

Ziel dieser Stunde ist es **nicht**, neuen Code zu schreiben. Stattdessen liest der Schüler eine bestehende Implementierung, versteht die Architektur und findet **16 bewusst eingebaute Fehler** (funktionale und kosmetische) in den Dateien `profiles/user.py`, `profiles/profile_manager.py` und `app.py`.

Die fertige Lösung – also der vollständig korrigierte Code – ist nicht in dieser Lehrerversion enthalten (anders als in Stunde 1), weil der Schüler die Fehler selbstständig finden und beheben soll. Die Fehler sind in den Quelldateien mit `# FEHLER X:`-Kommentaren markiert, und in `docs/profile_errors.md` gibt es eine vollständige Lösungsdokumentation.

---

## Architektur der Benutzerprofile

Die Implementierung folgt einem einfachen **Datenmodell-Manager-Speicher-Prinzip**:

### 1. User-Klasse (`profiles/user.py`)

Die Klasse `User` in `profiles/user.py` modelliert einen einzelnen Benutzer. Sie ist ein reines Datenmodell (keine GUI-Logik):

```python
class User:
    """Repräsentiert einen Benutzer mit Profilinformationen."""
    
    def __init__(self, user_id: str, name: str, email: str, 
                 role: str = "student", preferences: Optional[Dict[str, Any]] = None):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.role = role
        self.created_at = datetime.now().isoformat()
        self.last_login = None
        self.preferences = preferences if preferences is not None else {}
```

**Wichtige Methoden:**
- `to_dict()`: Wandelt das User-Objekt in ein Dictionary um (für JSON-Speicherung)
- `from_dict()`: Klassenmethode, die aus einem Dictionary ein User-Objekt erstellt
- `update_last_login()`: Aktualisiert den Login-Zeitpunkt

### 2. ProfileManager-Klasse (`profiles/profile_manager.py`)

Der `ProfileManager` in `profiles/profile_manager.py` ist für die Verwaltung aller Benutzerprofile zuständig:

```python
class ProfileManager:
    """Verwaltet Benutzerprofile in einer JSON-Datei."""
    
    def __init__(self, data_file: str = "profiles/profile_data.json"):
        self.data_file = data_file
        self.users: Dict[str, User] = {}
        self._load_profiles()
```

**Wichtige Methoden:**
- `_load_profiles()` / `_save_profiles()`: Laden und Speichern der JSON-Datei
- `create_user(name, email, role)`: Erstellt neuen Benutzer mit automatisch generierter ID
- `get_user(user_id)`: Sucht einen Benutzer anhand der ID
- `get_all_users()`: Gibt alle Benutzer als Liste zurück
- `update_user(user_id, **kwargs)`: Aktualisiert Felder eines Benutzers
- `delete_user(user_id)`: Löscht einen Benutzer

### 3. JSON-Persistenz (`profiles/profile_data.json`)

Die Daten werden im JSON-Format gespeichert. Die Datei enthält ein Objekt mit zwei Feldern:
- `"users"`: Eine Liste von Benutzer-Dictionaries
- `"last_updated"`: Zeitstempel der letzten Aktualisierung

Ein Ausschnitt aus der Beispiel-Datei:

```json
{
  "users": [
    {
      "user_id": "max_mustermann_1234567890",
      "name": "Max Mustermann",
      "email": "max@example.com",
      "role": "student",
      "created_at": "2024-01-15T10:30:00",
      "last_login": "2024-07-08T14:20:00",
      "preferences": { "theme": "dark", "language": "de", "auto_save": true }
    }
  ],
  "last_updated": "2024-07-08T15:30:00"
}
```

### 4. Einbindung in die Hauptanwendung (`app.py`)

In `RecordStudioApp.__init__()` wird der ProfileManager initialisiert:

```python
self.profile_manager = ProfileManager()
```

Die App zeigt nach dem Start in der Konsole an, wie viele Profile geladen wurden:

```python
def _show_loaded_profiles(self):
    users = self.profile_manager.get_all_users()
    print(f"Geladene Benutzerprofile: {len(users)}")
    for user in users:
        print(f"  - {user.name} ({user.role})")
```

Die UI bietet:
- Ein Dropdown (`ttk.Combobox`) zur Auswahl eines Profils
- Buttons zum Erstellen, Bearbeiten und Löschen von Profilen
- Ein Status-Label für Rückmeldungen

---

## Die 16 Fehler – didaktische Einordnung

Eine detaillierte Auflistung aller Fehler mit Zeilennummern und Lösungen findest du in **`docs/profile_errors.md`**. Hier geht es nicht um die reine Fehlerliste, sondern um die Einordnung in Lernkategorien:

### Funktionale Fehler (müssen behoben werden, sonst stürzt das Programm ab)

| Fehler | Datei | Problem | Auswirkung |
|--------|-------|---------|------------|
| 1 | user.py | `preferences` wird ohne None-Check zugewiesen | TypeError bei `None`-Preferences |
| 2 | user.py | `last_login` wird in `from_dict` nicht gesetzt | Login-Zeitstempel geht beim Laden verloren |
| 3 | profile_manager.py | Keine Existenz-Prüfung der JSON-Datei vor dem Öffnen | FileNotFoundError |
| 4+5 | profile_manager.py | `datetime.now()` ohne Import von `datetime` | NameError beim Speichern |

### Kosmetische Fehler (beeinträchtigen die Benutzerfreundlichkeit)

| Fehler | Bereich | Problem |
|--------|---------|---------|
| 6 | Label-Farbe | `fg="gray"` ist schwer lesbar |
| 7 | Typo | "Wähle dein Profil" statt "Wähle dein Profil" |
| 8 | Combobox-Breite | `width=30` ist zu schmal |
| 9-12 | Buttons | Verwirrende Texte ("Neuer Benutzer", "Löschen") und falsche Farben |
| 13 | Sortierung | Profilliste ist nicht alphabetisch sortiert |
| 14 | Validierung | Keine Email-Format-Prüfung im Create-Dialog |
| 15 | Bestätigung | Löschen ohne Rückfrage |
| 16 | Validierung | Keine Eingabe-Prüfung im Edit-Dialog |

**Zählung beachten:** In `docs/profile_errors.md` sind die Fehler 4 und 5 zusammengefasst, weil sie die gleiche Ursache haben (fehlender datetime-Import). Tatsächlich sind es 16 einzelne Probleme, die in den Dateien mit `# FEHLER X:` markiert sind.

---

## Hilfsmittel für die Fehlersuche

### `docs/commands.md`

Diese Datei enthält:

- **Konsolenbefehle** zum Starten der App und Testen der Profile
- **Drei Methoden** zum Finden der Fehler:
  1. Suche nach `# FEHLER`-Kommentaren mit `grep` / `Select-String`
  2. Suche nach bestimmten Mustern (`datetime.now()`, `fg="`, etc.)
  3. Laufzeit-Tests: App starten und Aktionen ausführen
- **Fehler-Übersichtstabelle** mit Datei, Zeile, Fehlernummer und Problembeschreibung
- **Lösungshinweise** für die wichtigsten Fehler

### `docs/cheatsheet.md`

Diese Datei enthält:

- **Terminal-Befehle** für PowerShell und cmd
- **Python-Codebeispiele** für die Arbeit mit User und ProfileManager
- **Tkinter-Widget-Referenz** mit korrekten und fehlerhaften Beispielen
- **Häufige Fehler und Lösungen** (NameError, FileNotFoundError, NoneTypeError, ImportError)
- **Schnell-Lösungen** für alle Fehler

---

## Warum diese Architektur?

### Datenmodell (User) getrennt von Manager (ProfileManager)

- **Single Responsibility Principle**: Die `User`-Klasse kümmert sich nur um die Daten eines Benutzers.
- Der `ProfileManager` übernimmt die Verwaltung (Speichern, Laden, Suchen).
- Änderungen am Datenmodell (z.B. neues Attribut) erfordern keine Änderungen an der Logik des Managers.

### JSON als Speicherformat

- **Menschlich lesbar**: Die Datei kann im Editor geöffnet und verstanden werden.
- **Einfach zu debuggen**: Fehler in der JSON-Struktur sind leicht zu erkennen.
- **Portabel**: Keine Datenbank-Abhängigkeit, reines Python.

### Fehler als Lernwerkzeug

- Bewusst eingebaute Fehler **simulieren reale Programmierfehler**.
- Der Schüler lernt, mit **Tracebacks umzugehen** und systematisch nach Fehlern zu suchen.
- Die Fehler decken verschiedene Kategorien ab: Import-Fehler, None-Checks, UI-Fehler, Validierung.

---

## Mögliche Stolperfallen beim Schüler

1. **NameError bei `datetime`**
   - Der Schüler startet die App, erstellt einen neuen Benutzer und bekommt `NameError: name 'datetime' is not defined`.
   - Verwechslungsgefahr: `datetime` ist sowohl das Modul als auch die Klasse. Der Import `from datetime import datetime` ist nötig.

2. **Verwechslung von `user_id` und `name`**
   - In der UI wird der Anzeigename `"Max Mustermann (student)"` verwendet, intern wird aber mit der `user_id` gearbeitet.
   - Der Schüler könnte versehentlich versuchen, einen User über seinen Namen zu löschen/suchen.

3. **JSON-Datei manuell kaputt editieren**
   - Der Schüler öffnet `profile_data.json` im Editor und löscht versehentlich ein Komma oder eine Klammer.
   - Die App startet dann mit leerer Benutzerliste, weil `json.JSONDecodeError` abgefangen wird (aber ohne Fehlermeldung).

4. **Falsche Arbeitsreihenfolge**
   - Der Schüler behebt zuerst alle kosmetischen Fehler (weil sie leichter zu finden sind) und wundert sich dann, dass die App immer noch abstürzt.
   - **Didaktischer Hinweis**: Funktionale Fehler (Import, None-Check) zuerst beheben!

5. **`grep`/`Select-String` nicht installiert oder unbekannt**
   - Auf Windows-Systemen ist `findstr` verfügbar, aber `Select-String` (PowerShell) oder `grep` (falls nicht installiert) könnten unbekannt sein.
   - Die `docs/commands.md` enthält PowerShell-spezifische Befehle.

6. **Unterschied zwischen `tkinter.messagebox` und `messagebox`**
   - Für Fehler 15 (Bestätigungsdialog) muss `from tkinter import messagebox` importiert werden.
   - Schüler könnten `import messagebox` versuchen, was nicht funktioniert.

7. **`fg` vs `foreground` / `bg` vs `background`**
   - Tkinter erlaubt beide Schreibweisen, aber in der Codebasis wird `fg`/`bg` verwendet.
   - Schüler könnten versehentlich `foreground="black"` schreiben, was ebenfalls funktioniert, aber inkonsistent wäre.

---

## Mögliche Erweiterungen (über den Unterricht hinaus)

- **Passwort-Schutz**: Ein Passwort-Feld in der User-Klasse und eine Login-Abfrage
- **Profil-Bild**: Ein Bild-Pfad als Attribut, das im UI angezeigt wird
- **Letzte Projekte**: Eine Liste von `last_projects` im User-Profil
- **Export/Import**: Profile als einzelne JSON-Dateien exportieren und importieren
- **Such-Funktion**: Profile nach Namen oder Email durchsuchen
- **Batch-Operationen**: Mehrere Profile auf einmal löschen oder bearbeiten
- **Datenbank-Backend**: Statt JSON eine SQLite-Datenbank verwenden

---

## Prüfungen

### Grundlegendes Verständnis
- [ ] Schüler kann die drei Dateien (`user.py`, `profile_manager.py`, `app.py`) und ihre Aufgaben erklären
- [ ] Schüler versteht den Unterschied zwischen `user_id` und `name`
- [ ] Schüler kann das JSON-Format der Profildaten erklären
- [ ] Schüler hat `docs/profile_errors.md` nach eigenem Lösungsversuch gelesen

### App-Funktionalität nach Fehlerbehebung
- [ ] App startet ohne Fehlermeldung
- [ ] Geladene Profile werden in der Konsole angezeigt (2 Beispiel-User sichtbar)
- [ ] Neuen Benutzer erstellen funktioniert ohne `NameError`
- [ ] Neuen Benutzer erstellen prüft Email-Format (`@`-Zeichen)
- [ ] Profil auswählen und Willkommens-Nachricht erscheint
- [ ] Profilliste ist alphabetisch sortiert
- [ ] Button-Texte sind eindeutig formuliert ("Neuen Benutzer erstellen", "Profil löschen")
- [ ] Bearbeiten-Button hat korrekte Farbe (blau oder Standard, nicht rot)
- [ ] Label hat lesbare Textfarbe (schwarz, nicht grau)
- [ ] Typo "dein" ist korrigiert zu "dein"
- [ ] Combobox ist breit genug (width=40 oder breiter)
- [ ] Löschen fragt vorher mit einem Bestätigungsdialog (`messagebox.askyesno`)
- [ ] Bearbeiten-Dialog speichert Änderungen korrekt (auch bei leeren Feldern abgesichert)
- [ ] Nach dem Löschen wird die Profilliste aktualisiert
- [ ] `profile_data.json` wird nach jeder Änderung korrekt aktualisiert
- [ ] Alle `# FEHLER`-Kommentare sind entfernt oder als "erledigt" markiert