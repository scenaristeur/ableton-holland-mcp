"""Generic MIDI remake preprocessor: split a multi-track .mid into scenes/groups.

USAGE:
  python prep_midi.py <midfile> --out <out.json> [--track-map JSON] [--scenes JSON]
                            [--detect-scenes N] [--drum-map JSON|auto]

Reads a multi-track MIDI, groups source tracks into Ableton instrument tracks,
splits the song into scenes (1 scene = 1 section), converts note timing to
scene-relative beats, de-duplicates unison doublons, and remaps drum pitches
(GM -> kit pads). Emits JSON ready for add_notes_to_clip / inject_scene.py.

Output JSON: { scene_index: { length, _bars, "0": [notes], ... } }
where each note = {pitch, velocity, start_time (beats, scene-rel), duration}.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from typing import Any

import mido

# Default GM -> Selector Kit Warm drum remap (override via --drum-map)
DRUM_PITCH_MAP: dict[int, int] = {
    35: 36,  # kick
    36: 36,  # kick
    38: 38,  # snare
    39: 39,  # clap
    40: 40,  # snare alt
    42: 42,  # closed hat
    44: 44,  # shaker
    46: 46,  # open hat
    49: 49,  # crash
    51: 51,  # ride
    53: 43,  # tom hi
    55: 45,  # tom mid
    57: 47,  # tom low
    82: 44,  # shaker
    # extraneous percussion -> Selector Kit Warm pads
    81: 51,  # bell/clavé -> Ride
    73: 48,  # vibra -> Perc
    58: 47,  # perc/cloche -> Tom 2
    83: 44,  # shaker/jingle -> Shaker
    71: 51,  # triangle -> Ride
    77: 51,  # clavet -> Ride
    56: 47,  # perc -> Tom 2
}

PPQ = 4  # beats per bar (4/4)


def analyze(mid: mido.MidiFile) -> list[dict[str, Any]]:
    """Return per-track summary: name, notes, channels, programs, isdrums."""
    out = []
    for i, tr in enumerate(mid.tracks):
        name = ""
        prog = {}
        chans = set()
        n = 0
        drums = False
        for m in tr:
            if m.type == "track_name":
                name = m.name
            elif m.type == "program_change":
                prog[m.channel] = m.program
            elif m.type == "note_on" and m.velocity > 0:
                n += 1
                if m.channel == 9:
                    drums = True
            if hasattr(m, "channel"):
                chans.add(m.channel)
        out.append(
            {
                "index": i,
                "name": name,
                "notes": n,
                "chans": sorted(chans),
                "prog": prog,
                "drums": drums,
            }
        )
    return out


def detect_scenes(
    mid: mido.MidiFile, max_scenes: int = 12, min_gap_bars: int = 3
) -> dict[int, tuple[int, int]]:
    """Heuristically split the song into sections.

    Combines (a) presence changes of major families (drums/melody) and (b) a
    sharp drop in DENSITY (note count / 4-bar block) of the drums — which catches
    instrumental breaks within a continuous groove. Falls back to equal slices.
    """
    tpb = mid.ticks_per_beat
    drum_counts: dict[int, int] = {}
    mel_bars: set[int] = set()
    for tr in mid.tracks:
        clock = 0
        is_drums = any(m.channel == 9 for m in tr if hasattr(m, "channel"))
        for m in tr:
            clock += m.time
            if m.type == "note_on" and m.velocity > 0:
                b = int(clock / tpb // 4)
                if is_drums:
                    drum_counts[b] = drum_counts.get(b, 0) + 1
                else:
                    mel_bars.add(b)

    max_bar = max(max(list(drum_counts.keys()) or [0]), max(list(mel_bars) or [0])) + 2

    # (a) presence changes of melody
    presence: list[int] = []
    prev_mel = 0 in mel_bars
    for b in range(1, max_bar):
        cur_mel = b in mel_bars
        if cur_mel != prev_mel:
            presence.append(b)
        prev_mel = cur_mel

    # (b) drum density break: 4-bar block density drops >55% vs preceding, and exits
    def block_density(b0: int) -> float:
        return sum(drum_counts.get(b, 0) for b in range(b0, min(b0 + 4, max_bar)))

    density: list[int] = []
    prev_d = block_density(0) or 1
    in_break = False
    for b0 in range(4, max_bar, 4):
        d = block_density(b0)
        if prev_d and d < 0.45 * prev_d and not in_break:
            density.append(b0)
            in_break = True
        elif in_break and prev_d and d > 1.5 * prev_d:
            density.append(b0)
            in_break = False
        prev_d = d if d else prev_d

    # merge + enforce min gap between consecutive boundaries
    raw = sorted(set([0] + presence + density + [max_bar]))
    boundaries = [raw[0]]
    for b in raw[1:]:
        if b - boundaries[-1] >= min_gap_bars:
            boundaries.append(b)

    # clamp to max_scenes (keep first if possible)
    if len(boundaries) - 1 > max_scenes:
        step = max(1, len(boundaries) // max_scenes)
        boundaries = (
            [boundaries[0]]
            + [boundaries[i] for i in range(step, len(boundaries) - 1, step)]
            + [max_bar]
        )
        boundaries = sorted(set(boundaries))

    scenes: dict[int, tuple[int, int]] = {}
    for i in range(len(boundaries) - 1):
        if boundaries[i + 1] > boundaries[i]:
            scenes[i] = (boundaries[i] + 1, boundaries[i + 1])
    return scenes


def extract_notes(mid: mido.MidiFile, track_idx: int) -> list[dict]:
    """Return note dicts {start_time, duration, velocity, pitch} in absolute beats."""
    tr = mid.tracks[track_idx]
    clock = 0
    active: dict[int, tuple[float, int]] = {}
    notes: list[dict] = []
    for m in tr:
        clock += m.time
        if m.type == "note_on" and m.velocity > 0:
            active[m.note] = (clock / mid.ticks_per_beat, m.velocity)
        elif m.type == "note_off" or (m.type == "note_on" and m.velocity == 0):
            info = active.pop(m.note, None)
            if info is not None:
                start, vel = info
                dur = (clock / mid.ticks_per_beat) - start
                notes.append(
                    {
                        "start_time": start,
                        "duration": max(dur, 0.001),
                        "velocity": vel,
                        "pitch": m.note,
                    }
                )
    return notes


def build_json(
    source: str,
    track_map: dict[str, list[int]],
    scenes: dict[int, tuple[int, int]],
    drum_map: dict[int, int] | None,
) -> dict[str, Any]:
    mid = mido.MidiFile(source)
    tracks_all = {t: extract_notes(mid, t) for t in set().union(*track_map.values())}
    result: dict[str, Any] = {}

    for scene_idx, (start_bar, end_bar) in scenes.items():
        s_beat = (start_bar - 1) * PPQ
        e_beat = end_bar * PPQ
        length = e_beat - s_beat
        st: dict[str, Any] = {"length": length, "_bars": (start_bar, end_bar)}
        for atrack, src_tracks in track_map.items():
            all_notes: list[dict] = []
            for src in src_tracks:
                all_notes.extend(tracks_all[src])
            all_notes.sort(key=lambda n: n["start_time"])
            clip: list[dict] = []
            seen: set[tuple] = set()
            for n in all_notes:
                if n["start_time"] < s_beat:
                    continue
                if n["start_time"] >= e_beat:
                    break
                rel = n["start_time"] - s_beat
                dur = min(n["duration"], length - rel)
                pitch = n["pitch"]
                if atrack == "0" and drum_map:
                    pitch = drum_map.get(pitch, pitch)
                note = {
                    "pitch": pitch,
                    "velocity": n["velocity"],
                    "start_time": round(rel, 3),
                    "duration": round(dur, 3),
                }
                key = (note["start_time"], note["pitch"], note["duration"])
                if key not in seen:
                    clip.append(note)
                    seen.add(key)
            st[atrack] = clip
        result[str(scene_idx)] = st

    return result


def factorization_analysis(result: dict[str, Any], atrack: str, ppq: int = PPQ) -> str:
    """Return a per-scene table of bar-pattern repetitions for one Ableton track.

    For each scene in `result`, group notes by 4-beat bar, count unique bar patterns,
    and report the most-repeated pattern count (`top xN`). `top xN>=3` signals a
    repetitive groove that should be factored into short looped clips + fills.
    """
    from collections import Counter, defaultdict

    lines: list[str] = []
    for si in sorted(result, key=int):
        st = result[si]
        arr = st.get(atrack, [])
        if not arr:
            continue
        length = int(st["length"])
        n_bars = max(1, length // ppq)
        perbar: dict[int, list[tuple]] = defaultdict(list)
        for n in arr:
            b = int(n["start_time"] // ppq)
            perbar[b].append(
                (round(n["start_time"] % ppq, 2), n["pitch"], n["velocity"])
            )
        pats = Counter(
            tuple(sorted(tuple(v) for v in perbar.get(b, []))) for b in range(n_bars)
        )
        uniq = len(pats)
        topcnt = pats.most_common(1)[0][1] if pats else 0
        suggest = (
            "FACTORISER (groove court + fills)"
            if topcnt >= 3
            else "variations (clips longs ok)"
        )
        lines.append(
            f"| sc{si} | {len(arr)} notes | {uniq} patterns | top x{topcnt} | {suggest} |"
        )
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description="Prep a MIDI for Ableton remake")
    ap.add_argument("source", help="path to .mid")
    ap.add_argument("--out", required=True, help="output json path")
    ap.add_argument(
        "--track-map", help="JSON dict {ableton_idx:[src_tracks]}", default=None
    )
    ap.add_argument(
        "--scenes", help="JSON dict {idx:[start_bar,end_bar]}", default=None
    )
    ap.add_argument(
        "--detect-scenes",
        type=int,
        default=0,
        help="auto-detect scenes with max N (ignores --scenes if 0)",
    )
    ap.add_argument(
        "--drum-map",
        default="auto",
        help="drum pitch map: 'auto' (default), 'none', or JSON",
    )
    args = ap.parse_args()

    mid = mido.MidiFile(args.source)
    print(f"== {args.source}")
    print(
        f"type={mid.type} tracks={len(mid.tracks)} tpb={mid.ticks_per_beat} len={round(mid.length, 1)}s"
    )
    for t in analyze(mid):
        print(
            f"  [{t['index']}] {t['name']!r} notes={t['notes']} chans={t['chans']} prog={t['prog']} drums={t['drums']}"
        )

    # Track map
    track_map = json.loads(args.track_map) if args.track_map else None
    if track_map is None:
        print("\n[usage] Provide --track-map JSON (see tracks above). Example:")
        print('  --track-map \'{"0":[7],"2":[0,1,2],"4":[3],"6":[4,5,6]}\'')
        return

    # Scenes
    scenes = None
    if args.scenes:
        scenes = {int(k): tuple(v) for k, v in json.loads(args.scenes).items()}
    elif args.detect_scenes:
        scenes = detect_scenes(mid, max_scenes=args.detect_scenes)
        print(
            f"\n[auto] detected {len(scenes)} scenes: { {i: v for i, v in scenes.items()} }"
        )

    # Drum map
    drum_map = None
    if args.drum_map == "none":
        drum_map = None
    elif args.drum_map == "auto":
        if any(t["drums"] for t in analyze(mid)):
            drum_map = DRUM_PITCH_MAP
    else:
        drum_map = {int(k): int(v) for k, v in json.loads(args.drum_map).items()}

    if scenes is None:
        print("\n[usage] Supply --scenes JSON or --detect-scenes N")
        return

    result = build_json(args.source, track_map, scenes, drum_map)

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False)

    for scene_idx, st in result.items():
        bars = st["_bars"]
        cnt = {k: len(v) for k, v in st.items() if k not in ("length", "_bars")}
        print(
            f"\nScene {scene_idx} (bars {bars[0]}-{bars[1]}, {st['length']} beats): "
            + ", ".join(f"tr{k}={v}n" for k, v in cnt.items())
        )
    print(f"\nWrote {args.out}")

    # Factorization analysis across every mapped track
    srcnames = {t["index"]: t["name"] or f"track{t['index']}" for t in analyze(mid)}
    print(
        "\n## Factorisation par piste (top xN>=3 → FACTORISER en groove court + fills)"
    )
    for at in sorted(track_map, key=int):
        label = srcnames.get(track_map[at][0], f"piste {at}")
        fac = factorization_analysis(result, at)
        print(f"\nPiste {at} — {label}\n{fac if fac else '  (vide)'}")


if __name__ == "__main__":
    main()
