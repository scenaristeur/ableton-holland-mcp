"""Diff generated notes vs what Live actually stored, for a few (track, slot) pairs."""
from collections import Counter

import prep_mona_ia as p

CASES = [(0, 0), (0, 1), (0, 2), (0, 6), (0, 11), (1, 2), (3, 2), (4, 0), (4, 2),
         (6, 2), (6, 11), (7, 7)]


def build(track, slot):
    name, nbars, style, chords = p.SCENES[slot][1:]
    gen = {
        0: lambda: p.gen_drums(style, nbars),
        1: lambda: p.gen_bass(style, chords),
        3: lambda: p.gen_ep(style, chords),
        4: lambda: p.gen_arp(style, chords),
        5: lambda: p.gen_pad(style, chords),
        6: lambda: p.gen_percs(style, nbars),
        7: lambda: [p.n(*e) for e in p.FX_PLAN.get(slot, [])],
    }
    return p.humanize(gen[track](), seed=slot * 100 + track)


def key(nd):
    return (round(float(nd["pitch"])), round(float(nd["start_time"]), 3))


for ti, si in CASES:
    want = build(ti, si)
    got = p.must("get_clip_notes", {"track_index": ti, "clip_index": si}).get("notes", [])
    cw, cg = Counter(map(key, want)), Counter(map(key, got))
    missing, extra = cw - cg, cg - cw
    clip_len = float(p.SCENES[si][2]) * 4
    print(f"\n=== track {ti} slot {si} ({p.SCENES[si][0]}): generated={len(want)} live={len(got)} len={clip_len}")
    for k, c in sorted(missing.items()):
        d = float([x for x in want if key(x) == k][0].get("duration") or 0)
        end = k[1] + d
        over = "  <-- FINISHES PAST THE CLIP" if end > clip_len + 0.001 else ""
        print(f"   MISSING x{c}  pitch={k[0]} start={k[1]} dur={d} end={round(end, 3)}{over}")
    for k, c in sorted(extra.items()):
        print(f"   EXTRA   x{c}  pitch={k[0]} start={k[1]}")
