# Temporarer Test: export_sequence + PreviewPlayer (headless)
import sys, os, shutil, traceback
sys.path.insert(0, ".")

import numpy as np
from app import RecordStudioApp
from core.export_sequence import build_export_sequence, DEFAULT_DURATION

ERRORS = []

def check(name, fn):
    try:
        r = fn()
        print(f"OK   {name}")
        return r
    except Exception:
        ERRORS.append((name, traceback.format_exc()))
        print(f"FAIL {name}")
        return None

from PIL import Image
os.makedirs("assets", exist_ok=True)
Image.new("RGB", (60, 60), (200, 30, 30)).save("assets/_test_scene.png")
Image.new("RGBA", (60, 60), (30, 200, 30, 255)).save("assets/_test_char.png")

def make_wav(am, seconds=1):
    audio = (np.sin(np.linspace(0, 300 * 2 * np.pi, 44100 * seconds)) * 10000).astype(np.int16).reshape(-1, 1)
    return am._save_wav(audio, f"seq_{seconds}.wav")

root = RecordStudioApp()
root.withdraw(); root.update()

scene = root.scene_library.create_scene("Test Szene 1", background_path="assets/_test_scene.png")
char = root.character_library.create_character("Test Held", views={"front": "assets/_test_char.png"})
spk = root.speaker_library.create_speaker("Test Sprecher")
root.speaker_library.update_speaker(spk.speaker_id, character_id=char.character_id)

# Projekt anlegen + Sprecher im Projekt referenzieren (gleiche ID)
proj = root.project_manager.create_project("PreviewTest")
root.project_manager.open_project(proj.folder_name)
root.project_manager.speaker_manager.create_speaker(display_name="Test Sprecher", speaker_id=spk.speaker_id)

# Globale Wort-Aufnahme (WAV) fuer den Sprecher -> abspielbar, mit Dauer
wav = make_wav(root.audio_manager, 2)
root.speaker_library.add_word_recording(spk.speaker_id, "Hallo", wav, root.audio_manager)

# Timeline-Eintrag + Projekt speichern
root.timeline_library.create_entry(spk.speaker_id, "Hallo", order=0, scene_id=scene.scene_id)
root.project_manager.save_project()

def make_steps():
    return build_export_sequence(
        root.project_manager.current_project,
        scene_library=root.scene_library,
        speaker_library=root.speaker_library,
        character_library=root.character_library,
        timeline_library=root.timeline_library,
        file_manager=root.file_manager,
        speaker_manager=root.project_manager.speaker_manager,
        audio_manager=root.audio_manager,
    )

# Test 1: Sequenz wird gebaut, Pfade und Dauer korrekt
steps = check("build_export_sequence", make_steps)
assert steps and len(steps) >= 1, f"Keine Schritte: {len(steps)}"
s0 = steps[0]
print("   Schritt0:", s0)
assert s0.scene_name == "Test Szene 1", s0.scene_name
assert s0.text == "Hallo", s0.text
assert s0.image_paths and s0.image_paths[0].endswith("_test_char.png"), s0.image_paths
assert s0.audio_path and os.path.exists(s0.audio_path), s0.audio_path
assert abs(s0.duration - 2.0) < 0.2, f"Dauer {s0.duration}"
print("OK   Dauer aus Audio korrekt (ca. 2s)")

# Test 2: Fehlendes Audio -> Default-Dauer, kein Crash
root.timeline_library.create_entry(spk.speaker_id, "GibtEsNicht", order=5, scene_id=scene.scene_id)
steps2 = make_steps()
s_ohne = next(s for s in steps2 if s.text == "GibtEsNicht")
assert s_ohne.audio_path is None, s_ohne.audio_path
assert s_ohne.duration == DEFAULT_DURATION, s_ohne.duration
print("OK   Schritt ohne Audio: audio=None, Default-Dauer")

# Test 3/4: Leere/fehlende Timeline -> [], kein Crash
for eid in list(root.timeline_library.entries):
    root.timeline_library.delete_entry(eid)
assert build_export_sequence(root.project_manager.current_project, scene_library=root.scene_library, timeline_library=None) == []
assert build_export_sequence(proj) == []
print("OK   Leere/fehlende Timeline -> [] (kein Absturz)")

# Test 5: PreviewPlayer instanziieren + steuern
root.timeline_library.create_entry(spk.speaker_id, "Hallo", order=0, scene_id=scene.scene_id)
steps5 = make_steps()
from ui.preview_player import PreviewPlayer
player = check("PreviewPlayer instanziieren", lambda: PreviewPlayer(root, steps5, audio_manager=root.audio_manager))
if player is not None:
    player.update_idletasks()
    player._toggle_play()
    player.update()
    assert player._playing, "Wiedergabe wurde nicht gestartet"
    player._next_step()
    player._prev_step()
    player.destroy()
    print("OK   Wiedergabe/Weiter/Zurueck im Player")

# Aufraeumen
for eid in list(root.timeline_library.entries):
    root.timeline_library.delete_entry(eid)
root.speaker_library.delete_speaker(spk.speaker_id)
root.character_library.delete_character(char.character_id)
root.scene_library.delete_scene(scene.scene_id)
os.remove("assets/_test_scene.png")
os.remove("assets/_test_char.png")
shutil.rmtree("projects/PreviewTest", ignore_errors=True)
shutil.rmtree("assets/speakers/Test_Sprecher", ignore_errors=True)
root.speaker_library._save_speakers()

print()
if ERRORS:
    for n, tb in ERRORS:
        print("ERROR:", n); print(tb)
    sys.exit(1)
print("ALLE TESTS BESTANDEN")
root.destroy()
