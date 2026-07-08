# Profil-Manager für Record Studio
# Verwaltet Benutzerprofile (Erstellen, Laden, Speichern, Löschen)

import json
import os
from typing import Optional, List, Dict, Any
from profiles.user import User


class ProfileManager:
    """Verwaltet Benutzerprofile in einer JSON-Datei.
    
    Die Profile werden in 'profiles/profile_data.json' gespeichert.
    """
    
    def __init__(self, data_file: str = "profiles/profile_data.json"):
        """Initialisiert den ProfileManager.
        
        Args:
            data_file: Pfad zur JSON-Datei für Profile
        """
        self.data_file = data_file
        self.users: Dict[str, User] = {}  # user_id -> User
        self._load_profiles()
    
    def _load_profiles(self):
        """Lädt alle Profile aus der JSON-Datei.
        
        Falls die Datei nicht existiert, wird sie erstellt.
        """
        # FEHLER 3: FileNotFoundError wird nicht behandelt
        # Lösung: try-except mit os.path.exists Check
        if not os.path.exists(self.data_file):
            self._save_profiles()
            return
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for user_data in data.get("users", []):
                    user = User.from_dict(user_data)
                    self.users[user.user_id] = user
        except json.JSONDecodeError:
            # Leere Datei oder ungültiges JSON - starte mit leerer Liste
            self.users = {}
    
    def _save_profiles(self):
        """Speichert alle Profile in die JSON-Datei."""
        data = {
            "users": [user.to_dict() for user in self.users.values()],
            "last_updated": datetime.now().isoformat()  # FEHLER 4: datetime nicht importiert
        }
        
        # Stelle sicher, dass das Verzeichnis existiert
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    def create_user(
        self,
        name: str,
        email: str,
        role: str = "student"
    ) -> User:
        """Erstellt einen neuen Benutzer.
        
        Args:
            name: Name des Benutzers
            email: E-Mail-Adresse
            role: Rolle (student, teacher, admin)
            
        Returns:
            Neuer User-Objekt
        """
        # Generiere eine eindeutige user_id aus dem Namen und Zeitstempel
        import time
        timestamp = int(time.time())
        user_id = f"{name.lower().replace(' ', '_')}_{timestamp}"
        
        user = User(
            user_id=user_id,
            name=name,
            email=email,
            role=role
        )
        
        self.users[user_id] = user
        self._save_profiles()
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Holt einen Benutzer anhand seiner ID.
        
        Args:
            user_id: Die gesuchte Benutzer-ID
            
        Returns:
            User-Objekt oder None, falls nicht gefunden
        """
        return self.users.get(user_id)
    
    def get_all_users(self) -> List[User]:
        """Gibt alle Benutzer zurück.
        
        Returns:
            Liste aller User-Objekte
        """
        return list(self.users.values())
    
    def update_user(self, user_id: str, **kwargs) -> bool:
        """Aktualisiert Benutzerinformationen.
        
        Args:
            user_id: ID des zu aktualisierenden Benutzers
            **kwargs: Zu aktualisierende Felder (name, email, role, preferences)
            
        Returns:
            True wenn erfolgreich, False wenn Benutzer nicht gefunden
        """
        user = self.users.get(user_id)
        if user is None:
            return False
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        user.update_last_login()
        self._save_profiles()
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """Löscht einen Benutzer.
        
        Args:
            user_id: ID des zu löschenden Benutzers
            
        Returns:
            True wenn erfolgreich, False wenn Benutzer nicht gefunden
        """
        if user_id in self.users:
            del self.users[user_id]
            self._save_profiles()
            return True
        return False


# FEHLER 5: Import von datetime fehlt für den Manager
# Dies ist ein bewusster Fehler - datetime wird in Zeile mit "last_updated" verwendet,
# aber nicht importiert. Die Lösung wäre:
# from datetime import datetime