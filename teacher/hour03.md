# Stunde 3 - Character Library: Datenmodell und Verwaltung (Lehrerversion)

In dieser Stunde baut der Schüler eine **Character Library** – eine Verwaltungskomponente für animierte Sprecher-Charaktere. Anders als in Stunde 2 (Debugging) schreibt der Schüler hier **selbstständig Code** nach Anleitung, analog zum Aufbau aus Stunde 1.

Im Gegensatz zu den Benutzerprofilen (Stunde 2) enthält der Code, den der Schüler schreibt, **keine absichtlichen Fehler**. Allerdings sind in der fertigen Musterlösung (in `core/character.py` und `core/character_library.py`) **3 kleine Fehler** eingebaut, die der Schüler als Bonus-Aufgabe finden und beheben kann (siehe **`docs/character_errors.md`**). Bitte dem Schüler erst zeigen, nachdem er selbst versucht hat, die Fehler zu finden.

---

## app.py (Erweiterung)

Die `app.py` wird in dieser Stunde nur minimal erweitert. Der Fokus liegt auf den beiden neuen Dateien `core/character.py` und `core/character_library.py`.

```python
# Record Studio - Hauptanwendung
# Diese Datei startet das Tkinter-Fenster der Anwendung.
# Inkludiert Benutzer-Profile Funktionalität

# Importiert die Tkinter-Bibliothek für GUI-Fenster
import tkinter as tk
# Importiert das font-Modul für Schriftarten-Einstellungen
from tkinter import font, ttk

# Importiert den ProfileManager für Benutzerprofile
from profiles.profile_manager import ProfileManager

# Importiert die CharacterLibrary für Charakter-Verwaltung
from core.character_library import CharacterLibrary


class RecordStudioApp(tk.Tk):
    """Hauptklasse der Record Studio Anwendung.
    
    Erbt von tk.Tk, um das Hauptfenster zu definieren.
    In zukünftigen Stunden können hier weitere Module (Frames)
    eingehängt werden.
    """
    
    def __init__(self):
        # Ruft den Konstruktor der Elternklasse (tk.Tk) auf
        super().__init__()
        
        # Initialisiert den Profil-Manager
        self.profile_manager = ProfileManager()
        
        # Initialisiert die Charakter-Bibliothek
        self.character_library = CharacterLibrary()
        
        # Setzt den Titel des Fensters (erscheint in der Titelleiste)
        self.title("Record Studio")
        # Definiert die Startgröße des Fensters (Breite x Höhe in Pixeln)
        self.geometry("1280x800")
        
        # Legt fest, dass das Fenster nicht kleiner als 800x600 Pixel werden kann
        self.minsize(800, 600)
        
        # Ruft die Methode auf, die das Fenster zentriert
        self._center_window()
        
        # Ruft die Methode auf, die die Benutzeroberfläche erstellt
        self._build_ui()
        
        # Zeigt die geladenen Profile beim Start an
        self._show_loaded_profiles()
        
        # Zeigt die geladenen Charaktere beim Start an
        self._show_loaded_characters()
    
    def _show_loaded_profiles(self):
        """Zeigt die geladenen Benutzerprofile in der Konsole an."""
        users = self.profile_manager.get_all_users()
        print(f"Geladene Benutzerprofile: {len(users)}")
        for user in users:
            print(f"  - {user.name} ({user.role})")
    
    def _show_loaded_characters(self):
        """Zeigt die geladenen Charaktere in der Konsole an."""
        characters = self.character_library.get_all_characters()
        print(f"Geladene Charaktere: {len(characters)}")
        for character in characters:
            print(f"  - {character.name} ({character.character_id})")
    
    # ... (_center_window, _build_ui, _get_user_display_names, _select_profile,
    #      _create_profile_dialog, _delete_profile, _edit_profile_dialog,
    #      _refresh_profile_list) bleiben unverändert


def main():
    """Einstiegspunkt der Anwendung."""
    # Erstellt eine Instanz der Hauptanwendung
    app = RecordStudioApp()
    # Startet die Tkinter-Ereignisschleife (wartet auf Benutzereingaben)
    app.mainloop()


# Standard-Guard: Nur ausführen, wenn diese Datei direkt gestartet wird
if __name__ == "__main__":
    # Ruft die main-Funktion auf
    main()
```

