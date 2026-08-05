"""Speaker Organizer: CRUD-Dialog für Sprecher innerhalb eines Projekts.

Erlaubt Erstellen, Bearbeiten und Löschen von Sprechern; nutzt
`ProjectManager.speaker_manager` für Operationen.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import os


class SpeakerOrganizer(tk.Toplevel):
    def __init__(self, parent, project_manager):
        super().__init__(parent)
        self.parent = parent
        self.pm = project_manager
        self.title("Sprecher organisieren")
        self.geometry("600x400")
        self.transient(parent)

        self._build_ui()
        self._refresh()

    def _build_ui(self):
        top = tk.Frame(self)
        top.pack(fill="both", expand=True, padx=10, pady=10)

        # Speakers list
        left = tk.Frame(top)
        left.pack(side="left", fill="y")
        tk.Label(left, text="Sprecher").pack()
        self.listbox = tk.Listbox(left, width=30)
        self.listbox.pack(fill="y", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        btns = tk.Frame(left)
        btns.pack(fill="x")
        tk.Button(btns, text="Neu", command=self._new).pack(side="left", padx=4)
        tk.Button(btns, text="Löschen", command=self._delete).pack(side="left", padx=4)

        # Details
        right = tk.Frame(top)
        right.pack(side="left", fill="both", expand=True, padx=(10,0))

        tk.Label(right, text="Details").pack(anchor="w")
        form = tk.Frame(right)
        form.pack(fill="both", expand=True)

        tk.Label(form, text="Anzeigename:").grid(row=0, column=0, sticky="e")
        self.name_var = tk.StringVar()
        tk.Entry(form, textvariable=self.name_var, width=40).grid(row=0, column=1, sticky="w")

        tk.Label(form, text="Reihenfolge:").grid(row=1, column=0, sticky="e")
        self.order_var = tk.IntVar(value=0)
        tk.Entry(form, textvariable=self.order_var, width=8).grid(row=1, column=1, sticky="w")

        tk.Label(form, text="Farbe:").grid(row=2, column=0, sticky="e")
        self.color_var = tk.StringVar()
        tk.Entry(form, textvariable=self.color_var, width=20).grid(row=2, column=1, sticky="w")

        tk.Label(form, text="Notizen:").grid(row=3, column=0, sticky="ne")
        self.notes_txt = tk.Text(form, height=6, width=40)
        self.notes_txt.grid(row=3, column=1, sticky="w")

        save_frame = tk.Frame(right)
        save_frame.pack(fill="x", pady=(10,0))
        tk.Button(save_frame, text="Speichern", command=self._save).pack(side="left", padx=4)
        tk.Button(save_frame, text="Schließen", command=self.destroy).pack(side="left", padx=4)

        # --- Textverwaltung ---
        sep = tk.Frame(right, height=2, bd=1, relief="sunken")
        sep.pack(fill="x", pady=8)

        tk.Label(right, text="Texte hinzufügen").pack(anchor="w")
        tframe = tk.Frame(right)
        tframe.pack(fill="x")

        tk.Label(tframe, text="Ordner:").grid(row=0, column=0, sticky="e")
        self.folder_var = tk.StringVar(value="A")
        choices = [*list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), "saetz"]
        self.folder_combo = ttk.Combobox(tframe, textvariable=self.folder_var, values=choices, state="readonly", width=6)
        self.folder_combo.grid(row=0, column=1, sticky="w")

        tk.Label(tframe, text="Dateiname (optional):").grid(row=1, column=0, sticky="e")
        self.text_name_var = tk.StringVar()
        tk.Entry(tframe, textvariable=self.text_name_var, width=30).grid(row=1, column=1, sticky="w")

        tk.Label(tframe, text="Text:").grid(row=2, column=0, sticky="ne")
        self.text_entry = tk.Text(tframe, height=6, width=40)
        self.text_entry.grid(row=2, column=1, sticky="w")

        tk.Button(right, text="Text hinzufügen", command=self._add_text).pack(anchor="w", pady=(6,0))

        tk.Label(right, text="Dateien im Ordner:").pack(anchor="w", pady=(8,0))
        self.files_list = tk.Listbox(right, height=6)
        self.files_list.pack(fill="x")
        file_btns = tk.Frame(right)
        file_btns.pack(fill="x")
        tk.Button(file_btns, text="Aktualisieren", command=self._refresh_files).pack(side="left", padx=4)
        tk.Button(file_btns, text="Löschen", command=self._delete_file).pack(side="left", padx=4)

    def _refresh(self):
        self.listbox.delete(0, "end")
        if not self.pm.current_project or not self.pm.speaker_manager:
            return
        for sp in self.pm.speaker_manager.get_all_speakers():
            self.listbox.insert("end", f"{sp.display_name} ({sp.speaker_id})")

    def _on_select(self, event):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        sp = self.pm.speaker_manager.get_all_speakers()[idx]
        self._load_details(sp)
        # refresh files for this speaker and default folder
        self._refresh_files()

    def _load_details(self, sp):
        self._cur_sp = sp
        self.name_var.set(sp.display_name)
        self.order_var.set(sp.order)
        self.color_var.set(sp.color or "")
        self.notes_txt.delete("1.0", "end")
        if sp.notes:
            self.notes_txt.insert("1.0", sp.notes)

    def _new(self):
        if not self.pm.current_project:
            messagebox.showwarning("Kein Projekt", "Bitte zuerst ein Projekt öffnen.")
            return
        name = simpledialog.askstring("Neuer Sprecher", "Anzeigename:")
        if not name:
            return
        sp = self.pm.speaker_manager.create_speaker(display_name=name)
        # Create A-Z + saetz structure
        try:
            self.pm.file_manager.create_speaker_structure(self.pm.current_project.folder_name, name)
        except Exception:
            pass
        self._refresh()


    def _delete(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        sp = self.pm.speaker_manager.get_all_speakers()[idx]
        if messagebox.askyesno("Löschen", "Sprecher inklusive Audiodateien löschen?"):
            self.pm.speaker_manager.delete_speaker(sp.speaker_id, delete_files=True)
        else:
            self.pm.speaker_manager.delete_speaker(sp.speaker_id, delete_files=False)
        self._refresh()

    def _save(self):
        if not hasattr(self, "_cur_sp") or self._cur_sp is None:
            messagebox.showwarning("Kein Sprecher", "Bitte zuerst einen Sprecher auswählen oder neu anlegen.")
            return
        name = self.name_var.get().strip()
        order = int(self.order_var.get()) if self.order_var.get() else 0
        color = self.color_var.get().strip()
        notes = self.notes_txt.get("1.0", "end").strip()
        self.pm.speaker_manager.update_speaker(self._cur_sp.speaker_id, display_name=name, order=order, color=color, notes=notes)
        self._refresh()

    def _add_text(self):
        if not hasattr(self, "_cur_sp") or self._cur_sp is None:
            messagebox.showwarning("Kein Sprecher", "Bitte zuerst einen Sprecher auswählen.")
            return
        folder = self.folder_var.get()
        name = self.text_name_var.get().strip()
        content = self.text_entry.get("1.0", "end").strip()
        if not content:
            messagebox.showwarning("Kein Text", "Bitte zuerst etwas Text eingeben.")
            return
        # build filename
        if not name:
            import time
            name = f"text_{int(time.time())}"
        if not name.lower().endswith(".txt"):
            name = name + ".txt"

        rel_folder = self.pm.file_manager.get_speaker_folder(self.pm.current_project.folder_name, self._cur_sp.display_name)
        rel = os.path.join(rel_folder, folder, name)
        abs_path = self.pm.file_manager.to_absolute(self.pm.current_project.folder_name, rel)
        try:
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Gespeichert", "Text wurde gespeichert.")
            self.text_entry.delete("1.0", "end")
            self.text_name_var.set("")
            self._refresh_files()
        except Exception as e:
            messagebox.showerror("Fehler", f"Datei konnte nicht gespeichert werden: {e}")

    def _refresh_files(self):
        self.files_list.delete(0, "end")
        if not hasattr(self, "_cur_sp") or self._cur_sp is None:
            return
        folder = self.folder_var.get()
        files = self.pm.file_manager.list_speaker_folder(self.pm.current_project.folder_name, self._cur_sp.display_name, folder)
        for f in files:
            self.files_list.insert("end", f)

    def _delete_file(self):
        sel = self.files_list.curselection()
        if not sel:
            return
        idx = sel[0]
        filename = self.files_list.get(idx)
        folder = self.folder_var.get()
        rel = os.path.join(self.pm.file_manager.get_speaker_folder(self.pm.current_project.folder_name, self._cur_sp.display_name), folder, filename)
        abs_path = self.pm.file_manager.to_absolute(self.pm.current_project.folder_name, rel)
        try:
            if os.path.exists(abs_path):
                os.remove(abs_path)
            self._refresh_files()
        except Exception as e:
            messagebox.showerror("Fehler", f"Datei konnte nicht gelöscht werden: {e}")
