# Stunde 4 - Character Editor: Grafische Verwaltung

## Was du heute lernst

- **Ein Toplevel-Fenster erstellen** – ein eigenständiges Fenster, das als Kind des Hauptfensters erscheint
- **Eine Treeview-Liste bauen** – eine Tabelle mit Spalten (Name, Beschreibung), in der alle Charaktere angezeigt werden
- **Buttons mit Zustand** – "Bearbeiten" und "Löschen" sind nur aktiv, wenn eine Zeile ausgewählt ist
- **Einen Dialog mit Eingabefeldern** – für das Erstellen und Bearbeiten von Charakteren
- **Bestätigungsdialog** – bevor etwas gelöscht wird, fragt der Benutzer "Bist du sicher?"
- **Die Treeview nach Änderungen aktualisieren** – nach dem Erstellen, Bearbeiten oder Löschen wird die Liste neu geladen

## Deine Aufgabe

In dieser Stunde baust du einen **Character Editor** – eine grafische Oberfläche, in der du Charaktere direkt in der App ansehen, erstellen, bearbeiten und löschen kannst. Die Daten bleiben in der CharacterLibrary (aus Stunde 3), du baust nur die **Benutzeroberfläche** dafür.

### Teil 1: `ui/__init__.py` anlegen

Erstelle eine `__init__.py`-Datei im `ui/`-Ordner – genau wie im `core/`-Ordner in Stunde 3. Sie macht den Ordner zu einem Python-Paket, damit der Import `from ui.character_editor import CharacterEditor` funktioniert.

**Tipp:** Kopiere einfach den Stil von `core/__init__.py` und ersetze `core` durch `ui`.

### Teil 2: `ui/character_editor.py` – Die `CharacterEditor`-Klasse

Jetzt kommt die Hauptarbeit. Du erstellst eine Klasse `CharacterEditor`, die von `tk.Toplevel` erbt – das ist ein eigenständiges Fenster, das als Kind des Hauptfensters erscheint.

#### Schritt 2a: Klasse und Konstruktor

```python
class CharacterEditor(tk.Toplevel):
    def __init__(self, parent, character_library):
        super().__init__(parent)
        ...
```

- `parent` ist das Hauptfenster (die `RecordStudioApp`-Instanz).
- `character_library` ist die `CharacterLibrary`-Instanz, die du in `app.py` erstellt hast.
- Speichere beide als `self.character_library` und `self.selected_character_id = None`.
- Setze Titel, Fenstergröße (600x400) und `self.transient(parent)`.
- Rufe `self._build_ui()` und `self._refresh_list()` auf.

#### Schritt 2b: Die Treeview-Liste

Erstelle eine `ttk.Treeview` mit zwei Spalten: **Name** und **Beschreibung**. Wichtig:

- Benutze `columns=("name", "description")` und `show="headings"`.
- `show="headings"` ist wichtig – ohne es erscheint eine leere Spalte links.
- Setze die Spaltenüberschriften mit `self.tree.heading(...)`.
- Verbinde das Auswahl-Ereignis: `self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)`.

#### Schritt 2c: Die drei Buttons

Erstelle einen `tk.Frame` als Button-Leiste mit drei Buttons:

- **"Neuer Charakter"** → ruft `self._open_create_dialog()` auf
- **"Bearbeiten"** → ruft `self._open_edit_dialog()` auf, **initial deaktiviert** (`state="disabled"`)
- **"Löschen"** → ruft `self._delete_character()` auf, **initial deaktiviert** (`state="disabled"`)

Unten ein **"Schließen"**-Button, der `self.destroy` aufruft.

#### Schritt 2d: `_refresh_list()` – Die Liste neu befüllen

Diese Methode löscht alle Einträge in der Treeview und füllt sie neu:

```python
def _refresh_list(self):
    for item in self.tree.get_children():
        self.tree.delete(item)
    characters = self.character_library.get_all_characters()
    for character in characters:
        self.tree.insert("", "end", iid=character.character_id, values=(character.name, character.description))
```

**Wichtig:** Benutze `iid=character.character_id` beim Einfügen! So weißt du später, welche character_id zur ausgewählten Zeile gehört – nicht nur den Namen.

#### Schritt 2e: `_on_tree_select()` – Buttons aktivieren

Wenn der Benutzer eine Zeile klickt, sollen "Bearbeiten" und "Löschen" aktiv werden:

```python
def _on_tree_select(self, event):
    selected = self.tree.selection()
    if selected:
        self.selected_character_id = selected[0]
        self.edit_btn.config(state="normal")
        self.delete_btn.config(state="normal")
    else:
        self.selected_character_id = None
        self.edit_btn.config(state="disabled")
        self.delete_btn.config(state="disabled")
```

