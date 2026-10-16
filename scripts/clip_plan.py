from __future__ import annotations
import json
import math
import random


# ── Note helper ──────────────────────────────────────────────────────────────
def n(p, s, d, v):
    return {
        "pitch": p,
        "start_time": round(s, 4),
        "duration": round(d, 4),
        "velocity": v,
        "mute": False,
    }


def hrng(seed):
    return random.Random(seed)


# ── Chord library (Cm key) ──────────────────────────────────────────────────
# notes = comp voicing (C3 region); root = octave-2 root; rootless = drop root;
# lead pool = notes +12 (one octave up).
CHORDS = {
    "Cm9": {"notes": [48, 51, 55, 58, 62], "bass": 36},
    "Cm11": {"notes": [48, 51, 53, 55, 58, 62], "bass": 36},
    "Cm13": {"notes": [48, 51, 55, 58, 62, 57], "bass": 36},
    "Cm7": {"notes": [48, 51, 55, 58], "bass": 36},
    "Fm9": {"notes": [53, 56, 60, 63, 67], "bass": 41},
    "Fm11": {"notes": [53, 56, 58, 60, 63, 67], "bass": 41},
    "Fm7": {"notes": [53, 56, 60, 63], "bass": 41},
    "G13": {"notes": None, "bass": 43},
    "G9": {"notes": [55, 59, 62, 65, 69], "bass": 43},
    "G7": {"notes": [55, 59, 62, 65], "bass": None},
    "Gm7": {"notes": [55, 58, 62, 65], "bass": 43},
    "Abmaj9": {"notes": [56, 60, 63, 67, 70], "bass": 44},
    "Bb9": {"notes": [58, 62, 65, 68, 72], "bass": 46},
    "Bbmaj7": {"notes": [58, 62, 65, 69], "bass": 46},
    "Eb9": {"notes": [51, 55, 58, 61, 65], "bass": 39},
    "Dbmaj7": {"notes": [49, 53, 56, 60], "bass": 37},
}
# G13 explicit voicing (G B D F E = b13 colour)
CHORDS["G13"]["notes"] = [55, 59, 62, 65, 64]

KICK, SN, CH, OH, CR = 36, 38, 42, 46, 49


# ── Humanize: swing off-8ths, jitter timing & velocity, micro overlap ───────
def humanize(notes, seed, swing=0.052, vj=11, tj=0.016):
    r = hrng(seed)
    out = []
    for nt in notes:
        s, p, d, v = nt["start_time"], nt["pitch"], nt["duration"], nt["velocity"]
        frac = s - math.floor(s)
        if abs(frac - 0.5) < 0.04:  # "and" of the beat -> push (swing)
            s += swing * r.uniform(0.75, 1.25)
        s += r.uniform(-tj, tj)
        v = max(1, min(127, int(v + r.uniform(-vj, vj))))
        d = max(0.05, d + r.uniform(-0.03, 0.045))
        out.append(n(p, round(s, 4), round(d, 4), v))
    return out


# ── Instrument generators ───────────────────────────────────────────────────
def bass(chords, style):
    notes = []
    nb = len(chords)
    for b in range(nb):
        root = CHORDS[chords[b]]["bass"]
        if style == "octave":
            ev = [
                (0.0, root + 12, 100),
                (0.5, root, 56),
                (1.0, root + 12, 92),
                (1.5, root, 62),
                (2.0, root + 12, 86),
                (2.5, root, 96),
                (3.0, root + 12, 80),
                (3.5, root, 66),
            ]
            if b == nb - 1:
                ev.append((3.75, root + 12, 54))
        elif style == "drive":
            ev = [
                (0.0, root, 100),
                (0.5, root, 76),
                (1.0, root, 88),
                (1.5, root + 12, 82),
                (2.0, root, 70),
                (2.5, root, 94),
                (3.0, root, 82),
                (3.5, root + 12, 76),
            ]
            if b == nb - 1:
                ev.append((3.75, root, 62))
        else:
            ev = [
                (0.0, root, 100),
                (0.75, root, 52),
                (1.0, root, 64),
                (2.0, root, 96),
                (2.5, root, 72),
                (3.0, root, 78),
            ]
        if b < nb - 1:  # chromatic approach to next root
            nxt = CHORDS[chords[b + 1]]["bass"]
            ap = nxt - 1 if nxt > root else nxt + 1
            ev.append((3.5, ap, 50))
        for o, p, v in ev:
            off = abs(o - round(o)) == 0.5
            notes.append(n(p, b * 4 + o, 0.34 if off else 0.4, v))
    return notes


