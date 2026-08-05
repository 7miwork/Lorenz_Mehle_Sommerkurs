# Project-Modell für Record Studio
# Definiert die Datenstruktur eines Projekts.
# Ein Projekt besitzt einen eigenen Ordner mit project.json,
# Szenen, Sprechern, BGM und Soundeffekten.

from datetime import datetime
from typing import Dict, Any, List


class Project:
    """Repräsentiert ein Record Studio Projekt.

    Ein Projekt ist ein eigener Ordner unter 'projects/'.
    Es enthält alle Informationen über Szenen, Sprecher,
    Hintergrundmusik und Soundeffekte.

    Attribute:
        project_id: Eindeutige ID des Projekts
        name: Anzeigename des Projekts (z.B. "Minecraft Folge 1")
        folder_name: Name des Projektordners
        created_at: Erstellungsdatum als ISO-String
        modified_at: Änderungsdatum als ISO-String
        scene_ids: Liste der Szenen-IDs
        speaker_ids: Liste der Sprecher-IDs
        bgm_files: Liste der BGM-Dateinamen
        sfx_files: Liste der SFX-Dateinamen
    """

    def __init__(
        self,
        project_id: str,
        name: str,
        folder_name: str = "",
    ):
        """Initialisiert ein neues Projekt."""
        self.project_id = project_id
        self.name = name
        self.folder_name = folder_name if folder_name else self._make_folder_name(name)
        self.created_at = datetime.now().isoformat()
        self.modified_at = self.created_at
        self.scene_ids: List[str] = []
        self.speaker_ids: List[str] = []
        self.bgm_files: List[str] = []
        self.sfx_files: List[str] = []

    @staticmethod
    def _make_folder_name(name: str) -> str:
        """Erstellt einen sicheren Ordnernamen aus dem Projektnamen."""
        # Erlaubte Zeichen: Buchstaben, Zahlen, Leerzeichen, Bindestrich, Unterstrich
        safe = "".join(
            c if c.isalnum() or c in " -_" else "_"
            for c in name
        ).strip()
        return safe if safe else "Projekt"

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert das Projekt in ein JSON-kompatibles Dictionary."""
        return {
            "project_id": self.project_id,
            "name": self.name,
            "folder_name": self.folder_name,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "scene_ids": self.scene_ids,
            "speaker_ids": self.speaker_ids,
            "bgm_files": self.bgm_files,
            "sfx_files": self.sfx_files,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        """Erstellt ein Projekt aus einem Dictionary."""
        project = cls(
            project_id=data["project_id"],
            name=data["name"],
            folder_name=data.get("folder_name", ""),
        )
        project.created_at = data.get("created_at", project.created_at)
        project.modified_at = data.get("modified_at", project.created_at)
        project.scene_ids = data.get("scene_ids", [])
        project.speaker_ids = data.get("speaker_ids", [])
        project.bgm_files = data.get("bgm_files", [])
        project.sfx_files = data.get("sfx_files", [])
        return project

    def __repr__(self) -> str:
        """Anzeige des Projekts für Debugging-Zwecke."""
        return f"Project(name='{self.name}', id='{self.project_id}')"