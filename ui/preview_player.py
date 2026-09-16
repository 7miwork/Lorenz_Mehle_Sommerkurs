"""PreviewPlayer: Diashow-artige Vorschau fuer ein Projekt.

Zeigt die von `build_export_sequence` erzeugte Sequenz Schritt fuer
Schritt: Szenenbild (gross), Charakterbilder und das zugehoerige
Sprecher-Audio. Die Wiedergabe laeuft automatisch durch die Schritte
in der Reihenfolge, die die Timeline vorgibt. Ist kein Audio
vorhanden, springt die Vorschau nach einer festen Anzeigezeit weiter.

Es wird bewusst KEINE Videodatei erzeugt - das geschieht erst in
einer spaeteren Stunde (export). Hier geht es nur um die Vorschau in
der Anwendung.

Wichtig fuer die Technik: Tkinter darf nur aus dem GUI-Thread
angefasst werden. Der Ton laeuft deshalb in einem Hintergrund-Thread,
das Weiterschalten macht ein Timer (after) im GUI-Thread.
"""

from typing import Optional

import os
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# Innen-Abmessungen des Bildbereichs (Breite x Hoehe in Pixeln)
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 450

# Mindest-Anzeigedauer eines Schritts in Millisekunden.
# Verhindert, dass ein Schritt mit leerem/fehlendem Audio zu schnell
# weiter springt.
MIN_DURATION_MS = 800

# Kleiner Zuschlag auf die gemessene Audio-Dauer (Millisekunden).
# So ist der Ton sicher fertig, bevor das Bild wechselt.
AUDIO_MARGIN_MS = 250


