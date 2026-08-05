# AudioManager für Record Studio
# Verwaltet Audioaufnahmen: Aufnahme, Wiedergabe, Speichern, Löschen.
# Verwendet sounddevice für die Aufnahme und wave für das Speichern.

import os
import threading
import time
import wave
from typing import Optional

import sounddevice as sd
import numpy as np
import subprocess
from typing import Literal

try:
    import imageio_ffmpeg as iioff
except Exception:
    iioff = None


class AudioManager:
    """Verwaltet Audioaufnahmen und Wiedergabe.

    Bietet Funktionen zum Starten/Stoppen/Pausieren von Aufnahmen,
    zum Abspielen von WAV-Dateien und zum Ermitteln der Dauer.

    Die Aufnahme läuft in einem separaten Thread, damit die GUI
    während der Aufnahme nicht blockiert wird.
    """

    # Standard-Aufnahmeeinstellungen
    SAMPLE_RATE = 44100
    CHANNELS = 1

    def __init__(self):
        """Initialisiert den AudioManager."""
        self._recording = False
        self._paused = False
        self._frames = []
        self._stream = None
        self._start_time = 0.0
        self._paused_time = 0.0
        self._elapsed_before_pause = 0.0
        self._thread = None

    # ---------- AUFNAHME ----------

    def start_recording(self) -> bool:
        """Startet eine neue Aufnahme.

        Returns:
            True wenn die Aufnahme gestartet wurde
        """
        if self._recording:
            return False

        self._recording = True
        self._paused = False
        self._frames = []
        self._start_time = time.time()
        self._elapsed_before_pause = 0.0

        # Aufnahme in einem separaten Thread starten
        self._thread = threading.Thread(target=self._record_loop, daemon=True)
        self._thread.start()
        return True

    def _record_loop(self):
        """Aufnahme-Schleife, die im Hintergrund-Thread läuft."""
        try:
            self._stream = sd.InputStream(
                samplerate=self.SAMPLE_RATE,
                channels=self.CHANNELS,
                dtype="int16",
            )
            self._stream.start()

            while self._recording:
                if not self._paused:
                    data, _ = self._stream.read(1024)
                    self._frames.append(data.copy())
                else:
                    time.sleep(0.05)

            self._stream.stop()
            self._stream.close()
            self._stream = None
        except Exception as e:
            print(f"Fehler bei der Aufnahme: {e}")
            self._recording = False

    def stop_recording(self) -> Optional[str]:
        """Stoppt die Aufnahme und gibt den Pfad zur WAV-Datei zurück.

        Returns:
            Pfad zur temporären WAV-Datei oder None bei Fehler
        """
        if not self._recording:
            return None

        self._recording = False
        if self._thread:
            self._thread.join(timeout=2)

        if not self._frames:
            return None

        # Frames zu einem Array zusammenfügen
        audio = np.concatenate(self._frames, axis=0)

        # Temporäre Datei speichern
        temp_path = self._save_wav(audio, "temp_recording.wav")
        return temp_path

    def pause_recording(self) -> bool:
        """Pausiert die laufende Aufnahme.

        Returns:
            True wenn pausiert wurde
        """
        if not self._recording or self._paused:
            return False

        self._paused = True
        self._elapsed_before_pause = self.get_elapsed_time()
        return True

    def resume_recording(self) -> bool:
        """Setzt eine pausierte Aufnahme fort.

        Returns:
            True wenn fortgesetzt wurde
        """
        if not self._recording or not self._paused:
            return False

        self._paused = False
        self._start_time = time.time()
        return True

    def is_recording(self) -> bool:
        """Gibt zurück, ob gerade aufgenommen wird."""
        return self._recording

    def is_paused(self) -> bool:
        """Gibt zurück, ob die Aufnahme pausiert ist."""
        return self._paused

    def get_elapsed_time(self) -> float:
        """Gibt die vergangene Aufnahmezeit in Sekunden zurück."""
        if not self._recording:
            return 0.0

        if self._paused:
            return self._elapsed_before_pause

        return self._elapsed_before_pause + (time.time() - self._start_time)

    # ---------- SPEICHERN ----------

    def save_recording(
        self, audio_path: str, target_path: str, display_name: str = ""
    ) -> bool:
        """Kopiert eine Aufnahme an den Zielort.

        Args:
            audio_path: Pfad zur temporären Aufnahme
            target_path: Zielpfad (relativ zum Projektordner)
            display_name: Anzeigename (nur für Logging)

        Returns:
            True wenn erfolgreich
        """
        try:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            if os.path.abspath(audio_path) != os.path.abspath(target_path):
                import shutil
                shutil.copy2(audio_path, target_path)
            return True
        except Exception as e:
            print(f"Fehler beim Speichern: {e}")
            return False

    def _save_wav(self, audio: np.ndarray, filename: str) -> str:
        """Speichert ein Audio-Array als WAV-Datei.

        Args:
            audio: Numpy-Array mit den Audiodaten
            filename: Name der Zieldatei

        Returns:
            Pfad zur gespeicherten Datei
        """
        temp_dir = "assets/audio"
        os.makedirs(temp_dir, exist_ok=True)
        path = os.path.join(temp_dir, filename)

        with wave.open(path, "wb") as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(2)  # 16 Bit = 2 Bytes
            wf.setframerate(self.SAMPLE_RATE)
            wf.writeframes(audio.tobytes())

        return path

    # ---------- WIEDERGABE ----------

    def play(self, file_path: str) -> bool:
        """Spielt eine WAV-Datei ab.

        Args:
            file_path: Pfad zur WAV-Datei

        Returns:
            True wenn die Wiedergabe gestartet wurde
        """
        if not os.path.exists(file_path):
            return False

        try:
            threading.Thread(target=self._play_loop, args=(file_path,), daemon=True).start()
            return True
        except Exception as e:
            print(f"Fehler bei der Wiedergabe: {e}")
            return False

    def _play_loop(self, file_path: str):
        """Wiedergabe-Schleife im Hintergrund-Thread."""
        try:
            with wave.open(file_path, "rb") as wf:
                data = wf.readframes(wf.getnframes())
                audio = np.frombuffer(data, dtype=np.int16)
                sd.play(audio, wf.getframerate())
                sd.wait()
        except Exception as e:
            print(f"Fehler bei der Wiedergabe: {e}")

    # ---------- HILFSFUNKTIONEN ----------

    def get_duration(self, file_path: str) -> float:
        """Ermittelt die Dauer einer WAV-Datei in Sekunden.

        Args:
            file_path: Pfad zur WAV-Datei

        Returns:
            Dauer in Sekunden (0.0 bei Fehler)
        """
        try:
            with wave.open(file_path, "rb") as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                return frames / rate if rate > 0 else 0.0
        except Exception:
            return 0.0

    def delete_file(self, file_path: str) -> bool:
        """Löscht eine Datei.

        Args:
            file_path: Pfad zur Datei

        Returns:
            True wenn gelöscht
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            print(f"Fehler beim Löschen: {e}")
        return False

    def format_duration(self, seconds: float) -> str:
        """Formatiert Sekunden als HH:MM:SS.

        Args:
            seconds: Dauer in Sekunden

        Returns:
            Formatierter Zeitstring (z.B. "00:00:15")
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    # ---------- FORMAT KONVERTIERUNG (ffmpeg) ----------
    def _get_ffmpeg_exe(self) -> Optional[str]:
        """Gibt den Pfad zur ffmpeg-Executable zurück, falls verfügbar."""
        if iioff is not None:
            try:
                return iioff.get_ffmpeg_exe()
            except Exception:
                return None
        return None

    def convert_to_format(self, input_wav: str, output_path: str, fmt: Literal["ogg", "opus"]) -> bool:
        """Konvertiert eine WAV-Datei in OGG Vorbis oder OPUS mithilfe von ffmpeg.

        Args:
            input_wav: Pfad zur Quell-WAV
            output_path: Zieldatei (vollständiger Pfad)
            fmt: "ogg" oder "opus"

        Returns:
            True wenn erfolgreich
        """
        ffmpeg = self._get_ffmpeg_exe()
        if ffmpeg is None:
            print("ffmpeg executable not found (imageio-ffmpeg missing)")
            return False

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if fmt == "ogg":
            args = [ffmpeg, "-y", "-i", input_wav, "-c:a", "libvorbis", "-q:a", "4", output_path]
        else:  # opus
            args = [ffmpeg, "-y", "-i", input_wav, "-c:a", "libopus", "-b:a", "64k", output_path]

        try:
            subprocess.check_call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            print(f"Fehler bei der Konvertierung: {e}")
            return False

    def convert_and_save(self, input_wav: str, target_abs_path: str, fmt: Literal["ogg", "opus"]) -> Optional[str]:
        """Konvertiert `input_wav` in das gewünschte Format und speichert es als `target_abs_path`.

        Wenn `fmt` ist 'ogg' oder 'opus', die Datei wird entsprechend konvertiert.
        """
        # Bestimme Zieldateiendung
        base, _ = os.path.splitext(target_abs_path)
        ext = ".ogg" if fmt == "ogg" else ".opus"
        out_path = base + ext

        success = self.convert_to_format(input_wav, out_path, fmt)
        return out_path if success else None