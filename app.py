# Record Studio - Hauptanwendung
# Diese Datei startet das Tkinter-Fenster der Anwendung.
# Inkludiert Benutzer-Profile Funktionalität

# Importiert die Tkinter-Bibliothek für GUI-Fenster
import tkinter as tk
# Importiert das font-Modul für Schriftarten-Einstellungen
from tkinter import font, ttk

# Importiert den ProfileManager für Benutzerprofile
from profiles.profile_manager import ProfileManager

# Importiert die CharacterLibrary für Charakter-Verwaltung
from core.character_library import CharacterLibrary

# Importiert die SceneLibrary für Szenen-Verwaltung
from core.scene_library import SceneLibrary

# Importiert den CharacterEditor für die grafische Charakter-Verwaltung
from ui.character_editor import CharacterEditor

# Importiert den SceneEditor für die grafische Szenen-Verwaltung
from ui.scene_editor import SceneEditor

# Importiert den ProjectEditor für Projektverwaltung, Sprecher und Audio
from ui.project_editor import ProjectEditor

# Importiert den SpeakerOrganizer für projektbezogene Sprecherverwaltung
from ui.speaker_organizer import SpeakerOrganizer

# Importiert den SpeakerDatabaseEditor für die globale Sprecher-Datenbank
from ui.speaker_database import SpeakerDatabaseEditor

# Importiert den TimelineEditor für die globale Timeline-Verwaltung
from ui.timeline_editor import TimelineEditor

# Importiert die Manager für Projekte, Dateien und Audio
import subprocess
import sys
import os


