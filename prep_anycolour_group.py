"""Prepare Money, Time, Breathe for remake: generate scene JSON + plan stubs.

For each song: define scene ranges (bars), Ableton track grouping (track_map),
then run prep_midi.build_json and write:
  - _scenes_notes.json
  - REMAKES_PLAN.md  (structure, mapping, notes)
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import mido

import prep_midi as P

BASE = Path(r"sources/Reprises/Pink Floyd")

# scene ranges (inclusive bars) per song — TEMPORARY, to validate at listen
PLANS: dict[str, dict] = {
    "Money": {
        "file": "Money/Pink Floyd — Money [MIDIfind.com].mid",
        "scenes": {
            0: (1, 6),
            1: (7, 14),
            2: (15, 24),
            3: (25, 40),
            4: (41, 56),
            5: (57, 75),
            6: (76, 96),
            7: (97, 124),
        },
        "track_map": {
            "0": [
                7,
                8,
                9,
                10,
                11,
                12,
                13,
            ],  # drums + percs (vibra/guiro/tri/shaker/jingle/2xdk)
            "2": [1, 2],  # rythm + rythm/lead guitar
            "3": [3],  # lead guitar
            "4": [4],  # bass
            "5": [5, 6],  # EP + sax
            "6": [0],  # vocals (guide)
        },
        "notes": "Morceau continu (4/4 ici). Sections a valider a l'ecoute. Percussions isolees = atout."
        " regrouper. Voix comme piste guide seule (piste 6). Fusion pour tailler 8 pistes.",
    },
    "Time": {
        "file": "Time/Pink Floyd — Time [MIDIfind.com].mid",
        "scenes": {
            0: (1, 4),
            1: (5, 15),
            2: (16, 43),
            3: (44, 75),
            4: (76, 105),
            5: (106, 156),
        },
        "track_map": {
            "0": [7, 8, 9],  # drums (2x) + woodblock
            "2": [2],  # rythm guitar
            "3": [3],  # lead guitar
            "4": [6],  # bass
            "5": [4, 5],  # EP + keyboard
            "6": [0, 1],  # vocals Gilmour+Wright (guide)
        },
        "notes": "Structure ambient(pre) -> rock. Break a bar ~43 (densite chute). Sections validees a l'ecoute.",
    },
    "Breathe": {
        "file": "Breathe/Pink Floyd — Breathe in the Air [MIDIfind.com].mid",
        "scenes": {
            0: (1, 26),
            1: (27, 60),
            2: (61, 89),
        },
        "track_map": {
            "0": [6],  # drums
            "1": [0],  # guitar
            "2": [2, 3],  # slide guitar 1+2
            "3": [5],  # bass
            "4": [1],  # keyboard
            "6": [4],  # vocals guide (MIDI) — piste 7 = TA VOIX audio
        },
        "notes": "Court (2.5min, 89 bars), 7 pistes propres, un seul drumkit. Idéal test rapide du workflow.",
    },
    "In the Flesh": {
        "file": "In the Flesh/Pink Floyd — In the Flesh [MIDIfind.com].mid",
        "scenes": {
            0: (1, 20),
            1: (21, 44),
            2: (45, 74),
        },
        "track_map": {
            "2": [0],  # guitar 1 (overdrive)
            "3": [1],  # guitar 2 (overdrive)
            "4": [2],  # guitar 3 (clean)
        },
        "notes": "Uniquement guitares (pas de drums/basse). Metre complexe 12/8-6/8 : bien verifier le "
        "reglage du metre en session Ableton. 74 bars ~3.9min. 3 pistes guitares.",
    },
}

PLAN_TEMPLATE = """# Remake — {name} (Pink Floyd)

Source : `{file}`
Tempo : {tempo} | Signature : {sig} | Durée : {dur} min | {tracks} pistes

## Structure (scènes détectées — à valider à l'écoute)
{scenes_table}

## Mapping pistes (8 Ableton → groupes)
{mapping_table}

## Notes
{notes}

