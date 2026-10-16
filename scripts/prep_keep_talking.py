"""Extract per-scene, per-Ableton-track MIDI notes from the Keep Talking source MIDI.

Maps source MIDI tracks to Ableton instrument tracks via the validated grouping,
then splits each group's notes into the 8 song scenes (bar ranges), converting
note start/duration to beats (scene-relative) using the source ticks_per_beat.

Outputs JSON: { scene_index: { ableton_track_index: [ {pitch, velocity, start_beats, duration_beats} ] } }
"""

from __future__ import annotations

import json
from typing import Any

import mido

SOURCE = r"sources/Reprises/Keep Talking/Pink Floyd — Keep Talking [MIDIfind.com].mid"

# Ableton track index -> list of source MIDI track indices (grouping validated)
TRACK_MAP: dict[int, list[int]] = {
    0: [13, 9, 11, 12],  # 1-Batterie+Percs
    # 1: []  -> 2-Libre (empty)
    2: [3, 4],  # 3-Guit Rythm
    3: [5, 6, 2],  # 4-Guit Lead
    4: [10],  # 5-Basse
    5: [7, 8],  # 6-Nappes
    6: [0, 1],  # 7-Claviers
    # 7: []  -> 8-Voix (audio)
}

# Scenes as (start_bar, end_bar) inclusive, 1-based bars.
SCENES: dict[int, tuple[int, int]] = {
    0: (1, 12),  # Intro
    1: (13, 28),  # Section A1 (doux, sans basse)
    2: (29, 40),  # Section A2 (basse entre)
    3: (41, 68),  # Refrain C1
    4: (69, 84),  # C2
    5: (85, 104),  # Keys
    6: (105, 112),  # Drop
    7: (113, 136),  # G
    8: (137, 151),  # Solo
}

PPQ = 4  # beats per bar (4/4)

# Pitch remap for the drums+percs Ableton track (track 0), source MIDI pitch -> Selector Kit Warm pad.
# Source GM drum notes -> kit pads available (36 kick,38 snare,39 clap,42 hh,44 shaker,49 crash,51 ride,43/45/47 toms).
DRUM_PITCH_MAP: dict[int, int] = {
    35: 36,  # kick
    36: 36,  # kick (kit)
    38: 38,  # snare
    39: 39,  # clap
    40: 40,  # snare alt
    42: 42,  # closed hat
    44: 44,  # shaker
    46: 46,  # open hat
    49: 49,  # crash
    51: 51,  # ride
    53: 43,  # tom hi -> tom
    55: 45,  # tom mid -> tom
    57: 47,  # tom low -> tom
    82: 44,  # shaker (source) -> kit shaker pad 44
}


def extract_notes_for_tracks(
    mid: mido.MidiFile, track_indices: list[int]
) -> dict[int, list[dict]]:
    """Return {source_track_index: [note dicts]} with absolute beat timing."""
    out: dict[int, list[dict]] = {}
    for idx in track_indices:
        tr = mid.tracks[idx]
        clock = 0
        active: dict[int, tuple[float, int]] = {}  # note -> (beat start, velocity)
        notes: list[dict] = []
        for msg in tr:
            clock += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                active[msg.note] = (clock / mid.ticks_per_beat, msg.velocity)
            elif msg.type == "note_off" or (
                msg.type == "note_on" and msg.velocity == 0
            ):
                info = active.pop(msg.note, None)
                if info is not None:
                    start, vel = info
                    dur = (clock / mid.ticks_per_beat) - start
                    notes.append(
                        {
                            "pitch": msg.note,
                            "velocity": vel,
                            "start_time": start,
                            "duration": max(dur, 0.001),
                        }
                    )
        out[idx] = notes
    return out


def main() -> None:
    mid = mido.MidiFile(SOURCE)
    scenes_all = extract_notes_for_tracks(
        mid, [i for v in TRACK_MAP.values() for i in v]
    )

    # Per-scene, per-track extraction.
    result: dict[str, Any] = {}
    for scene_idx, (start_bar, end_bar) in SCENES.items():
        s_beat = (start_bar - 1) * PPQ
        e_beat = end_bar * PPQ
        length = e_beat - s_beat
        scene_tracks: dict[str, Any] = {
            "length": length,
            "_bars": (start_bar, end_bar),
        }
        for atrack, src_tracks in TRACK_MAP.items():
            all_notes: list[dict] = []
            for src in src_tracks:
                all_notes.extend(scenes_all[src])
            all_notes.sort(key=lambda n: n["start_time"])
            clip: list[dict] = []
            seen_notes: set[tuple] = set()
            for n in all_notes:
                if n["start_time"] < s_beat:
                    continue
                if n["start_time"] >= e_beat:
                    break  # sorted: safe bound
                start_rel = n["start_time"] - s_beat
                dur = min(n["duration"], length - start_rel)
                pitch = n["pitch"]
                if atrack == 0:
                    pitch = DRUM_PITCH_MAP.get(pitch, pitch)
                note = {
                    "pitch": pitch,
                    "velocity": n["velocity"],
                    "start_time": round(start_rel, 3),
                    "duration": round(dur, 3),
                }
                key = (note["start_time"], note["pitch"], round(note["duration"], 3))
                if key not in seen_notes:
                    clip.append(note)
                    seen_notes.add(key)
            scene_tracks[str(atrack)] = clip
        result[str(scene_idx)] = scene_tracks

    out = json.dumps(result)
    with open(
        "sources/Reprises/Keep Talking/_scenes_notes.json", "w", encoding="utf-8"
    ) as fh:
        fh.write(out)
    # Summary
    for scene_idx, scene_tracks in result.items():
        bars = scene_tracks["_bars"]
        cnt = {
            str(k): len(v)
            for k, v in scene_tracks.items()
            if k not in ("length", "_bars")
        }
        print(
            f"Scene {scene_idx} (bars {bars[0]}-{bars[1]}, "
            f"{scene_tracks['length']} beats): "
            + ", ".join(f"tr{k}={v}n" for k, v in cnt.items())
        )


if __name__ == "__main__":
    main()
