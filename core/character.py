# Character-Modell für Record Studio
# Definiert die Datenstruktur eines animierten 2D-Sprecher-Charakters
# Unterstützt mehrere Ansichten (Vorder-, Seiten-, Rückansicht) und
# Bewegungs-Zustände (idle, walking, talking).

from datetime import datetime
from typing import Optional, Dict, Any


class Character:
    """Repräsentiert einen animierten 2D-Sprecher-Charakter.

    Ein Charakter ist ein Datensatz, der einen Sprecher in einer Szene
    identifiziert. Er enthält Basis-Informationen wie Name, Beschreibung
    und mehrere Ansichten für die Animation.

    Ansichten (views):
        - front:  Vorderansicht (von vorne)
        - side_left:  Seitenansicht von links
        - side_right: Seitenansicht von rechts
        - back:   Rückansicht

    Bewegungs-Zustände (poses):
        - idle:    Stehend / ruhig
        - walking: Laufend
        - talking: Sprechend (Mund offen)

    Attribute:
        character_id: Eindeutige ID des Charakters
        name: Anzeigename des Charakters (z.B. "Max Mustermann")
        description: Kurzbeschreibung des Charakters
        views: Dictionary mit Ansicht -> Bildpfad
        poses: Dictionary mit Zustand -> Bildpfad
        created_at: Erstellungsdatum als ISO-String
    """

    # Verfügbare Ansichten
    AVAILABLE_VIEWS = ["front", "side_left", "side_right", "back"]

    # Verfügbare Bewegungs-Zustände
    AVAILABLE_POSES = ["idle", "walking", "talking"]

    def __init__(
        self,
        character_id: str,
        name: str,
        description: str = "",
        views: Optional[Dict[str, str]] = None,
        poses: Optional[Dict[str, str]] = None,
    ):
        """Initialisiert einen neuen Character.

        Args:
            character_id: Eindeutige ID (wird von CharacterLibrary generiert)
            name: Anzeigename des Charakters
            description: Kurzbeschreibung (optional)
            views: Dictionary mit Ansicht -> Bildpfad (optional)
            poses: Dictionary mit Zustand -> Bildpfad (optional)
        """
        self.character_id = character_id
        self.name = name
        self.description = description
        # views: {"front": "assets/characters/max_front.png", ...}
        self.views = views if views is not None else {}
        # poses: {"idle": "assets/characters/max_idle.png", ...}
        self.poses = poses if poses is not None else {}
        self.created_at = datetime.now().isoformat()

    def get_view(self, view_name: str) -> str:
        """Gibt den Bildpfad für eine Ansicht zurück.

        Args:
            view_name: Name der Ansicht (front, side_left, side_right, back)

        Returns:
            Bildpfad oder leerer String, falls nicht vorhanden
        """
        return self.views.get(view_name, "")

    def set_view(self, view_name: str, image_path: str):
        """Setzt den Bildpfad für eine Ansicht.

        Args:
            view_name: Name der Ansicht
            image_path: Relativer Pfad zum Bild
        """
        self.views[view_name] = image_path

    def get_pose(self, pose_name: str) -> str:
        """Gibt den Bildpfad für einen Bewegungs-Zustand zurück.

        Args:
            pose_name: Name des Zustands (idle, walking, talking)

        Returns:
            Bildpfad oder leerer String, falls nicht vorhanden
        """
        return self.poses.get(pose_name, "")

    def set_pose(self, pose_name: str, image_path: str):
        """Setzt den Bildpfad für einen Bewegungs-Zustand.

        Args:
            pose_name: Name des Zustands
            image_path: Relativer Pfad zum Bild
        """
        self.poses[pose_name] = image_path

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert das Character-Objekt in ein Dictionary.

        Wird benötigt, um den Charakter als JSON speichern zu können.

        Returns:
            Dictionary mit allen Character-Informationen
        """
        return {
            "character_id": self.character_id,
            "name": self.name,
            "description": self.description,
            "views": self.views,
            "poses": self.poses,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Character":
        """Erstellt ein Character-Objekt aus einem Dictionary.

        Args:
            data: Dictionary mit Character-Daten (z.B. aus JSON geladen)

        Returns:
            Neue Character-Instanz mit den Werten aus data
        """
        character = cls(
            character_id=data["character_id"],
            name=data["name"],
            description=data.get("description", ""),
            views=data.get("views", {}),
            poses=data.get("poses", {})
        )
        character.created_at = data.get("created_at", datetime.now().isoformat())
        return character

    def __repr__(self) -> str:
        """Anzeige des Charakters für Debugging-Zwecke."""
        return f"Character(name='{self.name}', id='{self.character_id}')"