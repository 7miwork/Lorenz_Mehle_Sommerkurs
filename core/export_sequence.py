"""build_export_sequence: Baut aus einem geoeffneten Projekt eine geordnete
Liste von "Sequenz-Schritten" fuer die Vorschau-Wiedergabe.

Diese Funktion ist die Bruecke zwischen den globalen Datenbanken
(Szenen, Charaktere, Sprecher, Timeline) und der Diashow-Wiedergabe
im PreviewPlayer. Sie erzeugt dabei NICHT eine Videodatei, sondern
nur die Daten-Grundlage: Szene, Charakterbilder, Audiodatei und
Dauer - in der Reihenfolge, die die Timeline vorgibt.

Fehlerfaelle (fehlendes Bild, fehlendes Audio, leere Timeline) werden
sauber abgefangen und mit sinnvollen Standardwerten (Fallback) geloest,
statt die Anwendung abstuerzen zu lassen.
"""

import os
from typing import List, Optional


# Standard-Anzeigedauer in Sekunden, falls ein Sequenz-Schritt
# keinerlei Audiodaten besitzt. Die Vorschau springt dann nach
# dieser Zeit automatisch zum naechsten Schritt.
DEFAULT_DURATION = 4.0


class ExportStep:
    """Ein einzelner Schritt der Vorschau-Sequenz.

    Ein Schritt steht fuer einen Timeline-Eintrag: eine Szene, die
    Charakterbilder des Sprechers, das zugehoerige Audio und eine Dauer.

    Attribute:
        scene_id: ID der Szene (leer, falls keine gefunden)
        scene_name: Anzeigename der Szene
        background_path: relativer Pfad zum Szenenbild (leer moeglich)
        image_paths: Liste relativer Charakter-Bildpfade (leer moeglich)
        audio_path: absoluter Pfad zur Audiodatei (None, falls keins)
        duration: Dauer des Schritts in Sekunden (aus Audio oder Standard)
        text: der gesprochene Text aus der Timeline
    """

    def __init__(self, scene_id="", scene_name="", background_path="",
                 image_paths=None, audio_path=None,
                 duration=DEFAULT_DURATION, text=""):
        """Initialisiert einen Sequenz-Schritt mit Standard-Fallbacks."""
        self.scene_id = scene_id
        self.scene_name = scene_name if scene_name else "Szene"
        self.background_path = background_path
        self.image_paths = image_paths if image_paths else []
        self.audio_path = audio_path
        self.duration = duration if duration and duration > 0 else DEFAULT_DURATION
        self.text = text

    def __repr__(self) -> str:
        """Kurz-Text fuer Debugging-Zwecke."""
        return (f"ExportStep(scene='{self.scene_name}', "
                f"audio={'ja' if self.audio_path else 'nein'}, "
                f"{self.duration:.1f}s)")


def _resolve_scene(entry, scene_library):
    """Loest die Szene eines Timeline-Eintrags auf.

    Gibt ein Tupel (scene_id, scene_name, background_path) zurueck.
    Falls die Szene nicht gefunden wird, wird ein sinnvoller
    Fallback-Wert (leere Szene) zurueckgegeben, damit die Vorschau
    nicht abbricht.
    """
    if scene_library is None or not entry.scene_id:
        return (entry.scene_id, "Szene", "")
    scene = scene_library.get_scene(entry.scene_id)
    if scene is None:
        return (entry.scene_id, "Szene", "")
    return (scene.scene_id, scene.name, scene.background_path)


def _resolve_character_images(p_speaker, g_speaker, character_library) -> List[str]:
    """Sammelt die Charakter-Bildpfade zu einer Timeline-Szene.

    Der Charakter wird zumeist ueber den globalen Sprecher aufgeloest
    (dieser traegt die character_id). Der Projektspeaker ist eine
    Referenz mit gleicher ID und dient nur als Fallback.

    Returns:
        Liste relativer Charakter-Bildpfade (leer, falls keiner existiert)
    """
    for speaker in (g_speaker, p_speaker):
        if speaker is None or character_library is None or not speaker.character_id:
            continue
        character = character_library.get_character(speaker.character_id)
        if character is None:
            continue
        images = [path for path in (character.views or {}).values() if path]
        if not images and getattr(character, "image_path", ""):
            images = [character.image_path]
        return images
    return []


