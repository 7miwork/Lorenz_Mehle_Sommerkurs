"""Project Editor UI: Verwaltung von Projekten, Sprechern und Aufnahmen.

Dieses einfache Toplevel verbindet ProjectManager, SpeakerManager und
AudioManager mit einer kompakten Tkinter-Oberfläche, die für den Unterricht
leicht verständlich bleibt.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from typing import Optional


class ProjectEditor(tk.Toplevel):
    def __init__(self, parent, project_manager):
        super().__init__(parent)
        self.parent = parent
        self.pm = project_manager
        self.title("Projekt Editor")
        self.geometry("900x600")
        self.transient(parent)

        self.selected_project: Optional[str] = None
        self.selected_speaker_id: Optional[str] = None

        self._build_ui()
        self._refresh_projects()

    def _build_ui(self):
        # Left: Projects
        left = tk.Frame(self)
        left.pack(side="left", fill="y", padx=10, pady=10)

        tk.Label(left, text="Projekte").pack()
        self.project_list = tk.Listbox(left, width=30, height=20)
        self.project_list.pack()
        self.project_list.bind("<<ListboxSelect>>", self._on_project_select)

        tk.Button(left, text="Neues Projekt", command=self._new_project).pack(fill="x", pady=5)
        tk.Button(left, text="Projekt öffnen", command=self._open_project).pack(fill="x", pady=5)
        tk.Button(left, text="Projekt speichern", command=self._save_project).pack(fill="x", pady=5)

        # Middle: Speakers
        mid = tk.Frame(self)
        mid.pack(side="left", fill="y", padx=10, pady=10)
        tk.Label(mid, text="Sprecher").pack()
        self.speaker_tree = ttk.Treeview(mid, columns=("name",), show="headings", height=15)
        self.speaker_tree.heading("name", text="Name")
        self.speaker_tree.pack()
        self.speaker_tree.bind("<<TreeviewSelect>>", self._on_speaker_select)

        tk.Button(mid, text="Sprecher hinzufügen", command=self._add_speaker).pack(fill="x", pady=5)
        tk.Button(mid, text="Sprecher löschen", command=self._delete_speaker).pack(fill="x", pady=5)

        # Right: Recorder controls and recordings
        right = tk.Frame(self)
        right.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Status
        self.status_label = tk.Label(right, text="■ Bereit")
        self.status_label.pack(anchor="w")

        # Timer
        self.timer_label = tk.Label(right, text="00:00:00", font=(None, 20))
        self.timer_label.pack(anchor="w", pady=(5, 10))

        # Buttons
        btn_frame = tk.Frame(right)
        btn_frame.pack(anchor="w")

        self.start_btn = tk.Button(btn_frame, text="Aufnahme starten", command=self._start)
        self.start_btn.grid(row=0, column=0, padx=4, pady=4)

        self.pause_btn = tk.Button(btn_frame, text="Pause", command=self._pause, state="disabled")
        self.pause_btn.grid(row=0, column=1, padx=4, pady=4)

        self.stop_btn = tk.Button(btn_frame, text="Stop", command=self._stop, state="disabled")
        self.stop_btn.grid(row=0, column=2, padx=4, pady=4)

        self.play_btn = tk.Button(btn_frame, text="Abspielen", command=self._play, state="disabled")
        self.play_btn.grid(row=0, column=3, padx=4, pady=4)

        self.save_btn = tk.Button(btn_frame, text="Speichern", command=self._save_recording, state="disabled")
        self.save_btn.grid(row=0, column=4, padx=4, pady=4)

        # Recordings list
        tk.Label(right, text="Aufnahmen").pack(anchor="w", pady=(10, 0))
        self.rec_list = tk.Listbox(right)
        self.rec_list.pack(fill="both", expand=True)
        self.rec_list.bind("<<ListboxSelect>>", self._on_recording_select)

        # Internal timer update
        self._update_timer()

    def _refresh_projects(self):
        self.project_list.delete(0, "end")
        for name in self.pm.list_projects():
            self.project_list.insert("end", name)

    def _on_project_select(self, event):
        sel = self.project_list.curselection()
        if not sel:
            return
        name = self.project_list.get(sel[0])
        self.selected_project = name
        self.pm.open_project(name)
        self._refresh_speakers()

    def _new_project(self):
        name = simpledialog.askstring("Neues Projekt", "Projektname:")
        if not name:
            return
        proj = self.pm.create_project(name)
        self._refresh_projects()
        self.selected_project = proj.folder_name
        self.pm.open_project(self.selected_project)
        self._refresh_speakers()

    def _open_project(self):
        if not self.selected_project:
            messagebox.showwarning("Hinweis", "Bitte zuerst ein Projekt in der Liste auswählen.")
            return
        self.pm.open_project(self.selected_project)
        self._refresh_speakers()

    def _save_project(self):
        if not self.pm.current_project:
            messagebox.showwarning("Hinweis", "Kein geöffnetes Projekt.")
            return
        self.pm.save_project()
        messagebox.showinfo("Gespeichert", "Projekt gespeichert.")

    # --- Speaker UI ---
    def _refresh_speakers(self):
        for i in self.speaker_tree.get_children():
            self.speaker_tree.delete(i)

        if not self.pm.speaker_manager:
            return
        for sp in self.pm.speaker_manager.get_all_speakers():
            self.speaker_tree.insert("", "end", iid=sp.speaker_id, values=(sp.display_name,))

    def _add_speaker(self):
        if not self.pm.current_project:
            messagebox.showwarning("Hinweis", "Kein geöffnetes Projekt.")
            return
        name = simpledialog.askstring("Sprecher hinzufügen", "Anzeigename:")
        if not name:
            return
        sp = self.pm.speaker_manager.create_speaker(display_name=name)
        self._refresh_speakers()

    def _delete_speaker(self):
        sel = self.speaker_tree.selection()
        if not sel:
            return
        sp_id = sel[0]
        if messagebox.askyesno("Löschen", "Sprecher inklusive Audiodateien löschen?"):
            self.pm.speaker_manager.delete_speaker(sp_id, delete_files=True)
        else:
            self.pm.speaker_manager.delete_speaker(sp_id, delete_files=False)
        self._refresh_speakers()

    def _on_speaker_select(self, event):
        sel = self.speaker_tree.selection()
        if not sel:
            return
        sp_id = sel[0]
        self.selected_speaker_id = sp_id
        self._refresh_recordings()

    # --- Recordings ---
    def _refresh_recordings(self):
        self.rec_list.delete(0, "end")
        if not self.pm.speaker_manager or not self.selected_speaker_id:
            return
        sp = self.pm.speaker_manager.get_speaker(self.selected_speaker_id)
        if not sp:
            return
        for r in sp.recordings:
            self.rec_list.insert("end", f"{r.display_name} ({int(r.duration)}s)")
        # enable play if any
        self.play_btn.config(state="normal" if sp.recordings else "disabled")

    def _on_recording_select(self, event):
        sel = self.rec_list.curselection()
        if not sel:
            return
        idx = sel[0]
        # nothing else for now

    # --- Recorder controls (use ProjectManager.speaker_manager.audio_manager) ---
    def _start(self):
        am = self.pm.audio_manager
        if am.start_recording():
            self.status_label.config(text="● Aufnahme läuft...")
            self.start_btn.config(state="disabled")
            self.pause_btn.config(state="normal")
            self.stop_btn.config(state="normal")

    def _pause(self):
        am = self.pm.audio_manager
        if am.is_paused():
            am.resume_recording()
            self.pause_btn.config(text="Pause")
            self.status_label.config(text="● Aufnahme läuft...")
        else:
            am.pause_recording()
            self.pause_btn.config(text="Fortsetzen")
            self.status_label.config(text="|| Pausiert")

    def _stop(self):
        am = self.pm.audio_manager
        temp = am.stop_recording()
        if temp:
            self.status_label.config(text="■ Bereit")
            self.start_btn.config(state="normal")
            self.pause_btn.config(state="disabled", text="Pause")
            self.stop_btn.config(state="disabled")
            self.save_btn.config(state="normal")
            self.play_btn.config(state="normal")
            # store last temp path on instance
            self._last_temp = temp
            self._refresh_recordings()

    def _play(self):
        am = self.pm.audio_manager
        # Prefer selected recording playback; fallback to last temp
        sel = self.rec_list.curselection()
        if sel and self.selected_speaker_id:
            idx = sel[0]
            sp = self.pm.speaker_manager.get_speaker(self.selected_speaker_id)
            rec = sp.recordings[idx]
            abs_path = self.pm.file_manager.to_absolute(self.pm.current_project.folder_name, rec.filepath)
            am.play(abs_path)
        elif hasattr(self, "_last_temp"):
            am.play(self._last_temp)

    def _save_recording(self):
        if not hasattr(self, "_last_temp"):
            return
        if not self.selected_speaker_id:
            messagebox.showwarning("Hinweis", "Bitte zuerst einen Sprecher auswählen.")
            return
        name = simpledialog.askstring("Aufnahme speichern", "Anzeigename der Aufnahme:")
        if not name:
            return
        # Use OGG for recordings (space efficient), OPUS reserved for TTS/export.
        rec = self.pm.speaker_manager.add_recording(self.selected_speaker_id, name, self._last_temp, target_format="ogg")
        if rec:
            messagebox.showinfo("Gespeichert", "Aufnahme gespeichert.")
            self.save_btn.config(state="disabled")
            self._refresh_recordings()

    def _update_timer(self):
        am = self.pm.audio_manager
        if am.is_recording():
            elapsed = am.get_elapsed_time()
            self.timer_label.config(text=self._format_time(int(elapsed)))
        else:
            # reset to 00:00:00 if not recording
            if not hasattr(self, "_last_temp"):
                self.timer_label.config(text="00:00:00")
        self.after(300, self._update_timer)

    @staticmethod
    def _format_time(sec: int) -> str:
        h = sec // 3600
        m = (sec % 3600) // 60
        s = sec % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
