# Speaker-Modell für Record Studio
# Definiert die Datenstruktur eines Sprechers und seiner Aufnahmen.
# Ein Sprecher besitzt einen Charakter, einen Anzeigenamen, eine
# Reihenfolge und beliebig viele Audioaufnahmen.

from datetime import datetime
from typing import Dict, Any, List


class Recording:
    """Repräsentiert eine einzelne Audioaufnahme eines Sprechers.

    Attribute:
        recording_id: Eindeutige ID der Aufnahme
        display_name: Anzeigename (z.B. "Begrüßung")
        filename: Dateiname auf der Festplatte (z.B. "begruessung.wav")
        filepath: Relativer Pfad zum Projektordner (z.B. "speakers/Mama/...")
        created_at: Erstellungsdatum als ISO-String
        modified_at: Änderungsdatum als ISO-String
        duration: Dauer der Aufnahme in Sekunden
    """

    def __init__(
        self,
        recording_id: str,
        display_name: str,
        filename: str = "",
        filepath: str = "",
        duration: float = 0.0,
    ):
        """Initialisiert eine neue Aufnahme."""
        self.recording_id = recording_id
        self.display_name = display_name
        self.filename = filename
        self.filepath = filepath
        self.created_at = datetime.now().isoformat()
        self.modified_at = self.created_at
        self.duration = duration

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert die Aufnahme in ein JSON-kompatibles Dictionary."""
        return {
            "recording_id": self.recording_id,
            "display_name": self.display_name,
            "filename": self.filename,
            "filepath": self.filepath,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "duration": self.duration,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Recording":
        """Erstellt eine Aufnahme aus einem Dictionary."""
        recording = cls(
            recording_id=data["recording_id"],
            display_name=data["display_name"],
            filename=data.get("filename", ""),
            filepath=data.get("filepath", ""),
            duration=data.get("duration", 0.0),
        )
        recording.created_at = data.get("created_at", recording.created_at)
        recording.modified_at = data.get("modified_at", recording.created_at)
        return recording

    def __repr__(self) -> str:
        """Anzeige der Aufnahme für Debugging-Zwecke."""
        return f"Recording(name='{self.display_name}', id='{self.recording_id}')"


class Speaker:
    """Repräsentiert einen Sprecher in einer Szene.

    Ein Sprecher besitzt einen Charakter, einen Anzeigenamen,
    eine Reihenfolge und beliebig viele eigene Audioaufnahmen.

    Attribute:
        speaker_id: Eindeutige ID des Sprechers
        character_id: Referenz auf den zugehörigen Charakter
        display_name: Anzeigename (z.B. "Mama")
        order: Reihenfolge innerhalb der Szene
        color: Optionale Farbe für die Anzeige
        notes: Optionale Notizen
        recordings: Liste aller Audioaufnahmen des Sprechers
    """

    def __init__(
        self,
        speaker_id: str,
        character_id: str = "",
        display_name: str = "",
        order: int = 0,
        color: str = "",
        notes: str = "",
    ):
        """Initialisiert einen neuen Sprecher."""
        self.speaker_id = speaker_id
        self.character_id = character_id
        self.display_name = display_name
        self.order = order
        self.color = color
        self.notes = notes
        self.recordings: List[Recording] = []
        self.created_at = datetime.now().isoformat()

    def add_recording(self, recording: Recording):
        """Fügt eine Aufnahme zum Sprecher hinzu."""
        self.recordings.append(recording)

    def get_recording(self, recording_id: str) -> Recording:
        """Gibt eine Aufnahme anhand ihrer ID zurück."""
        for recording in self.recordings:
            if recording.recording_id == recording_id:
                return recording
        return None

    def remove_recording(self, recording_id: str) -> bool:
        """Entfernt eine Aufnahme anhand ihrer ID."""
        for recording in self.recordings:
            if recording.recording_id == recording_id:
                self.recordings.remove(recording)
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert den Sprecher in ein JSON-kompatibles Dictionary."""
        return {
            "speaker_id": self.speaker_id,
            "character_id": self.character_id,
            "display_name": self.display_name,
            "order": self.order,
            "color": self.color,
            "notes": self.notes,
            "created_at": self.created_at,
            "recordings": [rec.to_dict() for rec in self.recordings],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Speaker":
        """Erstellt einen Sprecher aus einem Dictionary."""
        speaker = cls(
            speaker_id=data["speaker_id"],
            character_id=data.get("character_id", ""),
            display_name=data.get("display_name", ""),
            order=data.get("order", 0),
            color=data.get("color", ""),
            notes=data.get("notes", ""),
        )
        speaker.created_at = data.get("created_at", speaker.created_at)
        for rec_data in data.get("recordings", []):
            speaker.recordings.append(Recording.from_dict(rec_data))
        return speaker

    def __repr__(self) -> str:
        """Anzeige des Sprechers für Debugging-Zwecke."""
        return f"Speaker(name='{self.display_name}', id='{self.speaker_id}')"