### Erklärung der app.py-Erweiterung

- **Import**: `from core.character_library import CharacterLibrary` importiert die neue Manager-Klasse.
- **Initialisierung**: `self.character_library = CharacterLibrary()` erzeugt eine Instanz. Standardmäßig lädt sie ihre Daten aus `assets/characters/character_data.json`.
- **Ausgabe**: `_show_loaded_characters()` gibt die Anzahl und Namen der geladenen Charaktere in der Konsole aus, analog zu `_show_loaded_profiles()`.
- **Keine UI-Änderungen**: Es werden noch keine Buttons, Listen oder andere sichtbare UI-Elemente für Charaktere eingebaut – das kommt in einer späteren Stunde.

---

## core/__init__.py

```python
# core - Paket für Geschäftslogik
# Enthält Datenmodelle und Manager für Charaktere, Szenen, Objekte etc.
```

Diese Datei macht den `core/`-Ordner zu einem Python-Paket. Sie ist leer (nur ein Kommentar) und dient nur dazu, dass man `from core.character import Character` schreiben kann.

---

## core/character.py

```python
# Character-Modell für Record Studio
# Definiert die Datenstruktur eines animierten Sprecher-Charakters

from datetime import datetime
from typing import Optional, Dict, Any


class Character:
    """Repräsentiert einen animierten Sprecher-Charakter.
    
    Ein Charakter ist ein Datensatz, der einen Sprecher in einer Szene
    identifiziert. Er enthält Basis-Informationen wie Name, Bildpfad
    und eine Beschreibung. Die eigentliche Animation (Mundbewegungen,
    Gesten etc.) wird später in eigenen Modulen umgesetzt.
    
    Attribute:
        character_id: Eindeutige ID des Charakters
        name: Anzeigename des Charakters (z.B. "Max Mustermann")
        image_path: Relativer Pfad zum Charakter-Bild (assets/characters/)
        description: Kurzbeschreibung des Charakters
        created_at: Erstellungsdatum als ISO-String
    """
    
    def __init__(
        self,
        character_id: str,
        name: str,
        image_path: str = "",
        description: str = "",
    ):
        """Initialisiert einen neuen Character.
        
        Args:
            character_id: Eindeutige ID (wird von CharacterLibrary generiert)
            name: Anzeigename des Charakters
            image_path: Relativer Pfad zum Bild (z.B. "assets/characters/max.png")
            description: Kurzbeschreibung (optional)
        """
        self.character_id = character_id
        self.name = name
        self.image_path = image_path
        self.description = description
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert das Character-Objekt in ein Dictionary.
        
        Wird benötigt, um den Charakter als JSON speichern zu können.
        Enthält nur JSON-kompatible Typen (str, int, list, dict).
        
        Returns:
            Dictionary mit allen Character-Informationen
        """
        return {
            "character_id": self.character_id,
            "name": self.name,
            "image_path": self.image_path,
            "description": self.description,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Character":
        """Erstellt ein Character-Objekt aus einem Dictionary.
        
        Diese Klassenmethode wird verwendet, um Charaktere aus der
        JSON-Datei zu laden. Sie erwartet ein Dictionary, das genau
        die Felder aus to_dict() enthält.
        
        Args:
            data: Dictionary mit Character-Daten (z.B. aus JSON geladen)
            
        Returns:
            Neue Character-Instanz mit den Werten aus data
        """
        character = cls(
            character_id=data["character_id"],
            name=data["name"],
            image_path=data.get("image_path", ""),
            description=data.get("description", "")
        )
        # created_at aus data übernehmen, falls vorhanden
        # (sonst wird in __init__ automatisch datetime.now() gesetzt)
        character.created_at = data.get("created_at", datetime.now().isoformat())
        return character
    
    def __repr__(self) -> str:
        """Anzeige des Charakters für Debugging-Zwecke.
        
        Beispiel: Character(name='Max Mustermann', id='max_mustermann_1234)
        """
        return f"Character(name='{self.name}', id='{self.character_id}')"
```

