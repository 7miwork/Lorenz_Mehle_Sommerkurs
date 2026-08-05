"""BGMManager: Verwaltung von Hintergrundmusik-Dateien.

Ermöglicht Import, Umbenennen und Löschen von Musikdateien (OGG).
"""
from __future__ import annotations

import os
from typing import List

from core.file_manager import FileManager


class BGMManager:
    def __init__(self, project_folder: str, file_manager: FileManager):
        self.project_folder = project_folder
        self.file_manager = file_manager

    def import_bgm(self, source_path: str, display_name: str) -> str:
        # Copy into bgm folder, keep filename safe
        safe = "".join(c if c.isalnum() or c in " -_" else "_" for c in display_name).strip()
        target = os.path.join("bgm", f"{safe}{os.path.splitext(source_path)[1]}")
        abs_target = self.file_manager.to_absolute(self.project_folder, target)
        os.makedirs(os.path.dirname(abs_target), exist_ok=True)
        import shutil
        shutil.copy2(source_path, abs_target)
        return target

    def list_bgm(self) -> List[str]:
        abs_folder = self.file_manager.to_absolute(self.project_folder, "bgm")
        if not os.path.isdir(abs_folder):
            return []
        return [f for f in os.listdir(abs_folder) if os.path.isfile(os.path.join(abs_folder, f))]

    def delete_bgm(self, filename: str) -> bool:
        abs_path = self.file_manager.to_absolute(self.project_folder, os.path.join("bgm", filename))
        try:
            if os.path.exists(abs_path):
                os.remove(abs_path)
            return True
        except Exception:
            return False
