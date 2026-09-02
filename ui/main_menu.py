# Hauptmenü für Record Studio
# Öffnet sich nach der Benutzeranmeldung und bietet Zugang zu allen
# Bereichen der Anwendung (Profile, Charaktere, Szenen).

import tkinter as tk
from tkinter import font


class MainMenu(tk.Toplevel):
    """Hauptmenü-Fenster, das nach der Benutzeranmeldung erscheint.

    Zeigt fünf Bereiche als Buttons an, die schrittweise durch die
    Anwendung führen:
        1. Benutzerprofile
        2. Character Library
        3. Character Editor
        4. Scene Library
        5. Scene Editor

    Jeder Button öffnet den zugehörigen Editor oder Dialog.

    Attribute:
        parent: Elternfenster (RecordStudioApp-Instanz)
        callbacks: Dictionary mit Callback-Funktionen für die einzelnen Bereiche
    """

    def __init__(self, parent, callbacks: dict):
        """Initialisiert das Hauptmenü.

        Args:
            parent: Elternfenster (RecordStudioApp-Instanz)
            callbacks: Dictionary mit den Callback-Funktionen:
                - "profiles":     Öffnet die Profil-Verwaltung
                - "char_library": Öffnet die Character Library
                - "char_editor":  Öffnet den Character Editor
                - "scene_library": Öffnet die Scene Library
                - "scene_editor":  Öffnet den Scene Editor
        """
        super().__init__(parent)

        self.parent = parent
        self.callbacks = callbacks

        # Fenster-Titel
        self.title("Record Studio – Hauptmenü")

        # Fenstergröße
        self.geometry("420x580")

        # Als Tochterfenster des Hauptfensters
        self.transient(parent)

        # Benutzeroberfläche aufbauen
        self._build_ui()

    def _build_ui(self):
        """Erstellt alle sichtbaren Elemente des Hauptmenüs."""
        # Überschrift
        heading_font = font.Font(family="Arial", size=18, weight="bold")
        tk.Label(
            self,
            text="Hauptmenü",
            font=heading_font
        ).pack(pady=(20, 5))

        # Unterüberschrift
        tk.Label(
            self,
            text="Wähle einen Bereich aus:",
            font=font.Font(family="Arial", size=12)
        ).pack(pady=(0, 20))

        # ---------- BEREICH-BUTTONS ----------
        # Ein Rahmen für die Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        # Gemeinsamer Font für alle Buttons
        btn_font = font.Font(family="Arial", size=12)
        btn_width = 30

        # 1. Benutzerprofile
        tk.Button(
            button_frame,
            text="1. Benutzerprofile",
            command=self._open("profiles"),
            font=btn_font,
            width=btn_width
        ).pack(pady=8)

        # 2. Character Library
        tk.Button(
            button_frame,
            text="2. Character Library",
            command=self._open("char_library"),
            font=btn_font,
            width=btn_width
        ).pack(pady=8)

        # 3. Character Editor
        tk.Button(
            button_frame,
            text="3. Character Editor",
            command=self._open("char_editor"),
            font=btn_font,
            width=btn_width
        ).pack(pady=8)

        # 4. Scene Library
        tk.Button(
            button_frame,
            text="4. Scene Library",
            command=self._open("scene_library"),
            font=btn_font,
            width=btn_width
        ).pack(pady=8)

        # 5. Scene Editor
        tk.Button(
            button_frame,
            text="5. Scene Editor",
            command=self._open("scene_editor"),
            font=btn_font,
            width=btn_width
        ).pack(pady=8)

        # 6. Projekt Editor (Sprecher, Audio, BGM, SFX)
        tk.Button(
            button_frame,
            text="6. Projekt Editor",
            command=self._open("project_editor"),
            font=btn_font,
            width=btn_width
        ).pack(pady=8)

        # 7. Sprecher Organizer
        tk.Button(
            button_frame,
            text="7. Sprecher organisieren",
            command=self._open("speaker_organizer"),
            font=btn_font,
            width=btn_width
        ).pack(pady=8)

        # 8. Globale Sprecher-Datenbank
        tk.Button(
            button_frame,
            text="8. Speaker Datenbank",
            command=self._open("speaker_database"),
            font=btn_font,
            width=btn_width
        ).pack(pady=8)

        # 9. Globale Timeline
        tk.Button(
            button_frame,
            text="9. Timeline verwalten",
            command=self._open("timeline_editor"),
            font=btn_font,
            width=btn_width
        ).pack(pady=8)

    def _open(self, area):
        """Gibt einen Handler zurück, der den Callback für den angegebenen Bereich aufruft."""
        def handler():
            callback = self.callbacks.get(area)
            if callback:
                callback()
        return handler