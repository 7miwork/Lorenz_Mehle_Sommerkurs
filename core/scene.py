# Scene-Modell für Record Studio
# Definiert die Datenstruktur einer Szene (Hintergrund/Bühne für Charaktere)

from datetime import datetime
from typing import Optional, Dict, Any


class Scene:
    """Repräsentiert eine Szene (Bühne/Hintergrund) für Record Studio.

    Eine Szene ist der Ort, an dem Charaktere sprechen und agieren.
    Sie enthält Basis-Informationen wie Name, Hintergrundbild-Pfad
    und eine Beschreibung. Später können hier auch Objekte, Licht
    oder Kamera-Einstellungen ergänzt werden.

    Attribute:
        scene_id: Eindeutige ID der Szene
        name: Anzeigename der Szene (z.B. "Wohnzimmer", "Park")
        background_path: Relativer Pfad zum Hintergrundbild (assets/scenes/)
        description: Kurzbeschreibung der Szene
        created_at: Erstellungsdatum als ISO-String
    """

    def __init__(
        self,
        scene_id: str,
        name: str,
        background_path: str = "",
        description: str = "",
    ):
        """Initialisiert eine neue Scene.

        Args:
            scene_id: Eindeutige ID (wird von SceneLibrary generiert)
            name: Anzeigename der Szene
            background_path: Relativer Pfad zum Hintergrundbild
                             (z.B. "assets/scenes/wohnzimmer.png")
            description: Kurzbeschreibung (optional)
        """
        self.scene_id = scene_id
        self.name = name
        self.background_path = background_path
        self.description = description
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert das Scene-Objekt in ein Dictionary.

        Wird benötigt, um die Szene als JSON speichern zu können.
        Enthält nur JSON-kompatible Typen (str, int, list, dict).

        Returns:
            Dictionary mit allen Scene-Informationen
        """
        return {
            "scene_id": self.scene_id,
            "name": self.name,
            "background_path": self.background_path,
            "description": self.description,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Scene":
        """Erstellt ein Scene-Objekt aus einem Dictionary.

        Diese Klassenmethode wird verwendet, um Szenen aus der
        JSON-Datei zu laden. Sie erwartet ein Dictionary, das genau
        die Felder aus to_dict() enthält.

        Args:
            data: Dictionary mit Scene-Daten (z.B. aus JSON geladen)

        Returns:
            Neue Scene-Instanz mit den Werten aus data
        """
        scene = cls(
            scene_id=data["scene_id"],
            name=data["name"],
            background_path=data.get("background_path", ""),
            description=data.get("description", "")
        )
        # created_at aus data übernehmen, falls vorhanden
        # (sonst wird in __init__ automatisch datetime.now() gesetzt)
        scene.created_at = data.get("created_at", datetime.now().isoformat())
        return scene

    def __repr__(self) -> str:
        """Anzeige der Szene für Debugging-Zwecke.

        Beispiel: Scene(name='Wohnzimmer', id='wohnzimmer_1234')
        """
        return f"Scene(name='{self.name}', id='{self.scene_id}')"