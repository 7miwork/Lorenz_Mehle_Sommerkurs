# Record Studio

## Änderungen (neu)

- `core/file_manager.py` — neues Modul für Projekt- und Dateisystem-Operationen.
- `core/project_manager.py` — neues Modul zum Erstellen, Öffnen und Speichern von Projekten.
- `ui/project_editor.py` — einfacher Tkinter-Editor zur Verwaltung von Projekten, Sprechern und Aufnahmen.
- `requirements.txt` — hinzugefügt: `sounddevice`, `numpy`.

Diese Änderungen fügen die Basisarchitektur für Projekte, Sprecherordner
und einen einfachen Audio-Recorder hinzu. Sie sind modulär gestaltet,
sodass später BGM, SFX, Timeline und KI-Sprecher ergänzt werden können.

Audio-Formate und Speicherung:

- Aufnahmen (Sprecher): standardmäßig als `OGG` (Vorbis) gespeichert, um Platz zu sparen.
- Text-to-Speech / KI-Ausgaben: vorgesehen als `OPUS`-Format (für spätere Integrationen).
- BGM und SFX: werden als `OGG` (Vorbis) verwaltet.

Die Konvertierung erfolgt lokal via `ffmpeg` (bereitgestellt durch `imageio-ffmpeg`).
Diese Formate dienen nur der internen, platzsparenden Speicherung; für den finalen
Export können später andere Formate (z. B. WAV/MP4) erzeugt werden.

Hinweise zum Testen:

1. Installiere Abhängigkeiten:

```powershell
python -m pip install -r requirements.txt
```

2. Starte die App:

```powershell
python app.py
```

3. Öffne `Projekt Editor` → erstelle ein Projekt → füge Sprecher hinzu →
	wähle einen Sprecher → starte Aufnahme → Stop → Speichern.

Record Studio ist ein Werkzeug zum Erstellen von animierten Sprecher-Szenen mit Audioaufnahme, Timeline und Videoexport.

## Funktionen

- [x] Grundgerüst der Anwendung (Tkinter-Hauptfenster)
- [x] Benutzerprofile
- [x] Character Library
- [x] Character Editor
- [x] Scene Library
- [x] Scene Editor
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
| 5 | Scene Library & Scene Editor | Scene-Klasse, SceneLibrary-Manager, SceneEditor-GUI, Hauptmenü nach Anmeldung, 2D-Charaktere mit Ansichten & Bewegungen, Zeichen-Canvas für Landschaften |

## Installation

1. Python 3.x installieren
2. Abhängigkeiten installieren: `pip install -r requirements.txt`
3. Anwendung starten: `python app.py`

## Nächster Schritt

In Stunde 6 kommt der Audio Recorder hinzu – damit können Sprecher ihre Stimme aufnehmen und der Szene zuordnen.
