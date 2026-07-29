# Scene-Library für Record Studio
# Verwaltet eine Sammlung von Szenen (Erstellen, Laden, Speichern, Löschen)

import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from core.scene import Scene


class SceneLibrary:
    """Verwaltet Szenen-Datensätze in einer JSON-Datei.

    Die Szenen werden in 'assets/scenes/scene_data.json' gespeichert
    und zur Laufzeit in einem Dictionary (scene_id -> Scene) gehalten.

    Die JSON-Datei hat folgende Struktur:
    {
        "scenes": [ ... ],
        "last_updated": "2024-01-15T10:30:00"
    }
    """

    def __init__(self, data_file: str = "assets/scenes/scene_data.json"):
        """Initialisiert die SceneLibrary.

        Args:
            data_file: Pfad zur JSON-Datei für Szenen-Daten.
                      Standardmäßig im assets/scenes/ Ordner.
        """
        self.data_file = data_file
        self.scenes: Dict[str, Scene] = {}  # scene_id -> Scene
        self._load_scenes()

    def _load_scenes(self):
        """Lädt alle Szenen aus der JSON-Datei.

        Falls die Datei nicht existiert, wird eine leere Datenbank erstellt
        (indem _save_scenes() eine leere Datei anlegt).
        Falls die Datei ungültiges JSON enthält, wird mit einer leeren
        Liste gestartet.
        """
        # Prüfen, ob die Datei existiert
        if not os.path.exists(self.data_file):
            # Datei existiert noch nicht -> leere Datenbank anlegen
            self._save_scenes()
            return

        # Datei existiert -> versuchen zu laden
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # Alle Szenen aus der Liste laden
                for scene_data in data.get("scenes", []):
                    scene = Scene.from_dict(scene_data)
                    self.scenes[scene.scene_id] = scene

        except json.JSONDecodeError:
            # Datei enthält ungültiges JSON -> mit leerer Liste weitermachen
            # und die Datei überschreiben
            print(f"Warnung: Die Datei {self.data_file} enthält ungültiges JSON.")
            print("Es wird eine neue, leere Datei erstellt.")
            self._save_scenes()

    def _save_scenes(self):
        """Speichert alle Szenen in die JSON-Datei."""
        # Daten für JSON vorbereiten
        data = {
            "scenes": [scene.to_dict() for scene in self.scenes.values()],
            "last_updated": datetime.now().isoformat()
        }

        # Stelle sicher, dass das Verzeichnis existiert
        # (z.B. assets/scenes/ muss vorhanden sein)
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)

        # Datei schreiben mit Einrückung und UTF-8 für Umlaute
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def create_scene(
        self,
        name: str,
        background_path: str = "",
        description: str = ""
    ) -> Scene:
        """Erstellt eine neue Szene und speichert sie.

        Die scene_id wird automatisch aus dem Namen und einem
        Zeitstempel generiert. Das macht sie eindeutig, auch wenn
        zwei Szenen den gleichen Namen haben.

        Args:
            name: Anzeigename der Szene (z.B. "Wohnzimmer")
            background_path: Relativer Pfad zum Hintergrundbild (optional)
            description: Kurzbeschreibung (optional)

        Returns:
            Das neu erstellte Scene-Objekt
        """
        # Generiere eine eindeutige ID aus Namen und aktuellem Unix-Zeitstempel
        import time
        timestamp = int(time.time())
        scene_id = f"{name.lower().replace(' ', '_')}_{timestamp}"

        # Neues Scene-Objekt erstellen
        scene = Scene(
            scene_id=scene_id,
            name=name,
            background_path=background_path,
            description=description
        )

        # Zum internen Dictionary hinzufügen und speichern
        self.scenes[scene_id] = scene
        self._save_scenes()

        return scene

    def get_scene(self, scene_id: str) -> Optional[Scene]:
        """Holt eine Szene anhand ihrer ID.

        Args:
            scene_id: Die gesuchte Scene-ID

        Returns:
            Scene-Objekt oder None, falls nicht gefunden
        """
        return self.scenes.get(scene_id)

    def get_all_scenes(self) -> List[Scene]:
        """Gibt alle Szenen zurück.

        Returns:
            Liste aller Scene-Objekte (alphabetisch nach Name sortiert)
        """
        return sorted(self.scenes.values(), key=lambda s: s.name)

    def update_scene(self, scene_id: str, **kwargs) -> bool:
        """Aktualisiert Szenen-Informationen.

        Mit **kwargs können beliebig viele Felder auf einmal aktualisiert
        werden. Beispiel: update_scene(id, name="Neuer Name", description="Neue Beschreibung")

        Args:
            scene_id: ID der zu aktualisierenden Szene
            **kwargs: Zu aktualisierende Felder (name, background_path, description)

        Returns:
            True wenn erfolgreich, False wenn Szene nicht gefunden
        """
        scene = self.scenes.get(scene_id)
        if scene is None:
            return False

        # Nur Felder aktualisieren, die es wirklich gibt (hasattr-Prüfung)
        for key, value in kwargs.items():
            if hasattr(scene, key):
                setattr(scene, key, value)

        # Änderungen speichern
        self._save_scenes()
        return True

    def delete_scene(self, scene_id: str) -> bool:
        """Löscht eine Szene.

        Args:
            scene_id: ID der zu löschenden Szene

        Returns:
            True wenn erfolgreich, False wenn Szene nicht gefunden
        """
        if scene_id in self.scenes:
            del self.scenes[scene_id]
            self._save_scenes()
            return True
        return False

    def count_scenes(self) -> int:
        """Gibt die Anzahl der gespeicherten Szenen zurück.

        Returns:
            Anzahl der Szenen im Dictionary
        """
        return len(self.scenes)