# Character Editor für Record Studio
# Grafische Oberfläche zur Verwaltung von 2D-Charakteren (CRUD-Operationen)
# Zeigt eine Liste aller Charaktere an und ermöglicht das
# Erstellen, Bearbeiten und Löschen von Charakteren.
#
# Jeder Charakter kann mehrere Ansichten haben:
#   - front:       Vorderansicht
#   - side_left:   Seitenansicht von links
#   - side_right:  Seitenansicht von rechts
#   - back:        Rückansicht
#
# Und mehrere Bewegungs-Zustände (Poses):
#   - idle:    Stehend / ruhig
#   - walking: Laufend
#   - talking: Sprechend (Mund offen)
#
# Bilder können auf zwei Arten erstellt werden:
#   1. "Durchsuchen..." – eine vorhandene Datei importieren
#   2. "Extern" – das OS-Zeichenprogramm (Paint/Freeform/GIMP) öffnen

# Importiert die Tkinter-Bibliothek für GUI-Fenster
import tkinter as tk
# Importiert das ttk-Modul für erweiterte Widgets (Treeview), messagebox für Dialoge
# und filedialog für Dateiauswahl-Dialoge
from tkinter import ttk, messagebox, filedialog
# tkinter.font muss explizit importiert werden, damit tk.font.* funktioniert
import tkinter.font

# Importiert die CharacterLibrary für CRUD-Operationen auf Charakteren
from core.character_library import CharacterLibrary

# Importiert die Character-Klasse für AVAILABLE_VIEWS und AVAILABLE_POSES
from core.character import Character

# Importiert shutil zum Kopieren von Bilddateien in das assets/-Verzeichnis
import shutil

# Importiert os für Pfad-Operationen (Verzeichnisse prüfen, Dateinamen extrahieren)
import os

# Importiert die Hilfsfunktionen für OS-Erkennung und externes Zeichenprogramm
from tools.drawing_helper import detect_os, get_drawing_app_name, open_in_drawing_app, create_blank_image


# Anzeigename für Ansichten in der GUI
VIEW_LABELS = {
    "front": "Vorderansicht",
    "side_left": "Seitenansicht (links)",
    "side_right": "Seitenansicht (rechts)",
    "back": "Rückansicht",
}

# Anzeigename für Bewegungs-Zustände in der GUI
POSE_LABELS = {
    "idle": "Stehend (idle)",
    "walking": "Laufend (walking)",
    "talking": "Sprechend (talking)",
}


