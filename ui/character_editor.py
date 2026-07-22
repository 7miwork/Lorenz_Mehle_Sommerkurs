# Character Editor für Record Studio
# Grafische Oberfläche zur Verwaltung von Charakteren (CRUD-Operationen)
# Zeigt eine Liste aller Charaktere an und ermöglicht das
# Erstellen, Bearbeiten und Löschen von Charakteren in der CharacterLibrary.

# Importiert die Tkinter-Bibliothek für GUI-Fenster
import tkinter as tk
# Importiert das ttk-Modul für erweiterte Widgets (Treeview) und messagebox für Dialoge
from tkinter import ttk, messagebox

# Importiert die CharacterLibrary für CRUD-Operationen auf Charakteren
from core.character_library import CharacterLibrary


class CharacterEditor(tk.Toplevel):
    """Grafischer Editor für die Character Library.

    Erbt von tk.Toplevel, um ein eigenständiges Fenster zu erzeugen,
    das als Kind des Hauptfensters (RecordStudioApp) erscheint.

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
        # Ruft den Konstruktor der Elternklasse (tk.Toplevel) auf
        super().__init__(parent)

        # Referenz auf die CharacterLibrary speichern, um später CRUD-Operationen auszuführen
        self.character_library = character_library

        # ID des aktuell ausgewählten Charakters (None, wenn nichts ausgewählt)
        self.selected_character_id = None

        # Fenster-Titel festlegen (erscheint in der Titelleiste)
        self.title("Charaktere verwalten")
        # Fenstergröße festlegen: 600 Pixel breit, 400 Pixel hoch
        self.geometry("600x400")
        # Das Fenster als Tochter des Hauptfensters kennzeichnen (transient)
        # Dadurch folgt es dem Hauptfenster bei Minimieren und erscheint zentriert darüber
        self.transient(parent)

        # Die Benutzeroberfläche erstellen (Treeview, Buttons, Schließen-Button)
        self._build_ui()

        # Die Liste der Charaktere beim Start initial befüllen
        self._refresh_list()

    def _build_ui(self):
        """Erstellt alle sichtbaren Elemente des Editor-Fensters.

        Aufbau:
        - Oben: ttk.Treeview mit zwei Spalten (Name, Beschreibung)
        - Darunter: Drei Buttons (Neuer Charakter, Bearbeiten, Löschen)
        - Unten: Schließen-Button
        """
        # ---------- TREVIEW (Charakterliste) ----------
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

        # Button: Neuer Charakter – öffnet einen Dialog zur Eingabe von Name, Bildpfad, Beschreibung
        self.new_btn = tk.Button(
            button_frame,
            text="Neuer Charakter",
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
            command=self._delete_character,
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
        """Lädt alle Charaktere neu und füllt die Treeview-Liste auf.

        Die Methode wird nach jeder Änderung (Neu/Bearbeiten/Löschen)
        aufgerufen, um sicherzustellen, dass die Anzeige aktuell ist.
        """
        # Alle vorhandenen Einträge in der Treeview entfernen
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Alle Charaktere laden (get_all_characters() liefert sie bereits alphabetisch sortiert)
        characters = self.character_library.get_all_characters()

        # Jeden Charakter als neue Zeile in die Treeview einfügen
        # Die character_id wird als iid (item id) verwendet, damit wir später
        # den zugehörigen Charakter für Bearbeiten/Löschen wiederfinden
        for character in characters:
            self.tree.insert(
                "",
                "end",
                iid=character.character_id,
                values=(character.name, character.description)
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
            # Eine Zeile ist ausgewählt: die character_id speichern und Buttons aktivieren
            self.selected_character_id = selected[0]
            self.edit_btn.config(state="normal")
            self.delete_btn.config(state="normal")
        else:
            # Keine Zeile mehr ausgewählt: ID zurücksetzen und Buttons deaktivieren
            self.selected_character_id = None
            self.edit_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")

    def _open_create_dialog(self):
        """Öffnet einen Dialog zum Erstellen eines neuen Charakters.

        Ruft die interne Methode _open_character_dialog auf, ohne eine
        character_id zu übergeben (was den Modus "Neu" auslöst).
        """
        # character_id=None signalisiert: Neuer Charakter (nicht Bearbeiten)
        self._open_character_dialog(character_id=None)

    def _open_edit_dialog(self):
        """Öffnet einen Dialog zum Bearbeiten des ausgewählten Charakters.

        Die Eingabefelder werden mit den aktuellen Werten des Charakters
        vorbelegt. Beim Speichern wird update_character() aufgerufen.
        """
        # Wenn nichts ausgewählt ist, nichts tun (Sicherheitscheck)
        if self.selected_character_id is None:
            return

        # character_id setzen: Der Dialog weiß, dass er bearbeiten (nicht erstellen) soll
        self._open_character_dialog(character_id=self.selected_character_id)

    def _open_character_dialog(self, character_id=None):
        """Öffnet einen gemeinsamen Dialog für Neu- und Bearbeiten-Modus.

        Der Dialog enthält Eingabefelder für Name, Bildpfad und Beschreibung.
        Im Bearbeiten-Modus (character_id ist gesetzt) werden die Felder
        mit den aktuellen Werten vorbelegt.

        Args:
            character_id: None für einen neuen Charakter, sonst die ID
                          des zu bearbeitenden Charakters
        """
        # Bestimme, ob es um Erstellen oder Bearbeiten geht
        # (wird für den Fenster-Titel verwendet)
        is_edit_mode = character_id is not None

        # ---------- DIALOG-FENSTER ERSTELLEN ----------
        dialog = tk.Toplevel(self)
        dialog.title("Charakter bearbeiten" if is_edit_mode else "Neuer Charakter")
        dialog.geometry("400x300")
        # Der Dialog ist ein Tochterfenster des Editors (transient)
        dialog.transient(self)

        # ---------- EINGABEFELDER ----------
        # Name-Eingabe
        tk.Label(dialog, text="Name:").pack(pady=(20, 5))
        name_var = tk.StringVar()
        tk.Entry(dialog, textvariable=name_var, width=40).pack()

        # Bildpfad-Eingabe
        tk.Label(dialog, text="Bildpfad:").pack(pady=(10, 5))
        image_var = tk.StringVar()
        tk.Entry(dialog, textvariable=image_var, width=40).pack()

        # Beschreibung-Eingabe
        tk.Label(dialog, text="Beschreibung:").pack(pady=(10, 5))
        desc_var = tk.StringVar()
        tk.Entry(dialog, textvariable=desc_var, width=40).pack()

        # Wenn Bearbeiten-Modus: Die Eingabefelder mit den aktuellen Werten vorbelegen
        if is_edit_mode:
            character = self.character_library.get_character(character_id)
            if character:
                name_var.set(character.name)
                image_var.set(character.image_path)
                desc_var.set(character.description)

        # ---------- SPEICHERN-BUTTON ----------
        # Die save()-Funktion wird als lokale Funktion definiert,
        # weil sie Zugriff auf die Eingabevariablen und character_id braucht
        def save():
            """Liest die Eingaben aus, speichert den Charakter und schließt den Dialog."""
            # Eingaben auslesen und trimmen (entfernt führende/trailing Leerzeichen)
            name = name_var.get().strip()
            image_path = image_var.get().strip()
            description = desc_var.get().strip()

            # Einfache Validierung: Name darf nicht leer sein
            if not name:
                messagebox.showwarning("Warnung", "Bitte gib einen Namen ein!")
                return

            if is_edit_mode:
                # Bearbeiten: update_character mit der character_id aufrufen
                self.character_library.update_character(
                    character_id,
                    name=name,
                    image_path=image_path,
                    description=description
                )
            else:
                # Neu erstellen: create_character aufrufen (ID wird automatisch generiert)
                self.character_library.create_character(
                    name=name,
                    image_path=image_path,
                    description=description
                )

            # Die Treeview-Liste nach der Änderung neu befüllen
            self._refresh_list()

            # Dialog schließen
            dialog.destroy()

        # Speichern-Button mit der save()-Funktion verknüpfen
        tk.Button(dialog, text="Speichern", command=save).pack(pady=20)

    def _delete_character(self):
        """Löscht den ausgewählten Charakter nach einer Bestätigung.

        Zeigt zuerst einen Bestätigungsdialog (messagebox.askyesno) an.
        Erst wenn der Benutzer mit "Ja" bestätigt, wird der Charakter
        aus der CharacterLibrary gelöscht und die Liste aktualisiert.
        """
        # Sicherheitscheck: Wenn nichts ausgewählt ist, nichts tun
        if self.selected_character_id is None:
            return

        # Bestätigungsdialog anzeigen: "Charakter wirklich löschen?"
        # askyesno gibt True zurück, wenn der Benutzer auf "Ja" klickt
        if not messagebox.askyesno(
            "Bestätigung",
            "Charakter wirklich löschen?"
        ):
            # Benutzer hat "Nein" geklickt: Nichts tun
            return

        # Charakter in der Bibliothek löschen
        self.character_library.delete_character(self.selected_character_id)

        # Liste neu laden, damit der gelöschte Charakter verschwindet
        self._refresh_list()

        # Auswahl zurücksetzen und Buttons deaktivieren
        self.selected_character_id = None
        self.edit_btn.config(state="disabled")
        self.delete_btn.config(state="disabled")
