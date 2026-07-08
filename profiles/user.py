# Benutzer-Modell für Record Studio
# Definiert die Datenstruktur eines Benutzerprofils

import json
from datetime import datetime
from typing import Optional, List, Dict, Any


class User:
    """Repräsentiert einen Benutzer mit Profilinformationen.
    
    Attribute:
        user_id: Eindeutige ID des Benutzers
        name: Vollständiger Name
        email: E-Mail-Adresse
        role: Rolle (student, teacher, admin)
        created_at: Erstellungsdatum
        last_login: Letzter Login-Zeitpunkt
        preferences: Benutzereinstellungen als Dictionary
    """
    
    def __init__(
        self,
        user_id: str,
        name: str,
        email: str,
        role: str = "student",
        preferences: Optional[Dict[str, Any]] = None
    ):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.role = role  # "student", "teacher", oder "admin"
        self.created_at = datetime.now().isoformat()
        self.last_login = None
        # FEHLER 1: preferences könnte None sein, aber wir wollen ein Dictionary
        # Lösung: Standardwert setzen, falls preferences None ist
        self.preferences = preferences if preferences is not None else {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert das User-Objekt in ein Dictionary.
        
        Returns:
            Dictionary mit allen Benutzerinformationen
        """
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "preferences": self.preferences
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Erstellt ein User-Objekt aus einem Dictionary.
        
        Args:
            data: Dictionary mit Benutzerdaten
            
        Returns:
            Neue User-Instanz
        """
        user = cls(
            user_id=data["user_id"],
            name=data["name"],
            email=data["email"],
            role=data.get("role", "student"),
            preferences=data.get("preferences")
        )
        user.created_at = data.get("created_at", datetime.now().isoformat())
        # FEHLER 2: last_login wird nicht korrekt gesetzt
        # Lösung: last_login direkt aus data holen
        user.last_login = data.get("last_login")
        return user
    
    def update_last_login(self):
        """Aktualisiert den letzten Login-Zeitpunkt."""
        self.last_login = datetime.now().isoformat()