### Erklärung der wichtigsten Code-Abschnitte

#### Import
```python
from datetime import datetime
from typing import Optional, Dict, Any
```
- `datetime` wird für den `created_at`-Zeitstempel benötigt (ISO-Format).
- Die `typing`-Importe sind für Typannotationen – sie helfen IDEs und machen den Code lesbarer.

#### `__init__` – Konstruktor
```python
def __init__(self, character_id, name, image_path="", description=""):
```
- `character_id` und `name` sind Pflichtfelder.
- `image_path` und `description` sind optional (Defaultwerte = leerer String).
- `created_at` wird automatisch auf den aktuellen Zeitstempel gesetzt – der Nutzer muss sich darum nicht kümmern.

#### `to_dict()` – Serialisierung
```python
def to_dict(self) -> Dict[str, Any]:
```
- Wandelt das Objekt in ein Dictionary um, das `json.dump()` verarbeiten kann.
- Enthält exakt die gleichen Feldnamen wie das JSON, was die Lesbarkeit erhöht.

#### `from_dict()` – Deserialisierung (Klassenmethode)
```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "Character":
```
- `@classmethod` bedeutet: Diese Methode gehört zur Klasse, nicht zur Instanz – man ruft sie auf mit `Character.from_dict(...)`.
- Der Rückgabetyp `"Character"` in Anführungszeichen ist ein Forward-Reference (weil die Klasse zu dem Zeitpunkt noch nicht fertig definiert ist).
- `data.get("image_path", "")` verwendet `.get()` mit Defaultwert, falls das Feld in der JSON-Datei fehlt (Abwärtskompatibilität).

#### `__repr__()`
```python
def __repr__(self) -> str:
```
- Wird aufgerufen, wenn man ein Character-Objekt in der Konsole ausgibt (`print(charakter)`).
- Zeigt Name und ID an – nützlich für Debugging.

---

## core/character_library.py

