# Hausaufgabe – Wiederholung & Vorbereitung (Lehrerversion mit Lösungen)

Diese Hausaufgabe wiederholt die Inhalte der Stunden 1–3 und bereitet gedanklich auf den Character Editor (Stunde 4) vor. Sie ist für eine Woche Ferienzeit ausgelegt – der Kurs findet nur einmal pro Woche statt, daher bewusst nicht überladen.

---

## Teil 1: Wiederholung Stunde 1 bis 3

### 1.1 Tkinter-Grundgerüst (Stunde 1)

**Frage 1:** Was bewirkt `super().__init__()` in der Klasse `RecordStudioApp`?

**Lösung:** `super().__init__()` ruft den Konstruktor der Elternklasse `tk.Tk` auf. Dadurch wird das eigentliche Tkinter-Fenster initialisiert. Ohne diesen Aufruf würde die Klasse kein Fenster erzeugen – `self.title()`, `self.geometry()` etc. würden fehlschlagen.

---

**Frage 2:** Warum steht `if __name__ == "__main__":` am Ende der Datei?

**Lösung:** Dieser Standard-Guard stellt sicher, dass der Code nur ausgeführt wird, wenn die Datei direkt gestartet wird (`python app.py`). Wird die Datei importiert (z.B. `from app import RecordStudioApp`), wird der Code im Guard nicht ausgeführt. Das verhindert unerwünschte Seiteneffekte bei Importen.

---

**Frage 3:** Was ist der Unterschied zwischen `pack()`, `grid()` und `place()`?

**Lösung:**
- `pack()`: Widgets werden nacheinander in einer Reihe oder Spalte angeordnet (einfach, aber wenig Kontrolle)
- `grid()`: Widgets werden in einem Raster (Zeilen/Spalten) angeordnet (`row=`, `column=`)
- `place()`: Widgets werden absolut positioniert (`x=`, `y=` oder relativ mit `relx=`, `rely=`) – gibt die meiste Kontrolle, aber ist unflexibel bei Fenstergrößenänderungen

---

### 1.2 Benutzerprofile – Debugging (Stunde 2)

**Frage 1:** Welche 4 funktionalen Fehler gab es? Was war ihre Ursache?

**Lösung:**
1. **Fehler 1** (user.py): `preferences` ohne None-Check → TypeError bei `None`
2. **Fehler 2** (user.py): `last_login` wird in `from_dict` nicht gesetzt → Login-Zeitstempel geht verloren
3. **Fehler 3** (profile_manager.py): Keine Existenz-Prüfung der JSON-Datei → FileNotFoundError
4. **Fehler 4+5** (profile_manager.py): `datetime.now()` ohne Import von `datetime` → NameError

---

**Frage 2:** Welche kosmetischen Fehler sind dir besonders aufgefallen?

**Lösung (Auswahl):**
- Label-Farbe `fg="gray"` (schwer lesbar)
- Typo "Wähle dein Profil" statt "Wähle dein Profil"
- Combobox-Breite `width=30` (zu schmal)
- Button-Texte "Neuer Benutzer" und "Löschen" (verwirrend)
- Bearbeiten-Button in rot statt blau
- Keine alphabetische Sortierung der Profilliste
- Kein Bestätigungsdialog vor dem Löschen

---

**Frage 3:** Wie hast du den `NameError: name 'datetime' is not defined` behoben?

**Lösung:** In `profile_manager.py` am Anfang der Datei den Import `from datetime import datetime` hinzufügen.

---

**Frage 4:** Warum sollte man vor dem Löschen eines Profils einen Bestätigungsdialog einbauen?

**Lösung:** Ein versehentlicher Klick auf "Löschen" würde das Profil sofort und unwiderruflich entfernen. Ein Bestätigungsdialog (`messagebox.askyesno`) gibt dem Benutzer die Chance, die Aktion zu überdenken oder abzubrechen. Das ist besonders wichtig, wenn die Aktion nicht rückgängig gemacht werden kann.

---

### 1.3 Character Library (Stunde 3)

**Aufgabe 1:** Erkläre in eigenen Worten: Was macht `to_dict()` und wozu braucht man es?

**Lösung:** `to_dict()` wandelt ein Character-Objekt in ein Dictionary um. Das ist nötig, weil `json.dump()` nur einfache Datentypen (str, int, list, dict) verarbeiten kann – keine Objekte. Das Dictionary wird dann als JSON in die Datei geschrieben. Ohne `to_dict()` könnte man die Objekte nicht speichern.

---

**Aufgabe 2:** Erkläre den Unterschied zwischen einer normalen Methode und einer `@classmethod`.

**Lösung:** Eine normale Methode bekommt `self` (die Instanz) als ersten Parameter übergeben. Eine `@classmethod` bekommt `cls` (die Klasse selbst) übergeben. Man kann eine `@classmethod` aufrufen, ohne vorher ein Objekt zu erstellen: `Character.from_dict(data)`. Das ist praktisch, um neue Objekte aus gespeicherten Daten zu erzeugen.

---

**Aufgabe 3:** Warum steht `"Character"` in Anführungszeichen beim Rückgabetyp von `from_dict()`?

