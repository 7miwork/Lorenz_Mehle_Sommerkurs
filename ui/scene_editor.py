# Scene Editor für Record Studio
# Grafische Oberfläche zur Verwaltung von Szenen (CRUD-Operationen)
# Zeigt eine Liste aller Szenen an und ermöglicht das
# Erstellen, Bearbeiten und Löschen von Szenen in der SceneLibrary.

# Importiert die Tkinter-Bibliothek für GUI-Fenster
import tkinter as tk
# Importiert das ttk-Modul für erweiterte Widgets (Treeview), messagebox für Dialoge
# und filedialog für Dateiauswahl-Dialoge
from tkinter import ttk, messagebox, filedialog

# Importiert die SceneLibrary für CRUD-Operationen auf Szenen
from core.scene_library import SceneLibrary

# Importiert shutil zum Kopieren von Bilddateien in das assets/-Verzeichnis
import shutil

# Importiert os für Pfad-Operationen (Verzeichnisse prüfen, Dateinamen extrahieren)
import os


class SceneEditor(tk.Toplevel):
    """Grafischer Editor für die Scene Library.

    Erbt von tk.Toplevel, um ein eigenständiges Fenster zu erzeugen,
    das als Kind des Hauptfensters (RecordStudioApp) erscheint.

    Die Klasse zeigt alle Szenen in einer ttk.Treeview-Liste an
    und bietet drei Aktionen: Neu erstellen, Bearbeiten und Löschen.
    Jede Aktion öffnet bei Bedarf einen Toplevel-Dialog mit Eingabefeldern.

    Attribute:
        scene_library: Die SceneLibrary-Instanz, die die Daten verwaltet
        selected_scene_id: ID der aktuell in der Liste ausgewählten Szene
        tree: Die ttk.Treeview-Widget mit den Spalten Name und Beschreibung
    """

    def __init__(self, parent, scene_library: SceneLibrary):
        """Initialisiert den Scene Editor.

        Args:
            parent: Elternfenster (RecordStudioApp-Instanz)
            scene_library: SceneLibrary-Instanz für CRUD-Operationen
        """
        # Ruft den Konstruktor der Elternklasse (tk.Toplevel) auf
        super().__init__(parent)

        # Referenz auf die SceneLibrary speichern, um später CRUD-Operationen auszuführen
        self.scene_library = scene_library

        # ID der aktuell ausgewählten Szene (None, wenn nichts ausgewählt)
        self.selected_scene_id = None

        # Fenster-Titel festlegen (erscheint in der Titelleiste)
        self.title("Szenen verwalten")
        # Fenstergröße festlegen: 600 Pixel breit, 400 Pixel hoch
        self.geometry("600x400")
        # Das Fenster als Tochter des Hauptfensters kennzeichnen (transient)
        # Dadurch folgt es dem Hauptfenster bei Minimieren und erscheint zentriert darüber
        self.transient(parent)

        # Die Benutzeroberfläche erstellen (Treeview, Buttons, Schließen-Button)
        self._build_ui()

        # Die Liste der Szenen beim Start initial befüllen
        self._refresh_list()

    def _build_ui(self):
        """Erstellt alle sichtbaren Elemente des Editor-Fensters.

        Aufbau:
        - Oben: ttk.Treeview mit zwei benannten Spalten (Name, Beschreibung)
        - Darunter: Drei Buttons (Neue Szene, Bearbeiten, Löschen)
        - Unten: Schließen-Button
        """
        # ---------- TREVIEW (Szenenliste) ----------
        # ttk.Treeview mit zwei benannten Spalten erstellen
        # show="headings" versteckt die Standard-Baum-Spalte ganz links
        self.tree = ttk.Treeview(
            self,
            columns=("name", "description"),
            show="headings"
        )

        # Spaltenüberschriften (Headings) festlegen
        self.tree.heading("name", text="Name")
        self.tree.heading("description", text="Beschreibung")

        # Spaltenbreiten festlegen (Gesamtbreite passt sich an Fenstergröße an)
        self.tree.column("name", width=200)
        self.tree.column("description", width=350)

        # Treeview mit Rand und automatischem Resize platzieren
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Wenn der Benutzer eine Zeile in der Treeview auswählt,
        # wird _on_tree_select aufgerufen (aktiviert/deaktiviert Edit- und Delete-Buttons)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # ---------- BUTTON-LEISTE ----------
        # Einen Rahmen (Frame) für die drei Aktions-Buttons erstellen
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        # Button: Neue Szene – öffnet einen Dialog zur Eingabe von Name, Hintergrundbild, Beschreibung
        self.new_btn = tk.Button(
            button_frame,
            text="Neue Szene",
            command=self._open_create_dialog,
            font=tk.font.Font(family="Arial", size=10)
        )
        self.new_btn.pack(side="left", padx=5)

        # Button: Bearbeiten – nur aktiv, wenn eine Zeile ausgewählt ist
        # Wird in _on_tree_select aktiviert/deaktiviert
        self.edit_btn = tk.Button(
            button_frame,
            text="Bearbeiten",
            command=self._open_edit_dialog,
            state="disabled",
            font=tk.font.Font(family="Arial", size=10)
        )
        self.edit_btn.pack(side="left", padx=5)

        # Button: Löschen – nur aktiv, wenn eine Zeile ausgewählt ist
        # Zeigt vor dem Löschen einen Bestätigungsdialog an
        self.delete_btn = tk.Button(
            button_frame,
            text="Löschen",
            command=self._delete_scene,
            state="disabled",
            font=tk.font.Font(family="Arial", size=10)
        )
        self.delete_btn.pack(side="left", padx=5)

        # ---------- SCHLIESSEN-BUTTON ----------
        # Schließt das Editor-Fenster
        self.close_btn = tk.Button(
            self,
            text="Schließen",
            command=self.destroy,
            font=tk.font.Font(family="Arial", size=10)
        )
        self.close_btn.pack(pady=10)

    def _refresh_list(self):
        """Lädt alle Szenen neu und füllt die Treeview-Liste auf.

        Die Methode wird nach jeder Änderung (Neu/Bearbeiten/Löschen)
        aufgerufen, um sicherzustellen, dass die Anzeige aktuell ist.
        """
        # Alle vorhandenen Einträge in der Treeview entfernen
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Alle Szenen laden (get_all_scenes() liefert sie bereits alphabetisch sortiert)
        scenes = self.scene_library.get_all_scenes()

        # Jede Szene als neue Zeile in die Treeview einfügen
        # Die scene_id wird als iid (item id) verwendet, damit wir später
        # die zugehörige Szene für Bearbeiten/Löschen wiederfinden
        for scene in scenes:
            self.tree.insert(
                "",
                "end",
                iid=scene.scene_id,
                values=(scene.name, scene.description)
            )

    def _on_tree_select(self, event):
        """Wird aufgerufen, wenn der Benutzer eine Zeile in der Treeview auswählt.

        Aktiviert die "Bearbeiten"- und "Löschen"-Buttons, wenn eine Zeile
        ausgewählt ist, und deaktiviert sie, wenn die Auswahl aufgehoben wird.

        Args:
            event: Das TreeviewSelect-Ereignis (wird von Tkinter automatisch übergeben)
        """
        # Die aktuell ausgewählten Item-IDs abrufen
        selected = self.tree.selection()

        if selected:
            # Eine Zeile ist ausgewählt: die scene_id speichern und Buttons aktivieren
            self.selected_scene_id = selected[0]
            self.edit_btn.config(state="normal")
            self.delete_btn.config(state="normal")
        else:
            # Keine Zeile mehr ausgewählt: ID zurücksetzen und Buttons deaktivieren
            self.selected_scene_id = None
            self.edit_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")

    def _open_create_dialog(self):
        """Öffnet einen Dialog zum Erstellen einer neuen Szene.

        Ruft die interne Methode _open_scene_dialog auf, ohne eine
        scene_id zu übergeben (was den Modus "Neu" auslöst).
        """
        # scene_id=None signalisiert: Neue Szene (nicht Bearbeiten)
        self._open_scene_dialog(scene_id=None)

    def _open_edit_dialog(self):
        """Öffnet einen Dialog zum Bearbeiten der ausgewählten Szene.

        Die Eingabefelder werden mit den aktuellen Werten der Szene
        vorbelegt. Beim Speichern wird update_scene() aufgerufen.
        """
        # Wenn nichts ausgewählt ist, nichts tun (Sicherheitscheck)
        if self.selected_scene_id is None:
            return

        # scene_id setzen: Der Dialog weiß, dass er bearbeiten (nicht erstellen) soll
        self._open_scene_dialog(scene_id=self.selected_scene_id)

    def _open_scene_dialog(self, scene_id=None):
        """Öffnet einen gemeinsamen Dialog für Neu- und Bearbeiten-Modus.

        Der Dialog enthält Eingabefelder für Name, Hintergrundbild und Beschreibung.
        Im Bearbeiten-Modus (scene_id ist gesetzt) werden die Felder
        mit den aktuellen Werten vorbelegt.

        Args:
            scene_id: None für eine neue Szene, sonst die ID
                      der zu bearbeitenden Szene
        """
        # Bestimme, ob es um Erstellen oder Bearbeiten geht
        # (wird für den Fenster-Titel verwendet)
        is_edit_mode = scene_id is not None

        # ---------- DIALOG-FENSTER ERSTELLEN ----------
        dialog = tk.Toplevel(self)
        dialog.title("Szene bearbeiten" if is_edit_mode else "Neue Szene")
        dialog.geometry("400x300")
        # Der Dialog ist ein Tochterfenster des Editors (transient)
        dialog.transient(self)

        # ---------- EINGABEFELDER ----------
        # Name-Eingabe
        tk.Label(dialog, text="Name:").pack(pady=(20, 5))
        name_var = tk.StringVar()
        tk.Entry(dialog, textvariable=name_var, width=40).pack()

        # Hintergrundbild-Eingabe (schreibgeschützt, wird nur über "Durchsuchen..." gesetzt)
        tk.Label(dialog, text="Hintergrundbild:").pack(pady=(10, 5))
        background_var = tk.StringVar()

        # Ein Frame für die horizontale Anordnung von Entry und Button
        background_frame = tk.Frame(dialog)
        background_frame.pack()

        # Das Entry-Feld ist schreibgeschützt (state="readonly"), damit der Benutzer
        # den Pfad nicht versehentlich von Hand falsch eingeben kann.
        # Der Pfad wird ausschließlich über den "Durchsuchen..."-Button gesetzt.
        background_entry = tk.Entry(
            background_frame,
            textvariable=background_var,
            width=35,
            state="readonly"
        )
        background_entry.pack(side="left", padx=(0, 5))

        # "Durchsuchen..."-Button öffnet den Windows-Dateidialog zur Bildauswahl
        # und kopiert die ausgewählte Datei automatisch in assets/scenes/
        tk.Button(
            background_frame,
            text="Durchsuchen...",
            command=lambda: self._select_background_file(background_var)
        ).pack(side="left")

        # Beschreibung-Eingabe
        tk.Label(dialog, text="Beschreibung:").pack(pady=(10, 5))
        desc_var = tk.StringVar()
        tk.Entry(dialog, textvariable=desc_var, width=40).pack()

        # Wenn Bearbeiten-Modus: Die Eingabefelder mit den aktuellen Werten vorbelegen
        if is_edit_mode:
            scene = self.scene_library.get_scene(scene_id)
            if scene:
                name_var.set(scene.name)
                background_var.set(scene.background_path)
                desc_var.set(scene.description)

        # ---------- SPEICHERN-BUTTON ----------
        # Die save()-Funktion wird als lokale Funktion definiert,
        # weil sie Zugriff auf die Eingabevariablen und scene_id braucht
        def save():
            """Liest die Eingaben aus, speichert die Szene und schließt den Dialog."""
            # Eingaben auslesen und trimmen (entfernt führende/trailing Leerzeichen)
            name = name_var.get().strip()
            background_path = background_var.get().strip()
            description = desc_var.get().strip()

            # Einfache Validierung: Name darf nicht leer sein
            if not name:
                messagebox.showwarning("Warnung", "Bitte gib einen Namen ein!")
                return

            if is_edit_mode:
                # Bearbeiten: update_scene mit der scene_id aufrufen
                self.scene_library.update_scene(
                    scene_id,
                    name=name,
                    background_path=background_path,
                    description=description
                )
            else:
                # Neu erstellen: create_scene aufrufen (ID wird automatisch generiert)
                self.scene_library.create_scene(
                    name=name,
                    background_path=background_path,
                    description=description
                )

            # Die Treeview-Liste nach der Änderung neu befüllen
            self._refresh_list()

            # Dialog schließen
            dialog.destroy()

        # Speichern-Button mit der save()-Funktion verknüpfen
        tk.Button(dialog, text="Speichern", command=save).pack(pady=20)

    def _select_background_file(self, background_var: tk.StringVar):
        """Öffnet einen Dateidialog zur Auswahl eines Hintergrundbildes.

        Der Benutzer wählt eine Bilddatei aus (*.png, *.jpg, *.jpeg, *.gif, *.bmp).
        Die Datei wird automatisch in den Ordner 'assets/scenes/' kopiert,
        damit sie im Projektverzeichnis liegt und nicht versehentlich gelöscht wird.

        Falls im Zielordner bereits eine Datei mit demselben Namen existiert
        (und es nicht genau dieselbe Datei ist), wird ein eindeutiger Name
        durch Anhängen eines Zeitstempels erzeugt.

        Args:
            background_var: Die StringVar-Variable des Hintergrundbild-Eingabefelds.
                           Nach erfolgreicher Auswahl wird sie auf den relativen
                           Zielpfad gesetzt (z.B. "assets/scenes/wohnzimmer.png").
        """
        # Windows-Dateidialog öffnen, nur Bildformate zulassen
        file_path = filedialog.askopenfilename(
            title="Hintergrundbild auswählen",
            filetypes=[
                ("Bilddateien", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Alle Dateien", "*.*")
            ]
        )

        # Wenn der Benutzer "Abbrechen" geklickt hat, ist der Pfad leer -> nichts tun
        if not file_path:
            return

        # Zielverzeichnis: assets/scenes/ (relativ zum Arbeitsverzeichnis)
        target_dir = "assets/scenes"

        # Prüfen, ob das Zielverzeichnis existiert, ggf. erstellen
        os.makedirs(target_dir, exist_ok=True)

        # Nur den Dateinamen aus dem Quellpfad extrahieren (z.B. "wohnzimmer.png")
        filename = os.path.basename(file_path)

        # Zielpfad zusammensetzen: "assets/scenes/wohnzimmer.png"
        target_path = os.path.join(target_dir, filename)

        # Prüfen, ob am Ziel bereits eine Datei mit diesem Namen existiert
        if os.path.exists(target_path):
            # Prüfen, ob es dieselbe Datei ist (gleicher Pfad)
            # Ein einfacher String-Vergleich der absoluten Pfade ist ausreichend
            if os.path.abspath(file_path) != os.path.abspath(target_path):
                # Es ist eine andere Datei mit demselben Namen -> Zeitstempel anhängen
                # z.B. "wohnzimmer_1721234567.png"
                import time
                timestamp = int(time.time())
                name_without_ext, ext = os.path.splitext(filename)
                unique_filename = f"{name_without_ext}_{timestamp}{ext}"
                target_path = os.path.join(target_dir, unique_filename)

        # Die Quelldatei in den Zielordner kopieren
        # shutil.copy2() erhält die Datei-Metadaten (Erstellungsdatum etc.)
        shutil.copy2(file_path, target_path)

        # Den relativen Zielpfad in der background_var speichern,
        # damit er im Eingabefeld angezeigt und später in scene_data.json gespeichert wird
        background_var.set(target_path)

    def _delete_scene(self):
        """Löscht die ausgewählte Szene nach einer Bestätigung.

        Zeigt zuerst einen Bestätigungsdialog (messagebox.askyesno) an.
        Erst wenn der Benutzer mit "Ja" bestätigt, wird die Szene
        aus der SceneLibrary gelöscht und die Liste aktualisiert.
        """
        # Sicherheitscheck: Wenn nichts ausgewählt ist, nichts tun
        if self.selected_scene_id is None:
            return

        # Bestätigungsdialog anzeigen: "Szene wirklich löschen?"
        # askyesno gibt True zurück, wenn der Benutzer auf "Ja" klickt
        if not messagebox.askyesno(
            "Bestätigung",
            "Szene wirklich löschen?"
        ):
            # Benutzer hat "Nein" geklickt: Nichts tun
            return

        # Szene in der Bibliothek löschen
        self.scene_library.delete_scene(self.selected_scene_id)

        # Liste neu laden, damit die gelöschte Szene verschwindet
        self._refresh_list()

        # Auswahl zurücksetzen und Buttons deaktivieren
        self.selected_scene_id = None
        self.edit_btn.config(state="disabled")
        self.delete_btn.config(state="disabled")