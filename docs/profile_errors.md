# Fehleranalyse: Benutzer-Profile Implementierung

## Die 16 bewussten Fehler und deren Lösungen

### Funktionale Fehler (5)

### FEHLER 1: `preferences` könnte None sein (user.py, Zeile 28)

**Problem:** In der `__init__` Methode wird `preferences` direkt zugewiesen, ohne zu prüfen, ob es `None` ist.

```python
# Richtig:
self.preferences = preferences if preferences is not None else {}
```

---

### FEHLER 2: `last_login` wird nicht korrekt gesetzt (user.py, in `from_dict`)

**Problem:** Die `last_login` Information wird aus dem Dictionary nicht korrekt übernommen.

```python
# Richtig:
user.last_login = data.get("last_login")
```

---

### FEHLER 3: FileNotFoundError wird nicht behandelt (profile_manager.py)

**Problem:** Datei wird geöffnet ohne Existenz-Prüfung.

```python
# Richtig:
if not os.path.exists(self.data_file):
    self._save_profiles()
    return
```

---

### FEHLER 4/5: `datetime` nicht importiert (profile_manager.py, Zeile 51)

**Problem:** `datetime.now()` wird verwendet, aber `datetime` nicht importiert.

```python
# Lösung am Anfang der Datei:
from datetime import datetime
```

---

### Kosmetische Fehler (3)

### FEHLER 6: Label-Farbe ist schwer lesbar (app.py)

```python
# Falsch:
fg="gray"
# Richtig:
fg="black"  # oder weglassen
```

---

### FEHLER 7/8: Typo und Layout (app.py)

```python
# Falsch:
text="Wähle dein Profil:"  # Typo ("dein" → "dein")
width=30  # Zu schmal
# Richtig:
text="Wähle dein Profil:"  # Korrektur
width=40  # Breiter
```

---

### FEHLER 9/12: Button-Probleme (app.py)

```python
# Falsch:
fg="red"  # Bearbeiten-Button sollte nicht rot sein
# Richtig:
fg="blue"  # oder Standardfarbe
```

---

### FEHLER 10/11: Verwirrende Button-Texte (app.py)

```python
# Falsch:
text="Neuer Benutzer"  # Unklar
text="Löschen"  # Was wird gelöscht?
# Richtig:
text="Neuen Benutzer erstellen"
text="Profil löschen"
```

---

### FEHLER 13: Keine Sortierung (app.py)

```python
# Falsch:
return [f"{u.name} ({u.role})" for u in users]
# Richtig:
return [f"{u.name} ({u.role})" for u in sorted(users, key=lambda x: x.name)]
```

---

### FEHLER 14/16: Fehlende Validierung (app.py)

**Create Dialog:** Email-Format wird nicht geprüft.
**Edit Dialog:** Eingaben werden ohne Validierung gespeichert.

---

### FEHLER 15: Fehlender Bestätigungsdialog (app.py)

```python
# Falsch:
self.profile_manager.delete_user(user.user_id)  # Direkt löschen
# Richtig:
if messagebox.askyesno("Bestätigen", "Profil wirklich löschen?"):
    self.profile_manager.delete_user(user.user_id)
```

---

## Zusammenfassung

Die Fehler sind bewusst so platziert, dass das Grundprogramm trotzdem funktioniert. Um die Fehler zu beheben, einfach die Kommentare in den jeweiligen Dateien lesen und die korrigierten Versionen übernehmen.