```python
# Character-Library für Record Studio
# Verwaltet eine Sammlung von Charakteren (Erstellen, Laden, Speichern, Löschen)

import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from core.character import Character


class CharacterLibrary:
    """Verwaltet Charakter-Datensätze in einer JSON-Datei.
    
    Die Charaktere werden in 'assets/characters/character_data.json' gespeichert
    und zur Laufzeit in einem Dictionary (character_id -> Character) gehalten.
    
    Die JSON-Datei hat folgende Struktur:
    {
        "characters": [ ... ],
        "last_updated": "2024-01-15T10:30:00"
    }
    """
    
    def __init__(self, data_file: str = "assets/characters/character_data.json"):
        """Initialisiert die CharacterLibrary.
        
        Args:
            data_file: Pfad zur JSON-Datei für Charakter-Daten.
                      Standardmäßig im assets/characters/ Ordner.
        """
        self.data_file = data_file
        self.characters: Dict[str, Character] = {}  # character_id -> Character
        self._load_characters()
    
    def _load_characters(self):
        """Lädt alle Charaktere aus der JSON-Datei.
        
        Falls die Datei nicht existiert, wird eine leere Datenbank erstellt
        (indem _save_characters() eine leere Datei anlegt).
        Falls die Datei ungültiges JSON enthält, wird mit einer leeren
        Liste gestartet.
        """
        # Prüfen, ob die Datei existiert
        if not os.path.exists(self.data_file):
            # Datei existiert noch nicht -> leere Datenbank anlegen
            self._save_characters()
            return
        
        # Datei existiert -> versuchen zu laden
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Alle Charaktere aus der Liste laden
                for char_data in data.get("characters", []):
                    character = Character.from_dict(char_data)
                    self.characters[character.character_id] = character
                    
        except json.JSONDecodeError:
            # Datei enthält ungültiges JSON -> mit leerer Liste weitermachen
            # und die Datei überschreiben
            print(f"Warnung: Die Datei {self.data_file} enthält ungültiges JSON.")
            print("Es wird eine neue, leere Datei erstellt.")
            self._save_characters()
    
    def _save_characters(self):
        """Speichert alle Charaktere in die JSON-Datei."""
        # Daten für JSON vorbereiten
        data = {
            "characters": [character.to_dict() for character in self.characters.values()],
            "last_updated": datetime.now().isoformat()
        }
        
        # Stelle sicher, dass das Verzeichnis existiert
        # (z.B. assets/characters/ muss vorhanden sein)
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        # Datei schreiben mit Einrückung und UTF-8 für Umlaute
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    def create_character(
        self,
        name: str,
        image_path: str = "",
        description: str = ""
    ) -> Character:
        """Erstellt einen neuen Charakter und speichert ihn.
        
        Die character_id wird automatisch aus dem Namen und einem
        Zeitstempel generiert. Das macht sie eindeutig, auch wenn
        zwei Charaktere den gleichen Namen haben.
        
        Args:
            name: Anzeigename des Charakters (z.B. "Max Mustermann")
            image_path: Relativer Pfad zum Bild (optional)
            description: Kurzbeschreibung (optional)
            
        Returns:
            Das neu erstellte Character-Objekt
        """
        # Generiere eine eindeutige ID aus Namen und aktuellem Unix-Zeitstempel
        import time
        timestamp = int(time.time())
        character_id = f"{name.lower().replace(' ', '_')}_{timestamp}"
        
        # Neues Character-Objekt erstellen
        character = Character(
            character_id=character_id,
            name=name,
            image_path=image_path,
            description=description
        )
        
        # Zum internen Dictionary hinzufügen und speichern
        self.characters[character_id] = character
        self._save_characters()
        
        return character
    
    def get_character(self, character_id: str) -> Optional[Character]:
        """Holt einen Charakter anhand seiner ID.
        
        Args:
            character_id: Die gesuchte Character-ID
            
        Returns:
            Character-Objekt oder None, falls nicht gefunden
        """
        return self.characters.get(character_id)
    
    def get_all_characters(self) -> List[Character]:
        """Gibt alle Charaktere zurück.
        
        Returns:
            Liste aller Character-Objekte (alphabetisch nach Name sortiert)
        """
        # Sortiere die Charaktere alphabetisch nach Namen
        return sorted(self.characters.values(), key=lambda c: c.name)
    
    def update_character(self, character_id: str, **kwargs) -> bool:
        """Aktualisiert Charakter-Informationen.
        
        Mit **kwargs können beliebig viele Felder auf einmal aktualisiert
        werden. Beispiel: update_character(id, name="Neuer Name", description="Neue Beschreibung")
        
        Args:
            character_id: ID des zu aktualisierenden Charakters
            **kwargs: Zu aktualisierende Felder (name, image_path, description)
            
        Returns:
            True wenn erfolgreich, False wenn Charakter nicht gefunden
        """
        character = self.characters.get(character_id)
        if character is None:
            return False
        
        # Nur Felder aktualisieren, die es wirklich gibt (hasattr-Prüfung)
        for key, value in kwargs.items():
            if hasattr(character, key):
                setattr(character, key, value)
        
        # Änderungen speichern
        self._save_characters()
        return True
    
    def delete_character(self, character_id: str) -> bool:
        """Löscht einen Charakter.
        
        Args:
            character_id: ID des zu löschenden Charakters
            
        Returns:
            True wenn erfolgreich, False wenn Charakter nicht gefunden
        """
        if character_id in self.characters:
            del self.characters[character_id]
            self._save_characters()
            return True
        return False
    
    def count_characters(self) -> int:
        """Gibt die Anzahl der gespeicherten Charaktere zurück.
        
        Returns:
            Anzahl der Charaktere im Dictionary
        """
        return len(self.characters)
```

### Erklärung der wichtigsten Code-Abschnitte

#### `__init__` – Konstruktor mit Standard-Pfad
```python
def __init__(self, data_file: str = "assets/characters/character_data.json"):
```
- Standardmäßig wird `assets/characters/character_data.json` verwendet.
- Der Pfad kann überschrieben werden (z.B. für Tests mit einer separaten Datei).

#### `_load_characters()` – Sicheres Laden
```python
if not os.path.exists(self.data_file):
    self._save_characters()
    return
```
- Existiert die Datei nicht, wird eine leere Datenbank angelegt.
- `try/except json.JSONDecodeError` fängt kaputte JSON-Dateien ab.

