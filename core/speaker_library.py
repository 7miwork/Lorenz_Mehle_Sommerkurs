"""SpeakerLibrary: Persistente Sprecher-Datenbank.

Speichert Sprecher in einer JSON-Datei unter assets/speakers/
und bietet CRUD-Operationen ohne Projektkontext.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime
from typing import Dict, Optional, List

from core.speaker import Speaker, Recording


class SpeakerLibrary:
    def __init__(self, data_file: str = "assets/speakers/speaker_data.json"):
        self.data_file = data_file
        self.speakers: Dict[str, Speaker] = {}
        self._load_speakers()

    def _load_speakers(self):
        if not os.path.exists(self.data_file):
            self._save_speakers()
            return

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data.get("speakers", []):
                    speaker = Speaker.from_dict(item)
                    self.speakers[speaker.speaker_id] = speaker
        except json.JSONDecodeError:
            print(f"Warnung: Ungültiges JSON in {self.data_file}. Erstelle neue Datenbank.")
            self._save_speakers()

    def _save_speakers(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        data = {
            "speakers": [speaker.to_dict() for speaker in self.speakers.values()],
            "last_updated": datetime.now().isoformat(),
        }
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def create_speaker(
        self,
        display_name: str,
        character_id: str = "",
        order: int = 0,
        color: str = "",
        notes: str = "",
    ) -> Speaker:
        timestamp = int(time.time())
        speaker_id = f"speaker_{display_name.lower().replace(' ', '_')}_{timestamp}"
        speaker = Speaker(
            speaker_id=speaker_id,
            display_name=display_name,
            character_id=character_id,
            order=order,
            color=color,
            notes=notes,
        )
        self.speakers[speaker_id] = speaker
        self._save_speakers()
        return speaker

    def get_speaker(self, speaker_id: str) -> Optional[Speaker]:
        return self.speakers.get(speaker_id)

    def get_all_speakers(self) -> List[Speaker]:
        return sorted(self.speakers.values(), key=lambda s: s.order)

    def update_speaker(self, speaker_id: str, **kwargs) -> bool:
        speaker = self.speakers.get(speaker_id)
        if speaker is None:
            return False
        for key, value in kwargs.items():
            if hasattr(speaker, key):
                setattr(speaker, key, value)
        self._save_speakers()
        return True

    def delete_speaker(self, speaker_id: str) -> bool:
        if speaker_id not in self.speakers:
            return False
        del self.speakers[speaker_id]
        self._save_speakers()
        return True

    # ---------- WORT-AUFNAHMEN ----------

    @staticmethod
    def _make_safe_name(text: str) -> str:
        """Erstellt einen sicheren Datei-/Ordnernamen aus einem Text."""
        safe = "".join(
            c if c.isalnum() or c in " -_" else "_"
            for c in text
        ).strip()
        return safe if safe else "aufnahme"

    def get_word_names(self, speaker_id: str) -> List[str]:
        """Gibt alle Wörter zurück, für die der Sprecher schon Aufnahmen hat."""
        speaker = self.get_speaker(speaker_id)
        if speaker is None:
            return []
        return [rec.display_name for rec in speaker.recordings]

    def get_word_recording_path(self, speaker_id: str, word: str) -> Optional[str]:
        """Gibt den Dateipfad der Aufnahme für Sprecher + Wort zurück.

        Args:
            speaker_id: ID des Sprechers
            word: Das Wort (Anzeigename der Aufnahme)

        Returns:
            Pfad zur Audiodatei oder None, wenn keine Aufnahme existiert
        """
        speaker = self.get_speaker(speaker_id)
        if speaker is None:
            return None
        for rec in speaker.recordings:
            if rec.display_name == word:
                return rec.filepath
        return None

    def add_word_recording(
        self,
        speaker_id: str,
        word: str,
        temp_audio_path: str,
        audio_manager,
    ) -> Optional[Speaker]:
        """Speichert eine Aufnahme eindeutig als Sprecher + Wort.

        Die WAV-Datei wird in 'assets/speakers/<sprecher>/<wort>.wav'
        abgelegt (Ordner wird automatisch erstellt). Existiert für das
        Wort bereits eine Aufnahme, wird nur deren Datei ersetzt
        (explizites Überschreiben, nichts anderes wird gelöscht).

        Args:
            speaker_id: ID des Sprechers
            word: Das aufgenommene Wort
            temp_audio_path: Pfad zur temporären WAV-Aufnahme
            audio_manager: AudioManager zum Kopieren/Dauer-Messen

        Returns:
            Das neue Recording oder None bei Fehler
        """
        speaker = self.get_speaker(speaker_id)
        if speaker is None or not word:
            return None

        # Zielordner: assets/speakers/<sprecher>/
        speaker_folder = "assets/speakers/" + self._make_safe_name(speaker.display_name)
        os.makedirs(speaker_folder, exist_ok=True)

        filename = self._make_safe_name(word) + ".wav"
        target_path = os.path.join(speaker_folder, filename)

        # Datei vom temporären Speicherort an den Zielort kopieren
        if not audio_manager.save_recording(temp_audio_path, target_path, word):
            return None

        # Dauer der neuen Aufnahme ermitteln
        duration = audio_manager.get_duration(target_path)
        recording = Recording(
            recording_id=f"rec_{int(time.time())}",
            display_name=word,
            filename=filename,
            filepath=target_path,
            duration=duration,
        )

        # Alte Aufnahme für dasselbe Wort ersetzen (nur den Eintrag)
        speaker.recordings = [
            rec for rec in speaker.recordings if rec.display_name != word
        ]
        speaker.recordings.append(recording)
        self._save_speakers()
        return recording
