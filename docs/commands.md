# Commands & Fehler-Suche - Record Studio

## Überblick

Diese Datei erklärt alle wichtigen Befehle und wie man die bewussten Fehler findet.

---

## Wichtige Befehle

### Anwendung starten
```bash
cd "Z:\Codes\Unterricht\Lorenz Mehle\Sommerkurs"
python app.py
```

### Profile testen (ohne GUI)
```bash
python -c "from profiles.profile_manager import ProfileManager; pm = ProfileManager(); print([u.name for u in pm.get_all_users()])"
```

### Neuen User erstellen (löst Fehler aus)
```bash
python -c "from profiles.profile_manager import ProfileManager; pm = ProfileManager(); pm.create_user('Test', 'test@test.com')"
# → Führt zu: NameError: name 'datetime' is not defined
```

---

## Wie man die Fehler findet

### Methode 1: Mit Kommentaren suchen
Suche nach `# FEHLER` in den Dateien:
```bash
grep -n "FEHLER" profiles/*.py app.py
```

### Methode 2: Nach Typologie
| Fehler-Typ | Suchbegriff | Befehl |
|-----------|-----------|--------|
| Import-Fehler | `datetime.now()` | `grep -n "datetime.now()" profiles/*.py` |
| None-Handling | `is not None` | `grep -n "is not None"` |
| UI-Fehler | `fg=` | `grep -n 'fg="'` |
| File-Prüfung | `os.path.exists` | `grep -n "os.path.exists"` |

### Methode 3: Laufzeit-Fehler beobachten
1. Starte die App: `python app.py`
2. Wähle ein Profil aus → Fehlermeldung erscheint
3. Klicke auf "Löschen" → Profil wird ohne Nachfrage gelöscht
4. Erstelle neuen User → NameError in Konsole

---

## Fehler-Übersicht mit Zeilennummern

| Datei | Zeile | Fehler-Nr | Problem |
|-------|------|-----------|---------|
| user.py | 28-30 | 1 | `preferences` ohne None-Check |
| user.py | 32-34 | 2 | `last_login` nicht geladen |
| profile_manager.py | 33-35 | 3 | File nicht geprüft (wird aber behandelt) |
| profile_manager.py | 51 | 4+5 | `datetime.now()` ohne Import |
| app.py | 96 | 6 | Label-Farbe "gray" |
| app.py | 94 | 7 | Typo im Label ("dein") |
| app.py | 107 | 8 | Combobox Breite zu schmal |
| app.py | 118-130 | 9-11 | Verwirrende Button-Texte |
| app.py | 120-123 | 12 | Button-Farbe "red" |
| app.py | 134 | 13 | Keine Sortierung |
| app.py | 166 | 14 | Keine Email-Validierung |
| app.py | 180 | 15 | Kein Bestätigungsdialog |
| app.py | 194-200 | 16 | Keine Validierung beim Editieren |

---

## Lösungshinweise

### Fehler 4+5 beheben (datetime):
In `profile_manager.py` am Anfang hinzufügen:
```python
from datetime import datetime
```

### Fehler 6 beheben (Label-Farbe):
```python
# Statt: fg="gray"
fg="black"  # oder weglassen
```

### Fehler 15 beheben (Bestätigung):
```python
from tkinter import messagebox

# Statt direktem Löschen:
if messagebox.askyesno("Bestätigen", "Wirklich löschen?"):
    self.profile_manager.delete_user(user.user_id)
```

---

## Quick Reference

```bash
# Alle Dateien anzeigen
dir profiles\

# Profile-Daten anzeigen
type profiles\profile_data.json

# Fehler in app.py finden
findstr /n "FEHLER" app.py