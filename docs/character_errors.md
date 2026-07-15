# Fehleranalyse: Character Library Implementierung

## Die 3 bewussten Fehler und deren Lösungen

### FEHLER 1: Falscher Default-Wert für `description` (character.py, Zeile 29)

**Problem:** Der Parameter `description` hat als Default-Wert `"TODO"` statt eines leeren Strings. Wenn ein neuer Charakter ohne Beschreibung angelegt wird, steht in der JSON-Datei automatisch `"TODO"`.

```python
# Falsch:
description: str = "TODO",

# Richtig:
description: str = "",  # Leerer String als Standard
```

---

### FEHLER 2: Typo in Konsolen-Ausgabe (character_library.py, Zeile 62)

**Problem:** In der Ausgabe beim Abfangen eines ungültigen JSONs steht fälschlicherweise "Warnnung" (mit doppeltem 'n') statt "Warnung".

```python
# Falsch:
print(f"Warnnung: Die Datei {self.data_file} enthält ungültiges JSON.")

# Richtig:
print(f"Warnung: Die Datei {self.data_file} enthält ungültiges JSON.")
```

---

### FEHLER 3: Falsche Sortierung in `get_all_characters()` (character_library.py, Zeile 139)

**Problem:** Die Methode `get_all_characters()` sortiert laut Docstring und Kommentar alphabetisch nach Namen, tatsächlich wird aber nach `created_at` sortiert. Die Reihenfolge in der Liste ist daher die Erstell-Reihenfolge, nicht alphabetisch.

```python
# Falsch (sortiert nach Erstellzeit):
return sorted(self.characters.values(), key=lambda c: c.created_at)

# Richtig (alphabetisch nach Name):
return sorted(self.characters.values(), key=lambda c: c.name)
```

---

## Zusammenfassung

Die drei Fehler sind bewusst einfach gehalten, damit der Schüler ein Erfolgserlebnis hat. Alle Fehler lassen sich durch genaues Lesen des Codes oder durch Ausprobieren der betroffenen Funktionen finden. Keiner der Fehler führt zu einem Programmabsturz.

| Fehler | Datei | Zeile | Typ | Problem |
|--------|-------|-------|-----|---------|
| 1 | character.py | 29 | Kosmetisch | Default-Wert `"TODO"` statt `""` |
| 2 | character_library.py | 62 | Kosmetisch | Typo "Warnung" |
| 3 | character_library.py | 139 | Funktional | Sortierung nach `created_at` statt `name` |