def _drum_fill(base):
    f = []
    for i, x in enumerate(
        [2.5, 2.625, 2.75, 2.875, 3.0, 3.125, 3.25, 3.375, 3.5, 3.625, 3.75, 3.875]
    ):
        f.append(n(SN, base + x, 0.1, 58 + i * 4))
    f.append(n(KICK, base + 3.5, 0.3, 82))
    f.append(n(CR, base + 3.95, 1.1, 72))
    return f


def drums(style, nbars):
    notes = []
    for b in range(nbars):
        base = b * 4
        last = b == nbars - 1
        if style == "light":
            notes += [
                n(KICK, base + 0, 0.4, 96),
                n(KICK, base + 2.5, 0.4, 80),
                n(SN, base + 2, 0.3, 84),
                n(CH, base + 0, 0.2, 58),
                n(CH, base + 1, 0.2, 52),
                n(CH, base + 2, 0.2, 58),
                n(CH, base + 3, 0.2, 52),
            ]
        elif style in ("full", "busy", "build", "solo", "climax"):
            ks = [0, 2.5]
            if style in ("busy", "build", "climax"):
                ks += [3.5]
            if style == "climax":
                ks += [1.5, 3.0]
            for k in ks:
                notes.append(n(KICK, base + k, 0.4, 100 if k in (0, 2.5) else 90))
            notes += [n(SN, base + 1, 0.3, 100), n(SN, base + 3, 0.3, 96)]
            if style in ("busy", "build", "climax", "solo"):
                notes.append(n(SN, base + 2.5, 0.18, 62))
            if b % 2 == 1:  # ghost snare
                notes.append(n(SN, base + 3.5, 0.12, 40))
            for h in [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5]:
                vel = 50 if abs(h - round(h)) == 0.5 else 76
                notes.append(n(CH, base + h, 0.18, vel))
            if style in ("busy", "build", "climax"):
                for h in [0.25, 0.75, 1.25, 1.75, 2.25, 2.75, 3.25, 3.75]:
                    notes.append(n(CH, base + h, 0.09, 34))
            notes.append(n(OH, base + 2.5, 0.3, 62))
            if b == 0:
                notes.append(n(CR, base + 0, 1.2, 54))
            if style in ("build", "climax") and last:
                for x in [3.0, 3.25, 3.5, 3.75]:
                    notes.append(n(SN, base + x, 0.12, 92))
            if last and style in ("full", "busy", "solo", "climax", "build"):
                notes += _drum_fill(base)
        elif style == "half":
            notes += [n(KICK, base + 0, 0.5, 100), n(SN, base + 2, 0.4, 92)]
            for h in [0, 1, 2, 3]:
                notes.append(n(CH, base + h, 0.18, 42))
            notes.append(n(OH, base + 2, 0.4, 52))
    return notes


COMP_RHYTHMS = [
    [1.5, 3.5],
    [0.5, 2.5],
    [1.0, 2.5, 3.5],
    [0.5, 1.5, 3.0],
    [2.0, 3.5],
    [1.5],
    [0.75, 2.75],
    [1.25, 3.25],
]


def comp(track, chords, style):
    shift = 12 if track != 0 else 0
    notes = []
    for b in range(len(chords)):
        base = b * 4
        voic = [v + shift for v in CHORDS[chords[b]]["notes"][1:]]  # rootless
        if style == "pad":
            for p in voic:
                notes.append(n(p, base + 0, 3.8, 58))
            continue
        if style == "sparse":
            offs = [1.5]
        else:
            offs = COMP_RHYTHMS[b % len(COMP_RHYTHMS)]
        play = voic if (b % 3 != 2) else voic[:3]  # breathe
        for o in offs:
            for p in play:
                notes.append(n(p, base + o, 0.42, 74))
            if b % 2 == 0 and o == offs[0]:  # grace/neighbor
                notes.append(n(play[0] - 2, base + o - 0.06, 0.07, 48))
        if b % 4 == 3:  # low root pickup
            notes.append(n(voic[0] - 12, base + 3.75, 0.2, 64))
    return notes


STAB_RHYTHMS = [[0, 2.5], [0.5, 2.0, 3.5], [0, 1.5, 3.0], [2.0, 3.5]]


def stab(track, chords, style):
    shift = 12
    notes = []
    for b in range(len(chords)):
        base = b * 4
        voic = [v + shift for v in CHORDS[chords[b]]["notes"][1:]]
        if track == 7:  # horns: tight 3-note
            voic = voic[:3]
        offs = STAB_RHYTHMS[b % len(STAB_RHYTHMS)]
        for o in offs:
            for p in voic:
                # tiny delayed attack + accent -> blown/struck feel
                notes.append(n(p, base + o + 0.012, 0.44, 96 if o == 0 else 82))
    return notes


