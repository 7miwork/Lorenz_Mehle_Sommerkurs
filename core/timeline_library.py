"""TimelineLibrary: Persistente Timeline-Datenbank.

Speichert Timeline-Einträge in assets/timeline/timeline_data.json.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime
from typing import Dict, Optional, List


class TimelineEntry:
    def __init__(
        self,
        entry_id: str,
        speaker_id: str,
        text: str,
        order: int = 0,
        scene_id: str = "",
    ):
        self.entry_id = entry_id
        self.speaker_id = speaker_id
        self.text = text
        self.order = order
        self.scene_id = scene_id
        self.created_at = datetime.now().isoformat()
        self.modified_at = self.created_at

    def to_dict(self) -> Dict[str, object]:
        return {
            "entry_id": self.entry_id,
            "speaker_id": self.speaker_id,
            "text": self.text,
            "order": self.order,
            "scene_id": self.scene_id,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "TimelineEntry":
        entry = cls(
            entry_id=data["entry_id"],
            speaker_id=data["speaker_id"],
            text=data.get("text", ""),
            order=int(data.get("order", 0)),
            scene_id=data.get("scene_id", ""),
        )
        entry.created_at = data.get("created_at", entry.created_at)
        entry.modified_at = data.get("modified_at", entry.created_at)
        return entry


class TimelineLibrary:
    def __init__(self, data_file: str = "assets/timeline/timeline_data.json"):
        self.data_file = data_file
        self.entries: Dict[str, TimelineEntry] = {}
        self._load_entries()

    def _load_entries(self):
        if not os.path.exists(self.data_file):
            self._save_entries()
            return

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data.get("entries", []):
                    entry = TimelineEntry.from_dict(item)
                    self.entries[entry.entry_id] = entry
        except json.JSONDecodeError:
            print(f"Warnung: Ungültiges JSON in {self.data_file}. Erstelle neue Datenbank.")
            self._save_entries()

    def _save_entries(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        data = {
            "entries": [entry.to_dict() for entry in self.entries.values()],
            "last_updated": datetime.now().isoformat(),
        }
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def create_entry(
        self,
        speaker_id: str,
        text: str,
        order: int = 0,
        scene_id: str = "",
    ) -> TimelineEntry:
        timestamp = int(time.time())
        entry_id = f"timeline_{speaker_id}_{timestamp}"
        entry = TimelineEntry(
            entry_id=entry_id,
            speaker_id=speaker_id,
            text=text,
            order=order,
            scene_id=scene_id,
        )
        self.entries[entry_id] = entry
        self._save_entries()
        return entry

    def get_entry(self, entry_id: str) -> Optional[TimelineEntry]:
        return self.entries.get(entry_id)

    def get_all_entries(self) -> List[TimelineEntry]:
        return sorted(self.entries.values(), key=lambda e: e.order)

    def update_entry(self, entry_id: str, **kwargs) -> bool:
        entry = self.entries.get(entry_id)
        if entry is None:
            return False
        for key, value in kwargs.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        entry.modified_at = datetime.now().isoformat()
        self._save_entries()
        return True

    def delete_entry(self, entry_id: str) -> bool:
        if entry_id not in self.entries:
            return False
        del self.entries[entry_id]
        self._save_entries()
        return True
