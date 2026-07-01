# Record Studio - Hauptanwendung
# Diese Datei startet das Tkinter-Fenster der Anwendung.

# Importiert die Tkinter-Bibliothek für GUI-Fenster
import tkinter as tk
# Importiert das font-Modul für Schriftarten-Einstellungen
from tkinter import font


class RecordStudioApp(tk.Tk):
    """Hauptklasse der Record Studio Anwendung.
    
    Erbt von tk.Tk, um das Hauptfenster zu definieren.
    In zukünftigen Stunden können hier weitere Module (Frames)
    eingehängt werden.
    """
    
    def __init__(self):
        # Ruft den Konstruktor der Elternklasse (tk.Tk) auf
        super().__init__()
        
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
        welcome_label.place(relx=0.5, rely=0.5, anchor="center")


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