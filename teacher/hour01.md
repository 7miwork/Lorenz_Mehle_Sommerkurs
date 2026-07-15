# Stunde 1 - Projekt erstellen (Lehrerversion)

In dieser ersten Unterrichtsstunde wird das technische Grundgerüst für das "Record Studio"-Projekt gelegt. Es werden noch keine fachlichen Funktionen (Profile, Charaktere, Szenen etc.) implementiert.

---

## app.py

```python
# Record Studio - Hauptanwendung
# Diese Datei startet das Tkinter-Fenster der Anwendung.

import tkinter as tk
from tkinter import font


class RecordStudioApp:
    """Hauptklasse der Record Studio Anwendung.
    
    Erbt von tk.Tk, um das Hauptfenster zu definieren.
    In zukünftigen Stunden können hier weitere Module (Frames)
    eingehängt werden.
    """
    
    def __init__(self):
        # Fenster initialisieren
        super().__init__()
        
        # Fenster konfigurieren
        self.title("Record Studio")
        self.geometry("1280x800")
        
        # Minimale Fenstergröße festlegen
        self.minsize(800, 600)
        
        # Fenster auf dem Bildschirm zentrieren
        self._center_window()
        
        # UI erstellen
        self._build_ui()
    
    def _center_window(self):
        """Berechnet die Position, damit das Fenster zentriert erscheint."""
        # Bildschirmgröße ermitteln
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Fenstergröße
        window_width = 1280
        window_height = 800
        
        # Position berechnen
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        
        # Geometrie mit Position setzen
        self.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    
    def _build_ui(self):
        """Erstellt die Benutzeroberfläche."""
        # Überschrift-Label erstellen
        # fette Schrift, Größe 24 für gute Lesbarkeit
        heading_font = font.Font(family="Arial", size=24, weight="bold")
        
        welcome_label = tk.Label(
            self,
            text="Record Studio – Willkommen",
            font=heading_font
        )
        
        # Label zentriert im Fenster platzieren
        welcome_label.place(relx=0.5, rely=0.5, anchor="center")


def main():
    """Einstiegspunkt der Anwendung."""
    # Tkinter-Anwendung erstellen und Hauptschleife starten
    app = RecordStudioApp()
    app.mainloop()


# Standard-Guard: Nur ausführen, wenn diese Datei direkt gestartet wird
if __name__ == "__main__":
    main()
```

### Erklärung der wichtigsten Code-Abschnitte

#### Import
```python
import tkinter as tk
from tkinter import font
```
- `tkinter` ist die Python-Standardbibliothek für GUI-Anwendungen
- `font` wird benötigt, um die Schriftgröße und -art zu konfigurieren
- `as tk` ist eine übliche Konvention, die den Code kürzer macht

#### Klassendefinition
```python
class RecordStudioApp:
```
- Die Hauptklasse erbt von `tk.Tk` (via `super().__init__()`), was sie zur Hauptfenster-Klasse macht
- **Vorteil**: Kapselung aller Anwendungslogik in einer Klasse, leichter erweiterbar
- Alle späteren Frames/Module können als Attribute dieser Klasse verwaltet werden

#### Fenster-Konfiguration
```python
self.title("Record Studio")
self.geometry("1280x800")
self.minsize(800, 600)
```
- `title()`: Setzt den Fenstertitel
- `geometry()`: Definiert die Startgröße (Breite x Höhe)
- `minsize()`: Verhindert, dass das Fenster kleiner als 800x600 gezogen werden kann

#### Zentrierung
```python
def _center_window(self):
    screen_width = self.winfo_screenwidth()
    screen_height = self.winfo_screenheight()
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
```
- `winfo_screenwidth/height()`: Fragt die aktuelle Bildschirmauflösung ab
- `// 2`: Ganzzahlige Division, um die Mitte zu berechnen
- Das Fenster erscheint unabhängig von der Bildschirmgröße immer zentriert

#### UI-Aufbau
```python
heading_font = font.Font(family="Arial", size=24, weight="bold")
welcome_label = tk.Label(self, text="Record Studio – Willkommen", font=heading_font)
welcome_label.place(relx=0.5, rely=0.5, anchor="center")
```
- `font.Font()`: Erstellt ein Font-Objekt mit gewünschten Eigenschaften
- `tk.Label()`: Erstellt ein Text-Label
- `place()`: Positioniert das Label absolut (alternativ ginge `pack()` oder `grid()`)
- `relx=0.5, rely=0.5`: Setzt die Position auf 50% der Fensterbreite/Höhe
- `anchor="center"`: Zentriert das Label an diesem Punkt

