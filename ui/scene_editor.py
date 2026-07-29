# Scene Editor für Record Studio
# Grafische Oberfläche zur Verwaltung von Szenen (Landschaften)
# Zeigt eine Liste aller Szenen an und ermöglicht das
# Erstellen, Bearbeiten und Löschen von Szenen.
#
# Landschaften können auf zwei Arten erstellt werden:
#   1. Bild importieren (PNG, JPG, etc.)
#   2. Zeichnen direkt im Canvas (mit Pinsel, Farben, etc.)

# Importiert die Tkinter-Bibliothek für GUI-Fenster
import tkinter as tk
# Importiert das ttk-Modul für erweiterte Widgets (Treeview), messagebox für Dialoge
# und filedialog für Dateiauswahl-Dialoge
from tkinter import ttk, messagebox, filedialog

# Importiert die SceneLibrary für CRUD-Operationen auf Szenen
from core.scene_library import SceneLibrary

# Importiert shutil zum Kopieren von Bilddateien
import shutil

# Importiert os für Pfad-Operationen
import os

# Importiert Pillow (PIL) für das Speichern der Zeichnung als PNG
from PIL import Image, ImageDraw, ImageTk


class SceneEditor(tk.Toplevel):
    """Grafischer Editor für die Scene Library.

    Erbt von tk.Toplevel, um ein eigenständiges Fenster zu erzeugen.

    Die Klasse zeigt alle Szenen in einer ttk.Treeview-Liste an
    und bietet drei Aktionen: Neu erstellen, Bearbeiten und Löschen.

    Beim Erstellen/Bearbeiten kann der Benutzer wählen zwischen:
      - Bild importieren: Eine vorhandene Landschafts-Datei auswählen
      - Zeichnen: Eine Landschaft direkt im Canvas zeichnen
    """

    def __init__(self, parent, scene_library: SceneLibrary):
        """Initialisiert den Scene Editor.

        Args:
            parent: Elternfenster (RecordStudioApp-Instanz)
            scene_library: SceneLibrary-Instanz für CRUD-Operationen
        """
        super().__init__(parent)

        self.scene_library = scene_library
        self.selected_scene_id = None

        self.title("Szenen verwalten – Landschaften")
        self.geometry("700x450")
        self.transient(parent)

        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        """Erstellt alle sichtbaren Elemente des Editor-Fensters."""
        # ---------- TREVIEW (Szenenliste) ----------
        self.tree = ttk.Treeview(
            self,
            columns=("name", "description"),
            show="headings"
        )

        self.tree.heading("name", text="Name")
        self.tree.heading("description", text="Beschreibung")

        self.tree.column("name", width=200)
        self.tree.column("description", width=450)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # ---------- BUTTON-LEISTE ----------
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        self.new_btn = tk.Button(
            button_frame,
            text="Neue Szene",
            command=self._open_create_dialog,
            font=tk.font.Font(family="Arial", size=10)
        )
        self.new_btn.pack(side="left", padx=5)

        self.edit_btn = tk.Button(
            button_frame,
            text="Bearbeiten",
            command=self._open_edit_dialog,
            state="disabled",
            font=tk.font.Font(family="Arial", size=10)
        )
        self.edit_btn.pack(side="left", padx=5)

        self.delete_btn = tk.Button(
            button_frame,
            text="Löschen",
            command=self._delete_scene,
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
        """Lädt alle Szenen neu und füllt die Treeview-Liste auf."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        scenes = self.scene_library.get_all_scenes()

        for scene in scenes:
            self.tree.insert(
                "",
                "end",
                iid=scene.scene_id,
                values=(scene.name, scene.description)
            )

    def _on_tree_select(self, event):
        """Wird aufgerufen, wenn der Benutzer eine Zeile auswählt."""
        selected = self.tree.selection()

        if selected:
            self.selected_scene_id = selected[0]
            self.edit_btn.config(state="normal")
            self.delete_btn.config(state="normal")
        else:
            self.selected_scene_id = None
            self.edit_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")

    def _open_create_dialog(self):
        """Öffnet einen Dialog zum Erstellen einer neuen Szene."""
        self._open_scene_dialog(scene_id=None)

    def _open_edit_dialog(self):
        """Öffnet einen Dialog zum Bearbeiten der ausgewählten Szene."""
        if self.selected_scene_id is None:
            return
        self._open_scene_dialog(scene_id=self.selected_scene_id)

    def _open_scene_dialog(self, scene_id=None):
        """Öffnet einen Dialog für Neu- und Bearbeiten-Modus.

        Der Dialog bietet zwei Möglichkeiten, eine Landschaft zu erstellen:
          1. Bild importieren: Datei-Dialog öffnen
          2. Zeichnen: Canvas mit Pinsel-Werkzeug öffnen

        Args:
            scene_id: None für eine neue Szene, sonst die ID
        """
        is_edit_mode = scene_id is not None

        dialog = tk.Toplevel(self)
        dialog.title("Szene bearbeiten" if is_edit_mode else "Neue Szene")
        dialog.geometry("500x400")
        dialog.transient(self)

        # ---------- BASIS-INFO ----------
        tk.Label(dialog, text="Name:").pack(pady=(15, 5))
        name_var = tk.StringVar()
        tk.Entry(dialog, textvariable=name_var, width=50).pack()

        tk.Label(dialog, text="Beschreibung:").pack(pady=(10, 5))
        desc_var = tk.StringVar()
        tk.Entry(dialog, textvariable=desc_var, width=50).pack()

        # ---------- HINTERGRUND ----------
        tk.Label(
            dialog,
            text="Landschaft / Hintergrund:",
            font=tk.font.Font(family="Arial", size=11, weight="bold")
        ).pack(pady=(15, 5))

        background_var = tk.StringVar()

        # Anzeige des aktuellen Pfads
        path_frame = tk.Frame(dialog)
        path_frame.pack()
        tk.Entry(path_frame, textvariable=background_var, width=45, state="readonly").pack(side="left", padx=(0, 5))

        # ---------- AUSWAHL-METHODEN ----------
        method_frame = tk.Frame(dialog)
        method_frame.pack(pady=10)

        # Button 1: Bild importieren
        tk.Button(
            method_frame,
            text="Bild importieren",
            command=lambda: self._select_background_file(background_var),
            font=tk.font.Font(family="Arial", size=10)
        ).pack(side="left", padx=5)

        # Button 2: Zeichnen
        tk.Button(
            method_frame,
            text="Zeichnen",
            command=lambda: self._open_drawing_canvas(background_var),
            font=tk.font.Font(family="Arial", size=10)
        ).pack(side="left", padx=5)

        # ---------- IM BEARBEITEN-MODUS VORBELEGEN ----------
        if is_edit_mode:
            scene = self.scene_library.get_scene(scene_id)
            if scene:
                name_var.set(scene.name)
                background_var.set(scene.background_path)
                desc_var.set(scene.description)

        # ---------- SPEICHERN-BUTTON ----------
        def save():
            name = name_var.get().strip()
            background_path = background_var.get().strip()
            description = desc_var.get().strip()

            if not name:
                messagebox.showwarning("Warnung", "Bitte gib einen Namen ein!")
                return

            if is_edit_mode:
                self.scene_library.update_scene(
                    scene_id,
                    name=name,
                    background_path=background_path,
                    description=description
                )
            else:
                self.scene_library.create_scene(
                    name=name,
                    background_path=background_path,
                    description=description
                )

            self._refresh_list()
            dialog.destroy()

        tk.Button(dialog, text="Speichern", command=save,
                  font=tk.font.Font(family="Arial", size=12)).pack(pady=20)

    def _select_background_file(self, background_var: tk.StringVar):
        """Öffnet einen Dateidialog zur Auswahl eines Hintergrundbildes.

        Die Datei wird automatisch in den Ordner 'assets/scenes/' kopiert.

        Args:
            background_var: Die StringVar-Variable des Hintergrundbild-Eingabefelds.
        """
        file_path = filedialog.askopenfilename(
            title="Hintergrundbild auswählen",
            filetypes=[
                ("Bilddateien", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Alle Dateien", "*.*")
            ]
        )

        if not file_path:
            return

        target_dir = "assets/scenes"
        os.makedirs(target_dir, exist_ok=True)

        filename = os.path.basename(file_path)
        target_path = os.path.join(target_dir, filename)

        if os.path.exists(target_path):
            if os.path.abspath(file_path) != os.path.abspath(target_path):
                import time
                timestamp = int(time.time())
                name_without_ext, ext = os.path.splitext(filename)
                unique_filename = f"{name_without_ext}_{timestamp}{ext}"
                target_path = os.path.join(target_dir, unique_filename)

        shutil.copy2(file_path, target_path)
        background_var.set(target_path)

    def _open_drawing_canvas(self, background_var: tk.StringVar):
        """Öffnet ein Zeichen-Canvas, in dem der Benutzer eine Landschaft zeichnen kann.

        Der Benutzer kann mit der Maus zeichnen, die Pinselgröße und Farbe
        einstellen. Beim Klick auf "Speichern" wird die Zeichnung als PNG
        in den Ordner 'assets/scenes/' gespeichert und der Pfad in
        background_var gesetzt.

        Args:
            background_var: Die StringVar-Variable des Hintergrundbild-Eingabefelds.
        """
        DrawingCanvas(self, background_var)

    def _delete_scene(self):
        """Löscht die ausgewählte Szene nach einer Bestätigung."""
        if self.selected_scene_id is None:
            return

        if not messagebox.askyesno(
            "Bestätigung",
            "Szene wirklich löschen?"
        ):
            return

        self.scene_library.delete_scene(self.selected_scene_id)
        self._refresh_list()

        self.selected_scene_id = None
        self.edit_btn.config(state="disabled")
        self.delete_btn.config(state="disabled")


class DrawingCanvas(tk.Toplevel):
    """Zeichen-Canvas-Fenster zum Zeichnen von Landschaften.

    Bietet ein Canvas an, in dem der Benutzer mit der Maus zeichnen kann.
    Einstellbar sind:
      - Pinselgröße (1-50 Pixel)
      - Farbe (über einen Color-Chooser)
      - Radiergummi (weiß)

    Beim Klick auf "Speichern" wird die Zeichnung als PNG gespeichert.

    Attribute:
        parent: Elternfenster (SceneEditor-Instanz)
        background_var: StringVar, in der der gespeicherte Pfad landet
        canvas: Das tk.Canvas-Widget zum Zeichnen
        brush_size: Aktuelle Pinselgröße
        brush_color: Aktuelle Pinselfarbe
        is_erasing: True, wenn der Radiergummi aktiv ist
        last_x, last_y: Letzte Mausposition für flüssiges Zeichnen
    """

    # Canvas-Größe
    CANVAS_WIDTH = 800
    CANVAS_HEIGHT = 500

    # Standard-Hintergrundfarbe des Canvas
    CANVAS_BG = "white"

    def __init__(self, parent, background_var: tk.StringVar):
        """Initialisiert das Zeichen-Canvas.

        Args:
            parent: Elternfenster (SceneEditor-Instanz)
            background_var: StringVar, in der der gespeicherte Pfad landet
        """
        super().__init__(parent)

        self.parent = parent
        self.background_var = background_var

        # Zeichnen-Einstellungen
        self.brush_size = 5
        self.brush_color = "black"
        self.is_erasing = False
        self.last_x = None
        self.last_y = None

        # Fenster-Einstellungen
        self.title("Landschaft zeichnen")
        self.geometry(f"{self.CANVAS_WIDTH + 200}x{self.CANVAS_HEIGHT + 100}")
        self.transient(parent)

        self._build_ui()

    def _build_ui(self):
        """Erstellt die Benutzeroberfläche des Zeichen-Canvas."""
        # ---------- WERKZEUG-LEISTE (links) ----------
        tool_frame = tk.Frame(self, width=180)
        tool_frame.pack(side="left", fill="y", padx=5, pady=5)

        tk.Label(
            tool_frame,
            text="Werkzeuge",
            font=tk.font.Font(family="Arial", size=12, weight="bold")
        ).pack(pady=(10, 15))

        # Pinselgröße
        tk.Label(tool_frame, text="Pinselgröße:").pack(anchor="w")
        self.size_var = tk.IntVar(value=self.brush_size)
        size_scale = tk.Scale(
            tool_frame,
            from_=1,
            to=50,
            orient="horizontal",
            variable=self.size_var,
            command=self._on_size_change
        )
        size_scale.pack(fill="x", pady=(0, 15))

        # Farbe
        tk.Label(tool_frame, text="Farbe:").pack(anchor="w")
        self.color_btn = tk.Button(
            tool_frame,
            text="Farbe wählen",
            command=self._choose_color,
            bg=self.brush_color,
            font=tk.font.Font(family="Arial", size=10)
        )
        self.color_btn.pack(fill="x", pady=(0, 5))

        # Aktuelle Farbe anzeigen
        self.color_preview = tk.Canvas(tool_frame, width=170, height=30, bg=self.brush_color)
        self.color_preview.pack(pady=(0, 15))

        # Radiergummi
        self.erase_btn = tk.Button(
            tool_frame,
            text="Radiergummi",
            command=self._toggle_eraser,
            font=tk.font.Font(family="Arial", size=10)
        )
        self.erase_btn.pack(fill="x", pady=(0, 15))

        # Pinsel (zurück zum Zeichnen)
        self.brush_btn = tk.Button(
            tool_frame,
            text="Pinsel",
            command=self._select_brush,
            font=tk.font.Font(family="Arial", size=10),
            relief="sunken"
        )
        self.brush_btn.pack(fill="x", pady=(0, 15))

        # Canvas leeren
        tk.Button(
            tool_frame,
            text="Canvas leeren",
            command=self._clear_canvas,
            font=tk.font.Font(family="Arial", size=10)
        ).pack(fill="x", pady=(0, 15))

        # Speichern
        tk.Button(
            tool_frame,
            text="Als PNG speichern",
            command=self._save_drawing,
            font=tk.font.Font(family="Arial", size=11, weight="bold"),
            bg="lightgreen"
        ).pack(fill="x", pady=(20, 5))

        # Abbrechen
        tk.Button(
            tool_frame,
            text="Abbrechen",
            command=self.destroy,
            font=tk.font.Font(family="Arial", size=10)
        ).pack(fill="x", pady=(5, 10))

        # ---------- CANVAS (rechts) ----------
        self.canvas = tk.Canvas(
            self,
            width=self.CANVAS_WIDTH,
            height=self.CANVAS_HEIGHT,
            bg=self.CANVAS_BG,
            cursor="crosshair"
        )
        self.canvas.pack(side="right", padx=5, pady=5)

        # Maus-Ereignisse binden
        self.canvas.bind("<Button-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)

    def _on_size_change(self, value):
        """Wird aufgerufen, wenn die Pinselgröße geändert wird."""
        self.brush_size = int(value)

    def _choose_color(self):
        """Öffnet den Farbwaehler-Dialog."""
        from tkinter import colorchooser
        color = colorchooser.askcolor(title="Pinselfarbe wählen")
        if color[1]:  # color[1] ist der Hex-String
            self.brush_color = color[1]
            self.color_btn.config(bg=self.brush_color)
            self.color_preview.config(bg=self.brush_color)
            # Wenn Radiergummi aktiv war, zurück zum Pinsel wechseln
            self.is_erasing = False
            self.erase_btn.config(relief="raised")
            self.brush_btn.config(relief="sunken")

    def _toggle_eraser(self):
        """Schaltet den Radiergummi-Modus um."""
        self.is_erasing = not self.is_erasing
        if self.is_erasing:
            self.erase_btn.config(relief="sunken")
            self.brush_btn.config(relief="raised")
        else:
            self.erase_btn.config(relief="raised")
            self.brush_btn.config(relief="sunken")

    def _select_brush(self):
        """Wählt den Pinsel-Modus (nicht Radiergummi)."""
        self.is_erasing = False
        self.brush_btn.config(relief="sunken")
        self.erase_btn.config(relief="raised")

    def _clear_canvas(self):
        """Leert das gesamte Canvas."""
        self.canvas.delete("all")

    def _on_mouse_down(self, event):
        """Wird aufgerufen, wenn die Maustaste gedrückt wird."""
        self.last_x = event.x
        self.last_y = event.y
        # Einen Punkt zeichnen (für einzelne Klicks)
        self._draw_point(event.x, event.y)

    def _on_mouse_move(self, event):
        """Wird aufgerufen, wenn die Maus bei gedrückter Taste bewegt wird."""
        if self.last_x is not None and self.last_y is not None:
            self._draw_line(self.last_x, self.last_y, event.x, event.y)
        self.last_x = event.x
        self.last_y = event.y

    def _on_mouse_up(self, event):
        """Wird aufgerufen, wenn die Maustaste losgelassen wird."""
        self.last_x = None
        self.last_y = None

    def _draw_point(self, x, y):
        """Zeichnet einen Punkt (Kreis) an der Position (x, y)."""
        color = self.CANVAS_BG if self.is_erasing else self.brush_color
        radius = self.brush_size / 2
        self.canvas.create_oval(
            x - radius, y - radius,
            x + radius, y + radius,
            fill=color,
            outline=color
        )

    def _draw_line(self, x1, y1, x2, y2):
        """Zeichnet eine Linie von (x1, y1) nach (x2, y2)."""
        color = self.CANVAS_BG if self.is_erasing else self.brush_color
        self.canvas.create_line(
            x1, y1, x2, y2,
            fill=color,
            width=self.brush_size,
            capstyle="round",
            smooth=True
        )

    def _save_drawing(self):
        """Speichert die Zeichnung als PNG-Datei.

        Die Datei wird in 'assets/scenes/' gespeichert.
        Der Dateiname wird aus einem Zeitstempel generiert.
        Der Pfad wird in background_var gesetzt.
        """
        # Zielverzeichnis
        target_dir = "assets/scenes"
        os.makedirs(target_dir, exist_ok=True)

        # Dateiname aus Zeitstempel
        import time
        timestamp = int(time.time())
        filename = f"drawing_{timestamp}.png"
        target_path = os.path.join(target_dir, filename)

        # Canvas-Inhalt als PostScript exportieren und mit Pillow in PNG umwandeln
        # PostScript ist die einzige Möglichkeit, den Canvas-Inhalt zu speichern
        ps_file = target_path.replace(".png", ".ps")
        self.canvas.postscript(file=ps_file, colormode="color")

        try:
            # PostScript mit Pillow in PNG umwandeln
            img = Image.open(ps_file)
            img.save(target_path, "png")

            # PostScript-Datei löschen (nicht mehr benötigt)
            if os.path.exists(ps_file):
                os.remove(ps_file)

            # Pfad in der background_var speichern
            self.background_var.set(target_path)

            messagebox.showinfo(
                "Gespeichert",
                f"Die Zeichnung wurde gespeichert:\n{target_path}"
            )
            self.destroy()

        except Exception as e:
            messagebox.showerror(
                "Fehler",
                f"Die Zeichnung konnte nicht gespeichert werden:\n{str(e)}"
            )
            # PostScript-Datei bei Fehler auch löschen
            if os.path.exists(ps_file):
                os.remove(ps_file)