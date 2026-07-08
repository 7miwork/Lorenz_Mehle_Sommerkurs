# Record Studio - Hauptanwendung
# Diese Datei startet das Tkinter-Fenster der Anwendung.
# Inkludiert Benutzer-Profile Funktionalität

# Importiert die Tkinter-Bibliothek für GUI-Fenster
import tkinter as tk
# Importiert das font-Modul für Schriftarten-Einstellungen
from tkinter import font, ttk

# Importiert den ProfileManager für Benutzerprofile
from profiles.profile_manager import ProfileManager


class RecordStudioApp(tk.Tk):
    """Hauptklasse der Record Studio Anwendung.
    
    Erbt von tk.Tk, um das Hauptfenster zu definieren.
    In zukünftigen Stunden können hier weitere Module (Frames)
    eingehängt werden.
    """
    
    def __init__(self):
        # Ruft den Konstruktor der Elternklasse (tk.Tk) auf
        super().__init__()
        
        # Initialisiert den Profil-Manager
        self.profile_manager = ProfileManager()
        
        # Setzt den Titel des Fensters (erscheint in der Titelleiste)
        self.title("Record Studio")
        # Definiert die Startgröße des Fensters (Breite x Höhe in Pixeln)
        self.geometry("1280x800")
        
        # Legt fest, dass das Fenster nicht kleiner als 800x600 Pixel werden kann
        self.minsize(800, 600)
        
        # Ruft die Methode auf, die das Fenster zentriert
        self._center_window()
        
        # Ruft die Methode auf, die die Benutzeroberfläche erstellt
        self._build_ui()
        
        # Zeigt die geladenen Profile beim Start an
        self._show_loaded_profiles()
    
    def _show_loaded_profiles(self):
        """Zeigt die geladenen Benutzerprofile in der Konsole an."""
        users = self.profile_manager.get_all_users()
        print(f"Geladene Benutzerprofile: {len(users)}")
        for user in users:
            print(f"  - {user.name} ({user.role})")
    
    def _center_window(self):
        """Berechnet die Position, damit das Fenster zentriert erscheint."""
        # Fragt die Breite des Bildschirms in Pixeln ab
        screen_width = self.winfo_screenwidth()
        # Fragt die Höhe des Bildschirms in Pixeln ab
        screen_height = self.winfo_screenheight()
        
        # Definiert die gewünschte Fensterbreite
        window_width = 1280
        # Definiert die gewünschte Fensterhöhe
        window_height = 800
        
        # Berechnet die X-Position (von links), damit das Fenster zentriert ist
        x_position = (screen_width - window_width) // 2
        # Berechnet die Y-Position (von oben), damit das Fenster zentriert ist
        y_position = (screen_height - window_height) // 2
        
        # Setzt die Fenstergeometrie mit Größe und Position
        self.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    
    def _build_ui(self):
        """Erstellt die Benutzeroberfläche."""
        # Erstellt ein Font-Objekt mit Arial, Größe 24 und fett
        heading_font = font.Font(family="Arial", size=24, weight="bold")
        
        # Erstellt ein Text-Label im Fenster mit dem Willkommenstext
        welcome_label = tk.Label(
            self,
            text="Record Studio – Willkommen",
            font=heading_font
        )
        
        # Platziert das Label in der Mitte des Fensters
        welcome_label.place(relx=0.5, rely=0.4, anchor="center")
        
        # ---------- BENUTZER-AUSWAHL ----------
        self.current_user = None  # Aktuell ausgewählter Benutzer
        
        # FEHLER 6: Label mit falscher Farbe (grau statt schwarz)
        profile_label = tk.Label(
            self,
            text="Wähle dein Profil:",  # FEHLER 7: "d" statt "dein" - Typo!
            font=font.Font(family="Arial", size=14),
            fg="gray"  # FEHLER: Sollte "black" sein
        )
        profile_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Dropdown für Benutzerauswahl
        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(
            self,
            textvariable=self.profile_var,
            values=self._get_user_display_names(),
            state="readonly",
            width=30  # FEHLER 8: Breite zu schmal
        )
        self.profile_combo.place(relx=0.5, rely=0.55, anchor="center")
        
        # Login Button
        self.login_btn = tk.Button(
            self,
            text="Profil auswählen",
            command=self._select_profile,
            font=font.Font(family="Arial", size=12, weight="bold")
        )
        self.login_btn.place(relx=0.5, rely=0.62, anchor="center")
        
        # Status Label
        self.status_label = tk.Label(
            self,
            text="",
            font=font.Font(family="Arial", size=10)
        )
        self.status_label.place(relx=0.5, rely=0.7, anchor="center")
    
    def _get_user_display_names(self) -> list:
        """Gibt Liste der Anzeigenamen zurück."""
        users = self.profile_manager.get_all_users()
        return [f"{u.name} ({u.role})" for u in users]
    
    def _select_profile(self):
        """Wird aufgerufen, wenn ein Profil ausgewählt wird."""
        display_name = self.profile_var.get()
        if not display_name:
            self.status_label.config(text="Bitte wähle ein Profil aus!", fg="red")
            return
        
        # Finde den User anhand des Anzeigenamens
        users = self.profile_manager.get_all_users()
        for user in users:
            if f"{user.name} ({user.role})" == display_name:
                self.current_user = user
                user.update_last_login()
                self.profile_manager._save_profiles()
                self.status_label.config(
                    text=f"Willkommen, {user.name}!", 
                    fg="green"
                )
                # FEHLER 9: Button verschwindet nicht richtig - fg statt state
                self.login_btn.config(state="disabled")
                break


def main():
    """Einstiegspunkt der Anwendung."""
    # Erstellt eine Instanz der Hauptanwendung
    app = RecordStudioApp()
    # Startet die Tkinter-Ereignisschleife (wartet auf Benutzereingaben)
    app.mainloop()


# Standard-Guard: Nur ausführen, wenn diese Datei direkt gestartet wird
if __name__ == "__main__":
    # Ruft die main-Funktion auf
    main()