def strings(chords, style):
    notes = []
    for b in range(len(chords)):
        base = b * 4
        voic = [v + 12 for v in CHORDS[chords[b]]["notes"]]
        vel = 44 if style == "soft" else 56
        # two bowed segments with a swell (breathing, not one static block)
        for seg, st, ln in [(0, 0.0, 2.0), (1, 2.0, 2.0)]:
            sb = base + st
            ramp = [vel - 6, vel + 4] if seg == 0 else [vel, vel + 8]
            for i, p in enumerate(voic):
                notes.append(n(p, sb + 0.02, ln - 0.04, ramp[min(i, len(ramp) - 1)]))
            if style == "lush":  # shimmer octave
                for p in voic[:2]:
                    notes.append(n(p + 12, sb + 0.05, ln - 0.12, vel - 14))
    return notes


LEAD_RIFFS = [
    [(0, 1.0, 90), (1.0, 0.5, 82), (1.5, 0.5, 82), (2.0, 1.0, 88), (3.0, 0.5, 84)],
    [
        (0, 0.5, 90),
        (0.5, 0.5, 80),
        (1.5, 1.0, 88),
        (2.5, 0.5, 82),
        (3.0, 0.5, 86),
        (3.5, 0.5, 80),
    ],
    [(0, 1.5, 92), (1.5, 0.5, 84), (2.0, 1.0, 88), (3.0, 1.0, 86)],
    [
        (0, 0.5, 90),
        (1.0, 1.0, 86),
        (2.0, 0.5, 84),
        (2.5, 0.5, 82),
        (3.0, 0.5, 88),
        (3.5, 0.5, 80),
    ],
]


def lead(chords, style):
    notes = []
    for b in range(len(chords)):
        base = b * 4
        pool = [p + 12 for p in CHORDS[chords[b]]["notes"]]
        riff = LEAD_RIFFS[b % len(LEAD_RIFFS)]
        for o, d, v in riff:
            p = pool[(b + int(o * 2)) % len(pool)]
            notes.append(n(p, base + o, d, v))
            if o > 0:  # grace note before
                notes.append(n(p - 2, base + o - 0.05, 0.06, 42))
    return notes


def gen(track, style, chords):
    if track == 0:
        return comp(0, chords, style)
    if track == 1:
        return drums(style, len(chords))
    if track == 2:
        return strings(chords, style)
    if track == 3:
        return bass(chords, style)
    if track == 4:
        return (
            stab(4, chords, "stab")
            if style in ("stab", "wah")
            else comp(4, chords, style or "comp")
        )
    if track == 5:
        return lead(chords, style)
    if track == 6:
        return stab(6, chords, "stab") if style == "stab" else comp(6, chords, "pad")
    if track == 7:
        return stab(7, chords, "stab")
    return []


# ── Full 16-scene epic (all 8 tracks; showcase sections lengthened to 8 bars) ─
Refrain8 = ["Cm9", "Fm9", "G13", "Cm9", "Abmaj9", "Bb9", "G13", "Cm9"]
RefrainFinal8 = ["Cm13", "Fm11", "G13", "Cm9", "Abmaj9", "Bb9", "G13", "Cm9"]
Bridge8 = ["Abmaj9", "Dbmaj7", "Bb9", "Eb9", "Abmaj9", "Dbmaj7", "Bb9", "Eb9"]
Climax8 = ["Cm13", "Fm11", "G13", "Cm9", "Cm13", "Fm11", "G13", "Cm9"]
Solo8 = ["Cm9", "Fm9", "G13", "Cm9", "Fm9", "Bb9", "G13", "Cm9"]

P = {
    0: "Piano",
    1: "Drums",
    2: "Strings",
    3: "Bass",
    4: "Guitar",
    5: "Lead",
    6: "Organ",
    7: "Horns",
}

