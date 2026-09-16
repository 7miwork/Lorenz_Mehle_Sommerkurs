# AudioManager für Record Studio
# Verwaltet Audioaufnahmen: Aufnahme, Wiedergabe, Speichern, Löschen.
# Verwendet sounddevice für die Aufnahme und wave für das Speichern.

import io
import os
import shutil
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

# soundfile kann OGG/OPUS direkt lesen und dauert nicht lange.
# Es ist OPTIONAL: Ist das Paket nicht installiert, dekodiert der
# AudioManager komprimierte Dateien mit ffmpeg (siehe _load_audio).
# So funktioniert die Wiedergabe auch ohne Zusatzpaket.
try:
    import soundfile as sf
except Exception:
    sf = None


class AudioManager:
    """Verwaltet Audioaufnahmen und Wiedergabe.

    Bietet Funktionen zum Starten/Stoppen/Pausieren von Aufnahmen,
    zum Abspielen von Audiodateien (WAV und OGG) und zum Ermitteln
    der Dauer.

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

    def has_input_device(self) -> bool:
        """Prüft, ob ein Mikrofon/Eingabegerät verfügbar ist.

        Returns:
            True wenn ein Eingabegerät gefunden wurde
        """
        try:
            dev = sd.default.device
            # sd.default.device kann ein Int oder (input, output) Tuple sein
            input_idx = dev[0] if isinstance(dev, (list, tuple)) else dev
            if input_idx is None or input_idx < 0:
                return False
            info = sd.query_devices(input_idx)
            return info.get("max_input_channels", 0) > 0
        except Exception:
            return False

    def start_recording(self) -> bool:
        """Startet eine neue Aufnahme.

        Returns:
            True wenn die Aufnahme gestartet wurde, False wenn
            kein Eingabegerät verfügbar ist oder schon aufgenommen wird
        """
        if self._recording:
            return False

        # Graceful: ohne Mikrofon gar nicht erst starten
        if not self.has_input_device():
            print("Fehler: Kein Mikrofon/Eingabegerät gefunden.")
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

    def _load_audio(self, file_path: str):
        """Laedt eine Audiodatei als (Daten, Samplerate).

        Das ist die EINE Stelle, an der Audiodateien gelesen werden -
        sowohl play() als auch play_blocking() nutzen sie. Dadurch gibt
        es den Lade-Code nur einmal.

        Reihenfolge:
            1. WAV  -> Standardbibliothek "wave" (immer verfuegbar)
            2. OGG/OPUS -> soundfile, falls installiert
            3. OGG/OPUS -> ffmpeg, falls soundfile fehlt

        Args:
            file_path: Pfad zur Audiodatei

        Returns:
            Tupel (data, samplerate). data ist ein numpy-int16-Array
            oder None, wenn die Datei nicht gelesen werden konnte.
        """
        if not file_path or not os.path.exists(file_path):
            print(f"Fehler beim Laden: Datei nicht gefunden ({file_path})")
            return (None, self.SAMPLE_RATE)

        if file_path.lower().endswith(".wav"):
            return self._load_wav(file_path)

        # Komprimierte Formate (OGG/OPUS): erst soundfile probieren
        if sf is not None:
            try:
                data, samplerate = sf.read(file_path, dtype="int16")
                return (data, samplerate)
            except Exception as e:
                print(f"soundfile konnte die Datei nicht lesen: {e}")

        # Ohne soundfile: ffmpeg dekodiert die Datei nach WAV (im RAM)
        raw = self._decode_with_ffmpeg(file_path)
        if raw is None:
            print("Wiedergabe nicht moeglich: bitte 'soundfile' oder "
                  "ffmpeg installieren.")
            return (None, self.SAMPLE_RATE)
        return self._load_wav_bytes(raw)

    def _load_wav(self, file_path: str):
        """Liest eine WAV-Datei mit der Standardbibliothek.

        Args:
            file_path: Pfad zur WAV-Datei

        Returns:
            Tupel (data, samplerate) oder (None, Standardrate) bei Fehler
        """
        try:
            with wave.open(file_path, "rb") as wf:
                raw = wf.readframes(wf.getnframes())
                data = np.frombuffer(raw, dtype=np.int16)
                return (self._to_channels(data, wf.getnchannels()), wf.getframerate())
        except Exception as e:
            print(f"Fehler beim Laden: {e}")
            return (None, self.SAMPLE_RATE)

    def _load_wav_bytes(self, raw: bytes):
        """Liest WAV-Daten aus dem Arbeitsspeicher (z. B. von ffmpeg).

        Args:
            raw: Komplette WAV-Datei als Bytes

        Returns:
            Tupel (data, samplerate) oder (None, Standardrate) bei Fehler
        """
        try:
            with wave.open(io.BytesIO(raw), "rb") as wf:
                frames = wf.readframes(wf.getnframes())
                data = np.frombuffer(frames, dtype=np.int16)
                return (self._to_channels(data, wf.getnchannels()), wf.getframerate())
        except Exception as e:
            print(f"Fehler beim Laden: {e}")
            return (None, self.SAMPLE_RATE)

    @staticmethod
    def _to_channels(data: np.ndarray, channels: int):
        """Bringt PCM-Daten in die Form, die sounddevice erwartet.

        Stereo-Daten liegen hintereinander (L, R, L, R ...). Fuer
        sounddevice werden daraus zwei Spalten gemacht, damit die
        Wiedergabe nicht zu schnell klingt.

        Args:
            data: 1D-Array mit den PCM-Werten
            channels: Anzahl der Kanaele in der Datei

        Returns:
            data unveraendert (Mono) oder als 2D-Array (Stereo)
        """
        if channels > 1 and data.size % channels == 0:
            return data.reshape(-1, channels)
        return data

    def _decode_with_ffmpeg(self, file_path: str) -> Optional[bytes]:
        """Dekodiert eine Audiodatei mit ffmpeg zu WAV-Bytes.

        Wird nur gebraucht, wenn soundfile nicht installiert ist.
        Die fertigen WAV-Daten kommen direkt in den Arbeitsspeicher
        (Ausgabe "-"), es wird also keine temporaere Datei angelegt.

        Args:
            file_path: Pfad zur Audiodatei (z. B. OGG)

        Returns:
            WAV-Datei als Bytes oder None bei Fehler
        """
        ffmpeg = self._get_ffmpeg_exe()
        if ffmpeg is None:
            return None

        args = [
            ffmpeg, "-v", "quiet", "-i", file_path,
            "-f", "wav", "-acodec", "pcm_s16le", "-",
        ]
        try:
            result = subprocess.run(args, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        except Exception as e:
            print(f"Fehler bei ffmpeg: {e}")
            return None

        if result.returncode != 0 or not result.stdout:
            print("Fehler: ffmpeg konnte die Datei nicht dekodieren.")
            return None
        return result.stdout

    def play(self, file_path: str) -> bool:
        """Spielt eine Audiodatei ab (WAV oder OGG).

        Args:
            file_path: Pfad zur Audiodatei

        Returns:
            True wenn die Wiedergabe gestartet wurde
        """
        if not os.path.exists(file_path):
            return False

        try:
            # Eine evtl. noch laufende Wiedergabe zuerst stoppen,
            # damit sich zwei Audios nicht überlagern.
            self.stop()
            threading.Thread(target=self._play_loop, args=(file_path,), daemon=True).start()
            return True
        except Exception as e:
            print(f"Fehler bei der Wiedergabe: {e}")
            return False

    def stop(self) -> None:
        """Hält eine laufende Wiedergabe an.

        Diese kleine Funktion braucht der Vorschau-Player: Beim Blättern
        (Vor/Zurück) oder Schließen soll das alte Audio sofort aufhören.
        Ein Fehler darf hier niemals die App abstürzen lassen.
        """
        try:
            # sounddevice beendet damit die aktuelle Ausgabe
            sd.stop()
        except Exception as e:
            print(f"Fehler beim Stoppen: {e}")

    def _play_loop(self, file_path: str):
        """Wiedergabe-Schleife im Hintergrund-Thread."""
        data, samplerate = self._load_audio(file_path)
        if data is None:
            return
        try:
            sd.play(data, samplerate)
            sd.wait()
        except Exception as e:
            print(f"Fehler bei der Wiedergabe: {e}")

    # ---------- HILFSFUNKTIONEN ----------

    def play_blocking(self, file_path: str) -> bool:
        """Spielt eine Audiodatei ab und wartet, bis sie fertig ist.

        Im Gegensatz zu play() blockiert diese Methode den aufrufenden
        Thread. Sie ist fuer Hintergrund-Threads gedacht (z. B. die
        Vorschau-Wiedergabe), damit die naechste Szene erst nach dem
        Ton startet - wie bei einer echten Diashow mit Vertonung.

        Args:
            file_path: Pfad zur Audiodatei (WAV oder OGG)

        Returns:
            True wenn die Wiedergabe geklappt hat
        """
        # Datei laden (WAV/OGG) - dieselbe Stelle wie bei play(),
        # nur dass hier direkt gewartet wird statt einen Thread zu starten.
        data, samplerate = self._load_audio(file_path)
        if data is None:
            return False
        # Abspielen und auf das Ende warten (blockierend).
        try:
            sd.play(data, samplerate)
            sd.wait()
            return True
        except Exception as e:
            print(f"Fehler bei der Wiedergabe: {e}")
            return False

    def get_duration(self, file_path: str) -> float:
        """Ermittelt die Dauer einer Audiodatei in Sekunden.

        WAV-Dateien werden direkt aus dem Datei-Kopf gelesen (schnell).
        Bei OGG/OPUS wird die Datei mit _load_audio geladen und die
        Laenge aus der Anzahl der Werte berechnet - so stimmt die
        Anzeigedauer auch fuer komprimierte Aufnahmen.

        Args:
            file_path: Pfad zur Audiodatei

        Returns:
            Dauer in Sekunden (0.0 bei Fehler)
        """
        if not file_path or not os.path.exists(file_path):
            return 0.0

        if file_path.lower().endswith(".wav"):
            try:
                with wave.open(file_path, "rb") as wf:
                    frames = wf.getnframes()
                    rate = wf.getframerate()
                    return frames / rate if rate > 0 else 0.0
            except Exception:
                return 0.0

        # Komprimierte Dateien: Laenge aus den geladenen Audiodaten
        data, samplerate = self._load_audio(file_path)
        if data is None or samplerate <= 0:
            return 0.0
        frames = data.shape[0]
        return frames / samplerate

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
        """Gibt den Pfad zur ffmpeg-Executable zurück, falls verfügbar.

        Zuerst wird imageio-ffmpeg gefragt (bringt ffmpeg mit). Ist das
        Paket nicht installiert, wird ffmpeg im System gesucht - so
        funktioniert die Konvertierung/Dekodierung auch dann, wenn
        ffmpeg bereits auf dem Rechner installiert ist.
        """
        if iioff is not None:
            try:
                return iioff.get_ffmpeg_exe()
            except Exception:
                pass
        # Fallback: ffmpeg aus dem System (PATH)
        return shutil.which("ffmpeg")

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