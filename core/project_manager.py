"""ProjectManager: Verwaltet Projekte (Erstellen, Laden, Speichern).

Erstellt Project-Ordner, speichert `project.json` und instanziiert
einen SpeakerManager für das geöffnete Projekt.
"""
from __future__ import annotations

import time
from typing import Optional, List

from core.project import Project
from core.file_manager import FileManager
from core.audio_manager import AudioManager
from core.speaker_manager import SpeakerManager


class ProjectManager:
    def __init__(self, file_manager: FileManager, audio_manager: AudioManager):
        self.file_manager = file_manager
        self.audio_manager = audio_manager
        self.current_project: Optional[Project] = None
        self.speaker_manager: Optional[SpeakerManager] = None

    def list_projects(self) -> List[str]:
        return self.file_manager.list_projects()

    def create_project(self, name: str) -> Project:
        project_id = f"proj_{int(time.time())}"
        project = Project(project_id=project_id, name=name)
        # Ordner anlegen
        self.file_manager.create_project_folder(project.folder_name)
        # Save project.json
        self.file_manager.write_json(project.folder_name, "project.json", project.to_dict())
        return project

    def open_project(self, folder_name: str) -> Optional[Project]:
        if not self.file_manager.project_exists(folder_name):
            return None

        data = self.file_manager.read_json(folder_name, "project.json")
        if data:
            project = Project.from_dict(data)
        else:
            # Fallback: create a minimal Project instance
            project = Project(project_id=f"proj_{int(time.time())}", name=folder_name, folder_name=folder_name)

        self.current_project = project
        # SpeakerManager für dieses Projekt erstellen
        self.speaker_manager = SpeakerManager(project.folder_name, self.file_manager, self.audio_manager)
        return project

    def save_project(self) -> bool:
        if not self.current_project:
            return False
        self.current_project.modified_at = time.ctime()
        return self.file_manager.write_json(self.current_project.folder_name, "project.json", self.current_project.to_dict())
