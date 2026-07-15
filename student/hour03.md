# Stunde 3 - Character Library: Datenmodell und Verwaltung

## Was du heute lernst

- **Eine neue Klasse `Character` schreiben** als Datenmodell für animierte Sprecher-Charaktere
- **Eine Manager-Klasse `CharacterLibrary` schreiben** zum Verwalten einer Sammlung von Charakteren
- **Das `to_dict()`/`from_dict()`-Muster** anwenden, um Objekte als JSON zu speichern und zu laden
- **Eine JSON-Datei** als einfache Datenbank verwenden
- **Die gleiche Architektur** wie bei den Benutzerprofilen (Stunde 2) auf ein neues Problem anwenden

## Deine Aufgabe

Baue eine **Character Library** – eine Komponente, mit der man animierte Sprecher-Charaktere verwalten kann. Das sind nur Datensätze mit Name, Bildpfad und Beschreibung – **noch kein Editor, keine Animation, keine Szenen-Verknüpfung**.

### Teil 1: `core/__init__.py` anlegen

Erstelle eine leere `__init__.py`-Datei im `core/`-Ordner. Sie macht den Ordner zu einem Python-Paket, damit man `from core.character import Character` schreiben kann.

### Teil 2: `core/character.py` – Die `Character`-Klasse

Erstelle eine Klasse `Character` mit folgenden Attributen:
- `character_id` (Pflicht) – eindeutige ID, wird später von der Bibliothek vergeben
- `name` (Pflicht) – Anzeigename des Charakters (z.B. "Max Mustermann")
- `image_path` (optional) – Pfad zum Charakter-Bild, relativ zu `assets/characters/`
- `description` (optional) – Kurzbeschreibung
- `created_at` (automatisch) – Erstellungszeit als ISO-String

Die Klasse braucht drei Methoden:
1. `to_dict()` – wandelt das Objekt in ein Dictionary um (für JSON)
2. `from_dict()` – Klassenmethode, die aus einem Dictionary ein Character-Objekt macht
3. `__repr__()` – gibt `Character(name='...', id='...')` zurück (für Debugging)

**Muster:** Orientiere dich an der `User`-Klasse aus `profiles/user.py`, aber baue **keine absichtlichen Fehler** ein.

### Teil 3: `core/character_library.py` – Die `CharacterLibrary`-Klasse

Erstelle eine Klasse `CharacterLibrary` mit folgenden Methoden:

| Methode | Beschreibung |
|---------|-------------|
| `__init__(data_file)` | Initialisiert die Bibliothek und lädt Daten aus JSON |
| `create_character(name, image_path, description)` | Erstellt neuen Charakter mit automatischer ID |
| `get_character(character_id)` | Gibt einen Charakter zurück (oder `None`) |
| `get_all_characters()` | Gibt alle Charaktere alphabetisch sortiert zurück |
| `update_character(character_id, **kwargs)` | Aktualisiert Felder eines Charakters |
| `delete_character(character_id)` | Löscht einen Charakter |
| `count_characters()` | Gibt die Anzahl der Charaktere zurück |

**Wichtige Details:**
- Speicherort: `assets/characters/character_data.json` (Standard-Pfad)
- Die `character_id` wird automatisch generiert: `name_lowercase_ohne_leerzeichen_` + Unix-Zeitstempel
- Die JSON-Datei hat folgende Struktur: `{ "characters": [...], "last_updated": "..." }`
- Existiert die Datei nicht, wird eine leere Datenbank angelegt
- Enthält die Datei ungültiges JSON, wird sie mit einer leeren Liste neu erstellt
- Die Liste in `get_all_characters()` soll alphabetisch nach `name` sortiert sein

**Muster:** Orientiere dich an `profiles/profile_manager.py`, aber ohne die absichtlichen Fehler. Beachte: `CharacterLibrary` speichert nach `create_character`, `update_character` und `delete_character` automatisch.

### Teil 4: `app.py` erweitern

Füge in `app.py` folgende Änderungen ein:
1. Importiere `CharacterLibrary` aus `core.character_library`
2. Erstelle in `RecordStudioApp.__init__()` eine Instanz: `self.character_library = CharacterLibrary()`
3. Erstelle eine Methode `_show_loaded_characters()`, die die Anzahl und Namen der geladenen Charaktere in der Konsole ausgibt (analog zu `_show_loaded_profiles()`)
4. Rufe `_show_loaded_characters()` am Ende von `__init__()` auf (nach `_show_loaded_profiles()`)

**Baue noch keine UI-Elemente (Buttons, Listen) für Charaktere ein** – das kommt erst in einer späteren Stunde!

## Was am Ende funktionieren soll

- **`python app.py` startet ohne Fehler** und zeigt in der Konsole an:
  ```
  Geladene Benutzerprofile: 2
    - Max Mustermann (student)
    - Anna Lehrerin (teacher)
  Geladene Charaktere: 0
  ```
- **`assets/characters/character_data.json`** wird automatisch erstellt (leere Datenbank)
- Über die Python-Konsole kannst du testen:
  ```python
  from core.character_library import CharacterLibrary
  lib = CharacterLibrary()
  lib.create_character("Max", description="Testcharakter")
  print(lib.count_characters())  # → 1
  print(lib.get_all_characters())  # → [Character(name='Max', id='max_1705312345')]
  ```
- Charaktere können erstellt, abgerufen, aktualisiert, gelöscht und gezählt werden
- Die JSON-Datei wird nach jeder Änderung aktualisiert
- Die Liste in `get_all_characters()` ist alphabetisch sortiert
- **Keine sichtbaren UI-Elemente** für Charaktere im Hauptfenster (nur Konsolen-Ausgabe)