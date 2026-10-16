"""Build the 12-scene skeleton of "Mon IA Lisa" in Ableton Live 12 Lite.

105 BPM, 4/4, D dorian. 76 bars in 12 scenes. 7 MIDI tracks + 1 audio (Lite = 8 max).
Swing is baked into note positions: Live's groove amount is global, not per scene.

Specs: sources/Monia_Lisa/PAROLES.md (lyrics, chords, topline)
       sources/Monia_Lisa/CLIP_PLAN.md (note plan, devices, automation)

Run:  .venv\\Scripts\\python prep_mona_ia.py
Then verify with get_clip_notes before touching the arrangement. Do NOT save.
"""

from __future__ import annotations

import json
import math
import random
import socket
import time

HOST = "127.0.0.1"
PORT = 9877

# ── swing baked into the notes ────────────────────────────────────────────────
# +0.04 beat on 8th offbeats == Live's "58% swing" ratio (S-0.5)*0.5 = 0.04
SWING_8TH = 0.04
SWING_16TH = 0.015


def sw(pos: float) -> float:
    """Apply the baked swing to a nominal beat position."""
    frac = round(pos - math.floor(pos), 4)
    if frac == 0.5:
        pos += SWING_8TH
    elif frac in (0.25, 0.75):
        pos += SWING_16TH
    return pos


def n(pitch: int, start: float, dur: float, vel: int) -> dict:
    return {
        "pitch": int(pitch),
        "start_time": round(sw(start), 4),
        "duration": round(dur, 4),
        "velocity": int(max(1, min(100, vel))),
        "mute": False,
    }


def humanize(notes: list[dict], seed: int, vj: int = 4, tj: float = 0.008) -> list[dict]:
    """Timing/velocity jitter. The downbeat (t=0) is never moved: a negative
    start_time is invalid and Live silently drops the note."""
    r = random.Random(seed)
    out = []
    for nt in notes:
        nt = dict(nt)
        if nt["start_time"] > 0.0:
            nt["start_time"] = max(0.0, nt["start_time"] + r.uniform(-tj, tj))
        nt["start_time"] = round(nt["start_time"], 4)
        nt["velocity"] = max(1, min(100, nt["velocity"] + r.randint(-vj, vj)))
        out.append(nt)
    return out


