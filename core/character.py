# Character-Modell für Record Studio
# Definiert die Datenstruktur eines animierten Sprecher-Charakters

from datetime import datetime
from typing import Optional, Dict, Any


class Character:
    """Repräsentiert einen animierten Sprecher-Charakter.
    
    Ein Charakter ist ein Datensatz, der einen Sprecher in einer Szene
    identifiziert. Er enthält Basis-Informationen wie Name, Bildpfad
    und eine Beschreibung. Die eigentliche Animation (Mundbewegungen,
    Gesten etc.) wird später in eigenen Modulen umgesetzt.
    
    Attribute:
        character_id: Eindeutige ID des Charakters
        name: Anzeigename des Charakters (z.B. "Max Mustermann")
        image_path: Relativer Pfad zum Charakter-Bild (assets/characters/)
        description: Kurzbeschreibung des Charakters
        created_at: Erstellungsdatum als ISO-String
    """
    
    def __init__(
        self,
        character_id: str,
        name: str,
        image_path: str = "",
        description: str = "",  # FEHLER 1: Default-Wert sollte "" sein, nicht "TODO"
    ):
        """Initialisiert einen neuen Character.
        
        Args:
            character_id: Eindeutige ID (wird von CharacterLibrary generiert)
            name: Anzeigename des Charakters
            image_path: Relativer Pfad zum Bild (z.B. "assets/characters/max.png")
            description: Kurzbeschreibung (optional)
        """
        self.character_id = character_id
        self.name = name
        self.image_path = image_path
        # FEHLER 1 (Fortsetzung): description wird zugewiesen, aber der Default-Wert
        # "TODO" ist unschön. Wer keinen description-Wert übergibt, bekommt "TODO"
        # statt eines leeren Strings.
        self.description = description
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert das Character-Objekt in ein Dictionary.
        
        Wird benötigt, um den Charakter als JSON speichern zu können.
        Enthält nur JSON-kompatible Typen (str, int, list, dict).
        
        Returns:
            Dictionary mit allen Character-Informationen
        """
        return {
            "character_id": self.character_id,
            "name": self.name,
            "image_path": self.image_path,
            "description": self.description,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Character":
        """Erstellt ein Character-Objekt aus einem Dictionary.
        
        Diese Klassenmethode wird verwendet, um Charaktere aus der
        JSON-Datei zu laden. Sie erwartet ein Dictionary, das genau
        die Felder aus to_dict() enthält.
        
        Args:
            data: Dictionary mit Character-Daten (z.B. aus JSON geladen)
            
        Returns:
            Neue Character-Instanz mit den Werten aus data
        """
        character = cls(
            character_id=data["character_id"],
            name=data["name"],
            image_path=data.get("image_path", ""),
            description=data.get("description", "")
        )
        # created_at aus data übernehmen, falls vorhanden
        # (sonst wird in __init__ automatisch datetime.now() gesetzt)
        character.created_at = data.get("created_at", datetime.now().isoformat())
        return character
    
    def __repr__(self) -> str:
        """Anzeige des Charakters für Debugging-Zwecke.
        
        Beispiel: Character(name='Max Mustermann', id='max_mustermann_1234)
        """
        return f"Character(name='{self.name}', id='{self.character_id}')"