def _resolve_audio(entry, p_speaker, g_speaker, project,
                   file_manager, audio_manager):
    """Ermittelt die passende Audiodatei und Dauer fuer einen Schritt.

    Es wird eine Aufnahme gesucht, deren Anzeigename zum Timeline-Text
    passt (z. B. Wort "Hallo"). Es werden sowohl die Aufnahmen des
    Projektspeakers als auch die des globalen Sprechers durchsucht.

    Returns:
        Tupel (audio_path, duration). audio_path ist None, wenn nichts
        abspielbares gefunden wurde.
    """
    candidates = []
    for speaker in (p_speaker, g_speaker):
        if speaker is not None:
            candidates.extend(speaker.recordings)

    recording = None
    for rec in candidates:
        if rec.display_name == entry.text:
            recording = rec
            break
    if recording is None and candidates:
        recording = candidates[0]
    if recording is None:
        return (None, DEFAULT_DURATION)

    # Pfadje nach Speicherort: Projektspeaker -> Projektordner,
    # globaler Sprecher -> Arbeitsverzeichnis.
    is_project = False
    if p_speaker is not None:
        for other in p_speaker.recordings:
            if other is recording or other.recording_id == recording.recording_id:
                is_project = True
                break

    if is_project and file_manager is not None and project is not None:
        abs_path = file_manager.to_absolute(project.folder_name, recording.filepath)
    else:
        abs_path = os.path.abspath(recording.filepath)

    if abs_path and os.path.exists(abs_path):
        if audio_manager is not None:
            duration = audio_manager.get_duration(abs_path)
        if not duration or duration <= 0:
            duration = DEFAULT_DURATION
        return (abs_path, duration)

    return (None, DEFAULT_DURATION)


def build_export_sequence(
    project,
    scene_library=None,
    speaker_library=None,
    character_library=None,
    timeline_library=None,
    file_manager=None,
    speaker_manager=None,
    audio_manager=None,
) -> List[ExportStep]:
    """Baut die geordnete Liste der Sequenz-Schritte fuer ein Projekt.

    Die Reihenfolge kommt aus der (globalen) Timeline: Alle Eintraege
    werden nach ihrem `order`-Wert sortiert. Fuer jeden Eintrag wird
    Szene, Charakterbilder, Audio und Dauer aufgeloest.

    Args:
        project: Das geoeffnete Project-Objekt
        scene_library: Bibliothek der (globalen) Szenen
        speaker_library: Bibliothek der (globalen) Sprecher
        character_library: Bibliothek der Charaktere (fuer Bilder)
        timeline_library: Bibliothek der Timeline-Eintraege
        file_manager: FileManager (fuer Projektpfad-Aufloesung)
        speaker_manager: SpeakerManager des geoeffneten Projekts
        audio_manager: AudioManager (fuer die Dauer-Berechnung)

    Returns:
        Liste von ExportStep-Objekten. Bei leerer Timeline wird eine
        leere Liste zurueckgegeben (kein Absturz).
    """
    if timeline_library is None:
        return []

    entries = timeline_library.get_all_entries()
    steps: List[ExportStep] = []

    for entry in entries:
        scene_id, scene_name, background = _resolve_scene(entry, scene_library)

        # Sprecher auf beiden Ebenen aufloesen (Projekt + global)
        p_speaker = None
        g_speaker = None
        if speaker_manager is not None:
            p_speaker = speaker_manager.get_speaker(entry.speaker_id)
        if speaker_library is not None:
            g_speaker = speaker_library.get_speaker(entry.speaker_id)

        images = _resolve_character_images(p_speaker, g_speaker, character_library)
        audio_path, duration = _resolve_audio(
            entry, p_speaker, g_speaker, project, file_manager, audio_manager,
        )

        steps.append(ExportStep(
            scene_id=scene_id,
            scene_name=scene_name,
            background_path=background,
            image_paths=images,
            audio_path=audio_path,
            duration=duration,
            text=entry.text,
        ))

    return steps