class CharacterEditor(tk.Frame):
    """Grafischer Editor für die Character Library.

    Erbt von tk.Frame, damit er als Ansicht im Hauptfenster
    (content_frame) eingebettet werden kann.

    Die Klasse zeigt alle Charaktere in einer ttk.Treeview-Liste an
    und bietet drei Aktionen: Neu erstellen, Bearbeiten und Löschen.
    Jede Aktion öffnet bei Bedarf einen Toplevel-Dialog mit Eingabefeldern.

    Attribute:
        character_library: Die CharacterLibrary-Instanz, die die Daten verwaltet
        selected_character_id: ID des aktuell in der Liste ausgewählten Charakters
        tree: Die ttk.Treeview-Widget mit den Spalten Name und Beschreibung
    """

    def __init__(self, parent, character_library: CharacterLibrary):
        """Initialisiert den Character Editor.

        Args:
            parent: Elternfenster (RecordStudioApp-Instanz)
            character_library: CharacterLibrary-Instanz für CRUD-Operationen
        """
        # Ruft den Konstruktor der Elternklasse (tk.Frame) auf
        super().__init__(parent)

        # Referenz auf die CharacterLibrary speichern, um später CRUD-Operationen auszuführen
        self.character_library = character_library

        # ID des aktuell ausgewählten Charakters (None, wenn nichts ausgewählt)
        self.selected_character_id = None

        # Fenster-Titel festlegen (erscheint in der Titelleiste)
        # (character_editor.py: Frame besitzt kein title() – Zeile entfernt)
        # Fenstergröße festlegen: 700 Pixel breit, 450 Pixel hoch
        # (character_editor.py: Frame besitzt kein geometry() – Zeile entfernt)

        # Die Benutzeroberfläche erstellen
        self._build_ui()

        # Die Liste der Charaktere beim Start initial befüllen
        self._refresh_list()

    def _build_ui(self):
        """Erstellt alle sichtbaren Elemente des Editor-Fensters.

        Aufbau:
        - Oben: ttk.Treeview mit drei Spalten (Name, Ansichten, Beschreibung)
        - Darunter: Drei Buttons (Neuer Charakter, Bearbeiten, Löschen)
        - Unten: Schließen-Button
        """
        # ---------- TREVIEW (Charakterliste) ----------
        # ttk.Treeview mit drei benannten Spalten erstellen
        self.tree = ttk.Treeview(
            self,
            columns=("name", "views", "description"),
            show="headings"
        )

        # Spaltenüberschriften festlegen
        self.tree.heading("name", text="Name")
        self.tree.heading("views", text="Ansichten")
        self.tree.heading("description", text="Beschreibung")

        # Spaltenbreiten festlegen
        self.tree.column("name", width=180)
        self.tree.column("views", width=120)
        self.tree.column("description", width=350)

        # Treeview platzieren
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Wenn der Benutzer eine Zeile in der Treeview auswählt,
        # wird _on_tree_select aufgerufen
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # ---------- BUTTON-LEISTE ----------
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        # Button: Neuer Charakter
        self.new_btn = tk.Button(
            button_frame,
            text="Neuer Charakter",
            command=self._open_create_dialog,
            font=tk.font.Font(family="Arial", size=10)
        )
        self.new_btn.pack(side="left", padx=5)

        # Button: Bearbeiten
        self.edit_btn = tk.Button(
            button_frame,
            text="Bearbeiten",
            command=self._open_edit_dialog,
            state="disabled",
            font=tk.font.Font(family="Arial", size=10)
        )
        self.edit_btn.pack(side="left", padx=5)

        # Button: Löschen
        self.delete_btn = tk.Button(
            button_frame,
            text="Löschen",
            command=self._delete_character,
            state="disabled",
            font=tk.font.Font(family="Arial", size=10)
        )
        self.delete_btn.pack(side="left", padx=5)

        # ---------- SCHLIESSEN-BUTTON ----------
        self.close_btn = tk.Button(
            self,
            text="Schließen",
            command=self.destroy,
            font=tk.font.Font(family="Arial", size=10)
        )
        self.close_btn.pack(pady=10)

    def _refresh_list(self):
        """Lädt alle Charaktere neu und füllt die Treeview-Liste auf."""
        # Alle vorhandenen Einträge in der Treeview entfernen
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Alle Charaktere laden (alphabetisch sortiert)
        characters = self.character_library.get_all_characters()

        # Jeden Charakter als neue Zeile einfügen
        for character in characters:
            # Anzahl der gesetzten Ansichten anzeigen
            view_count = len([v for v in character.views.values() if v])
            view_text = f"{view_count}/{len(Character.AVAILABLE_VIEWS)}"
            self.tree.insert(
                "",
                "end",
                iid=character.character_id,
                values=(character.name, view_text, character.description)
            )

    def _on_tree_select(self, event):
        """Wird aufgerufen, wenn der Benutzer eine Zeile auswählt."""
        selected = self.tree.selection()

        if selected:
            self.selected_character_id = selected[0]
            self.edit_btn.config(state="normal")
            self.delete_btn.config(state="normal")
        else:
            self.selected_character_id = None
            self.edit_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")

    def _open_create_dialog(self):
        """Öffnet einen Dialog zum Erstellen eines neuen Charakters."""
        self._open_character_dialog(character_id=None)

    def _open_edit_dialog(self):
        """Öffnet einen Dialog zum Bearbeiten des ausgewählten Charakters."""
        if self.selected_character_id is None:
            return
        self._open_character_dialog(character_id=self.selected_character_id)

    def _open_character_dialog(self, character_id=None):
        """Öffnet einen gemeinsamen Dialog für Neu- und Bearbeiten-Modus.

        Der Dialog enthält:
        - Name und Beschreibung Eingabefelder
        - Für jede Ansicht (front, side_left, side_right, back):
          "Durchsuchen..." und "Extern" Buttons
        - Für jeden Bewegungs-Zustand (idle, walking, talking):
          "Durchsuchen..." und "Extern" Buttons

        Args:
            character_id: None für einen neuen Charakter, sonst die ID
        """
        is_edit_mode = character_id is not None

        # ---------- DIALOG-FENSTER ERSTELLEN ----------
        dialog = tk.Toplevel(self)
        dialog.title("Charakter bearbeiten" if is_edit_mode else "Neuer Charakter")
        dialog.geometry("650x750")
        dialog.transient(self)

        # Scrollbarer Bereich für viele Eingabefelder
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ---------- BASIS-INFO ----------
        tk.Label(scroll_frame, text="Name:").pack(pady=(15, 5))
        name_var = tk.StringVar()
        tk.Entry(scroll_frame, textvariable=name_var, width=50).pack()

        tk.Label(scroll_frame, text="Beschreibung:").pack(pady=(10, 5))
        desc_var = tk.StringVar()
        tk.Entry(scroll_frame, textvariable=desc_var, width=50).pack()

        # OS-Info anzeigen
        app_name = get_drawing_app_name()
        os_name = detect_os()
        tk.Label(
            scroll_frame,
            text=f"Betriebssystem: {os_name.capitalize()} – Extern öffnet {app_name}",
            font=tk.font.Font(family="Arial", size=9, slant="italic"),
            fg="gray"
        ).pack(pady=(5, 10))

        # ---------- ANSICHTEN ----------
        tk.Label(
            scroll_frame,
            text="Ansichten (2D Figuren aus verschiedenen Richtungen):",
            font=tk.font.Font(family="Arial", size=11, weight="bold")
        ).pack(pady=(10, 5))

        # Dictionary für die Ansicht-Variablen
        view_vars = {}

        for view_name in Character.AVAILABLE_VIEWS:
            label_text = VIEW_LABELS.get(view_name, view_name)
            tk.Label(scroll_frame, text=label_text).pack(pady=(5, 0))

            view_var = tk.StringVar()
            view_vars[view_name] = view_var

            frame = tk.Frame(scroll_frame)
            frame.pack()

            entry = tk.Entry(frame, textvariable=view_var, width=38, state="readonly")
            entry.pack(side="left", padx=(0, 5))

            tk.Button(
                frame,
                text="Durchsuchen...",
                command=lambda vn=view_name, vv=view_var: self._select_image_file(vv, vn)
            ).pack(side="left", padx=(0, 5))

            tk.Button(
                frame,
                text="Extern",
                command=lambda vn=view_name, vv=view_var: self._open_external_for_view(vv, vn)
            ).pack(side="left")

        # ---------- BEWEGUNGS-ZUSTÄNDE ----------
        tk.Label(
            scroll_frame,
            text="Bewegungs-Zustände (Poses):",
            font=tk.font.Font(family="Arial", size=11, weight="bold")
        ).pack(pady=(15, 5))

        # Dictionary für die Pose-Variablen
        pose_vars = {}

        for pose_name in Character.AVAILABLE_POSES:
            label_text = POSE_LABELS.get(pose_name, pose_name)
            tk.Label(scroll_frame, text=label_text).pack(pady=(5, 0))

            pose_var = tk.StringVar()
            pose_vars[pose_name] = pose_var

            frame = tk.Frame(scroll_frame)
            frame.pack()

            entry = tk.Entry(frame, textvariable=pose_var, width=38, state="readonly")
            entry.pack(side="left", padx=(0, 5))

            tk.Button(
                frame,
                text="Durchsuchen...",
                command=lambda pn=pose_name, pv=pose_var: self._select_image_file(pv, pn)
            ).pack(side="left", padx=(0, 5))

            tk.Button(
                frame,
                text="Extern",
                command=lambda pn=pose_name, pv=pose_var: self._open_external_for_pose(pv, pn)
            ).pack(side="left")

        # ---------- IM BEARBEITEN-MODUS VORBELEGEN ----------
        if is_edit_mode:
            character = self.character_library.get_character(character_id)
            if character:
                name_var.set(character.name)
                desc_var.set(character.description)
                # Ansichten vorbelegen
                for view_name in Character.AVAILABLE_VIEWS:
                    path = character.get_view(view_name)
                    if path:
                        view_vars[view_name].set(path)
                # Poses vorbelegen
                for pose_name in Character.AVAILABLE_POSES:
                    path = character.get_pose(pose_name)
                    if path:
                        pose_vars[pose_name].set(path)

        # ---------- SPEICHERN-BUTTON ----------
        def save():
            """Liest die Eingaben aus, speichert den Charakter und schließt den Dialog."""
            name = name_var.get().strip()
            description = desc_var.get().strip()

            # Validierung: Name darf nicht leer sein
            if not name:
                messagebox.showwarning("Warnung", "Bitte gib einen Namen ein!")
                return

            # Ansichten sammeln (nur nicht-leere Pfade)
            views = {}
            for view_name, var in view_vars.items():
                path = var.get().strip()
                if path:
                    views[view_name] = path

            # Poses sammeln (nur nicht-leere Pfade)
            poses = {}
            for pose_name, var in pose_vars.items():
                path = var.get().strip()
                if path:
                    poses[pose_name] = path

            if is_edit_mode:
                # Bearbeiten: update_character aufrufen
                self.character_library.update_character(
                    character_id,
                    name=name,
                    description=description,
                    views=views,
                    poses=poses
                )
            else:
                # Neu erstellen
                self.character_library.create_character(
                    name=name,
                    description=description,
                    views=views,
                    poses=poses
                )

            # Treeview neu befüllen
            self._refresh_list()
            dialog.destroy()

        tk.Button(scroll_frame, text="Speichern", command=save,
                  font=tk.font.Font(family="Arial", size=12)).pack(pady=20)

    def _select_image_file(self, image_var: tk.StringVar, context: str = ""):
        """Öffnet einen Dateidialog zur Auswahl eines Charakter-Bildes.

        Die Datei wird automatisch in den Ordner 'assets/characters/' kopiert.

        Args:
            image_var: Die StringVar-Variable des Bildpfad-Eingabefelds.
            context: Zusätzlicher Kontext für eindeutige Dateinamen (z.B. "front")
        """
        file_path = filedialog.askopenfilename(
            title="Charakterbild auswählen",
            filetypes=[
                ("Bilddateien", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Alle Dateien", "*.*")
            ]
        )

        if not file_path:
            return

        target_dir = "assets/characters"
        os.makedirs(target_dir, exist_ok=True)

        filename = os.path.basename(file_path)

        # Wenn ein Kontext gegeben ist, präfixen wir den Dateinamen
        # z.B. "front_held.png" für die Vorderansicht
        if context:
            name_without_ext, ext = os.path.splitext(filename)
            filename = f"{context}_{name_without_ext}{ext}"

        target_path = os.path.join(target_dir, filename)

        # Eindeutigen Namen erzeugen, falls Datei existiert
        if os.path.exists(target_path):
            if os.path.abspath(file_path) != os.path.abspath(target_path):
                import time
                timestamp = int(time.time())
                name_without_ext, ext = os.path.splitext(filename)
                unique_filename = f"{name_without_ext}_{timestamp}{ext}"
                target_path = os.path.join(target_dir, unique_filename)

        shutil.copy2(file_path, target_path)
        image_var.set(target_path)

    def _open_external_for_view(self, image_var: tk.StringVar, view_name: str):
        """Öffnet das externe Zeichenprogramm für eine Ansicht.

        Erstellt eine leere PNG-Datei in 'assets/characters/' und öffnet sie
        im Standard-Zeichenprogramm des Betriebssystems.

        Args:
            image_var: Die StringVar-Variable des Bildpfad-Eingabefelds.
            view_name: Name der Ansicht (z.B. "front")
        """
        self._open_external_drawing(image_var, "characters", view_name)

    def _open_external_for_pose(self, image_var: tk.StringVar, pose_name: str):
        """Öffnet das externe Zeichenprogramm für einen Bewegungs-Zustand.

        Erstellt eine leere PNG-Datei in 'assets/characters/' und öffnet sie
        im Standard-Zeichenprogramm des Betriebssystems.

        Args:
            image_var: Die StringVar-Variable des Bildpfad-Eingabefelds.
            pose_name: Name des Zustands (z.B. "idle")
        """
        self._open_external_drawing(image_var, "characters", pose_name)

    def _open_external_drawing(self, image_var: tk.StringVar, asset_subdir: str, context: str):
        """Allgemeine Methode zum Öffnen des externen Zeichenprogramms.

        Erstellt eine leere PNG-Datei und öffnet sie im OS-Zeichenprogramm.
        Falls bereits ein Bild gesetzt ist, wird dieses zum Bearbeiten geöffnet.

        Args:
            image_var: Die StringVar-Variable des Bildpfad-Eingabefelds.
            asset_subdir: Unterordner in assets/ (z.B. "characters" oder "scenes")
            context: Kontext für den Dateinamen (z.B. "front", "idle")
        """
        # Prüfen, ob bereits ein Bild vorhanden ist (zum Bearbeiten)
        existing_path = image_var.get().strip()

        if existing_path and os.path.exists(existing_path):
            # Bestehendes Bild im externen Programm öffnen
            file_to_open = existing_path
        else:
            # Neue leere Datei erstellen
            import time
            timestamp = int(time.time())
            filename = f"{context}_{timestamp}.png"
            target_dir = os.path.join("assets", asset_subdir)
            file_to_open = os.path.join(target_dir, filename)

            if not create_blank_image(file_to_open, 400, 400):
                messagebox.showerror(
                    "Fehler",
                    "Die leere Datei konnte nicht erstellt werden."
                )
                return

        # Pfad setzen
        image_var.set(file_to_open)

        # Externes Zeichenprogramm öffnen
        success = open_in_drawing_app(file_to_open)

        if success:
            app_name = get_drawing_app_name()
            messagebox.showinfo(
                f"{app_name} geöffnet",
                f"{app_name} wurde geöffnet und die Datei geladen:\n\n"
                f"{file_to_open}\n\n"
                f"Zeichne deine 2D-Figur in {app_name}, speichere die Datei,\n"
                f"und klicke dann auf 'Speichern', um den Charakter zu übernehmen."
            )
        else:
            messagebox.showerror(
                "Fehler",
                f"Das Zeichenprogramm konnte nicht geöffnet werden.\n"
                f"Du kannst stattdessen 'Durchsuchen...' verwenden."
            )

    def _delete_character(self):
        """Löscht den ausgewählten Charakter nach einer Bestätigung."""
        if self.selected_character_id is None:
            return

        if not messagebox.askyesno(
            "Bestätigung",
            "Charakter wirklich löschen?"
        ):
            return

        self.character_library.delete_character(self.selected_character_id)
        self._refresh_list()

        self.selected_character_id = None
        self.edit_btn.config(state="disabled")
        self.delete_btn.config(state="disabled")