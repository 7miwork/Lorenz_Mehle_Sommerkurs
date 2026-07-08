# Fehleranalyse: Benutzer-Profile Implementierung

## Die 5 bewussten Fehler und deren Lösungen

### FEHLER 1: `preferences` könnte None sein (user.py, Zeile 28)

**Problem:** In der `__init__` Methode wird `preferences` direkt zugewiesen, ohne zu prüfen, ob es `None` ist.

```python
# Falsch:
self.preferences = preferences  # Kann None sein!

# Richtig:
self.preferences = preferences if preferences is not None else {}
```

**Auswirkung:** Wenn ein User ohne preferences erstellt wird, würde später beim Zugriff auf `self.preferences` ein `AttributeError` auftreten.

---

### FEHLER 2: `last_login` wird nicht korrekt gesetzt (user.py, in `from_dict`)

**Problem:** Die `last_login` Information wird aus dem Dictionary nicht korrekt übernommen.

```python
# Falsch:
# user.last_login = ...  # Würde aktuelle Zeit setzen statt geladene Zeit

# Richtig:
user.last_login = data.get("last_login")  # Lädt gespeicherte Zeit
```

**Auswirkung:** Beim Laden eines Profils würde die ursprüngliche `last_login` Zeit verloren gehen.

---

### FEHLER 3: FileNotFoundError wird nicht behandelt (profile_manager.py, `_load_profiles`)

**Problem:** Der ursprüngliche Code versuchte, eine Datei zu öffnen, ohne zu prüfen ob sie existiert.

```python
# Falsch:
with open(self.data_file, 'r') as f:  # wirft FileNotFoundError
    ...

# Richtig:
if not os.path.exists(self.data_file):
    self._save_profiles()  # Erstelle leere Datei
    return
```

**Auswirkung:** Das Programm würde abstürzen, wenn die Profil-Datei noch nicht existiert.

---

### FEHLER 4: `datetime` nicht importiert (profile_manager.py, `_save_profiles`)

**Problem:** In der `_save_profiles` Methode wird `datetime.now()` verwendet, aber `datetime` wurde nicht importiert.

```python
# Fehlender Import am Anfang der Datei:
# from datetime import datetime

# Korrektur:
import json
import os
from datetime import datetime  # ← Hinzufügen!
from typing import Optional, List, Dict, Any
from profiles.user import User
```

**Auswirkung:** `NameError: name 'datetime' is not defined` beim Speichern der Profile.

---

### FEHLER 5: `datetime` Import komplett fehlt (profile_manager.py, Kopfzeile)

**Problem:** `datetime` wird in der Datei verwendet (Zeile mit `last_updated`), ist aber nicht importiert.

```python
# Lösung - am Anfang der Datei hinzufügen:
from datetime import datetime
```

**Auswirkung:** `NameError` wenn `_save_profiles()` aufgerufen wird.

---

## Zusammenfassung

Diese Fehler sind typische Anfängerfehler in Python-Anwendungen:

1. **None-Handling** - Vergessen, Standardwerte für optionale Parameter zu setzen
2. **Daten-Serialisierung** - Vergessen, alle Felder beim Laden zu übernehmen
3. **Datei-Existenz prüfen** - Nicht auf Datei-Existenz vor dem Öffnen prüfen
4. **Import-Fehler** - Vergessen, benötigte Module zu importieren
5. **Wiederholte Import-Fehler** - Gleiches wie Fehler 4, aber andersherum

Die Fehler sind bewusst so platziert, dass das Grundprogramm trotzdem funktioniert, wenn die betroffenen Code-Pfade nicht ausgeführt werden.