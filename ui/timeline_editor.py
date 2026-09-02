"""GUI zur Verwaltung der globalen Timeline-Datenbank."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from core.timeline_library import TimelineLibrary
from core.speaker_library import SpeakerLibrary


class TimelineEditor(tk.Frame):
    def __init__(self, parent, timeline_library: TimelineLibrary, speaker_library: SpeakerLibrary):
        super().__init__(parent)
        self.timeline_library = timeline_library
        self.speaker_library = speaker_library
        self.selected_id = None

        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        self.tree = ttk.Treeview(self, columns=("speaker", "text", "order", "scene"), show="headings")
        self.tree.heading("speaker", text="Sprecher")
        self.tree.heading("text", text="Text")
        self.tree.heading("order", text="Reihenfolge")
        self.tree.heading("scene", text="Szene")
        self.tree.column("speaker", width=180)
        self.tree.column("text", width=500)
        self.tree.column("order", width=80)
        self.tree.column("scene", width=120)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Neuer Eintrag", command=self._create).pack(side="left", padx=5)
        self.edit_btn = tk.Button(btn_frame, text="Bearbeiten", command=self._edit, state="disabled")
        self.edit_btn.pack(side="left", padx=5)
        self.delete_btn = tk.Button(btn_frame, text="Löschen", command=self._delete, state="disabled")
        self.delete_btn.pack(side="left", padx=5)
        tk.Button(self, text="Schließen", command=self.destroy).pack(pady=8)

    def _refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for entry in self.timeline_library.get_all_entries():
            speaker = self.speaker_library.get_speaker(entry.speaker_id)
            speaker_name = speaker.display_name if speaker else "<unbekannt>"
            self.tree.insert(
                "",
                "end",
                iid=entry.entry_id,
                values=(speaker_name, entry.text, entry.order, entry.scene_id),
            )
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
        if messagebox.askyesno("Löschen", "Eintrag wirklich löschen?"):
            self.timeline_library.delete_entry(self.selected_id)
            self._refresh_list()

    def _open_editor(self, entry_id: str = None):
        editor = TimelineEntryDialog(self, self.timeline_library, self.speaker_library, entry_id)
        self.wait_window(editor)
        self._refresh_list()


class TimelineEntryDialog(tk.Toplevel):
    def __init__(self, parent, timeline_library: TimelineLibrary, speaker_library: SpeakerLibrary, entry_id: str = None):
        super().__init__(parent)
        self.timeline_library = timeline_library
        self.speaker_library = speaker_library
        self.entry_id = entry_id
        self.title("Timeline-Eintrag bearbeiten" if entry_id else "Neuer Timeline-Eintrag")
        self.geometry("600x360")
        self.transient(parent)

        self.speaker_var = tk.StringVar()
        self.text_var = tk.StringVar()
        self.order_var = tk.IntVar(value=0)
        self.scene_var = tk.StringVar()

        self._build_ui()
        if entry_id:
            self._load_entry()

    def _build_ui(self):
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(frame, text="Sprecher:").grid(row=0, column=0, sticky="e", pady=6)
        speaker_names = [f"{s.display_name} | {s.speaker_id}" for s in self.speaker_library.get_all_speakers()]
        self.speaker_combo = ttk.Combobox(frame, textvariable=self.speaker_var, values=speaker_names, state="readonly", width=45)
        self.speaker_combo.grid(row=0, column=1, sticky="w")

        tk.Label(frame, text="Text:").grid(row=1, column=0, sticky="ne", pady=6)
        self.text_txt = tk.Text(frame, width=45, height=8)
        self.text_txt.grid(row=1, column=1, sticky="w")

        tk.Label(frame, text="Reihenfolge:").grid(row=2, column=0, sticky="e", pady=6)
        tk.Entry(frame, textvariable=self.order_var, width=8).grid(row=2, column=1, sticky="w")

        tk.Label(frame, text="Szene ID:").grid(row=3, column=0, sticky="e", pady=6)
        tk.Entry(frame, textvariable=self.scene_var, width=30).grid(row=3, column=1, sticky="w")

        tk.Button(self, text="Speichern", command=self._save).pack(pady=10)

    def _load_entry(self):
        entry = self.timeline_library.get_entry(self.entry_id)
        if not entry:
            return
        speaker = self.speaker_library.get_speaker(entry.speaker_id)
        if speaker:
            self.speaker_var.set(f"{speaker.display_name} | {speaker.speaker_id}")
        self.text_txt.insert("1.0", entry.text)
        self.order_var.set(entry.order)
        self.scene_var.set(entry.scene_id)

    def _save(self):
        speaker_label = self.speaker_var.get().strip()
        if not speaker_label:
            messagebox.showwarning("Fehler", "Bitte einen Sprecher wählen.")
            return
        speaker_id = speaker_label.split(" | ")[-1]
        text = self.text_txt.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Fehler", "Bitte einen Text eingeben.")
            return
        order = self.order_var.get()
        scene_id = self.scene_var.get().strip()

        if self.entry_id:
            self.timeline_library.update_entry(
                self.entry_id,
                speaker_id=speaker_id,
                text=text,
                order=order,
                scene_id=scene_id,
            )
        else:
            self.timeline_library.create_entry(
                speaker_id=speaker_id,
                text=text,
                order=order,
                scene_id=scene_id,
            )
        self.destroy()
