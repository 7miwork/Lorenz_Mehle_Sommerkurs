"""FileManager: Verantwortlich für Dateisystemoperationen und Projektstruktur.

Erstellt automatisch Projektordner und Unterordner (scenes, speakers, bgm, sfx, exports).
Bietet Hilfsfunktionen, um relative Pfade in absolute Pfade zu übersetzen.
"""
from __future__ import annotations

import os
import json
from typing import List


class FileManager:
    """Hilfsklasse für Dateisystem-Operationen und Projekt-Layout.

    Alle Dateipfade werden relativ zum Arbeitsverzeichnis unter `projects/`
    verwaltet. Methoden liefern relative Pfade innerhalb des Projektordners
    (z. B. `speakers/Mama/begruessung.wav`) und konvertieren bei Bedarf in
    absolute Pfade.
    """

    BASE_DIR = "projects"

    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or self.BASE_DIR
        os.makedirs(self.base_dir, exist_ok=True)

    # --- Projekt-Ordner ---
    def create_project_folder(self, folder_name: str) -> str:
        path = os.path.join(self.base_dir, folder_name)
        os.makedirs(path, exist_ok=True)
        # Standard-Unterordner
        for sub in ("scenes", "speakers", "bgm", "sfx", "exports"):
            os.makedirs(os.path.join(path, sub), exist_ok=True)
        return path

    def project_exists(self, folder_name: str) -> bool:
        return os.path.isdir(os.path.join(self.base_dir, folder_name))

    def list_projects(self) -> List[str]:
        try:
            return sorted([
                name for name in os.listdir(self.base_dir)
                if os.path.isdir(os.path.join(self.base_dir, name))
            ])
        except FileNotFoundError:
            return []

    # --- Speaker-Folder Helpers ---
    def create_speaker_folder(self, project_folder: str, speaker_name: str) -> str:
        rel = os.path.join("speakers", speaker_name)
        abs_path = self.to_absolute(project_folder, rel)
        os.makedirs(abs_path, exist_ok=True)
        return rel

    def rename_speaker_folder(self, project_folder: str, old_name: str, new_name: str) -> bool:
        old_rel = os.path.join("speakers", old_name)
        new_rel = os.path.join("speakers", new_name)
        old_abs = self.to_absolute(project_folder, old_rel)
        new_abs = self.to_absolute(project_folder, new_rel)
        try:
            if os.path.exists(old_abs) and not os.path.exists(new_abs):
                os.rename(old_abs, new_abs)
            return True
        except Exception:
            return False

    def delete_speaker_folder(self, project_folder: str, speaker_name: str) -> bool:
        import shutil

        rel = os.path.join("speakers", speaker_name)
        abs_path = self.to_absolute(project_folder, rel)
        try:
            if os.path.exists(abs_path):
                shutil.rmtree(abs_path)
            return True
        except Exception:
            return False

    def get_speaker_folder(self, project_folder: str, speaker_name: str) -> str:
        return os.path.join("speakers", speaker_name)

    def create_speaker_structure(self, project_folder: str, speaker_name: str) -> bool:
        """Erstellt Unterordner A-Z und einen Ordner 'saetz' für einen Sprecher."""
        base = self.to_absolute(project_folder, self.get_speaker_folder(project_folder, speaker_name))
        try:
            for ch in list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + ["saetz"]:
                os.makedirs(os.path.join(base, ch), exist_ok=True)
            return True
        except Exception:
            return False

    def list_speaker_folder(self, project_folder: str, speaker_name: str, subfolder: str):
        rel = os.path.join(self.get_speaker_folder(project_folder, speaker_name), subfolder)
        abs_folder = self.to_absolute(project_folder, rel)
        if not os.path.isdir(abs_folder):
            return []
        return [f for f in os.listdir(abs_folder) if os.path.isfile(os.path.join(abs_folder, f))]

    # --- Path Utilities ---
    def to_absolute(self, project_folder: str, relative_path: str) -> str:
        # Normalisiere und entferne führende Slashes
        rel = relative_path.replace("/", os.sep).lstrip(os.sep)
        return os.path.abspath(os.path.join(self.base_dir, project_folder, rel))

    def read_json(self, project_folder: str, filename: str):
        path = self.to_absolute(project_folder, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def write_json(self, project_folder: str, filename: str, data) -> bool:
        path = self.to_absolute(project_folder, filename)
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