# ── RS plumbing ───────────────────────────────────────────────────────────────
def send(cmd: str, params: dict, timeout: float = 90.0) -> dict:
    payload = json.dumps({"type": cmd, "params": params}).encode("utf-8")
    with socket.create_connection((HOST, PORT), timeout=timeout) as s:
        s.settimeout(timeout)
        s.sendall(payload)
        buf = b""
        while True:
            chunk = s.recv(65536)
            if not chunk:
                break
            buf += chunk
            try:
                return json.loads(buf.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
    raise RuntimeError("connection closed")


def must(cmd: str, params: dict, timeout: float = 90.0) -> dict:
    resp = send(cmd, params, timeout)
    if resp.get("status") == "error":
        raise RuntimeError(f"{cmd}: {resp.get('message')}")
    return resp.get("result", {})


# ── harmony ───────────────────────────────────────────────────────────────────
# D dorian. ep = EP voicing (rootless), bass = bass root, arp = arpeggio pool,
# pad = sustained voicing.
CH = {
    "Dm9":    {"ep": [53, 57, 60, 64], "bass": 38, "arp": [62, 65, 69, 72], "pad": [50, 53, 57, 60], "end": 60},
    "Cmaj9":  {"ep": [52, 55, 59, 62], "bass": 36, "arp": [60, 64, 67, 72], "pad": [48, 52, 55, 59], "end": 59},
    "G13":    {"ep": [59, 62, 65, 69], "bass": 43, "arp": [59, 62, 65, 69], "pad": [43, 59, 62, 64], "end": 57},
    "A7b9":   {"ep": [61, 64, 67],    "bass": 45, "arp": [61, 64, 67, 70], "pad": [45, 61, 64, 67], "end": 57},
    "Bbmaj7": {"ep": [62, 65, 69],    "bass": 34, "arp": [62, 65, 69, 72], "pad": [46, 62, 65], "end": 46},
    "C7":     {"ep": [64, 67, 70],    "bass": 36, "arp": [64, 67, 70, 72], "pad": [48, 64, 67], "end": 46},
    "Dm7":    {"ep": [65, 69, 72],    "bass": 38, "arp": [65, 69, 72, 74], "pad": [50, 65, 69], "end": 46},
    "Gm7":    {"ep": [58, 62, 65],    "bass": 43, "arp": [58, 62, 65, 69], "pad": [43, 58, 62], "end": 46},
    "Ebmaj7": {"ep": [55, 58, 62],    "bass": 39, "arp": [58, 62, 65, 67], "pad": [39, 55, 58], "end": 43},
    "Cm7":    {"ep": [51, 55, 58],    "bass": 36, "arp": [58, 60, 63, 67], "pad": [36, 51, 55], "end": 45},
}
# "end" = last note of the 8-note arpeggio. It is NOT a formula: it is the pitch that
# leads into the next chord (Dm9 -> C needs B, not Bb). Values come from CLIP_PLAN.md §7.

VERSE = ["Dm9", "Cmaj9", "G13", "A7b9"] * 2
CHORUS = ["Bbmaj7", "C7", "Dm7", "Gm7"] * 2
CHORUS1 = ["Bbmaj7", "C7", "Dm7", "Gm7"] * 2
DOUBLE = ["Bbmaj7", "C7", "Dm7", "Gm7", "Bbmaj7", "C7", "Dm7", "A7b9"]
BRIDGE = ["Ebmaj7", "Dm7", "Cm7", "Bbmaj7", "Ebmaj7", "Dm7", "Cm7", "A7b9"]
POST = ["Bbmaj7", "Gm7", "Cm7", "A7b9"]
OUTRO = ["Dm9", "Cmaj9", "G13", "Dm9"]

# ── drum pads ─────────────────────────────────────────────────────────────────
# CHH = charley (closed hat). Named CHH, not CH: CH is the harmony table.
# Boom Bap Kit (verified with get_drum_pad_info): 36 Kick Shadow · 38 Snare Hat Chop
#   39 Clap Ina · 42 Hihat Closed Memphis · 46 Hihat Open Bonzo · 49 Crash Stacked
#   51 Ride Gated · 48 Stab Brass Blast -- and nothing above 51.
KICK, SN, CLAP, CHH, OH, CR, RID, STAB = 36, 38, 39, 42, 46, 49, 51, 48
# Perc Kitchen Kit is NOT a GM kit: 16 pads, 36-51, all percussion/FX.
#   36 Perc Pan · 37 Perc Pot 1 · 38 Perc Pot 2 · 39 Perc Strike · 42 Perc Knifes
#   46 Perc Spoons · 48 Perc Glass Low · 49 Perc Kettle · 50 Perc Kling · 51 Perc Klang
# 64/70/75 DO NOT EXIST there, so the shaker/tambourine/clave roles are remapped.
P_SHAKER, P_SHAKER2, P_STRIKE, P_SPOONS, P_KLING = 37, 38, 39, 46, 50
P_CRASH = 52  # Crash Lofi, depose par David sur le pad E2 (note 52, convention Ableton C3=60)

# ── track + scene layout ──────────────────────────────────────────────────────
TRACK_NAMES = [
    "1-Batterie",
    "2-Basse",
    "3-Voix",        # the set's existing empty audio track, kept at index 2
    "4-Clav EP",
    "5-Arp+Hook",
    "6-Nappe",
    "7-Percs",
    "8-FX",
]
AUDIO_TRACK = 2  # the RS cannot create or move an audio track -- see CLIP_PLAN.md §2

SCENES = [
    # slot, name, bars, style, chords
    (0,  "S0 Intro",       4, "intro",  ["Dm9", "Cmaj9", "G13", "A7b9"]),
    (1,  "S1 Couplet 1",   8, "verse",  VERSE),
    (2,  "S2 Refrain 1",   8, "chorus", CHORUS1),
    (3,  "S3 Couplet 2",   8, "verse",  VERSE),
    (4,  "S4 Refrain 2",   8, "chorus", CHORUS),
    (5,  "S5 Pre-Hook",    4, "pre",    ["Dm9", "Cmaj9", "G13", "A7b9"]),
    (6,  "S6 Mini-Hook",   4, "hook4",  ["Bbmaj7", "C7", "Dm7", "Gm7"]),
    (7,  "S7 Post-Hook",   4, "post",   POST),
    (8,  "S8 Pont",        8, "bridge", BRIDGE),
    (9,  "S9 Double-Hook", 8, "double", DOUBLE),
    (10, "S10 Refrain 3",  8, "chorus", CHORUS),
    (11, "S11 Outro",      4, "outro",  OUTRO),
]

DEVICES = {
    0: [("query:Drums#FileId_15029", "Toy LoFi Kit")],  # drums (choisi par David, verifie get_drum_pad_info)
    1: [("query:Synths#Drift", "Drift")],              # bass
    3: [("query:Synths#Drift", "Drift")],              # EP
    4: [("query:Synths#Drift", "Drift")],              # arp / hook
    5: [("query:Synths#Drift", "Drift")],              # pad
    6: [("query:Drums#FileId_5421", "Perc Kitchen Kit")],  # percs
    7: [("query:Synths#Drift", "Drift")],              # FX noise / impacts / dings
}
# Live 12 Lite has NO Analog, Electric, Wavetable, Operator, Collision or Tension.
# The whole synth palette is Drift (a multis: 12 preset families). The presets are
# chosen and shaped per role after the build -- see CLIP_PLAN.md section 2.


# ── generators ────────────────────────────────────────────────────────────────
def gen_drums(style: str, nbars: int) -> list[dict]:
    """Closed hats are 8ths everywhere (16ths when building). Quarter notes kill the funk."""
    out: list[dict] = []

    def hats(base: float, step: float, count: int, vel, dur: float = 0.15, pitch: int = CHH):
        for i in range(count):
            v = vel(i) if callable(vel) else vel
            out.append(n(pitch, base + i * step, dur, v))

    for b in range(nbars):
        base = b * 4.0
        last = b == nbars - 1

        if style == "intro":
            # charley seules, croches, crescendo -- pas de kick
            hats(base, 0.5, 8, lambda i, b=b: 40 + b * 8 + (6 if i % 2 else 0))
            if last:
                # pas de crash batterie : Toy LoFi n'a pas de crash, pad 49 = clap2.
                # l'impact est sur la piste FX (FX_PLAN scene 0).
                out.append(n(OH, base + 3.75, 0.4, 46))
            continue

        if style == "pre":
            out.append(n(KICK, base + 0, 0.4, 104))
            if b < 2:
                hats(base, 0.5, 8, lambda i, b=b: 46 + b * 6 + (10 if i % 2 == 0 else 0))
            else:  # mes. 39-40: hats to 16ths under the riser
                hats(base, 0.25, 16, lambda i, b=b: 44 + b * 8 + (6 if i % 2 else 0), 0.1)
            if last:  # roulement caisse claire 2.0 -> 3.75
                for i in range(8):
                    out.append(n(SN, base + 2 + i * 0.25, 0.1, 62 + i * 7))
            continue

        if style == "hook4":
            # half-time : kick 0 et 2, caisse claire 2, charley croches
            if last:
                # mes. 44 : le "eh" tombe sur le temps 3 -> on joue jusque-la, puis plus rien
                out += [n(KICK, base + 0, 0.45, 108), n(KICK, base + 2, 0.45, 100),
                        n(SN, base + 2, 0.32, 108)]
                hats(base, 0.5, 4, lambda i: 66 if i % 2 == 0 else 50)
                continue
            out += [n(KICK, base + 0, 0.45, 108), n(KICK, base + 2, 0.45, 100),
                    n(SN, base + 2, 0.32, 108)]
            hats(base, 0.5, 8, lambda i, b=b: (68 + b % 3 * 3) if i % 2 == 0 else (56 + (b + 1) % 3 * 3))
            out.append(n(OH, base + 3.5, 0.35, 58))
            if b == 1:
                # mes. 42 : la voix laisse 2,5 temps d'air a partir de 1.54.
                # AUCUN fill ici -- la basse seule tient le trou, c'est tout le gimmick.
                out = [x for x in out if x["start_time"] < base + 1.5]
            continue

        if style == "post":
            # mes. 45-48 : le vide. Aucun crash ici -- il mangerait "Elle te voit"
            # (mes. 45, temps 1). L'"impact" apres le "eh" du mini-hook, c'est la
            # cymbale inverse de la piste FX qui deborde depuis la mesure 44.
            if last:
                out.append(n(KICK, base + 0, 0.5, 70))
            continue

        if style == "bridge":
            # charley croches seules -- le crescendo de maracas vit sur la piste Percs
            hats(base, 0.5, 8, lambda i, b=b: 50 + b * 3 + (4 if i % 2 == 0 else 0))
            if last:
                out.append(n(OH, base + 3.5, 0.5, 52))
            continue

        if style == "outro":
            if b == 0:
                out += [n(KICK, base, 0.4, 100), n(KICK, base + 2, 0.4, 92),
                        n(SN, base + 1, 0.3, 96), n(SN, base + 3, 0.3, 92)]
            elif b == 1:
                out += [n(KICK, base, 0.4, 92), n(KICK, base + 2, 0.4, 84),
                        n(SN, base + 1, 0.3, 88), n(SN, base + 3, 0.3, 84)]
            elif b == 2:
                out += [n(KICK, base, 0.4, 84), n(SN, base + 1, 0.3, 78)]
            if last:
                continue  # mes. 76 : rien, cymbale inverse seule (piste FX)
            hats(base, 0.5, 8, lambda i, b=b: 50 - b * 8 + (4 if i % 2 == 0 else 0))
            if b <= 1:
                out.append(n(OH, base + 3.5, 0.35, 54))
            continue

        # verse / chorus / double
        if style == "double" and last:
            # mes. 64 : le "eh" crie -- un kick, puis un temps de silence absolu
            out += [n(KICK, base + 0, 0.45, 112), n(RID, base + 0.5, 0.3, 40)]
            continue
        is_fill = style == "verse" and b % 4 == 3
        for k, v in ((0, 112), (2.5, 96), (3.5, 88)):
            out.append(n(KICK, base + k, 0.4, v))
        out.append(n(SN, base + 1, 0.3, 104))
        if not is_fill:
            # sur une mesure de fill, le roulement possede les deux derniers temps, backbeat inclus
            out.append(n(SN, base + 3, 0.3, 98))
            out.append(n(SN, base + (2.75 if style == "verse" else 3.25), 0.12, 40))
        hats(base, 0.5, 8, lambda i, b=b: (72 + b % 3 * 3) if i % 2 == 0 else (58 + (b + 1) % 3 * 3))
        out.append(n(OH, base + 3.5, 0.35, 60))
        if style in ("chorus", "double"):
            out += [n(CLAP, base + 1, 0.28, 72), n(CLAP, base + 3, 0.28, 70)]
        if style == "double":
            hats(base, 1.0, 4, 46, 0.4, RID)
        if is_fill:  # roulement 16emes 2.54 -> 3.765, kick d'anticipation sur le temps suivant
            for i in range(6):
                out.append(n(SN, base + 2.5 + i * 0.25, 0.1, 60 + i * 9))
            out.append(n(KICK, base + 3.9, 0.3, 82))
    return out


def gen_bass(style: str, chords: list[str]) -> list[dict]:
    out: list[dict] = []
    if style == "bridge":
        roots = [39, 38, 36, 34, 39, 38, 36, 33]
        for b, r in enumerate(roots):
            dur = 7.0 if b == len(roots) - 1 else 3.9
            out.append(n(r, b * 4.0, dur, 76 if b < 3 else 70))
        return out
    if style == "post":
        return [n(33, 3 * 4.0, 3.8, 60)]
    if style == "pre":
        # pedal only: the tension of the build lives in the drums and the riser
        return [n(CH[c]["bass"], b * 4.0, 3.9, 70) for b, c in enumerate(chords)]
    if style == "hook4":
        # the bass fills the 2.5-beat hole the voice leaves in mes. 42
        out.append(n(34, 1.5, 2.4, 88))
        return out
    hole_bar = 1 if style == "double" else None  # the "eh" measure of the double-hook

    for b, name in enumerate(chords):
        base = b * 4.0
        last = b == len(chords) - 1
        if style == "double" and last:
            continue  # mes. 64: the shouted "eh", one beat of silence
        if hole_bar is not None and b == hole_bar:
            # everything cuts except the bass holding the hole open
            out.append(n(34, base + 1.5, 2.4, 88))
            continue
        root = CH[name]["bass"]
        nxt = CH[chords[b + 1]]["bass"] if b + 1 < len(chords) else root
        appr = nxt - 1 if nxt > root else nxt + 1

        if style == "chorus":
            cells = {
                "Bbmaj7": [(0, root, 96), (0.75, root + 12, 88), (1.5, 41, 82), (2, root, 92),
                           (2.5, root + 12, 84), (3, 38, 78), (3.5, root, 88)],
                "C7":     [(0, root, 96), (0.5, root + 12, 90), (1, root, 84), (1.5, 34, 74),
                           (2, root, 92), (2.5, 43, 84), (3, 46, 86), (3.5, 43, 72)],
                "Dm7":    [(0, root, 96), (0.75, root + 12, 90), (1.5, 41, 84), (2, root, 92),
                           (2.5, root + 12, 86), (3, 43, 80), (3.5, 41, 84)],
                "Gm7":    [(0, root, 94), (0.75, root - 12, 84), (1.5, 34, 82), (2, root - 12, 90),
                           (2.5, root, 86), (3, 34, 80), (3.5, root - 12, 88)],
            }
            for pos, pitch, vel in cells.get(name, [(0, root, 92), (2, root, 88)]):
                out.append(n(pitch, base + pos, 0.4, vel))
            continue

        if name == "A7b9":  # chromatic descent -- the phrygian turnaround
            for pos, pitch, vel in ((0, 45, 94), (0.75, 44, 78), (1, 43, 86), (1.5, 45, 80),
                                    (2, 45, 90), (2.5, 44, 74), (3, 43, 84), (3.5, 41, 70)):
                out.append(n(pitch, base + pos, 0.36, vel))
            continue
        if name == "G13":
            for pos, pitch, vel in ((0, 43, 94), (1.5, 55, 84), (2, 38, 88),
                                    (2.5, 43, 80), (3, 55, 82), (3.5, 45, 74)):
                out.append(n(pitch, base + pos, 0.38, vel))
            continue
        for pos, pitch, vel in ((0, root, 96), (1.5, root + 12, 84), (2, root, 90),
                                (2.75, root, 60), (3.5, appr, 68)):
            out.append(n(pitch, base + pos, 0.4, vel))
    return out


def gen_ep(style: str, chords: list[str]) -> list[dict]:
    out: list[dict] = []
    for b, name in enumerate(chords):
        base = b * 4.0
        last = b == len(chords) - 1
        voic = CH[name]["ep"]
        if name == "A7b9":
            voic = voic + [58]  # Bb = the b9, quiet
        if style in ("verse", "chorus", "double"):
            shift = 12 if style == "verse" else 0
            hits = [(0, 92), (2.5, 84)] if style == "verse" else [(0, 96), (2.5, 84), (3.5, 70)]
            if style == "chorus":
                for j, (pos, vel) in enumerate(hits):
                    for k, p in enumerate(voic):
                        v = vel if not (name == "A7b9" and p == 58) else 60
                        out.append(n(p + shift, base + pos + 0.012 * k, 0.44, v))
                    if j == 0:  # extra root stab answering every "A a Z"
                        out.append(n(voic[0] - 12 + shift, base + pos, 0.4, 100))
            elif style == "double" and not last:
                for pos, vel in hits[:2]:
                    for k, p in enumerate(voic):
                        out.append(n(p, base + pos + 0.012 * k, 0.44, vel))
                    if pos == 0:
                        out.append(n(voic[0] - 12, base + pos, 0.4, 100))
            elif style == "verse":
                for pos, vel in hits:
                    for k, p in enumerate(voic):
                        out.append(n(p + shift, base + pos + 0.012 * k, 0.44, vel))
                    if pos == 0 and b % 2 == 0:
                        out.append(n(voic[0] - 12 + shift, base + pos, 0.4, 100))
        elif style == "hook4":
            for pos, vel in ((0, 94), (1.5, 80), (2.5, 88)):
                for k, p in enumerate(voic):
                    out.append(n(p, base + pos + 0.012 * k, 0.42, vel))
    return out


def gen_arp(style: str, chords: list[str]) -> list[dict]:
    out: list[dict] = []
    if style in ("verse", "intro"):
        for b, name in enumerate(chords):
            base = b * 4.0
            a = CH[name]["arp"]
            # the 8th note is the pitch that leads into the next chord, not a formula
            seq = [a[0], a[1], a[2], a[3], a[2], a[1], a[0], CH[name]["end"]]
            for i, p in enumerate(seq):
                vel = 74 if i in (0, 4) else 62
                if name == "A7b9" and p == 70:
                    vel = 62
                out.append(n(p, base + i * 0.5, 0.28, vel))
        return out
    if style == "chorus":
        # contre-chant : l'arpège s'arrête, la piste passe sous la voix
        for b, name in enumerate(chords):
            base = b * 4.0
            if b == 0:
                for s, p in ((0, 46), (0.5, 45), (1, 46), (1.5, 48)):
                    out.append(n(p, base + s, 0.36, 76))
            elif b == 1:
                out.append(n(46, base + 0, 3.9, 72))  # Bb2 tenu 4 temps
            elif b == 6:
                for s, p in ((0, 46), (0.5, 46), (1, 48), (1.5, 45)):
                    out.append(n(p, base + s, 0.36, 74))
            elif b == 7:
                for s, p in ((0, 46), (0.5, 46), (1, 45), (1.5, 43), (2, 41)):
                    out.append(n(p, base + s, 0.36, 70))
            else:
                continue
        return out
    if style in ("hook4", "double"):
        for b in range(len(chords)):
            if style == "double" and b == len(chords) - 1:
                continue  # mes. 64: the "eh" cuts the arp too
            base = b * 4.0
            # motif A (ascendant) bars 0, 2 ; motif B (descendant) bars 1, 3
            if b % 2 == 0:
                # Bb3 C4 D4 -- D4 tenu 2 temps
                out.append(n(58, base + 0, 0.4, 84))
                out.append(n(60, base + 1, 0.4, 82))
                out.append(n(62, base + 2, 1.9, 80))
            else:
                # Bb3 A3 G3 -- puis le silence du gimmick
                for s, p in ((0, 58), (0.5, 57), (1, 55)):
                    out.append(n(p, base + s, 0.3, 80))
        return out
    if style == "bridge":
        for b in range(len(chords)):
            p = [46, 45, 43, 45, 46, 45, 43, 41][b]
            out.append(n(p, b * 4.0, 3.9, 58))
        return out
    if style == "pre":
        return [n(50, 0, 3.8, 46), n(50, 12.0, 3.8, 50)]
    return out


def gen_pad(style: str, chords: list[str]) -> list[dict]:
    out: list[dict] = []
    if style == "post":
        for b, name in enumerate(chords):
            for p in CH[name]["pad"]:
                out.append(n(p, b * 4.0, 3.8, 48 if b < 3 else 42))
        return out
    for b, name in enumerate(chords):
        voic = CH[name]["pad"]
        vel = 54 if style != "chorus" else 58
        segs = (0, 2) if not (style == "double" and b == len(chords) - 1) else (0,)
        for seg in segs:
            for i, p in enumerate(voic):
                v = vel - 4 if seg == 0 else vel + 2
                out.append(n(p, b * 4.0 + seg + 0.02, 1.9, v))
    return out


def gen_percs(style: str, nbars: int) -> list[dict]:
    out: list[dict] = []
    for b in range(nbars):
        base = b * 4.0
        last = b == nbars - 1
        if style == "post":
            # near-silence: a shaker felt more than heard, so the "ding" lands alone
            for i in range(8):
                out.append(n(P_SHAKER, base + i * 0.5, 0.08, 22))
            continue
        if style == "bridge":
            # 16ths on Perc Kling (metallic, reads as maracas over the held pad),
            # punctuated with Spoons on bars 4 and 8
            for i in range(16):
                out.append(n(P_KLING, base + i * 0.25, 0.08,
                             38 + b * 10 + (8 if i % 4 == 0 else 0)))
            if b in (3, 7):
                out.append(n(P_SPOONS, base + 2, 0.3, 56))
            continue
        if style == "intro":
            # le crash du debut de verse
            if last:
                out.append(n(P_CRASH, base + 3.5, 1.4, 70))
            continue
        for i in range(8):
            out.append(n(P_SHAKER, base + i * 0.5, 0.08, 50 if i % 2 == 0 else 38))
        out += [n(P_SHAKER2, base + 1, 0.3, 66), n(P_SHAKER2, base + 3, 0.3, 64)]
        if style in ("chorus", "double", "hook4"):
            out.append(n(P_STRIKE, base + 2.5, 0.2, 52))
        if b % 4 == 3 and style == "verse":
            for i in range(3):
                out.append(n(P_STRIKE, base + 2.5 + i * 0.25, 0.15, 46 + i * 8))
        # crashs sur la cymbale reelle (pad E2 = note 52)
        if style == "chorus" and b in (0, 4):
            out.append(n(P_CRASH, base + 0, 1.4, 76))
        if style == "double" and b == 0:
            out.append(n(P_CRASH, base + 0, 1.4, 76))
        if style == "outro" and last:
            out.append(n(P_CRASH, base + 3.5, 1.4, 66))
    return out


# one-shot FX on the FX Drift (track 7), scene-relative.
# The crash accents now live on the Percs track (real cymbal, pad E2 = note 52).
# FX keeps only the risers / reverse cymbals / the "ding".
FX_PLAN = {
    0:  [],
    2:  [],
    4:  [],
    5:  [(OH, 14.0, 3.8, 44)],                      # riser into the hook
    6:  [(OH, 15.0, 0.8, 40)],                      # reverse tail under the "eh"
    7:  [(P_STRIKE, 2.5, 0.2, 88), (OH, 2.6, 1.0, 46)],  # the "ding" on "Elle te voit"
    8:  [(OH, 24.0, 3.8, 50)],                       # reverse cymbal
    9:  [(OH, 27.5, 1.0, 42)],
    10: [],
    11: [(OH, 0.0, 3.4, 58)],                       # reverse cymbal longue
}


# ── build ─────────────────────────────────────────────────────────────────────
def log(msg: str) -> None:
    print(msg, flush=True)


def ensure_tracks() -> None:
    """Reach 7 MIDI + 1 audio.

    The Remote Script exposes no create_audio_track and no move_track, so the one
    audio track we keep is the one already in the set -- it stays at index 2.
    """
    info = must("get_session_info", {})
    count = int(info["track_count"])
    log(f"[tracks] start: {count} tracks")
    tracks = [must("get_track_info", {"track_index": i}) for i in range(count)]

    audio = [i for i, t in enumerate(tracks) if t.get("is_audio_track")]
    midi = [i for i, t in enumerate(tracks) if t.get("is_midi_track")]
    log(f"[tracks] midi={midi} audio={audio}")

    # keep one audio track, delete the rest (all empty)
    for i in reversed(audio[1:]):
        log(f"[tracks] deleting empty audio track {i} ({tracks[i].get('name')})")
        must("delete_track", {"track_index": i, "track_name": tracks[i].get("name", "")})

    for _ in range(7 - len(midi)):
        must("create_midi_track", {"index": -1})
        log("[tracks] created MIDI track")

    info = must("get_session_info", {})
    log(f"[tracks] after: {info['track_count']} tracks")


def ensure_scenes(count: int) -> None:
    """Report how many scene rows the grid has.

    The RS can create_scene but has no delete_scene, and set_scene_name is declared
    in the dispatch table while _set_scene_name does not exist -- so a re-run must
    never append rows and scene names have to be typed in Live. We only count the
    rows, with a throw-away clip on a MIDI track (create_clip fails on an audio
    track, which would report 0).
    """
    have = 0
    while have < 64:
        try:
            must("create_clip", {"track_index": 0, "clip_index": have, "length": 4.0})
            must("delete_session_clip", {"track_index": 0, "clip_index": have})
            have += 1
        except Exception:
            break
    log(f"[scenes] grid rows available: {have} "
        f"(scene naming is broken in the RS -> rename the 12 rows in Live)")


def main() -> None:
    log("=== Mon IA Lisa : build des 12 scenes ===")
    must("set_tempo", {"bpm": 105})
    must("set_signature", {"numerator": 4, "denominator": 4})
    must("set_groove_amount", {"amount": 0.0})  # swing is baked into the notes
    log("[session] 105 BPM, 4/4, groove amount 0")

    ensure_tracks()
    info = must("get_session_info", {})
    if int(info["track_count"]) != 8:
        log(f"[abort] expected 8 tracks, got {info['track_count']} -- fix the track list by hand")
        return

    for i, name in enumerate(TRACK_NAMES):
        must("set_track_name", {"track_index": i, "name": name})
    log(f"[tracks] renamed to {TRACK_NAMES}")

    # devices are cleared first: a re-run must not stack a second Drift on a track
    for idx in sorted(DEVICES):
        info_t = must("get_track_info", {"track_index": idx})
        for d in reversed(info_t.get("devices", [])):
            must("delete_device", {"track_index": idx, "device_index": d["index"]})
    for idx, chain in DEVICES.items():
        for uri, label in chain:
            must("load_instrument_or_effect", {"track_index": idx, "uri": uri}, timeout=180)
            log(f"[device] track {idx} <- {label}")

    # returns: A-Reverb and B-Delay already carried Reverb/Delay from David's earlier
    # work in this set. The RS cannot delete a device on a return track, so we only
    # load one if the return is empty -- never stack a second Reverb.
    rts = must("get_return_tracks", {}).get("return_tracks", [])
    for ri, uri in ((0, "query:AudioFx#Reverb"), (1, "query:AudioFx#Delay")):
        if ri < len(rts) and not rts[ri].get("devices"):
            must("load_browser_item_on_return_track", {"return_index": ri, "uri": uri})
            log(f"[device] return {ri} <- {uri.rsplit('#', 1)[-1]} (was empty)")
        else:
            have = ", ".join(d["name"] for d in rts[ri].get("devices", [])) if ri < len(rts) else "?"
            log(f"[device] return {ri} left as is: {have}")

    # clear the grid, including slots beyond the last scene (stale clips)
    cleared = 0
    for slot in range(16):
        for trk in range(8):
            try:
                send("delete_session_clip", {"track_index": trk, "clip_index": slot})
                cleared += 1
            except Exception:
                pass
    log(f"[clips] grid cleared ({cleared} slots)")

    ensure_scenes(len(SCENES))

    created = 0
    for slot, name, nbars, style, chords in SCENES:
        bars_beats = nbars * 4
        per_track = {
            0: gen_drums(style, nbars),
            1: gen_bass(style, chords),
            3: gen_ep(style, chords),
            4: gen_arp(style, chords),
            5: gen_pad(style, chords),
            6: gen_percs(style, nbars),
            7: [n(*e) for e in FX_PLAN.get(slot, [])],
        }
        for trk in sorted(per_track):
            # drums get a stronger humanization (played feel); the rest stay subtle
            vj, tj = (8, 0.012) if trk == 0 else (4, 0.008)
            notes = humanize(per_track[trk], seed=slot * 100 + trk, vj=vj, tj=tj)
            try:
                must("create_clip", {"track_index": trk, "clip_index": slot, "length": bars_beats})
                if notes:
                    must("add_notes_to_clip",
                         {"track_index": trk, "clip_index": slot, "notes": notes}, timeout=180)
                must("set_clip_name",
                     {"track_index": trk, "clip_index": slot, "name": f"{name} {nbars}M"})
                created += 1
            except Exception as e:
                log(f"[FAIL] slot {slot} track {trk}: {e}")
            time.sleep(0.04)
        log(f"[clip] {name} ({nbars} bars) "
            f"drums={len(per_track[0])} bass={len(per_track[1])} ep={len(per_track[3])} "
            f"arp={len(per_track[4])} pad={len(per_track[5])} percs={len(per_track[6])} "
            f"fx={len(per_track[7])}")

    log(f"=== done: {created} clips, 76 bars, 105 BPM ===")
    log("Next: verify get_clip_notes on the drums, the bass and the hook, then DO NOT save.")


if __name__ == "__main__":
    main()
