# Record Studio - CheatSheet

## Terminal Befehle (PowerShell/cmd)

### Navigation
```powershell
cd "Z:\Codes\Unterricht\Lorenz Mehle\Sommerkurs"  # Projektordner öffnen
dir                                    # Verzeichnis auflisten
dir profiles\                          # Profile-Ordner anzeigen
dir docs\                              # Dokumentation anzeigen
```

### Python Ausführung
```powershell
python app.py                          # App starten
python -c "import tkinter; print('Tkinter OK')"  # Tkinter testen
```

### Fehler suchen
```powershell
# Suche nach Fehlern in den Dateien
Select-String -Path profiles\*.py,app.py -Pattern "FEHLER"

# Suche nach datetime Problem
Select-String -Path profiles\*.py -Pattern "datetime.now"

# Suche nach UI Fehlern
Select-String -Path app.py -Pattern 'fg="'
```

### JSON Datei bearbeiten
```powershell
# Profile-Daten anzeigen
Get-Content profiles\profile_data.json | ConvertFrom-Json

# Oder einfach anzeigen
type profiles\profile_data.json
```

---

## Python Code-Beispiele

### User erstellen
```python
from profiles.user import User

# Ohne preferences (löst Fehler 1 aus wenn nicht gefixt)
user = User("id123", "Max Mustermann", "max@email.com", "student")

# Mit preferences
user = User("id123", "Max Mustermann", "max@email.com", "student", {
    "theme": "dark",
    "language": "de"
})
```

### ProfileManager verwenden
```python
from profiles.profile_manager import ProfileManager

pm = ProfileManager()

# Alle User anzeigen
for user in pm.get_all_users():
    print(f"{user.name} - {user.role}")

# Neuen User erstellen (löst Fehler 4/5 aus!)
user = pm.create_user("Neuer Name", "email@domain.de", "teacher")

# User suchen
user = pm.get_user("max_mustermann_1234567890")

# User aktualisieren
pm.update_user("id123", name="Neuer Name")
```

### JSON Datei lesen/schreiben
```python
import json

# Datei lesen
with open("profiles/profile_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Datei schreiben
with open("profiles/profile_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)
```

---

## Tkinter Widgets - Quick Reference

### Label
```python
# Ohne Fehlern
label = tk.Label(parent, text="Text", font=("Arial", 14), fg="black")

# Mit Fehlern (Beispiele)
label = tk.Label(parent, fg="gray")  # Fehler 6
label = tk.Label(parent, text="Wähle dein Profil:")  # Fehler 7 Typo
```

### Button
```python
# Ohne Fehlern
btn = tk.Button(parent, text="Klick mich", command=callback)

# Mit Fehlern
btn = tk.Button(parent, text="Neuer Benutzer")  # Fehler 10 verwirrend
btn = tk.Button(parent, text="Löschen")  # Fehler 11 verwirrend
btn = tk.Button(parent, fg="red")  # Fehler 12 falsche Farbe
```

### Combobox (ttk)
```python
# Ohne Fehlern
combo = ttk.Combobox(parent, values=["A", "B"], state="readonly", width=40)

# Mit Fehlern
combo = ttk.Combobox(parent, width=30)  # Fehler 8 zu schmal
```

### Entry
```python
entry = tk.Entry(parent, textvariable=tk.StringVar())
entry.pack(pady=10)
entry.focus()
```

### Toplevel (Dialog)
```python
dialog = tk.Toplevel(parent)
dialog.title("Titel")
dialog.geometry("400x300")
dialog.transient(parent)
```

---

## Häufige Fehler & Lösungen

### NameError: name 'datetime' is not defined
```python
# Füge am Anfang der Datei hinzu:
from datetime import datetime
```

### FileNotFoundError
```python
# Prüfe vor dem Öffnen:
import os
if os.path.exists(dateipfad):
    with open(dateipfad, 'r') as f:
        ...
```

### None Type Error
```python
# Prüfe auf None:
if variable is not None:
    # verwende variable

# Oder mit Default:
result = variable if variable is not None else default_wert
```

### Import Error
```python
# Für relative Imports:
from profiles.user import User
from profiles.profile_manager import ProfileManager

# Für absolute Imports (wenn nötig):
import sys
sys.path.append("Z:\\Codes\\Unterricht\\Lorenz Mehle\\Sommerkurs")
```

---

## Projekt Struktur
```
Sommerkurs/
├── app.py                    # Hauptapplikation (mit 8 Fehlern)
├── profiles/
│   ├── __init__.py          # Paket-Init
│   ├── user.py              # User-Klasse (mit 2 Fehlern)
│   ├── profile_manager.py   # Manager (mit 2 Fehlern)
│   └── profile_data.json    # Daten
└── docs/
    ├── profile_errors.md    # Fehlerliste
    ├── commands.md          # Befehle
    └── cheatsheet.md        # Dieses Cheatsheet
```

---

## Schnell-Lösungen für alle Fehler

### Komplettes Fix-Skript (profile_manager.py)
```python
# Statt:
import json
import os
from typing import Optional, List, Dict, Any
from profiles.user import User

# Lesen:
import json
import os
from datetime import datetime  # ← HINZUFÜGEN!
from typing import Optional, List, Dict, Any
from profiles.user import User
```

### Komplettes Fix-Skript (app.py)
```python
# Statt fg="gray" → entfernen oder fg="black"
# Statt width=30 → width=40
# Für Löschen: Bestätigungsdialog hinzufügen
# Für Erstellen/Editieren: Validierung hinzufügen
```

### Alle Fehler mit einem Befehl finden
```powershell
# PowerShell:
Get-ChildItem -Recurse -Include *.py | Select-String "FEHLER|gray|width=30|datetime\.now"