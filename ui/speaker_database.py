"""GUI zur Verwaltung der globalen Speaker-Datenbank."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from core.speaker_library import SpeakerLibrary


class SpeakerDatabaseEditor(tk.Frame):
    def __init__(self, parent, speaker_library: SpeakerLibrary):
        super().__init__(parent)
        self.speaker_library = speaker_library
        self.selected_id = None

        self._build_ui()
        self._refresh_list()

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

        tk.Button(self, text="Schließen", command=self.destroy).pack(pady=10)

    def _refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for speaker in self.speaker_library.get_all_speakers():
            self.tree.insert("", "end", iid=speaker.speaker_id, values=(speaker.display_name, speaker.order, speaker.notes))
        self.edit_btn.config(state="disabled")
        self.delete_btn.config(state="disabled")

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