#### `_save_characters()` – Sicheres Speichern
```python
os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
```
- `exist_ok=True` verhindert einen Fehler, falls das Verzeichnis bereits existiert.
- `ensure_ascii=False` erlaubt Umlaute und Sonderzeichen in der JSON-Datei.

#### `create_character()` – ID-Generierung
```python
import time
timestamp = int(time.time())
character_id = f"{name.lower().replace(' ', '_')}_{timestamp}"
```
- `time.time()` gibt den aktuellen Unix-Zeitstempel (Sekunden seit 1970).
- Die ID ist eindeutig, weil zwei Aufrufe nie den exakt gleichen Zeitstempel haben.
- `name.lower().replace(' ', '_')` macht den Namen URL-freundlich (z.B. `max_mustermann_1705312345`).

#### `get_all_characters()` – Sortierung
```python
return sorted(self.characters.values(), key=lambda c: c.name)
```
- `sorted()` sortiert die Liste alphabetisch.
- `key=lambda c: c.name` gibt das Sortierkriterium an (nach Name).

#### `update_character()` – Flexible Aktualisierung mit **kwargs
```python
def update_character(self, character_id: str, **kwargs) -> bool:
```
- `**kwargs` sammelt alle benannten Parameter in einem Dictionary.
- `hasattr(object, name)` prüft, ob das Attribut existiert (Sicherheitscheck).
- `setattr(object, name, value)` setzt das Attribut dynamisch.

#### `delete_character()` – Löschen mit Existenz-Prüfung
```python
if character_id in self.characters:
    del self.characters[character_id]
    self._save_characters()
    return True
return False
```
- Prüft zuerst, ob die ID existiert, bevor gelöscht wird.
- Speichert nach dem Löschen automatisch die Änderungen.

---

## Warum diese Architektur?

### CharacterLibrary als Gegenstück zu ProfileManager
- **Symmetrie**: Beide folgen dem gleichen Muster (Klasse + Manager + JSON).
- **Wiederverwendbarkeit**: Spätere Komponenten (SceneLibrary, ObjectLibrary) folgen dem gleichen Schema.
- **Vorhersagbarkeit**: Ein Schüler, der ProfileManager versteht, versteht auch CharacterLibrary sofort.

### `__repr__()` statt `print()`-Methoden
- `__repr__()` ist die Python-Standardmethode für String-Repräsentation.
- Sie wird automatisch aufgerufen, wenn ein Objekt im Debugger oder in der Konsole angezeigt wird.
- Sauberer als eine eigene `print_info()`-Methode.

### `to_dict()` / `from_dict()` als Standard-Serialisierung
- Dieses Muster findet sich in vielen Python-Bibliotheken (z.B. Django Rest Framework, Marshmallow).
- Es trennt die Objekt-Logik von der Serialisierungs-Logik klar voneinander.
- Erweiterungen (z.B. Validierung vor dem Speichern) lassen sich leicht einbauen.

### getter/setter vermeiden (im Vergleich zu Java)
- In Python ist es idiomatisch, direkt auf Attribute zuzugreifen (`character.name`), statt Getter/Setter zu schreiben.
- Falls später Validierung nötig ist, kann man auf `@property` umsteigen, ohne die API zu ändern.

---

## Mögliche Stolperfallen beim Schüler

1. **`__init__.py` vergessen**
   - Ohne `__init__.py` im `core/`-Ordner kann Python das Paket nicht importieren.
   - Symptom: `ModuleNotFoundError: No module named 'core'`

2. **Verwechslung von `character_id` und `name`**
   - Intern wird mit der `character_id` gearbeitet (z.B. in `get_character()`), der Benutzer sieht aber nur den Namen.
   - Schüler versuchen, `get_character("Max Mustermann")` aufzurufen – das schlägt fehl.

3. **`from_dict` vergisst `@classmethod`**
   - Ohne `@classmethod` bekommt die Methode `self` statt `cls` übergeben und funktioniert nicht.
   - Symptom: `TypeError: from_dict() missing 1 required positional argument: 'data'`

4. **`datetime.now()` ohne Import**
   - Der Import `from datetime import datetime` muss in `character.py` und `character_library.py` stehen.
   - Symptom: `NameError: name 'datetime' is not defined`

