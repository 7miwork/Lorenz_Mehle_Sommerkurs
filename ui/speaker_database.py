"""GUI zur Verwaltung der globalen Speaker-Datenbank."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from typing import Optional

from core.speaker_library import SpeakerLibrary


class SpeakerDatabaseEditor(tk.Frame):
    def __init__(self, parent, speaker_library: SpeakerLibrary, audio_manager):
        super().__init__(parent)
        self.speaker_library = speaker_library
        self.audio_manager = audio_manager
        self.selected_id = None

        # Temporäre Aufnahme (noch nicht gespeichert)
        self._temp_audio_path: Optional[str] = None

        self._build_ui()
        self._refresh_list()
        self._refresh_speaker_combo()
        self._update_recording_timer()

    def _build_ui(self):
        self.tree = ttk.Treeview(self, columns=("name", "order", "notes"), show="headings")
        self.tree.heading("name", text="Name")
        self.tree.heading("order", text="Reihenfolge")
        self.tree.heading("notes", text="Notizen")
        self.tree.column("name", width=250)
        self.tree.column("order", width=100)
        self.tree.column("notes", width=330)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Neuer Sprecher", command=self._create).pack(side="left", padx=5)
        self.edit_btn = tk.Button(button_frame, text="Bearbeiten", command=self._edit, state="disabled")
        self.edit_btn.pack(side="left", padx=5)
        self.delete_btn = tk.Button(button_frame, text="Löschen", command=self._delete, state="disabled")
        self.delete_btn.pack(side="left", padx=5)

        # ---------- SPRECHER-AUFNAHME ----------
        self._build_recording_ui()

    def _build_recording_ui(self):
        """Erstellt den Bereich 'Sprecher-Aufnahme' unterhalb der Liste."""
        rec_frame = tk.LabelFrame(self, text="🎙 Sprecher-Aufnahme")
        rec_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Sprecher-Auswahl
        top = tk.Frame(rec_frame)
        top.pack(fill="x", padx=10, pady=(10, 4))
        tk.Label(top, text="Sprecher:").pack(side="left")
        self.rec_speaker_var = tk.StringVar()
        self.rec_speaker_combo = ttk.Combobox(
            top, textvariable=self.rec_speaker_var, state="readonly", width=25
        )
        self.rec_speaker_combo.pack(side="left", padx=8)
        self.rec_speaker_combo.bind(
            "<<ComboboxSelected>>", lambda e: self._update_word_combo()
        )

        # Wort-Auswahl (frei editierbar, Vorschläge = vorhandene Wörter)
        tk.Label(top, text="Wort:").pack(side="left")
        self.rec_word_var = tk.StringVar()
        self.rec_word_combo = ttk.Combobox(top, textvariable=self.rec_word_var, width=25)
        self.rec_word_combo.pack(side="left", padx=8)

        # Status (Aufnahme läuft / gestoppt / gespeichert)
        self.rec_status_label = tk.Label(rec_frame, text="■ Bereit", fg="black")
        self.rec_status_label.pack(anchor="w", padx=10)

        # Zeit-Anzeige der laufenden Aufnahme
        self.rec_timer_label = tk.Label(rec_frame, text="00:00", font=(None, 12))
        self.rec_timer_label.pack(anchor="w", padx=10)

        # Buttons
        rec_btns = tk.Frame(rec_frame)
        rec_btns.pack(fill="x", padx=10, pady=(4, 10))

        self.rec_start_btn = tk.Button(
            rec_btns, text="🎙 Aufnahme starten", command=self._start_word_recording
        )
        self.rec_start_btn.grid(row=0, column=0, padx=4)

        self.rec_stop_btn = tk.Button(
            rec_btns, text="⏹ Aufnahme stoppen",
            command=self._stop_word_recording, state="disabled"
        )
        self.rec_stop_btn.grid(row=0, column=1, padx=4)

        self.rec_play_btn = tk.Button(
            rec_btns, text="▶ Wiedergabe", command=self._play_word_recording,
            state="disabled"
        )
        self.rec_play_btn.grid(row=0, column=2, padx=4)

        self.rec_redo_btn = tk.Button(
            rec_btns, text="🔄 Neu aufnehmen", command=self._discard_word_recording,
            state="disabled"
        )
        self.rec_redo_btn.grid(row=0, column=3, padx=4)

        self.rec_save_btn = tk.Button(
            rec_btns, text="💾 Aufnahme speichern", command=self._save_word_recording,
            state="disabled"
        )
        self.rec_save_btn.grid(row=0, column=4, padx=4)

    # --- Hilfsfunktionen für die Sprecher-Aufnahme ---

    def _refresh_speaker_combo(self):
        """Füllt das Sprecher-Dropdown neu auf."""
        speakers = self.speaker_library.get_all_speakers()
        self.rec_speaker_combo['values'] = [s.display_name for s in speakers]
        if speakers and not self.rec_speaker_var.get():
            self.rec_speaker_var.set(speakers[0].display_name)
        self._update_word_combo()

    def _selected_speaker(self):
        """Gibt den aktuell im Aufnahme-Bereich gewählten Sprecher zurück."""
        name = self.rec_speaker_var.get()
        for speaker in self.speaker_library.get_all_speakers():
            if speaker.display_name == name:
                return speaker
        return None

    def _selected_word(self) -> str:
        """Gibt das aktuell eingegebene/gewählte Wort zurück."""
        return self.rec_word_var.get().strip()

    def _update_word_combo(self):
        """Aktualisiert die Wort-Vorschläge passend zum gewählten Sprecher."""
        speaker = self._selected_speaker()
        if speaker is None:
            self.rec_word_combo['values'] = []
            return
        self.rec_word_combo['values'] = self.speaker_library.get_word_names(
            speaker.speaker_id
        )

        tk.Button(self, text="Schließen", command=self.destroy).pack(pady=10)

    def _start_word_recording(self):
        """Startet die Aufnahme für den gewählten Sprecher + Wort."""
        speaker = self._selected_speaker()
        if speaker is None:
            messagebox.showwarning(
                "Kein Sprecher",
                "Bitte zuerst einen Sprecher auswählen.\n"
                "Falls keine Sprecher vorhanden sind, lege zuerst einen an."
            )
            return
        if not self._selected_word():
            messagebox.showwarning(
                "Kein Wort", "Bitte zuerst ein Wort auswählen oder eingeben."
            )
            return
        if self.audio_manager.is_recording():
            messagebox.showwarning(
                "Aufnahme läuft",
                "Es läuft bereits eine andere Aufnahme.\nBitte stoppe diese zuerst."
            )
            return

        if self._temp_audio_path:
            # Alte unverarbeitete Aufnahme verwerfen
            self.audio_manager.delete_file(self._temp_audio_path)
            self._temp_audio_path = None

        if not self.audio_manager.start_recording():
            # Graceful: verständliche Meldung statt Absturz
            messagebox.showerror(
                "Aufnahme nicht möglich",
                "Kein Mikrofon verfügbar.\nBitte überprüfe dein Aufnahmegerät."
            )
            return

        self.rec_status_label.config(text="🔴 Aufnahme läuft...", fg="red")
        self.rec_start_btn.config(state="disabled")
        self.rec_stop_btn.config(state="normal")
        self.rec_play_btn.config(state="disabled")
        self.rec_redo_btn.config(state="disabled")
        self.rec_save_btn.config(state="disabled")

    def _stop_word_recording(self):
        """Stoppt die Aufnahme und hält sie temporär (noch nicht gespeichert)."""
        temp_path = self.audio_manager.stop_recording()
        self.rec_status_label.config(text="■ Aufnahme gestoppt", fg="black")
        self.rec_start_btn.config(state="normal")
        self.rec_stop_btn.config(state="disabled")

        if temp_path:
            self._temp_audio_path = temp_path
            self.rec_play_btn.config(state="normal")
            self.rec_redo_btn.config(state="normal")
            self.rec_save_btn.config(state="normal")
        else:
            # Aufnahme fehlgeschlagen oder leer
            self.rec_play_btn.config(state="disabled")
            self.rec_redo_btn.config(state="disabled")
            self.rec_save_btn.config(state="disabled")
            messagebox.showerror(
                "Aufnahme fehlgeschlagen",
                "Die Aufnahme enthielt keine Audiodaten.\nBitte versuche es erneut."
            )

    def _play_word_recording(self):
        """Spielt die aktuelle (temporäre) Aufnahme ab."""
        if not self._temp_audio_path:
            messagebox.showinfo(
                "Keine Aufnahme vorhanden.", "Es gibt noch nichts abzuspielen."
            )
            return
        if not self.audio_manager.play(self._temp_audio_path):
            messagebox.showerror(
                "Wiedergabe fehlgeschlagen",
                "Die Aufnahme konnte nicht abgespielt werden."
            )

    def _discard_word_recording(self):
        """Verwirft die temporäre Aufnahme - gespeicherte Daten bleiben unberührt."""
        if self._temp_audio_path:
            self.audio_manager.delete_file(self._temp_audio_path)
            self._temp_audio_path = None
        self.rec_status_label.config(text="■ Bereit", fg="black")
        self.rec_play_btn.config(state="disabled")
        self.rec_redo_btn.config(state="disabled")
        self.rec_save_btn.config(state="disabled")

    def _save_word_recording(self):
        """Speichert die Aufnahme dauerhaft als Sprecher + Wort."""
        speaker = self._selected_speaker()
        if speaker is None:
            messagebox.showwarning(
                "Kein Sprecher", "Bitte zuerst einen Sprecher auswählen."
            )
            return
        word = self._selected_word()
        if not word:
            messagebox.showwarning(
                "Kein Wort", "Bitte zuerst ein Wort auswählen oder eingeben."
            )
            return
        if not self._temp_audio_path:
            messagebox.showinfo(
                "Keine Aufnahme vorhanden.", "Nimm zuerst eine Aufnahme auf."
            )
            return

        recording = self.speaker_library.add_word_recording(
            speaker.speaker_id, word, self._temp_audio_path, self.audio_manager
        )
        if recording is None:
            messagebox.showerror(
                "Speichern fehlgeschlagen",
                "Die Aufnahme konnte nicht gespeichert werden."
            )
            return

        # Temporäre Datei aufräumen (sie wurde an den Zielort kopiert)
        self.audio_manager.delete_file(self._temp_audio_path)
        self._temp_audio_path = None

        self.rec_status_label.config(
            text=f"💾 Gespeichert: {speaker.display_name} – {word}", fg="green"
        )
        self.rec_play_btn.config(state="disabled")
        self.rec_redo_btn.config(state="disabled")
        self.rec_save_btn.config(state="disabled")
        self._update_word_combo()

    def _update_recording_timer(self):
        """Aktualisiert die Zeit-Anzeige der laufenden Aufnahme."""
        # Nach dem Schließen des Fensters den Timer sauber beenden
        if not self.winfo_exists():
            return
        am = self.audio_manager
        if am.is_recording():
            seconds = int(am.get_elapsed_time())
            minutes = seconds // 60
            rest = seconds % 60
            self.rec_timer_label.config(text=f"{minutes:02d}:{rest:02d}")
        elif not self._temp_audio_path:
            self.rec_timer_label.config(text="00:00")
        self.after(300, self._update_recording_timer)

    def _refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for speaker in self.speaker_library.get_all_speakers():
            self.tree.insert("", "end", iid=speaker.speaker_id, values=(speaker.display_name, speaker.order, speaker.notes))
        self.edit_btn.config(state="disabled")
        self.delete_btn.config(state="disabled")
        # Auch das Aufnahme-Dropdown aktualisieren (neue/geänderte Sprecher)
        self._refresh_speaker_combo()

    def _on_select(self, event):
        selection = self.tree.selection()
        self.selected_id = selection[0] if selection else None
        enabled = bool(self.selected_id)
        self.edit_btn.config(state="normal" if enabled else "disabled")
        self.delete_btn.config(state="normal" if enabled else "disabled")

    def _create(self):
        self._open_editor()

    def _edit(self):
        if not self.selected_id:
            return
        self._open_editor(self.selected_id)

    def _delete(self):
        if not self.selected_id:
            return
        if messagebox.askyesno("Löschen", "Sprecher wirklich löschen?"):
            self.speaker_library.delete_speaker(self.selected_id)
            self._refresh_list()

    def _open_editor(self, speaker_id: str = None):
        editor = SpeakerEditDialog(self, self.speaker_library, speaker_id)
        self.wait_window(editor)
        self._refresh_list()


class SpeakerEditDialog(tk.Toplevel):
    def __init__(self, parent, speaker_library: SpeakerLibrary, speaker_id: str = None):
        super().__init__(parent)
        self.speaker_library = speaker_library
        self.speaker_id = speaker_id
        self.title("Sprecher bearbeiten" if speaker_id else "Neuer Sprecher")
        self.geometry("500x300")
        self.transient(parent)

        self.name_var = tk.StringVar()
        self.order_var = tk.IntVar(value=0)
        self.color_var = tk.StringVar()
        self.notes_var = tk.StringVar()

        self._build_ui()
        if speaker_id:
            self._load_speaker()

    def _build_ui(self):
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(frame, text="Name:").grid(row=0, column=0, sticky="e", pady=6)
        tk.Entry(frame, textvariable=self.name_var, width=40).grid(row=0, column=1, sticky="w")

        tk.Label(frame, text="Reihenfolge:").grid(row=1, column=0, sticky="e", pady=6)
        tk.Entry(frame, textvariable=self.order_var, width=10).grid(row=1, column=1, sticky="w")

        tk.Label(frame, text="Farbe:").grid(row=2, column=0, sticky="e", pady=6)
        tk.Entry(frame, textvariable=self.color_var, width=20).grid(row=2, column=1, sticky="w")

        tk.Label(frame, text="Notizen:").grid(row=3, column=0, sticky="ne", pady=6)
        self.notes_txt = tk.Text(frame, width=40, height=6)
        self.notes_txt.grid(row=3, column=1, sticky="w")

        tk.Button(self, text="Speichern", command=self._save).pack(pady=10)

    def _load_speaker(self):
        speaker = self.speaker_library.get_speaker(self.speaker_id)
        if not speaker:
            return
        self.name_var.set(speaker.display_name)
        self.order_var.set(speaker.order)
        self.color_var.set(speaker.color)
        self.notes_txt.delete("1.0", "end")
        self.notes_txt.insert("1.0", speaker.notes)

    def _save(self):
        name = self.name_var.get().strip()
        order = self.order_var.get()
        color = self.color_var.get().strip()
        notes = self.notes_txt.get("1.0", "end").strip()
        if not name:
            messagebox.showwarning("Fehler", "Bitte einen Namen eingeben.")
            return
        if self.speaker_id:
            self.speaker_library.update_speaker(
                self.speaker_id,
                display_name=name,
                order=order,
                color=color,
                notes=notes,
            )
        else:
            self.speaker_library.create_speaker(
                display_name=name,
                order=order,
                color=color,
                notes=notes,
            )
        self.destroy()