def _ensure_dependencies() -> bool:
    """Prüft fehlende Pakete, installiert sie still und startet die App neu.

    Verhalten:
    - Wenn Pakete fehlen, wird `pip install <missing...>` still (stdout/stderr -> DEVNULL)
      ausgeführt.
    - Bei erfolgreicher Installation wird der aktuelle Python-Prozess durch einen
      Neustart (`os.execv`) ersetzt, so dass die neuen Pakete sofort verfügbar sind.
    - Bei Installationsfehlern kehrt die Funktion mit False zurück.
    """
    required = ["sounddevice", "numpy"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except Exception:
            missing.append(pkg)

    if not missing:
        return True

    # Versuche stille Installation der fehlenden Pakete
    try:
        cmd = [sys.executable, "-m", "pip", "install"] + missing
        with open(os.devnull, "wb") as devnull:
            subprocess.check_call(cmd, stdout=devnull, stderr=devnull)

        # Nach erfolgreicher Installation App neu starten (ersetze Prozess)
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception:
        # Installation fehlgeschlagen
        return False


# Prüfe Abhängigkeiten vor weiteren Imports
if not _ensure_dependencies():
    sys.exit(1)

# Manager-Importe, nach Abhängigkeitsprüfung
from core.project_manager import ProjectManager
from core.file_manager import FileManager
from core.audio_manager import AudioManager
from core.speaker_library import SpeakerLibrary
from core.timeline_library import TimelineLibrary


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
        
        # Initialisiert die Charakter-Bibliothek
        self.character_library = CharacterLibrary()
        
        # Initialisiert die Szenen-Bibliothek
        self.scene_library = SceneLibrary()

        # Initialisiert die Manager für Projekte, Dateien und Audio
        self.file_manager = FileManager()
        self.audio_manager = AudioManager()
        self.project_manager = ProjectManager(self.file_manager, self.audio_manager)
        self.speaker_library = SpeakerLibrary()
        self.timeline_library = TimelineLibrary()
        
        # Setzt den Titel des Fensters (erscheint in der Titelleiste)
        self.title("Record Studio")
        # Definiert die Startgröße des Fensters (Breite x Höhe in Pixeln)
        self.geometry("1280x800")
        
        # Legt fest, dass das Fenster nicht kleiner als 800x600 Pixel werden kann
        self.minsize(800, 600)
        
        # Ruft die Methode auf, die das Fenster zentriert
        self._center_window()
        
        # Aktuell angemeldeter Benutzer (None = nicht angemeldet)
        self.current_user = None

        # Ruft die Methode auf, die die Benutzeroberfläche erstellt
        self._build_ui()
        # Menubar hinzufügen (Sprecher -> Organisieren)
        self._add_menubar()
        
        # Zeigt die geladenen Profile beim Start an
        self._show_loaded_profiles()
        
        # Zeigt die geladenen Charaktere beim Start an
        self._show_loaded_characters()
        
        # Zeigt die geladenen Szenen beim Start an
        self._show_loaded_scenes()
    
    def _show_loaded_profiles(self):
        """Zeigt die geladenen Benutzerprofile in der Konsole an."""
        users = self.profile_manager.get_all_users()
        print(f"Geladene Benutzerprofile: {len(users)}")
        for user in users:
            print(f"  - {user.name} ({user.role})")
    
    def _show_loaded_characters(self):
        """Zeigt die geladenen Charaktere in der Konsole an."""
        characters = self.character_library.get_all_characters()
        print(f"Geladene Charaktere: {len(characters)}")
        for character in characters:
            print(f"  - {character.name} ({character.character_id})")
    
    def _show_loaded_scenes(self):
        """Zeigt die geladenen Szenen in der Konsole an."""
        scenes = self.scene_library.get_all_scenes()
        print(f"Geladene Szenen: {len(scenes)}")
        for scene in scenes:
            print(f"  - {scene.name} ({scene.scene_id})")
    
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
        """Erstellt die Hauptoberfläche mit Navigation und Inhaltspanel."""
        # ---------- LINKES NAVIGATIONSFELD ----------
        self.nav_frame = tk.Frame(self, width=260, bg="#f0f0f0")
        self.nav_frame.pack(side="left", fill="y")
        self.nav_frame.pack_propagate(False)

        heading_font = font.Font(family="Arial", size=18, weight="bold")
        tk.Label(
            self.nav_frame,
            text="Record Studio",
            font=heading_font,
            bg="#f0f0f0"
        ).pack(pady=(20, 10))

        self.nav_buttons = {}
        nav_items = [
            ("Profile", "profiles"),
            ("Charaktere verwalten", "character_editor"),
            ("Szenen verwalten", "scene_editor"),
            ("Projekte & Aufnahme", "project_editor"),
            ("Sprecher organisieren", "speaker_organizer"),
            ("Speaker Datenbank", "speaker_database"),
            ("Timeline verwalten", "timeline_editor"),
        ]
        for label, key in nav_items:
            btn = tk.Button(
                self.nav_frame,
                text=label,
                anchor="w",
                width=24,
                command=lambda key=key: self._show_view(key)
            )
            btn.pack(fill="x", padx=16, pady=4)
            btn.config(state="disabled")
            self.nav_buttons[key] = btn

        # ---------- INHALTSPANEL ----------
        self.content_frame = tk.Frame(self, bg="white")
        self.content_frame.pack(side="left", fill="both", expand=True)

        self.views = {}
        self.views["profiles"] = self._build_profile_view()
        self.views["character_editor"] = CharacterEditor(self.content_frame, self.character_library)
        self.views["scene_editor"] = SceneEditor(self.content_frame, self.scene_library)
        self.views["project_editor"] = ProjectEditor(self.content_frame, self.project_manager, self.speaker_library)
        self.views["speaker_organizer"] = SpeakerOrganizer(self.content_frame, self.project_manager)
        self.views["speaker_database"] = SpeakerDatabaseEditor(self.content_frame, self.speaker_library, self.audio_manager)
        self.views["timeline_editor"] = TimelineEditor(self.content_frame, self.timeline_library, self.speaker_library)

        self._disable_navigation()
        self._show_view("profiles")

    def _build_profile_view(self):
        frame = tk.Frame(self.content_frame, bg="white")

        heading_font = font.Font(family="Arial", size=18, weight="bold")
        tk.Label(frame, text="Profile", font=heading_font, bg="white").pack(anchor="w", padx=20, pady=(20, 10))

        form_frame = tk.Frame(frame, bg="white")
        form_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(form_frame, text="Wähle ein Profil:", bg="white", font=font.Font(size=12)).grid(row=0, column=0, sticky="w", pady=4)
        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(
            form_frame,
            textvariable=self.profile_var,
            values=self._get_user_display_names(),
            state="readonly",
            width=35
        )
        self.profile_combo.grid(row=0, column=1, sticky="w", padx=8)

        self.login_btn = tk.Button(frame, text="Profil auswählen", command=self._select_profile, font=font.Font(size=12, weight="bold"))
        self.login_btn.pack(anchor="w", padx=20, pady=(10, 4))

        self.profile_status_label = tk.Label(frame, text="Bitte melde dich an oder erstelle ein neues Profil.", bg="white", fg="black")
        self.profile_status_label.pack(anchor="w", padx=20, pady=(0, 12))

        button_frame = tk.Frame(frame, bg="white")
        button_frame.pack(anchor="w", padx=20, pady=(0, 20))

        tk.Button(button_frame, text="Neues Profil", command=self._create_profile_dialog).pack(side="left", padx=4)
        tk.Button(button_frame, text="Profil löschen", command=self._delete_profile).pack(side="left", padx=4)
        tk.Button(button_frame, text="Profil bearbeiten", command=self._edit_profile_dialog).pack(side="left", padx=4)

        return frame

    def _show_view(self, key: str):
        if key not in self.views:
            return
        for name, view in self.views.items():
            view.pack_forget()
        self.views[key].pack(fill="both", expand=True)

    def _disable_navigation(self):
        for btn in self.nav_buttons.values():
            btn.config(state="disabled")

    def _enable_navigation(self):
        for btn in self.nav_buttons.values():
            btn.config(state="normal")
    
    def _get_user_display_names(self) -> list:
        """Gibt Liste der Anzeigenamen zurück (nur der Name, ohne Rolle)."""
        users = self.profile_manager.get_all_users()
        # FEHLER 13: Keine Sortierung, sollte alphabetisch sein
        return sorted(u.name for u in users)
    
    def _select_profile(self):
        """Wird aufgerufen, wenn ein Profil ausgewählt wird."""
        display_name = self.profile_var.get()
        if not display_name:
            self.profile_status_label.config(text="Bitte wähle ein Profil aus!", fg="red")
            return
        
        users = self.profile_manager.get_all_users()
        for user in users:
            if user.name == display_name:
                self.current_user = user
                user.update_last_login()
                try:
                    self.profile_manager._save_profiles()
                except NameError:
                    pass
                self.profile_status_label.config(
                    text=f"Willkommen, {user.name}!", 
                    fg="green"
                )
                self.login_btn.config(state="disabled")
                self._enable_navigation()
                self._show_view("profiles")
                break
    
    def _create_profile_dialog(self):
        """Öffnet Dialog zum Erstellen eines neuen Profils."""
        dialog = tk.Toplevel(self)
        dialog.title("Neues Profil erstellen")
        dialog.geometry("400x300")
        dialog.transient(self)
        
        # Name Eingabe
        tk.Label(dialog, text="Name:").pack(pady=10)
        name_var = tk.StringVar()
        tk.Entry(dialog, textvariable=name_var, width=30).pack()
        
        # Speichern Button
        def save_profile():
            name = name_var.get().strip()
            
            if name:
                # E-Mail und Rolle werden nicht mehr abgefragt,
                # jeder neue Benutzer ist automatisch Admin
                self.profile_manager.create_user(name)
                self._refresh_profile_list()
                dialog.destroy()
        
        tk.Button(dialog, text="Speichern", command=save_profile).pack(pady=20)
    
    def _delete_profile(self):
        """Löscht das ausgewählte Profil."""
        display_name = self.profile_var.get()
        if not display_name:
            self.profile_status_label.config(text="Kein Profil zum Löschen ausgewählt!", fg="red")
            return
        
        for user in self.profile_manager.get_all_users():
            if user.name == display_name:
                self.profile_manager.delete_user(user.user_id)
                self._refresh_profile_list()
                self.profile_status_label.config(text=f"Profil gelöscht: {user.name}", fg="orange")
                break
    
    def _edit_profile_dialog(self):
        """Öffnet Dialog zum Bearbeiten eines Profils."""
        if not self.current_user:
            self.profile_status_label.config(text="Bitte wähle erst ein Profil aus!", fg="red")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title("Profil bearbeiten")
        dialog.geometry("400x300")
        dialog.transient(self)
        
        # Name Eingabe (vorausgefüllt)
        tk.Label(dialog, text="Name:").pack(pady=10)
        name_var = tk.StringVar(value=self.current_user.name)
        tk.Entry(dialog, textvariable=name_var, width=30).pack()
        
        # Speichern Button
        def save_changes():
            # Nur der Name wird bearbeitet (E-Mail und Rolle sind deaktiviert)
            new_name = name_var.get().strip()
            if not new_name:
                return
            self.current_user.name = new_name
            try:
                self.profile_manager._save_profiles()
            except NameError:
                pass
            self._refresh_profile_list()
            dialog.destroy()
        
        tk.Button(dialog, text="Speichern", command=save_changes).pack(pady=20)
    
    def _refresh_profile_list(self):
        """Aktualisiert die Profil-Liste im Dropdown."""
        self.profile_combo['values'] = self._get_user_display_names()
    
    def _open_character_editor(self):
        """Wechselt zur Charakter-Verwaltung im Hauptfenster."""
        self._show_view("character_editor")
    
    def _open_scene_editor(self):
        """Wechselt zur Szenenverwaltung im Hauptfenster."""
        self._show_view("scene_editor")
    
    def _open_main_menu(self):
        """Aktiviert die linke Navigation und zeigt die Profilseite im Hauptfenster."""
        self._enable_navigation()
        self._show_view("profiles")
    
    def _open_profile_manager(self):
        """Zeigt die Profilübersicht im Hauptfenster."""
        self._show_view("profiles")
    
    def _open_character_library_info(self):
        """Öffnet einen Informationsdialog zur Character Library.
        
        Zeigt die Anzahl der gespeicherten Charaktere und eine
        Kurzbeschreibung der Character Library an.
        """
        from tkinter import messagebox
        count = self.character_library.count_characters()
        messagebox.showinfo(
            "Character Library",
            f"Character Library\n\n"
            f"Gespeicherte Charaktere: {count}\n\n"
            f"Die Character Library verwaltet alle Charaktere\n"
            f"und speichert sie in einer JSON-Datei.\n\n"
            f"Über den 'Character Editor' kannst du Charaktere\n"
            f"erstellen, bearbeiten und löschen."
        )
    
    def _open_project_editor(self):
        """Wechselt zur Projekt- und Aufnahmeverwaltung im Hauptfenster."""
        self._show_view("project_editor")

    def _open_speaker_organizer(self):
        """Wechselt zur Sprecher-Organisation im Hauptfenster."""
        if not self.project_manager.current_project:
            from tkinter import messagebox
            messagebox.showwarning("Kein Projekt", "Bitte zuerst ein Projekt öffnen.")
            return
        self._show_view("speaker_organizer")

    def _open_speaker_database(self):
        """Wechselt zur globalen Speaker-Datenbank im Hauptfenster."""
        self._show_view("speaker_database")

    def _open_timeline_editor(self):
        """Wechselt zur globalen Timeline im Hauptfenster."""
        self._show_view("timeline_editor")

    def _add_menubar(self):
        """Ergänzt eine einfache Menüleiste mit einem Sprecher-Menü."""
        menubar = tk.Menu(self)
        speaker_menu = tk.Menu(menubar, tearoff=0)
        speaker_menu.add_command(label="Organisieren", command=self._open_speaker_organizer)
        menubar.add_cascade(label="Sprecher", menu=speaker_menu)
        self.config(menu=menubar)

    def _open_scene_library_info(self):
        """Öffnet einen Informationsdialog zur Scene Library.
        
        Zeigt die Anzahl der gespeicherten Szenen und eine
        Kurzbeschreibung der Scene Library an.
        """
        from tkinter import messagebox
        count = self.scene_library.count_scenes()
        messagebox.showinfo(
            "Scene Library",
            f"Scene Library\n\n"
            f"Gespeicherte Szenen: {count}\n\n"
            f"Die Scene Library verwaltet alle Szenen\n"
            f"und speichert sie in einer JSON-Datei.\n\n"
            f"Über den 'Scene Editor' kannst du Szenen\n"
            f"erstellen, bearbeiten und löschen."
        )


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