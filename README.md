# Record Studio

Record Studio ist ein Werkzeug zum Erstellen von animierten Sprecher-Szenen mit Audioaufnahme, Timeline und Videoexport.

## Funktionen

- [x] Grundgerüst der Anwendung (Tkinter-Hauptfenster)
- [x] Benutzerprofile
- [x] Character Library
- [x] Character Editor
- [ ] Scene Library
- [ ] Scene Editor
- [ ] Audio Recorder
- [ ] Mehrere Sprecher
- [ ] Timeline
- [ ] Projektverwaltung
- [ ] Vorschau
- [ ] Video Export
- [ ] Lippensynchronisation
- [ ] Upload-Funktionen

## Projektstruktur

```
Z:\Codes\Unterricht\Lorenz Mehle\Sommerkurs
├── assets
│   ├── characters
│   ├── scenes
│   ├── objects
│   ├── audio
│   ├── music
│   ├── icons
│   └── fonts
├── core
├── ui
├── projects
├── profiles
├── exports
├── teacher
├── student
├── docs
└── tools
```

## Screenshots

*(Screenshots werden nach jeder Unterrichtsstunde ergänzt.)*

## Verlauf der Unterrichtsstunden

| Stunde | Titel | Was wurde gelernt |
|--------|-------|-------------------|
| 1 | Projekt erstellen | Tkinter-Grundgerüst, Projektstruktur, Standard-Guard, main()-Funktion |
| 2 | Benutzerprofile | Code lesen, Debugging, Fehlersuche in bestehender Implementierung |
| 3 | Character Library | Character-Klasse, CharacterLibrary-Manager, JSON-Persistenz |
| 4 | Character Editor | Treeview, Toplevel-Dialoge, CRUD-Operationen in der GUI |

## Installation

1. Python 3.x installieren
2. Abhängigkeiten installieren: `pip install -r requirements.txt`
3. Anwendung starten: `python app.py`

## Nächster Schritt

In Stunde 5 wird eine Scene Library analog zur Character Library aufgebaut – ein Datenmodell für Szenen und ein Manager zur Verwaltung von Szenen in einer JSON-Datei.
