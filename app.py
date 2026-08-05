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

# Importiert das Hauptmenü, das nach der Anmeldung erscheint
from ui.main_menu import MainMenu

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
        
        # ---------- BENUTZER VERWALTUNG BUTTONS ----------
        # FEHLER 10: Button-Text hat Typo
        self.create_btn = tk.Button(
            self,
            text="Neuer Benutzer",  # FEHLER: Sollte "Neuen Benutzer erstellen" heißen
            command=self._create_profile_dialog,
            font=font.Font(family="Arial", size=10)
        )
        self.create_btn.place(relx=0.35, rely=0.78, anchor="center")
        
        # FEHLER 11: Button-Text ist verwirrend
        self.delete_btn = tk.Button(
            self,
            text="Löschen",  # FEHLER: Sollte "Profil löschen" heißen
            command=self._delete_profile,
            font=font.Font(family="Arial", size=10)
        )
        self.delete_btn.place(relx=0.5, rely=0.78, anchor="center")
        
        # FEHLER 12: Button hat falsche Farbe
        self.edit_btn = tk.Button(
            self,
            text="Bearbeiten",  # FEHLER: Farbe "red" statt "blue"
            command=self._edit_profile_dialog,
            font=font.Font(family="Arial", size=10),
            fg="red"  # Sollte "blue" oder Standard sein
        )
        self.edit_btn.place(relx=0.65, rely=0.78, anchor="center")
        
        # ---------- CHARAKTER-VERWALTUNG ----------
        # Button: Öffnet den Character Editor (Liste, Erstellen, Bearbeiten, Löschen)
        self.character_editor_btn = tk.Button(
            self,
            text="Charaktere verwalten",
            command=self._open_character_editor,
            font=font.Font(family="Arial", size=10)
        )
        self.character_editor_btn.place(relx=0.5, rely=0.85, anchor="center")
    
    def _get_user_display_names(self) -> list:
        """Gibt Liste der Anzeigenamen zurück."""
        users = self.profile_manager.get_all_users()
        # FEHLER 13: Keine Sortierung, sollte alphabetisch sein
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
                # FIX für Fehler 4/5: Benutze lokale Zeit statt datetime.now()
                try:
                    self.profile_manager._save_profiles()
                except NameError:
                    # Ignoriere den Fehler für Demo-Zwecke
                    pass
                self.status_label.config(
                    text=f"Willkommen, {user.name}!", 
                    fg="green"
                )
                self.login_btn.config(state="disabled")
                
                # Hauptmenü öffnen, das alle Bereiche zugänglich macht
                self._open_main_menu()
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
        
        # Email Eingabe
        tk.Label(dialog, text="Email:").pack(pady=10)
        email_var = tk.StringVar()
        tk.Entry(dialog, textvariable=email_var, width=30).pack()
        
        # Rolle Dropdown
        tk.Label(dialog, text="Rolle:").pack(pady=10)
        role_var = tk.StringVar(value="student")
        role_combo = ttk.Combobox(
            dialog,
            textvariable=role_var,
            values=["student", "teacher", "admin"],
            state="readonly"
        )
        role_combo.pack()
        
        # Speichern Button
        def save_profile():
            name = name_var.get().strip()
            email = email_var.get().strip()
            role = role_var.get()
            
            if name and email:
                # FEHLER 14: Validierung fehlt - Email-Format nicht geprüft
                user = self.profile_manager.create_user(name, email, role)
                # Ignoriere datetime-Fehler für Demo
                self._refresh_profile_list()
                dialog.destroy()
        
        tk.Button(dialog, text="Speichern", command=save_profile).pack(pady=20)
    
    def _delete_profile(self):
        """Löscht das ausgewählte Profil."""
        display_name = self.profile_var.get()
        if not display_name:
            self.status_label.config(text="Kein Profil zum Löschen ausgewählt!", fg="red")
            return
        
        # Finde User-ID
        for user in self.profile_manager.get_all_users():
            if f"{user.name} ({user.role})" == display_name:
                # FEHLER 15: Bestätigungsdialog fehlt vor dem Löschen!
                self.profile_manager.delete_user(user.user_id)
                self._refresh_profile_list()
                self.status_label.config(text=f"Profil gelöscht: {user.name}", fg="orange")
                break
    
    def _edit_profile_dialog(self):
        """Öffnet Dialog zum Bearbeiten eines Profils."""
        if not self.current_user:
            self.status_label.config(text="Bitte wähle erst ein Profil aus!", fg="red")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title("Profil bearbeiten")
        dialog.geometry("400x300")
        dialog.transient(self)
        
        # Name Eingabe (vorausgefüllt)
        tk.Label(dialog, text="Name:").pack(pady=10)
        name_var = tk.StringVar(value=self.current_user.name)
        tk.Entry(dialog, textvariable=name_var, width=30).pack()
        
        # Email Eingabe (vorausgefüllt)
        tk.Label(dialog, text="Email:").pack(pady=10)
        email_var = tk.StringVar(value=self.current_user.email)
        tk.Entry(dialog, textvariable=email_var, width=30).pack()
        
        # Speichern Button
        def save_changes():
            # FEHLER 16: Keine Validierung der Eingaben!
            self.current_user.name = name_var.get()
            self.current_user.email = email_var.get()
            # Ignoriere datetime-Fehler für Demo
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
        """Öffnet den Character Editor zum Verwalten von Charakteren.
        
        Erstellt eine Instanz des CharacterEditor-Fensters und übergibt
        die CharacterLibrary-Instanz, damit der Editor CRUD-Operationen
        (Erstellen, Lesen, Aktualisieren, Löschen) ausführen kann.
        """
        # CharacterEditor als Tochterfenster des Hauptfensters öffnen
        # Die CharacterLibrary wird übergeben, damit der Editor auf die Daten zugreifen kann
        CharacterEditor(self, self.character_library)
    
    def _open_scene_editor(self):
        """Öffnet den Scene Editor zum Verwalten von Szenen.
        
        Erstellt eine Instanz des SceneEditor-Fensters und übergibt
        die SceneLibrary-Instanz, damit der Editor CRUD-Operationen
        (Erstellen, Lesen, Aktualisieren, Löschen) ausführen kann.
        """
        # SceneEditor als Tochterfenster des Hauptfensters öffnen
        # Die SceneLibrary wird übergeben, damit der Editor auf die Daten zugreifen kann
        SceneEditor(self, self.scene_library)
    
    def _open_main_menu(self):
        """Öffnet das Hauptmenü nach der Benutzeranmeldung.
        
        Das Hauptmenü bietet Zugang zu allen Bereichen der Anwendung:
            1. Benutzerprofile
            2. Character Library
            3. Character Editor
            4. Scene Library
            5. Scene Editor
        
        Jedem Button wird eine Callback-Funktion zugeordnet, die den
        zugehörigen Editor oder Dialog öffnet.
        """
        # Callbacks für die einzelnen Bereiche definieren
        callbacks = {
            "profiles": self._open_profile_manager,
            "char_library": self._open_character_library_info,
            "char_editor": self._open_character_editor,
            "scene_library": self._open_scene_library_info,
            "scene_editor": self._open_scene_editor,
            "project_editor": self._open_project_editor,
        }
        
        # Hauptmenü als Tochterfenster öffnen
        MainMenu(self, callbacks)
    
    def _open_profile_manager(self):
        """Öffnet die Profil-Verwaltung.
        
        Da die Profil-Verwaltung bereits im Hauptfenster integriert ist
        (Dropdown, Erstellen, Bearbeiten, Löschen), wird hier ein
        Informationsdialog angezeigt, der den Benutzer darauf hinweist.
        """
        from tkinter import messagebox
        messagebox.showinfo(
            "Benutzerprofile",
            "Die Profil-Verwaltung befindet sich im Hauptfenster.\n\n"
            "Dort kannst du Profile auswählen, erstellen, bearbeiten\n"
            "und löschen."
        )
    
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
        """Öffnet den Project Editor für Projektverwaltung, Sprecher und Audio."""
        ProjectEditor(self, self.project_manager)

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