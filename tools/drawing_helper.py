# OS-Erkennung und externes Zeichenprogramm für Record Studio
# Erkennt das Betriebssystem und öffnet das passende Zeichenprogramm:
#   - Windows: Microsoft Paint (mspaint.exe)
#   - macOS:   Freeform (oder Preview als Fallback)
#   - Linux:   GIMP oder xdg-open mit Standard-Bildeditor

import os
import sys
import subprocess
import platform
from typing import Optional


def detect_os() -> str:
    """Erkennt das aktuelle Betriebssystem.

    Returns:
        "windows", "macos" oder "linux"
    """
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    else:
        return "linux"


def get_drawing_app_name() -> str:
    """Gibt den Namen des Standard-Zeichenprogramms für das aktuelle OS zurück.

    Returns:
        Name des Zeichenprogramms (z.B. "Paint", "Freeform")
    """
    os_name = detect_os()
    if os_name == "windows":
        return "Paint"
    elif os_name == "macos":
        return "Freeform"
    else:
        return "Standard-Bildeditor"


def open_in_drawing_app(file_path: str) -> bool:
    """Öffnet eine Datei im Standard-Zeichenprogramm des Betriebssystems.

    Auf Windows wird Microsoft Paint (mspaint.exe) geöffnet.
    Auf macOS wird Freeform (oder Preview als Fallback) geöffnet.
    Auf Linux wird versucht, GIMP oder den Standard-Bildeditor zu öffnen.

    Args:
        file_path: Pfad zur Datei, die im Zeichenprogramm geöffnet werden soll

    Returns:
        True wenn das Programm erfolgreich geöffnet wurde, False bei Fehler
    """
    os_name = detect_os()

    try:
        if os_name == "windows":
            # Windows: Microsoft Paint öffnen
            # mspaint.exe ist auf allen Windows-Versionen verfügbar
            subprocess.Popen(["mspaint.exe", file_path])
            return True

        elif os_name == "macos":
            # macOS: Zuerst Freeform versuchen, dann Preview als Fallback
            # Freeform ist ab macOS 13.1 (Ventura) verfügbar
            try:
                # Versuche Freeform
                subprocess.Popen(["open", "-a", "Freeform", file_path])
                return True
            except FileNotFoundError:
                # Fallback: Preview (kann auch zeichnen/annotieren)
                subprocess.Popen(["open", "-a", "Preview", file_path])
                return True

        else:
            # Linux: GIMP versuchen, sonst xdg-open
            try:
                subprocess.Popen(["gimp", file_path])
                return True
            except FileNotFoundError:
                # Fallback: Standard-Anwendung für die Datei
                subprocess.Popen(["xdg-open", file_path])
                return True

    except Exception as e:
        print(f"Fehler beim Öffnen des Zeichenprogramms: {e}")
        return False


def create_blank_image(file_path: str, width: int = 800, height: int = 500) -> bool:
    """Erstellt eine leere weiße PNG-Datei für das Zeichenprogramm.

    Args:
        file_path: Pfad, unter dem die Datei erstellt werden soll
        width: Breite des Bildes in Pixeln (Standard: 800)
        height: Höhe des Bildes in Pixeln (Standard: 500)

    Returns:
        True wenn die Datei erfolgreich erstellt wurde, False bei Fehler
    """
    try:
        from PIL import Image
        # Weißes Bild erstellen
        img = Image.new("RGB", (width, height), "white")
        # Verzeichnis erstellen, falls nicht vorhanden
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        img.save(file_path, "png")
        return True
    except Exception as e:
        print(f"Fehler beim Erstellen der leeren Datei: {e}")
        return False