#### main() und if __name__
```python
def main():
    app = RecordStudioApp()
    app.mainloop()

if __name__ == "__main__":
    main()
```
- `main()`: Trennt den Startcode von der Klassendefinition (übersichtlicher)
- `mainloop()`: Startet die Tkinter-Ereignisschleife (unerlässlich!)
- `if __name__ == "__main__":`: Stellt sicher, dass der Code nur ausgeführt wird, wenn app.py direkt gestartet wird (nicht bei Import)

---

## Warum diese Architektur?

### Klasse statt Prozedural
- **Vorteile**:
  - Einfache Verwaltung von Zuständen (z.B. aktuelles Projekt, ausgewählter Charakter)
  - Klare Trennung von Daten und UI
  - Methoden können leicht aufgerufen werden (z.B. `self._build_ui()`)
  - Bessere Lesbarkeit für komplexere Anwendungen
  - Einfache Erweiterung durch Vererbung oder Komposition

### Ordnerstruktur
- **assets/**: Alle Medien (Grafik, Audio, Schriften) – klar getrennt von Code
- **core/**: Später die Geschäftslogik (Charaktere laden, Szenen verwalten etc.)
- **ui/**: Später weitere UI-Komponenten (Menüs, Dialoge, Editor-Fenster)
- **projects/**: Speicherort für Benutzerprojekte
- **profiles/**: Benutzerprofile (Lehrer/Schüler-Einstellungen)
- **exports/**: Exportierte Videos/Dateien
- **teacher/**: Lehrermaterial (Arbeitsblätter, Lösungen)
- **student/**: Schülermaterial (Anleitungen, Aufgaben)
- **docs/**: Dokumentation
- **tools/**: Hilfstools (Konverter, Prüfer etc.)

### Erweiterbarkeit
- In Stunde 2 wird ein `MainFrame` oder `MenuFrame` hinzugefügt
- Neue Frames können als Toplevel-Fenster oder als eingebettete Widgets realisiert werden
- Die `RecordStudioApp`-Klasse bleibt bestehen und dient als Container

---

## Mögliche Stolperfallen beim Schüler

1. **Tkinter-Import vergessen**
   - Fehler: `NameError: name 'tk' is not defined`
   - Lösung: `import tkinter as tk` nicht vergessen

2. **Falsche Datei ausgeführt**
   - Problem: Schüler starten versehentlich eine andere Datei
   - Lösung: Im Terminal immer `python app.py` ausführen (nicht `python teacher/hour01.py`)

3. **Einfüge-/Einrückungsfehler**
   - Problem: Tkinter braucht korrekte Einrückung (4 Leerzeichen oder Tabulator)
   - Lösung: Editor mit Python-Unterstützung verwenden (VS Code mit Python-Extension)

4. **super().__init__() vergessen**
   - Problem: Fenster wird nicht richtig initialisiert
   - Lösung: Zeile `super().__init__()` muss in `__init__` vorhanden sein

5. **mainloop() fehlt**
   - Problem: Fenster öffnet sich und schließt sofort wieder
   - Lösung: `app.mainloop()` muss am Ende von `main()` aufgerufen werden

6. **if __name__ == "__main__":** vergessen
   - Problem: Code wird auch bei Import ausgeführt
   - Lösung: Immer den Guard verwenden

7. **Pfad-Probleme bei assets/**
   - Problem: Wenn später Bilder geladen werden, relative Pfade nutzen
   - Lösung: Immer `assets/characters/bild.png` verwenden (nie absolute Pfade)

---

## Mögliche Erweiterungen (ohne den Kursplan zu verändern)

- **Fenster-Icon setzen**: `self.iconbitmap("assets/icons/icon.ico")`
- **Andere Schriftart**: Z.B. `family="Helvetica"` oder systemeigene Fonts verwenden
- **Hintergrundfarbe**: `self.configure(bg="#f0f0f0")` für hellgrauen Hintergrund
- **Statusleiste unten**: Ein `tk.Label` mit `place(relx=0, rely=1, anchor="sw")` für eine Fußzeile
- **Tastenkürzel**: `<F11>` für Vollbild, `<Escape>` zum Beenden
- **Window-Manager-Protocol**: `self.protocol("WM_DELETE_WINDOW", self._on_close)` für eigenen Schließen-Code

---

## Prüfungen

### Funktioniert das Fenster?
- [ ] Fenster öffnet sich ohne Fehlermeldung
- [ ] Titel lautet "Record Studio"
- [ ] Größe ist 1280x800 Pixel
- [ ] Fenster ist zentriert
- [ ] Label "Record Studio – Willkommen" ist sichtbar
- [ ] Minimale Größe 800x600 funktioniert
- [ ] Fenster lässt sich über X schließen