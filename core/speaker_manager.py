# SpeakerManager für Record Studio
# Verwaltet Sprecher innerhalb eines Projekts.
# Jeder Sprecher besitzt einen eigenen Ordner und eigene Aufnahmen.

import os
import time
from datetime import datetime
from typing import List, Optional

from core.speaker import Speaker, Recording
from core.file_manager import FileManager
from core.audio_manager import AudioManager


class SpeakerManager:
    """Verwaltet Sprecher und ihre Aufnahmen in einem Projekt.

    Der SpeakerManager arbeitet mit dem FileManager zusammen,
    um für jeden Sprecher einen eigenen Ordner zu erstellen.
    Alle Pfade werden relativ zum Projektordner gespeichert.
    """

    def __init__(
        self,
        project_folder: str,
        file_manager: FileManager,
        audio_manager: AudioManager,
    ):
        """Initialisiert den SpeakerManager.

        Args:
            project_folder: Name des Projektordners
            file_manager: FileManager für Ordner-Operationen
            audio_manager: AudioManager für Aufnahme/Wiedergabe
        """
        self.project_folder = project_folder
        self.file_manager = file_manager
        self.audio_manager = audio_manager
        self.speakers: List[Speaker] = []

    # ---------- SPRECHER ----------

    def create_speaker(
        self,
        display_name: str,
        character_id: str = "",
        order: int = 0,
        color: str = "",
        notes: str = "",
    ) -> Speaker:
        """Erstellt einen neuen Sprecher und seinen Ordner.

        Args:
            display_name: Anzeigename des Sprechers
            character_id: Referenz auf den Charakter (optional)
            order: Reihenfolge innerhalb der Szene
            color: Optionale Farbe
            notes: Optionale Notizen

        Returns:
            Der neu erstellte Speaker
        """
        timestamp = int(time.time())
        speaker_id = f"{display_name.lower().replace(' ', '_')}_{timestamp}"

        speaker = Speaker(
            speaker_id=speaker_id,
            character_id=character_id,
            display_name=display_name,
            order=order,
            color=color,
            notes=notes,
        )

        # Eigenen Ordner für den Sprecher erstellen
        self.file_manager.create_speaker_folder(self.project_folder, display_name)

        self.speakers.append(speaker)
        return speaker

    def get_speaker(self, speaker_id: str) -> Optional[Speaker]:
        """Gibt einen Sprecher anhand seiner ID zurück."""
        for speaker in self.speakers:
            if speaker.speaker_id == speaker_id:
                return speaker
        return None

    def get_all_speakers(self) -> List[Speaker]:
        """Gibt alle Sprecher sortiert nach Reihenfolge zurück."""
        return sorted(self.speakers, key=lambda s: s.order)

    def update_speaker(self, speaker_id: str, **kwargs) -> bool:
        """Aktualisiert Sprecher-Informationen.

        Wenn der Anzeigename geändert wird, wird auch der
        Sprecherordner umbenannt.

        Args:
            speaker_id: ID des Sprechers
            **kwargs: Felder zum Aktualisieren (display_name, character_id, ...)

        Returns:
            True wenn erfolgreich
        """
        speaker = self.get_speaker(speaker_id)
        if speaker is None:
            return False

        old_name = speaker.display_name

        for key, value in kwargs.items():
            if hasattr(speaker, key):
                setattr(speaker, key, value)

        # Ordner umbenennen, wenn sich der Name geändert hat
        if "display_name" in kwargs and old_name != speaker.display_name:
            self.file_manager.rename_speaker_folder(
                self.project_folder, old_name, speaker.display_name
            )

        return True

    def delete_speaker(self, speaker_id: str, delete_files: bool = False) -> bool:
        """Löscht einen Sprecher.

        Args:
            speaker_id: ID des Sprechers
            delete_files: True, wenn auch der Ordner mit Audiodateien gelöscht wird

        Returns:
            True wenn erfolgreich
        """
        speaker = self.get_speaker(speaker_id)
        if speaker is None:
            return False

        if delete_files:
            self.file_manager.delete_speaker_folder(
                self.project_folder, speaker.display_name
            )

        self.speakers.remove(speaker)
        return True

    # ---------- AUFNAHMEN ----------

    def add_recording(
        self,
        speaker_id: str,
        display_name: str,
        temp_audio_path: str,
        target_format: str = "ogg",
    ) -> Optional[Recording]:
        """Fügt einem Sprecher eine neue Aufnahme hinzu.

        Die temporäre Aufnahme wird in den Sprecherordner kopiert.

        Args:
            speaker_id: ID des Sprechers
            display_name: Anzeigename der Aufnahme
            temp_audio_path: Pfad zur temporären WAV-Datei

        Returns:
            Das neue Recording oder None bei Fehler
        """
        speaker = self.get_speaker(speaker_id)
        if speaker is None:
            return None

        timestamp = int(time.time())
        recording_id = f"rec_{timestamp}"

        # Dateiname aus Anzeigename und Zeitstempel
        safe_name = "".join(
            c if c.isalnum() or c in " -_" else "_"
            for c in display_name
        ).strip()
        # Dateiendung basierend auf gewünschtem Format
        ext = ".ogg" if target_format == "ogg" else ".opus"
        filename = f"{safe_name}_{timestamp}{ext}"

        # Relativer Pfad im Sprecherordner
        speaker_folder = self.file_manager.get_speaker_folder(
            self.project_folder, speaker.display_name
        )
        relative_path = os.path.join(speaker_folder, filename)

        # Absolute Pfade für die Datei-Operation
        absolute_path = self.file_manager.to_absolute(
            self.project_folder, relative_path
        )

        # Aufnahme in den Sprecherordner kopieren / konvertieren
        out_path = None
        if target_format in ("ogg", "opus"):
            out_path = self.audio_manager.convert_and_save(temp_audio_path, absolute_path, target_format)
            if out_path is None:
                return None
        else:
            if not self.audio_manager.save_recording(temp_audio_path, absolute_path, display_name):
                return None
            out_path = absolute_path

        # Dauer ermitteln
        duration = self.audio_manager.get_duration(out_path)

        recording = Recording(
            recording_id=recording_id,
            display_name=display_name,
            filename=filename,
            filepath=relative_path,
            duration=duration,
        )

        speaker.add_recording(recording)
        return recording

    def rename_recording(
        self, speaker_id: str, recording_id: str, new_name: str
    ) -> bool:
        """Benennt eine Aufnahme um.

        Args:
            speaker_id: ID des Sprechers
            recording_id: ID der Aufnahme
            new_name: Neuer Anzeigename

        Returns:
            True wenn erfolgreich
        """
        speaker = self.get_speaker(speaker_id)
        if speaker is None:
            return False

        recording = speaker.get_recording(recording_id)
        if recording is None:
            return False

        recording.display_name = new_name
        recording.modified_at = datetime.now().isoformat()
        return True

    def delete_recording(self, speaker_id: str, recording_id: str) -> bool:
        """Löscht eine Aufnahme inklusive Datei.

        Args:
            speaker_id: ID des Sprechers
            recording_id: ID der Aufnahme

        Returns:
            True wenn erfolgreich
        """
        speaker = self.get_speaker(speaker_id)
        if speaker is None:
            return False

        recording = speaker.get_recording(recording_id)
        if recording is None:
            return False

        # Datei löschen
        absolute_path = self.file_manager.to_absolute(
            self.project_folder, recording.filepath
        )
        self.audio_manager.delete_file(absolute_path)

        return speaker.remove_recording(recording_id)

    def play_recording(self, speaker_id: str, recording_id: str) -> bool:
        """Spielt eine Aufnahme ab.

        Args:
            speaker_id: ID des Sprechers
            recording_id: ID der Aufnahme

        Returns:
            True wenn die Wiedergabe gestartet wurde
        """
        speaker = self.get_speaker(speaker_id)
        if speaker is None:
            return False

        recording = speaker.get_recording(recording_id)
        if recording is None:
            return False

        absolute_path = self.file_manager.to_absolute(
            self.project_folder, recording.filepath
        )
        return self.audio_manager.play(absolute_path)

    # ---------- SERIALISIERUNG ----------

    def to_dict(self) -> List[dict]:
        """Konvertiert alle Sprecher in eine Liste von Dictionaries."""
        return [speaker.to_dict() for speaker in self.speakers]

    def from_dict(self, data: List[dict]):
        """Lädt Sprecher aus einer Liste von Dictionaries."""
        self.speakers = [Speaker.from_dict(item) for item in data]