class PreviewPlayer(tk.Toplevel):
    """Zeigt eine Sequenz von Schritten als abspielbare Vorschau an."""

    def __init__(self, parent, steps: list, audio_manager=None):
        """Initialisiert den Vorschau-Player.

        Args:
            parent: Elternfenster (RecordStudioApp-Instanz)
            steps: Liste von ExportStep-Objekten aus build_export_sequence
            audio_manager: AudioManager fuer die Ton-Wiedergabe
        """
        super().__init__(parent)
        self.parent = parent
        self.steps = steps
        self.audio_manager = audio_manager

        # Aktueller Fortschritt und Wiedergabe-Zustand
        self._index = 0
        self._playing = False
        self._paused = False
        # True, wenn die Sequenz komplett durchgelaufen ist. Dann startet
        # "Abspielen" wieder beim ersten Schritt.
        self._finished = False
        # Speichert das geplante automatische Weiterschalten (after-ID)
        self._advance_after: Optional[str] = None
        # Behaelt das aktuelle Bild, damit es nicht vom Garbage-Collector
        # geloescht wird, bevor es angezeigt wurde
        self._photo = None

        self.title("Vorschau - Record Studio")
        self.geometry(f"{CANVAS_WIDTH + 40}x{CANVAS_HEIGHT + 140}")
        self.transient(parent)

        self._build_ui()
        # Ueber das Fenster-X soll dieselbe Aufraeum-Logik laufen
        # wie ueber den Schliessen-Button (Ton stoppen!).
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        # Zeigt direkt den ersten Schritt als Standbild an
        self._show_index(0)

    def _build_ui(self):
        """Erstellt alle sichtbaren Elemente des PreviewPlayer."""
        # Fortschritt ("Szene 2 von 5") mit Balken darunter
        self.progress_label = tk.Label(self, text="Szene 0 von 0", font=(None, 12, "bold"))
        self.progress_label.pack(pady=(10, 2))

        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, maximum=100.0)
        self.progress_bar.pack(fill="x", padx=12)

        # Szenenname und Text des Timeline-Eintrags
        self.title_label = tk.Label(self, text="", font=(None, 14))
        self.title_label.pack()
        self.text_label = tk.Label(self, text="", font=(None, 11),
                                   wraplength=CANVAS_WIDTH - 60)
        self.text_label.pack(pady=(0, 4))

        # Grosser Anzeigebereich fuer das Bild
        self.canvas = tk.Canvas(self, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="#2a2a3a")
        self.canvas.pack(padx=10, pady=4)

        # Bedien-Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=8)

        self.play_btn = tk.Button(btn_frame, text="Abspielen", command=self._toggle_play)
        self.play_btn.grid(row=0, column=0, padx=4)

        tk.Button(btn_frame, text="Zurueck", command=self._prev_step).grid(row=0, column=1, padx=4)
        tk.Button(btn_frame, text="Vor", command=self._next_step).grid(row=0, column=2, padx=4)
        tk.Button(btn_frame, text="Schliessen", command=self._on_close).grid(row=0, column=3, padx=4)

    def _on_close(self):
        """Haelt die Wiedergabe an und schliesst das Vorschau-Fenster.

        Verhindert, dass das Audio nach dem Schliessen weiterlaeuft.
        """
        # Geplantes Weiterschalten abbrechen
        self._cancel_advance()
        self._playing = False
        self._paused = False
        # Laufendes Audio stoppen
        self._stop_playback()
        self.destroy()

    def _toggle_play(self):
        """Schaltet die Wiedergabe: Starten, Pause oder Weiter.

        Die Taste hat drei Zustaende (Beschriftung zeigt den naechsten
        Schritt an):
            - "Abspielen" -> Wiedergabe startet (wird zu "Pause")
            - "Pause"     -> Bild bleibt stehen, Ton stoppt ("Weiter")
            - "Weiter"    -> Schritt laeuft weiter ("Pause")

        Hinweis: Beim Weiter wird der Ton des aktuellen Schritts von
        vorne abgespielt. sounddevice kann eine Ausgabe nicht anhalten
        und spaeter an derselben Stelle fortsetzen.
        """
        if self._playing and not self._paused:
            # Pause: Ton sofort stoppen und Timer abbrechen, das Bild
            # bleibt stehen.
            self._paused = True
            self._stop_playback()
            self._cancel_advance()
            self.play_btn.config(text="Weiter")
            return

        if self._playing and self._paused:
            # Weiter: aktuellen Schritt fortsetzen
            self._paused = False
            self.play_btn.config(text="Pause")
            self._schedule_advance()
            return

        # Start. Nach dem Ende der Sequenz beginnt sie wieder von vorne.
        if self._finished:
            self._show_index(0)
        self._playing = True
        self._paused = False
        self._finished = False
        self.play_btn.config(text="Pause")
        self._schedule_advance()

    def _show_index(self, index: int):
        """Zeigt den Schritt mit dem gegebenen Index an.

        Startet bei laufender Wiedergabe auch dessen Audio (im
        Hintergrund-Thread) und plant das automatische Weiter-Schalten.

        Args:
            index: Index des anzuzeigenden Schritts (wird geklemmt)
        """
        if not self.steps:
            return

        # Index innerhalb der gueltigen Grenzen halten
        self._index = max(0, min(index, len(self.steps) - 1))
        step = self.steps[self._index]

        # Fortschritt und Text aktualisieren
        self.progress_label.config(text=f"Szene {self._index + 1} von {len(self.steps)}")
        self.title_label.config(text=step.scene_name)
        self.text_label.config(text=step.text if step.text else "")

        # Fortschrittsbalken auf den aktuellen Schritt setzen
        self._update_progress()

        # Bild zeichnen
        self._render_frame(step)

        # Wiedergabe-Zustand zuruecksetzen, falls wir manuell gesprungen sind
        self._finished = False
        self._cancel_advance()
        if self._playing and not self._paused:
            self._schedule_advance()

    def _next_step(self):
        """Blaettert einen Schritt vor (haelt den Ton an)."""
        if not self.steps:
            return
        # Ton sofort stoppen; den Timer bricht _show_index ab.
        self._stop_playback()
        self._show_index(self._index + 1)

    def _prev_step(self):
        """Blaettert einen Schritt zurueck (haelt den Ton an)."""
        if not self.steps:
            return
        # Ton sofort stoppen; den Timer bricht _show_index ab.
        self._stop_playback()
        self._show_index(self._index - 1)

    def _schedule_advance(self):
        """Startet den Ton und plant das automatische Weiter-Schalten.

        Der Ton eines Schritts laeuft in einem Hintergrund-Thread, damit
        die Buttons waehrend des Sprechens klickbar bleiben. Das
        Weiterschalten macht ein Timer im GUI-Thread (Tkinter darf nur
        dort benutzt werden) - und zwar nach der Dauer des Schritts,
        also genau dann, wenn der Ton fertig ist.
        """
        if not self.steps or self._paused or not self._playing:
            return

        step = self.steps[self._index]
        has_audio = bool(
            step.audio_path and self.audio_manager is not None
            and os.path.exists(step.audio_path)
        )

        if has_audio:
            # Ton im Hintergrund abspielen (blockierend, aber ohne GUI)
            worker = threading.Thread(
                target=self._play_step_thread,
                args=(step.audio_path,),
                daemon=True,
            )
            worker.start()

        # Weiter-Schalten: Dauer des Tons (mit kleinem Zuschlag), sonst
        # die Anzeigedauer des Schritts. Nie kuerzer als MIN_DURATION_MS.
        duration_ms = int(step.duration * 1000)
        if has_audio:
            duration_ms += AUDIO_MARGIN_MS
        duration_ms = max(duration_ms, MIN_DURATION_MS)
        self._advance_after = self.after(duration_ms, self._on_step_finished)

    # ---------- BILD ----------

    def _render_frame(self, step):
        """Rendert das grosse Bild fuer einen Schritt und zeigt es im Canvas.

        Es wird zuerst das Szenenbild in das Canvas eingepasst. Fehlt
        ein Szenenbild, wird ein neutraler Hintergrund verwendet. Die
        Charakterbilder werden darueber (unten) eingeblendet.
        """
        # 1) Grundbild: Szenenbild oder neutraler Platzhalter
        try:
            if step.background_path and os.path.exists(step.background_path):
                base = Image.open(step.background_path).convert("RGB")
                base = self._fit(base, CANVAS_WIDTH, CANVAS_HEIGHT)
            else:
                # Kein Szenenbild -> dunkler Platzhalter
                base = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), (40, 40, 60))
        except Exception:
            base = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), (40, 40, 60))

        # 2) Charakterbilder unten einblenden (hoechstens zwei)
        for i, image_path in enumerate(step.image_paths[:2]):
            try:
                if not os.path.exists(image_path):
                    continue
                character = Image.open(image_path).convert("RGBA")
                character = self._fit(character, 220, 220)
                # Positionsbestimmung: untere Mitte, versetzt je Charakter
                x = (CANVAS_WIDTH - character.width) // 2 + (i - 0.5) * 170
                base.paste(character, (int(x), CANVAS_HEIGHT - character.height - 20), character)
            except Exception:
                # Einzelnes kaputtes Bild darf die Vorschau nicht brechen
                continue

        # 3) Bild im Canvas anzeigen (Referenz behalten!)
        self._photo = ImageTk.PhotoImage(base)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self._photo)

    @staticmethod
    def _fit(image: Image.Image, max_w: int, max_h: int) -> Image.Image:
        """Passt ein Bild proportional so an, dass es in eine Box passt.

        Args:
            image: Das Ursprungsbild
            max_w: Maximale Breite
            max_h: Maximale Hoehe

        Returns:
            Bild, das genau in die Box passt (Bildgroesse wird erhalten)
        """
        original_w, original_h = image.size
        # Skalierungsfaktor so waehlen, dass keine der Massangaben
        # die Box ueberschreitet
        ratio = min(max_w / original_w, max_h / original_h, 1.0)
        new_w = max(1, int(original_w * ratio))
        new_h = max(1, int(original_h * ratio))
        return image.resize((new_w, new_h), Image.Resampling.LANCZOS)

    def _update_progress(self):
        """Aktualisiert den Fortschrittsbalken zum aktuellen Schritt.

        Kleine Hilfsfunktion: Der Balken zeigt, wie weit die Vorschau
        schon ist. Beispiel: Schritt 1 von 4 -> 25 %.
        """
        total = len(self.steps)
        if total <= 0:
            self.progress_var.set(0.0)
            return
        percent = ((self._index + 1) / total) * 100.0
        self.progress_var.set(percent)

    def _play_step_thread(self, audio_path):
        """Spielt das Audio EINES Schritts im Hintergrund ab.

        Laeuft NICHT im GUI-Thread, damit die Buttons waehrend des Tons
        klickbar bleiben. Diese Funktion fasst deshalb Tkinter nicht an -
        sie spielt nur den Ton und ist danach fertig. Das Weiterschalten
        uebernimmt der Timer aus _schedule_advance().

        Args:
            audio_path: Pfad zur Audiodatei dieses Schritts
        """
        try:
            play = getattr(self.audio_manager, "play_blocking", None)
            if callable(play):
                play(audio_path)
            else:
                # Fallback: play() spielt nicht blockierend, der Timer
                # schaltet trotzdem nach der Dauer weiter.
                self.audio_manager.play(audio_path)
        except Exception:
            # Ein kaputter Ton darf die Vorschau nicht abbrechen
            pass

    def _cancel_advance(self):
        """Bricht ein geplantes automatisches Weiter-Schalten ab."""
        if self._advance_after is not None:
            try:
                self.after_cancel(self._advance_after)
            except Exception:
                pass
            self._advance_after = None

    def _on_step_finished(self):
        """Wird aufgerufen, wenn das automatische Weiter-Schalten zuschlaegt."""
        self._advance_after = None
        # Nicht weiterschalten, wenn pausiert oder die Wiedergabe gestoppt wurde
        if self._paused or not self._playing:
            return
        nxt = self._index + 1
        if nxt >= len(self.steps):
            # Ende erreicht -> Wiedergabe anhalten und wieder "Abspielen" zeigen
            self._playing = False
            self._paused = False
            self._finished = True
            self.play_btn.config(text="Abspielen")
            return
        self._show_index(nxt)

    def _stop_playback(self):
        """Haelt das laufende Audio an (falls der AudioManager das kann).

        Kleine Hilfsfunktion, damit beim Blaettern (Vor/Zurueck), beim
        Pausieren und beim Schliessen kein alter Ton weiterlaeuft.
        """
        # stop() gibt es im AudioManager. Der getattr-Check ist ein
        # Sicherheitsnetz: So stuerzt die Vorschau auch dann nicht ab,
        # wenn der AudioManager die Methode einmal nicht haben sollte.
        stop = getattr(self.audio_manager, "stop", None)
        if callable(stop):
            try:
                stop()
            except Exception:
                # Ein Fehler beim Stoppen darf die Vorschau nicht abbrechen
                pass