scenes = [
    (
        0,
        "Intro",
        8,
        ["Cm9", "Cm9"],
        {
            0: "sparse",
            1: "light",
            2: None,
            3: "root",
            4: None,
            5: None,
            6: "pad",
            7: None,
        },
    ),
    (
        1,
        "Couplet 1",
        16,
        ["Cm9", "Fm9", "G13", "Cm9"],
        {
            0: "comp",
            1: "full",
            2: "soft",
            3: "root",
            4: "comp",
            5: None,
            6: "pad",
            7: None,
        },
    ),
    (
        2,
        "Refrain",
        32,
        Refrain8,
        {
            0: "comp",
            1: "full",
            2: "lush",
            3: "octave",
            4: "comp",
            5: "motif",
            6: "stab",
            7: "stab",
        },
    ),
    (
        3,
        "Pont",
        16,
        ["Abmaj9", "Abmaj9", "Bb9", "Bb9"],
        {
            0: "sparse",
            1: "half",
            2: "lush",
            3: "root",
            4: None,
            5: None,
            6: "pad",
            7: None,
        },
    ),
    (
        4,
        "Refrain Final",
        32,
        RefrainFinal8,
        {
            0: "comp",
            1: "climax",
            2: "lush",
            3: "octave",
            4: "comp",
            5: "motif",
            6: "stab",
            7: "stab",
        },
    ),
    (
        5,
        "Outro",
        16,
        ["G13", "Cm9", "Cm9", "Cm9"],
        {
            0: "sparse",
            1: "light",
            2: "soft",
            3: "root",
            4: None,
            5: None,
            6: "pad",
            7: None,
        },
    ),
    (
        6,
        "Couplet 2",
        16,
        ["Cm9", "Fm9", "G13", "Cm9"],
        {
            0: "comp",
            1: "busy",
            2: "soft",
            3: "octave",
            4: "stab",
            5: None,
            6: "stab",
            7: "stab",
        },
    ),
    (
        7,
        "Build",
        16,
        ["Cm11", "Fm11", "G13", "G13"],
        {
            0: "comp",
            1: "build",
            2: "lush",
            3: "drive",
            4: "stab",
            5: "motif",
            6: "pad",
            7: None,
        },
    ),
    (
        8,
        "Refrain Reprise",
        32,
        Refrain8,
        {
            0: "comp",
            1: "climax",
            2: "lush",
            3: "octave",
            4: "comp",
            5: "motif",
            6: "stab",
            7: "stab",
        },
    ),
    (
        9,
        "Pont 2",
        16,
        ["Abmaj9", "Abmaj9", "Bb9", "Bb9"],
        {
            0: "sparse",
            1: "half",
            2: "lush",
            3: "root",
            4: None,
            5: None,
            6: "pad",
            7: None,
        },
    ),
    (
        10,
        "Bridge",
        32,
        Bridge8,
        {
            0: "comp",
            1: "full",
            2: "lush",
            3: "root",
            4: "comp",
            5: "motif",
            6: "pad",
            7: "stab",
        },
    ),
    (
        11,
        "Climax",
        32,
        Climax8,
        {
            0: "comp",
            1: "climax",
            2: "lush",
            3: "octave",
            4: "stab",
            5: "motif",
            6: "stab",
            7: "stab",
        },
    ),
    (
        12,
        "Solo",
        32,
        Solo8,
        {
            0: "comp",
            1: "solo",
            2: "soft",
            3: "drive",
            4: "comp",
            5: "motif",
            6: "pad",
            7: "stab",
        },
    ),
    (
        13,
        "Refrain Final 2",
        32,
        RefrainFinal8,
        {
            0: "comp",
            1: "climax",
            2: "lush",
            3: "octave",
            4: "comp",
            5: "motif",
            6: "stab",
            7: "stab",
        },
    ),
    (
        14,
        "Outro 2",
        16,
        ["Cm9", "Abmaj9", "Bb9", "Cm9"],
        {
            0: "sparse",
            1: "half",
            2: None,
            3: "root",
            4: None,
            5: None,
            6: "pad",
            7: None,
        },
    ),
    (
        15,
        "Coda",
        8,
        ["Cm9"],
        {
            0: "sparse",
            1: "light",
            2: None,
            3: "root",
            4: None,
            5: None,
            6: "pad",
            7: None,
        },
    ),
]

plan = {}
for slot, name, length, chords, styles in scenes:
    plan[slot] = {}
    for trk in range(8):
        style = styles.get(trk)
        if style:
            notes = humanize(gen(trk, style, chords), seed=slot * 100 + trk)
            plan[slot][trk] = {"length": length, "notes": notes, "name": name}

with open("clip_plan.json", "w") as f:
    json.dump(plan, f)

for slot in sorted(plan, key=lambda x: int(x)):
    print(
        f"slot {slot} ({plan[slot][list(plan[slot])[0]]['name']}): tracks {sorted(plan[slot], key=lambda x: int(x))}"
    )
print("TOTAL clips:", sum(len(plan[s]) for s in plan))
