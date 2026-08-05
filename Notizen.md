# 📝 Sommerkurs – Wichtige Notizen

> Diese Datei dient als persönlicher Spickzettel.
> Lies sie vor jeder Programmierstunde kurz durch.

---

# 🎯 Unser Ziel

Wir entwickeln gemeinsam das Programm **Record Studio**.

Nicht nur, dass es funktioniert – der Code soll auch:

- sauber
- verständlich
- erweiterbar
- professionell

sein.

---

# 💡 Die wichtigste Regel

> **Erst nachdenken, dann programmieren.**

Bevor du Code schreibst:

- Was soll passieren?
- Welche Klasse ist zuständig?
- Gibt es bereits eine passende Funktion?
- Muss ich wirklich neuen Code schreiben?

---

# 📂 Projektstruktur

Merke dir:

```
Projekt

│
├── Models
│
├── Views
│
├── Controller
│
├── Manager
│
└── Assets
```

Nicht alles gehört in eine Datei.

---

# 🧱 MVC

## Model

Speichert Daten.

Beispiele:

- Scene
- Speaker
- Audio
- Project

---

## View

Zeigt alles an.

Hier gehört die GUI hin.

Keine komplizierte Logik.

---

## Controller

Verbindet GUI und Daten.

---

## Manager

Kümmert sich um bestimmte Aufgaben.

Zum Beispiel:

- AudioManager
- ProjectManager
- SpeakerManager

---

# 🚫 Niemals

Nicht alles in eine Datei schreiben.

Nicht 500 Zeilen lange Funktionen schreiben.

Nicht Code kopieren.

Nicht denselben Code mehrfach schreiben.

Keine absoluten Pfade benutzen.

---

# ✅ Stattdessen

Lieber:

kleine Funktionen

kleine Klassen

gut lesbare Namen

eine Aufgabe pro Klasse

---

# 📁 Projektordner

Jedes Projekt besitzt:

```
Projektname/

project.json

scenes/

speakers/

bgm/

sfx/

exports/
```

---

# 👤 Sprecher

Jeder Sprecher bekommt einen eigenen Ordner.

Beispiel

```
speakers/

Mama/

Papa/

Erzähler/
```

Darin liegen alle Sprachaufnahmen.

---

# 🎙 Audio

Jede Aufnahme besitzt

- Name
- Dateiname
- Dauer
- Pfad

---

# 🎵 Hintergrundmusik

Kommt immer in

```
bgm/
```

---

# 🔊 Soundeffekte

Kommen immer in

```
sfx/
```

---

# 💾 Speichern

Alle Informationen gehören in

```
project.json
```

Dort werden gespeichert:

- Szenen
- Sprecher
- Audio
- Musik
- Soundeffekte

---

# ❗ Dateipfade

Immer:

✅ relative Pfade

Beispiel

```
speakers/Mama/hallo.wav
```

Nicht

```
C:\Users\Lorenz\Desktop\...
```

---

# 🧹 Sauberer Code

Frage dich immer:

Kann ich den Code in 6 Monaten noch verstehen?

Kann jemand anderes den Code lesen?

Brauche ich Kommentare?

Ist der Name verständlich?

---

# 📖 Gute Funktionsnamen

Gut

```
save_project()

load_project()

record_audio()

create_speaker()

delete_audio()
```

Nicht

```
do()

test()

funktion1()

abc()
```

---

# 🏗 Bevor du programmierst

Immer zuerst überlegen:

Welche Klasse?

Welche Funktion?

Welche Daten?

Wer ruft wen auf?

---

# 🐞 Wenn ein Fehler kommt

Nicht sofort alles ändern.

1. Fehlermeldung lesen
2. Verstehen
3. Ursache suchen
4. Erst dann ändern

---

# 📚 Wenn du nicht weiterkommst

Frage dich:

- Existiert die Variable?
- Existiert die Datei?
- Existiert der Ordner?
- Wird die Funktion überhaupt aufgerufen?

---

# ⭐ Goldene Regel

> Lieber langsam und sauber programmieren als schnell und chaotisch.

Professionelle Software entsteht Schritt für Schritt.

---

# 🚀 Unser langfristiges Ziel

Record Studio soll später können:

- Audio aufnehmen
- Mehrere Sprecher
- Hintergrundmusik
- Soundeffekte
- Timeline
- Videoexport
- Untertitel
- KI-Stimmen
- Lip Sync
- Mehrsprachigkeit

Deshalb entwickeln wir von Anfang an sauber und modular.

---

# ✅ Vor jedem Commit

Frage dich:

- Funktioniert alles?
- Habe ich nichts kaputt gemacht?
- Ist der Code lesbar?
- Sind unnötige Dateien entfernt?
- Ist alles gespeichert?

Dann erst committen.

---

# 🎉 Wichtig

Fehler sind völlig normal.

Jeder gute Entwickler macht Fehler.

Der Unterschied ist:

**Gute Entwickler lernen aus ihren Fehlern und verbessern ihren Code.**