`self.tree.selection()` gibt die Item-IDs der ausgewählten Zeilen zurück – und weil du `iid=character_id` gesetzt hast, ist das genau die character_id!

#### Schritt 2f: Der Dialog (Neu + Bearbeiten)

Erstelle eine Methode `_open_character_dialog(self, character_id=None)`, die für **beide** Modi verwendet wird:

- `character_id=None` → Neuer Charakter (leere Felder)
- `character_id` gesetzt → Bearbeiten (Felder vorbelegen)

Der Dialog ist ein `tk.Toplevel` mit:
- Eingabefeld "Name:" + `tk.Entry`
- Eingabefeld "Bildpfad:" + `tk.Entry`
- Eingabefeld "Beschreibung:" + `tk.Entry`
- "Speichern"-Button

Wenn `character_id` gesetzt ist, fülle die Felder mit `self.character_library.get_character(character_id)` vor.

Die `save()`-Funktion (lokale Funktion) liest die Eingaben aus und ruft auf:
- **Neu:** `self.character_library.create_character(name=..., image_path=..., description=...)`
- **Bearbeiten:** `self.character_library.update_character(character_id, name=..., image_path=..., description=...)`

Danach: `self._refresh_list()` und `dialog.destroy()`.

**Tipp:** Denke an eine einfache Prüfung – der Name darf nicht leer sein!

#### Schritt 2g: `_delete_character()` – Mit Bestätigung löschen

```python
def _delete_character(self):
    if self.selected_character_id is None:
        return
    if not messagebox.askyesno("Bestätigung", "Charakter wirklich löschen?"):
        return
    self.character_library.delete_character(self.selected_character_id)
    self._refresh_list()
    self.selected_character_id = None
    self.edit_btn.config(state="disabled")
    self.delete_btn.config(state="disabled")
```

- `messagebox.askyesno()` zeigt einen Dialog mit "Ja" und "Nein".
- Erst bei "Ja" wird gelöscht!
- Danach: Liste aktualisieren und Buttons deaktivieren.

### Teil 3: `app.py` erweitern

Jetzt verbindest du den Character Editor mit dem Hauptfenster:

1. **Import hinzufügen** (unterhalb des CharacterLibrary-Imports):
   ```python
   from ui.character_editor import CharacterEditor
   ```

2. **Button hinzufügen** in `_build_ui()` (unterhalb der Profil-Buttons, bei `relx=0.5, rely=0.85`):
   ```python
   self.character_editor_btn = tk.Button(
       self,
       text="Charaktere verwalten",
       command=self._open_character_editor,
       font=font.Font(family="Arial", size=10)
   )
   self.character_editor_btn.place(relx=0.5, rely=0.85, anchor="center")
   ```

3. **Methode hinzufügen** (nach `_refresh_profile_list`):
   ```python
   def _open_character_editor(self):
       CharacterEditor(self, self.character_library)
   ```

Das ist alles! Der Character Editor öffnet sich als Tochterfenster, wenn du auf "Charaktere verwalten" klickst.

## Was am Ende funktionieren soll

- **`python app.py` startet ohne Fehler** und zeigt den "Charaktere verwalten"-Button im Hauptfenster
- **Character Editor öffnet sich** als Tochterfenster (transient) mit einer Treeview-Liste
- **Treeview zeigt zwei Spalten** (Name, Beschreibung) – keine leere Spalte links
- **Liste ist alphabetisch sortiert** (nutzt `get_all_characters()`)
- **Neuer Charakter**: Klick auf "Neuer Charakter" → Dialog mit drei Eingabefeldern → Name eingeben + "Speichern" → neuer Charakter erscheint in der Liste
- **Bearbeiten**: Zeile auswählen → "Bearbeiten" wird aktiv → Dialog mit vorbelegten Werten → ändern + "Speichern" → Liste aktualisiert sich
- **Löschen**: Zeile auswählen → "Löschen" wird aktiv → Bestätigungsdialog erscheint → "Ja" = Charakter gelöscht, "Nein" = nichts passiert
- **Buttons ohne Auswahl**: "Bearbeiten" und "Löschen" sind deaktiviert, solange keine Zeile ausgewählt ist
- **Schließen**: Der "Schließen"-Button schließt das Editor-Fenster
- **JSON-Datei**: Nach jeder Änderung ist `assets/characters/character_data.json` aktualisiert
- **Keine absichtlichen Fehler** im Code – alles funktioniert sauber!