{factor}
## À faire
- [ ] Écouter et valider/ajuster les frontières de scènes
- [ ] Charger instruments + FX sur chaque piste
- [ ] Injecter les notes (add_notes_to_clip / inject_scene.py)
- [ ] Tuner les vols, mix, master
"""


def fmt_scenes(scenes):
    rows = []
    for i, (a, b) in scenes.items():
        rows.append(f"| {i} | {a} - {b} | {(b - a + 1) * 4} |")
    return "\n".join(rows)


def factorization_analysis(result: dict, atrack: str) -> str:
    """Analyse, pour une piste d'une scene, la repetitivite des mesures.

    Returns a short table: how many unique 4-beat bar patterns exist in the clip,
    the most-repeated pattern count, and (if repetitive) a suggestion to use a
    short groove clip loop + fills instead of a long clip.
    """
    lines = []
    for si, st in result.items():
        arr = st.get(atrack, [])
        if not arr:
            continue
        length = st["length"]
        n_bars = length // 4
        # group notes by 4-beat bar
        from collections import Counter, defaultdict

        perbar = defaultdict(list)
        for n in arr:
            b = int(n["start_time"] // 4)
            perbar[b].append((round(n["start_time"] % 4, 2), n["pitch"], n["velocity"]))
        pats = Counter(
            tuple(sorted(tuple(v) for v in perbar.get(b, []))) for b in range(n_bars)
        )
        uniq = len(pats)
        top = pats.most_common(1)
        topcnt = top[0][1] if top else 0
        suggest = (
            "FACTORISER (groove court + fills)"
            if topcnt >= 3
            else "variations (clips longs ok)"
        )
        lines.append(
            f"| sc{si} | {len(arr)} notes | {uniq} patterns | top x{topcnt} | {suggest} |"
        )
    return "\n".join(lines)


def main():
    for name, cfg in PLANS.items():
        src = str(BASE / cfg["file"])
        mid = mido.MidiFile(src)
        tracks = len(mid.tracks)
        sig = "4/4"
        tempo = ""
        for m in mid.tracks[0]:
            if m.type == "time_signature":
                sig = f"{m.numerator}/{m.denominator}"
            elif m.type == "set_tempo" and not tempo:
                tempo = f"{int(round(60_000_000 / m.tempo))}"
        scenes = {int(k): tuple(v) for k, v in cfg["scenes"].items()}
        tm = {str(k): [int(x) for x in v] for k, v in cfg["track_map"].items()}
        result = P.build_json(src, tm, scenes, P.DRUM_PITCH_MAP)

        outdir = BASE / name
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "_scenes_notes.json").write_text(
            json.dumps(result, ensure_ascii=False), encoding="utf-8"
        )

        # mapping table
        srcnames = {i: t for i, t in enumerate(P.analyze(mid))}
        mrows = []
        for at in sorted(tm, key=int):
            names = "; ".join(f"({s})" for s in tm[at])
            try:
                namelist = "; ".join(srcnames[s]["name"] for s in tm[at])
            except KeyError:
                namelist = names
            mrows.append(f"| {at} | {namelist} |")
        mapping = "\n".join(mrows)

        # factorization of EVERY instrument track across scenes
        factor_parts = []
        srcnames = {i: t for i, t in enumerate(P.analyze(mid))}
        for at in sorted(tm, key=int):
            label = srcnames[tm[at][0]]["name"] if tm[at] else f"piste {at}"
            factor_parts.append(
                f"\n### Piste {at} — {label}\n"
                + factorization_analysis(result, str(at))
            )
        factor = (
            "\n## Factorisation par piste (factoriser si top>3)\n"
            + "\n".join(factor_parts)
            + "\n"
        )

        plan = PLAN_TEMPLATE.format(
            name=name,
            file=cfg["file"],
            tempo=tempo or "<n/a>",
            sig=sig,
            dur=round(mid.length / 60, 1),
            tracks=tracks,
            scenes_table=fmt_scenes(scenes),
            mapping_table=mapping,
            notes=cfg["notes"],
            factor=factor,
        )
        (outdir / "REMAKES_PLAN.md").write_text(plan, encoding="utf-8")

        # summary
        for si, st in result.items():
            bars = st["_bars"]
            cnt = {k: len(v) for k, v in st.items() if k not in ("length", "_bars")}
            print(
                f"{name} sc{si} (bars {bars[0]}-{bars[1]}): "
                + ", ".join(f"{k}={v}" for k, v in cnt.items())
            )
        print(f"[wrote] {outdir}")


if __name__ == "__main__":
    main()
