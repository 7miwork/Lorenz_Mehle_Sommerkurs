# Hausaufgabe – Wiederholung & Vorbereitung

Da die nächste Stunde erst in einer Woche stattfindet, wiederholst du mit dieser Hausaufgabe die ersten drei Stunden und bereitest dich gedanklich auf den **Character Editor** vor.

Bearbeite die Aufgaben in deinem eigenen Tempo. Notiere dir Fragen, die du in der nächsten Stunde stellen kannst.

---

## Teil 1: Wiederholung Stunde 1 bis 3

### 1.1 Tkinter-Grundgerüst (Stunde 1)

```python
import tkinter as tk
from tkinter import font

class RecordStudioApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Record Studio")
        self.geometry("1280x800")
        self._center_window()
        self._build_ui()
    
    def _center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 1280) // 2
        y = (screen_height - 800) // 2
        self.geometry(f"1280x800+{x}+{y}")
    
    def _build_ui(self):
        heading_font = font.Font(family="Arial", size=24, weight="bold")
        welcome_label = tk.Label(self, text="Record Studio – Willkommen", font=heading_font)
        welcome_label.place(relx=0.5, rely=0.5, anchor="center")

if __name__ == "__main__":
    app = RecordStudioApp()
    app.mainloop()
```

**Fragen:**
1. Was bewirkt `super().__init__()` in der Klasse `RecordStudioApp`?
2. Warum steht `if __name__ == "__main__":` am Ende der Datei?
3. Was ist der Unterschied zwischen `pack()`, `grid()` und `place()`?

---

### 1.2 Benutzerprofile – Debugging (Stunde 2)

In `profiles/user.py`, `profiles/profile_manager.py` und `app.py` waren **16 Fehler** versteckt.

**Fragen:**
1. Welche 4 funktionalen Fehler gab es? Was war ihre Ursache?
2. Welche kosmetischen Fehler sind dir besonders aufgefallen?
3. Wie hast du den `NameError: name 'datetime' is not defined` behoben?
4. Warum sollte man vor dem Löschen eines Profils einen Bestätigungsdialog einbauen?

---

### 1.3 Character Library (Stunde 3)

```python
from datetime import datetime
from typing import Dict, Any

class Character:
    def __init__(self, character_id: str, name: str, image_path: str = "", description: str = ""):
        self.character_id = character_id
        self.name = name
        self.image_path = image_path
        self.description = description
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_id": self.character_id,
            "name": self.name,
            "image_path": self.image_path,
            "description": self.description,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Character":
        return cls(
            character_id=data["character_id"],
            name=data["name"],
            image_path=data.get("image_path", ""),
            description=data.get("description", "")
        )
```

**Aufgaben:**
1. Erkläre in eigenen Worten: Was macht `to_dict()` und wozu braucht man es?
2. Erkläre den Unterschied zwischen einer normalen Methode und einer `@classmethod`.
3. Warum steht `"Character"` in Anführungszeichen beim Rückgabetyp von `from_dict()`?

---

## Teil 2: Vorbereitung Character Editor

In einer der nächsten Stunden bauen wir einen **Character Editor** – ein Fenster, in dem man einen Charakter bearbeiten kann (Name ändern, Bild auswählen, Beschreibung eingeben).

### 2.1 Gedankliche Vorbereitung

Lies dir folgenden Code-Ausschnitt durch und beantworte die Fragen:

```python
class CharacterEditor:
    """Editor-Fenster zum Bearbeiten eines Character-Objekts."""
    
    def __init__(self, parent, character: Character, on_save_callback):
        self.parent = parent
        self.character = character
        self.on_save_callback = on_save_callback
        self._build_ui()
    
    def _build_ui(self):
        # Hier wird später die GUI gebaut
        pass
    
    def _on_save(self):
        # Hier werden später die Änderungen gespeichert
        pass
```

**Fragen:**
1. Was bedeutet der Parameter `on_save_callback`? Warum übergibt man eine Funktion statt direkt zu speichern?
2. Welche GUI-Elemente braucht ein Character-Editor deiner Meinung nach? (z.B. Eingabefelder, Button, ...)
3. Soll der Editor ein eigenes Fenster (`tk.Toplevel`) werden oder in das Hauptfenster eingebaut sein? Begründe.

### 2.2 Code-Snippet erweitern (freiwillig)

Wenn du Lust hast, versuche, die `_build_ui()`-Methode mit Leben zu füllen:

```python
def _build_ui(self):
    # Erstelle ein neues Fenster (Toplevel)
    dialog = tk.Toplevel(self.parent)
    dialog.title("Charakter bearbeiten")
    dialog.geometry("400x300")
    
    # Hier könnten Labels, Entry-Felder und Buttons kommen
    # ...
```

**Zusatzfrage:** Was müsste in `_on_save()` passieren, damit die Änderungen gespeichert werden?

---

## Abgabe

Die Hausaufgabe ist **freiwillig**, aber empfehlenswert. Du musst nichts abgeben – bring deine Fragen und Lösungsvorschläge einfach in die nächste Stunde mit. Wir besprechen die Aufgaben dann gemeinsam.