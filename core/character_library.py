# Character-Library für Record Studio
# Verwaltet eine Sammlung von Charakteren (Erstellen, Laden, Speichern, Löschen)

import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from core.character import Character


class CharacterLibrary:
    """Verwaltet Charakter-Datensätze in einer JSON-Datei.
    
    Die Charaktere werden in 'assets/characters/character_data.json' gespeichert
    und zur Laufzeit in einem Dictionary (character_id -> Character) gehalten.
    
    Die JSON-Datei hat folgende Struktur:
    {
        "characters": [ ... ],
        "last_updated": "2024-01-15T10:30:00"
    }
    """
    
    def __init__(self, data_file: str = "assets/characters/character_data.json"):
        """Initialisiert die CharacterLibrary.
        
        Args:
            data_file: Pfad zur JSON-Datei für Charakter-Daten.
                      Standardmäßig im assets/characters/ Ordner.
        """
        self.data_file = data_file
        self.characters: Dict[str, Character] = {}  # character_id -> Character
        self._load_characters()
    
    def _load_characters(self):
        """Lädt alle Charaktere aus der JSON-Datei.
        
        Falls die Datei nicht existiert, wird eine leere Datenbank erstellt
        (indem _save_characters() eine leere Datei anlegt).
        Falls die Datei ungültiges JSON enthält, wird mit einer leeren
        Liste gestartet.
        """
        # Prüfen, ob die Datei existiert
        if not os.path.exists(self.data_file):
            # Datei existiert noch nicht -> leere Datenbank anlegen
            self._save_characters()
            return
        
        # Datei existiert -> versuchen zu laden
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Alle Charaktere aus der Liste laden
                for char_data in data.get("characters", []):
                    character = Character.from_dict(char_data)
                    self.characters[character.character_id] = character
                    
        except json.JSONDecodeError:
            # Datei enthält ungültiges JSON -> mit leerer Liste weitermachen
            # und die Dateiüberschreiben
            print(f"Warnung: Die Datei {self.data_file} enthält ungültiges JSON.")
            print("Es wird eine neue, leere Datei erstellt.")
            self._save_characters()
    
    def _save_characters(self):
        """Speichert alle Charaktere in die JSON-Datei."""
        # Daten für JSON vorbereiten
        data = {
            "characters": [character.to_dict() for character in self.characters.values()],
            "last_updated": datetime.now().isoformat()
        }
        
        # Stelle sicher, dass das Verzeichnis existiert
        # (z.B. assets/characters/ muss vorhanden sein)
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        # Datei schreiben mit Einrückung und UTF-8 für Umlaute
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    def create_character(
        self,
        name: str,
        image_path: str = "",
        description: str = ""
    ) -> Character:
        """Erstellt einen neuen Charakter und speichert ihn.
        
        Die character_id wird automatisch aus dem Namen und einem
        Zeitstempel generiert. Das macht sie eindeutig, auch wenn
        zwei Charaktere den gleichen Namen haben.
        
        Args:
            name: Anzeigename des Charakters (z.B. "Max Mustermann")
            image_path: Relativer Pfad zum Bild (optional)
            description: Kurzbeschreibung (optional)
            
        Returns:
            Das neu erstellte Character-Objekt
        """
        # Generiere eine eindeutige ID aus Namen und aktuellem Unix-Zeitstempel
        import time
        timestamp = int(time.time())
        character_id = f"{name.lower().replace(' ', '_')}_{timestamp}"
        
        # Neues Character-Objekt erstellen
        character = Character(
            character_id=character_id,
            name=name,
            image_path=image_path,
            description=description
        )
        
        # Zum internen Dictionary hinzufügen und speichern
        self.characters[character_id] = character
        self._save_characters()
        
        return character
    
    def get_character(self, character_id: str) -> Optional[Character]:
        """Holt einen Charakter anhand seiner ID.
        
        Args:
            character_id: Die gesuchte Character-ID
            
        Returns:
            Character-Objekt oder None, falls nicht gefunden
        """
        return self.characters.get(character_id)
    
    def get_all_characters(self) -> List[Character]:
        """Gibt alle Charaktere zurück.
        
        Returns:
            Liste aller Character-Objekte (alphabetisch nach Name sortiert)
        """
        # Sortiere die Charaktere alphabetisch nach Namen
        return sorted(self.characters.values(), key=lambda c: c.name)
    
    def update_character(self, character_id: str, **kwargs) -> bool:
        """Aktualisiert Charakter-Informationen.
        
        Mit **kwargs können beliebig viele Felder auf einmal aktualisiert
        werden. Beispiel: update_character(id, name="Neuer Name", description="Neue Beschreibung")
        
        Args:
            character_id: ID des zu aktualisierenden Charakters
            **kwargs: Zu aktualisierende Felder (name, image_path, description)
            
        Returns:
            True wenn erfolgreich, False wenn Charakter nicht gefunden
        """
        character = self.characters.get(character_id)
        if character is None:
            return False
        
        # Nur Felder aktualisieren, die es wirklich gibt (hasattr-Prüfung)
        for key, value in kwargs.items():
            if hasattr(character, key):
                setattr(character, key, value)
        
        # Änderungen speichern
        self._save_characters()
        return True
    
    def delete_character(self, character_id: str) -> bool:
        """Löscht einen Charakter.
        
        Args:
            character_id: ID des zu löschenden Charakters
            
        Returns:
            True wenn erfolgreich, False wenn Charakter nicht gefunden
        """
        if character_id in self.characters:
            del self.characters[character_id]
            self._save_characters()
            return True
        return False
    
    def count_characters(self) -> int:
        """Gibt die Anzahl der gespeicherten Charaktere zurück.
        
        Returns:
            Anzahl der Charaktere im Dictionary
        """
        return len(self.characters)