5. **Falscher Pfad in `CharacterLibrary(data_file=...)`**
   - Der Standard-Pfad ist relativ zum Arbeitsverzeichnis (`assets/characters/character_data.json`).
   - Startet der Schüler `app.py` aus einem anderen Ordner, findet er die Datei nicht.

6. **`ensure_ascii=False` vergessen**
   - Ohne diesen Parameter werden Umlaute (ä, ö, ü) zu `\u00e4` escaped.
   - Die JSON-Datei ist dann schwer lesbar.

7. **Unterschied zwischen `json.load()` und `json.loads()`**
   - `json.load()` liest aus einer Datei (`open()`), `json.loads()` aus einem String.
   - Verwechslung führt zu `AttributeError: 'str' object has no attribute 'read'`.

---

## Mögliche Erweiterungen

- **Validierung beim Erstellen**: Prüfen, ob der Name leer ist oder ob ein Charakter mit dem gleichen Namen bereits existiert
- **Charakter-Bild kopieren**: Beim Erstellen wird das Bild automatisch in `assets/characters/` kopiert
- **Tags/Kategorien**: Zusätzliche Attribute wie `tags=["männlich", "jung", "freundlich"]`
- **Such-Funktion**: `find_characters(search_term: str)` für Name und Beschreibung
- **Import/Export**: Einzelne Charaktere als separate JSON-Dateien importieren/exportieren
- **Datenvalidierung mit `@property`**: Z.B. sicherstellen, dass `image_path` nie None ist
- **Charakter-Vorschau**: Ein kleiner UI-Bereich, der den Charakter mit seinem Bild anzeigt

---

## Prüfungen

### Code existiert und ist korrekt
- [ ] `core/__init__.py` existiert
- [ ] `core/character.py` existiert mit Klasse `Character` (Attribute: `character_id`, `name`, `image_path`, `description`, `created_at`)
- [ ] `core/character_library.py` existiert mit Klasse `CharacterLibrary` (Methoden: `create_character`, `get_character`, `get_all_characters`, `update_character`, `delete_character`, `count_characters`)
- [ ] `Character` hat `to_dict()` und `from_dict()` Methoden
- [ ] `CharacterLibrary` speichert Daten in `assets/characters/character_data.json`
- [ ] `app.py` importiert `CharacterLibrary` und initialisiert sie in `RecordStudioApp.__init__()`
- [ ] `app.py` hat `_show_loaded_characters()` Methode

### App startet ohne Fehler
- [ ] `python app.py` startet ohne Fehlermeldung
- [ ] In der Konsole erscheint "Geladene Charaktere: 0" (oder eine Zahl)
- [ ] `assets/characters/character_data.json` wird beim ersten Start automatisch erstellt
- [ ] Die JSON-Datei enthält gültiges JSON mit `"characters": []`

### Funktionalität (über Python-Konsole testbar)
- [ ] Neuen Charakter erstellen: `lib = CharacterLibrary(); lib.create_character("Test", description="Testcharakter")` funktioniert
- [ ] Erstellter Charakter ist in der JSON-Datei sichtbar
- [ ] Charakter nach ID abrufen: `lib.get_character(id)` gibt das richtige Objekt zurück
- [ ] Alle Charaktere auflisten: `lib.get_all_characters()` gibt eine Liste zurück
- [ ] Charakter aktualisieren: `lib.update_character(id, name="Neuer Name")` ändert den Namen
- [ ] Charakter löschen: `lib.delete_character(id)` entfernt den Charakter
- [ ] Nach dem Löschen ist die JSON-Datei aktualisiert
- [ ] `count_characters()` gibt die korrekte Anzahl zurück
- [ ] `get_all_characters()` gibt die Liste alphabetisch sortiert zurück

### Code-Qualität
- [ ] Alle Kommentare sind auf Deutsch und ausführlich
- [ ] Docstrings in allen Methoden sind im gleichen Format wie in `profiles/user.py`
- [ ] Keine `print()`-Anweisungen außerhalb von dokumentierten Ausnahmen
- [ ] Keine hardcodierten Werte, die besser als Parameter definiert wären