**Lösung:** Das ist ein **Forward Reference**. Zum Zeitpunkt, wo Python die `from_dict`-Methode parst, ist die Klasse `Character` noch nicht vollständig definiert. Der Name in Anführungszeichen (`"Character"`) ist ein String, den Python erst später auflöst. Das ist nötig, weil `from_dict` ein `Character`-Objekt zurückgibt, aber die Klasse selbst noch im Entstehen ist.

---

## Teil 2: Vorbereitung Character Editor

### 2.1 Gedankliche Vorbereitung

**Frage 1:** Was bedeutet der Parameter `on_save_callback`? Warum übergibt man eine Funktion statt direkt zu speichern?

**Lösung:** `on_save_callback` ist eine Funktion, die aufgerufen wird, wenn der Benutzer auf "Speichern" klickt. Man übergibt eine Funktion (Callback) statt direkt zu speichern, weil der Editor nicht wissen muss, **was** nach dem Speichern passiert (z.B. Liste aktualisieren, Datenbank schreiben, UI neu laden). Das macht den Editor flexibel und wiederverwendbar. Das ist das **Callback-Muster** (auch bekannt als Dependency Inversion).

---

**Frage 2:** Welche GUI-Elemente braucht ein Character-Editor deiner Meinung nach?

**Lösung (mögliche Antwort):**
- Ein `tk.Entry` für den Namen
- Ein `tk.Entry` für den Bildpfad (oder ein "Durchsuchen"-Button)
- Ein `tk.Text` oder `tk.Entry` für die Beschreibung
- Ein Label, das das aktuelle Bild anzeigt (später)
- Ein "Speichern"-Button und ein "Abbrechen"-Button
- Ein Status-Label für Rückmeldungen

---

**Frage 3:** Soll der Editor ein eigenes Fenster (`tk.Toplevel`) werden oder in das Hauptfenster eingebaut sein? Begründe.

**Lösung (beides vertretbar):**
- **Eigenes Fenster (Toplevel):** Vorteil – der Editor ist modular und kann unabhängig vom Hauptfenster geöffnet/geschlossen werden. Nachteil – mehrere Fenster können verwirren.
- **Im Hauptfenster (Frame):** Vorteil – alles in einem Fenster, übersichtlicher. Nachteil – das Hauptfenster wird vollgestopft.
- **Empfehlung für den Kurs:** Ein Toplevel-Dialog, wie es auch der Profil-Editor in `app.py` macht. Das ist das bekannte Muster aus Stunde 2.

---

### 2.2 Code-Snippet erweitern (freiwillig)

**Musterlösung für `_build_ui()`:**

```python
def _build_ui(self):
    dialog = tk.Toplevel(self.parent)
    dialog.title("Charakter bearbeiten")
    dialog.geometry("400x300")
    dialog.transient(self.parent)
    
    # Name
    tk.Label(dialog, text="Name:").pack(pady=5)
    self.name_var = tk.StringVar(value=self.character.name)
    tk.Entry(dialog, textvariable=self.name_var, width=40).pack()
    
    # Bildpfad
    tk.Label(dialog, text="Bildpfad:").pack(pady=5)
    self.image_var = tk.StringVar(value=self.character.image_path)
    tk.Entry(dialog, textvariable=self.image_var, width=40).pack()
    
    # Beschreibung
    tk.Label(dialog, text="Beschreibung:").pack(pady=5)
    self.desc_text = tk.Text(dialog, height=5, width=40)
    self.desc_text.insert("1.0", self.character.description)
    self.desc_text.pack()
    
    # Buttons
    tk.Button(dialog, text="Speichern", command=self._on_save).pack(side="left", padx=20, pady=10)
    tk.Button(dialog, text="Abbrechen", command=dialog.destroy).pack(side="right", padx=20, pady=10)
```

**Zusatzfrage:** Was müsste in `_on_save()` passieren, damit die Änderungen gespeichert werden?

**Lösung:**

```python
def _on_save(self):
    # Werte aus der GUI holen
    self.character.name = self.name_var.get()
    self.character.image_path = self.image_var.get()
    self.character.description = self.desc_text.get("1.0", "end-1c")
    
    # Callback aufrufen, damit der Aufrufer die Änderungen speichern kann
    if self.on_save_callback:
        self.on_save_callback(self.character)
    
    # Fenster schließen
    self.master.destroy()
```

---

## Hinweise für den Lehrer

- Die Hausaufgabe ist bewusst als **Wiederholung und Denkanstoß** konzipiert, nicht als zusätzliche Belastung.
- Die Fragen zu Stunde 1–3 sind so gewählt, dass der Schüler die Konzepte **in eigenen Worten** erklären muss – das vertieft das Verständnis.
- Teil 2 (Character Editor) ist eine **Vorbereitung auf Stunde 4**. Der Schüler soll sich Gedanken machen, aber noch keinen Code schreiben müssen. Das Code-Snippet in 2.2 ist freiwillig.
- In der nächsten Stunde können die Lösungen kurz besprochen werden (10–15 Minuten), bevor mit dem Character Editor weitergemacht wird.
- Die Musterlösungen sind als **Erwartungshorizont** gedacht – der Schüler muss nicht alles wortwörtlich so sagen, sondern das Konzept verstanden haben.