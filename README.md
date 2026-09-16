# Record Studio

Record Studio ist eine Tkinter-basierte App für Lehrzwecke zur Verwaltung von Sprecher-Projekten, Szenen, Charakteren und Audioaufnahmen.

## Aktueller Stand

- Ein Hauptfenster mit linker Navigation und rechtem Inhaltspanel.
- Benutzerprofile, die als Einstieg in die Anwendung dienen.
- Charakterverwaltung mit `CharacterEditor`.
- Szenenverwaltung mit `SceneEditor`.
- Projektverwaltung inkl. Sprecher, Aufnahme- und Speicherfunktionen mit `ProjectEditor`.
- Projektbezogene Sprecherorganisation mit `SpeakerOrganizer`.
- Globale Sprecher-Datenbank mit `SpeakerDatabaseEditor`.
- Globale Timeline-Verwaltung mit `TimelineEditor`.
- Projekt-Vorschau als Diashow: `ui/preview_player.py` zeigt Szenen,
  Charakterbilder und Sprecher-Audio in der Reihenfolge der Timeline;
  `core/export_sequence.py` baut die passenden Sequenz-Schritte.
- Projekt- und Dateisystemlogik in `core/file_manager.py` und `core/project_manager.py`.
- Persistente globale Speaker- und Timeline-Daten in `core/speaker_library.py` und `core/timeline_library.py`.

## Was die App jetzt kann

- Login / Profilwahl und Profilverwaltung
- Selektion über linke Navigation
- Charakterliste anzeigen, bearbeiten und löschen
- Szenenliste anzeigen, bearbeiten und löschen
- Projekt erstellen, öffnen und speichern
- Projekt-spezifische Sprecher erstellen und verwalten
- Audioaufnahme für Projektsprecher starten, stoppen und speichern
- Sprecher global anlegen und Wörter für sie aufnehmen (Sprecher-Aufnahme)
- Globale Sprecher-Datenbank bearbeiten
- Globale Timeline-Einträge erstellen, bearbeiten und löschen
- Vorschau als Diashow abspielen (Szenen + Charakterbilder + Sprecher-Audio)

## Aktuelle Funktionen

- [x] Ein einzelnes Hauptfenster mit Navigation
- [x] Benutzerprofile
- [x] Charakterverwaltung
- [x] Szenenverwaltung
- [x] Projektverwaltung
- [x] Projekt-spezifische Sprecherverwaltung
- [x] Audio Recorder / Aufnahme speichern
- [x] Globale Sprecher-Datenbank
- [x] Globale Timeline-Verwaltung
- [x] Vorschau (Diashow mit Bildern und Audio)
- [ ] Video Export
- [ ] Lippensynchronisation
- [ ] Upload-Funktionen

## Installation

1. Python 3.x installieren
2. Abhängigkeiten installieren:

```powershell
python -m pip install -r requirements.txt
```

3. App starten:

```powershell
python app.py
```

## Projektstruktur

```
Sommerkurs/
├── assets/
├── core/
│   ├── audio_manager.py
│   ├── export_sequence.py
│   ├── file_manager.py
│   ├── project_manager.py
│   ├── speaker_library.py
│   └── timeline_library.py
├── docs/
├── exports/
├── profiles/
│   └── profile_manager.py
├── projects/
├── tools/
├── ui/
│   ├── character_editor.py
│   ├── preview_player.py
   ├── main_menu.py
   ├── project_editor.py
   ├── scene_editor.py
   ├── speaker_database.py
   ├── speaker_organizer.py
   └── timeline_editor.py
├── app.py
└── requirements.txt
```

## Bedienung

1. Starte `python app.py`.
2. Wähle ein Profil oder lege ein neues Profil an.
3. Verwende die linke Navigation, um den aktuellen Bereich zu wechseln:
   - `Profile`: Anmeldung / Profilverwaltung
   - `Charaktere verwalten`: Charakterliste anzeigen, bearbeiten, löschen
   - `Szenen verwalten`: Szenenliste anzeigen, bearbeiten, löschen
   - `Projekte & Aufnahme`: Projektverwaltung, Sprecherliste und Audioaufnahme
   - `Sprecher organisieren`: Projektbezogene Speaker bearbeiten und Textdateien verwalten
   - `Speaker Datenbank`: Globale Sprecherdatenbank bearbeiten
   - `Timeline verwalten`: Globale Timeline-Einträge erstellen, bearbeiten, löschen
4. In Projekten kannst du Sprecher anlegen, aufnehmen und speichern.
5. In der globalen Datenbank kannst du Sprecher und Timeline-Einträge zentral verwalten.
6. Öffne ein Projekt und klicke auf `Vorschau abspielen`, um es als Diashow
   zu sehen: Szene für Szene mit Charakterbildern und Sprecher-Audio in
   der Reihenfolge der Timeline. Der Player hat Abspielen/Pause, Vor,
   Zurück und Schließen; ohne Ton schaltet er nach 4 Sekunden weiter.

## Navigation im Hauptfenster

- Links: Hauptnavigation mit allen Bereichen.
- Rechts: Inhalte des aktuell ausgewählten Bereichs.
- Nach der Profilanmeldung wird die Navigation freigeschaltet.
- Jeder Bereich bleibt im selben Fenster, es werden keine neuen Popup-Fenster mehr geöffnet.

## Hinweise

- Die GUI verwendet Tkinter und läuft lokal unter Windows.
- Audioaufnahmen nutzen `sounddevice` und speichern standardmäßig als OGG.
- Die App kann später um Exportfunktionen und KI-gesteuertes Text-zu-Sprache erweitert werden.

## Abhängigkeiten

- Pillow
- sounddevice
- numpy
- imageio-ffmpeg
- soundfile (optional, schnelleres Laden von OGG; ohne das Paket wird ffmpeg benutzt)

## Nächster Schritt

Der echte Video-Export (`core/video_exporter.py`) baut auf `export_sequence.py`
auf und rendert die Vorschau als mp4-Datei in den Ordner `exports/`.
