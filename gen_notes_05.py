import json

# Chord definitions in Fmaj9 key (MIDI pitches)
# Fmaj9: F2(41), A2(45), C3(48), E3(52), G3(55)
chords = {
    "Fmaj9": [41, 45, 48, 52, 55],  # F A C E G
    "Em7b5": [40, 43, 47, 50],  # E G Bb D
    "A7_sharp9": [45, 49, 52, 55, 60],  # A C# E G C
    "Dm9": [38, 41, 45, 48, 52],  # D F A C E
    "Gm7": [43, 46, 50, 53],  # G Bb D F
    "C13": [36, 40, 43, 47, 50, 57],  # C E G Bb D A
    "F6_9": [41, 45, 48, 50, 55],  # F A C D G
    "Am7": [45, 48, 52, 55],  # A C E G
    "Bbmaj7": [46, 50, 53, 57],  # Bb D F A
    "Dm7": [38, 41, 45, 48],  # D F A C
    "C7": [36, 40, 43, 46],  # C E G Bb
    "G13": [43, 47, 50, 52, 57],  # G B D F A (simplified)
    "Cmaj9": [36, 40, 43, 47, 50],  # C E G B D
    "Bbmaj9": [46, 50, 53, 57, 60],  # Bb D F A C
    "A7b9": [45, 49, 52, 55, 58],  # A C# E G Bb
    "C7_sharp9": [36, 40, 43, 46, 51],  # C E G Bb D#
    "Fsharp_dim7": [42, 45, 48, 51],  # F# A C Eb
    "C7sus4": [36, 41, 43, 46],  # C F G Bb
}

sections = [
    {
        "name": "intro",
        "start": 0,
        "chords": ["Fmaj9", "Em7b5", "A7_sharp9", "Dm9", "Gm7", "C13", "Fmaj9", "F6_9"],
        "repeat": 1,
    },
    {
        "name": "A",
        "start": 32,
        "chords": ["Fmaj9", "Gm7", "Am7", "Bbmaj7", "Am7", "Dm7", "Gm7", "C13"],
        "repeat": 2,
    },
    {
        "name": "B",
        "start": 96,
        "chords": ["Dm9", "G13", "Cmaj9", "Fmaj9", "Bbmaj9", "Em7b5", "A7b9", "Dm9"],
        "repeat": 2,
    },
    {
        "name": "pont",
        "start": 160,
        "chords": [
            "Dm9",
            "G13",
            "Cmaj9",
            "C7_sharp9",
            "Fmaj9",
            "Fsharp_dim7",
            "Gm7",
            "C7sus4",
            "C7",
        ],
        "repeat": 1,
    },
    {
        "name": "solo",
        "start": 208,
        "chords": ["Fmaj9", "Gm7", "Am7", "Bbmaj7", "Am7", "Dm7", "Gm7", "C13"],
        "repeat": 3,
    },
    {
        "name": "B2",
        "start": 304,
        "chords": ["Dm9", "G13", "Cmaj9", "Fmaj9", "Bbmaj9", "Em7b5", "A7b9", "Dm9"],
        "repeat": 1,
    },
    {
        "name": "outro",
        "start": 336,
        "chords": ["Fmaj9", "Gm7", "C13", "Fmaj9"],
        "repeat": 1,
    },
]

# Wait, let me recalculate:
# Intro: 1-8 = 8 measures = 32 beats, start 0
# A: 9-28 = 20 measures = 80 beats ×2 = 160, start 32
# B: 29-48 = 20 measures ×2, start 192
# Pont: 49-60 = 12 measures, start 352
# Sax solo: 61-88 = 28 measures ×1 (already 28), start 400
# Actually let me recalculate more carefully

# 1 measure = 4 beats
# Intro: m1-8 = 8 measures = 32 beats, beat 0
# A: m9-28 = 20 measures = 80 beats, beat 32
# B: m29-48 = 20 measures = 80 beats, beat 112
# Pont: m49-60 = 12 measures = 48 beats, beat 192
# Sax solo: m61-88 = 28 measures = 112 beats, beat 240
# B': m89-104 = 16 measures = 64 beats, beat 352
# Outro: m105-112 = 8 measures = 32 beats, beat 416
# Total: 8+20+20+12+28+16+8 = 112 measures ✓

sections = [
    {
        "name": "intro",
        "start": 0,
        "chords": ["Fmaj9", "Em7b5", "A7_sharp9", "Dm9", "Gm7", "C13", "Fmaj9", "F6_9"],
        "repeat": 1,
    },
    {
        "name": "A",
        "start": 32,
        "chords": ["Fmaj9", "Gm7", "Am7", "Bbmaj7", "Am7", "Dm7", "Gm7", "C13"],
        "repeat": 2,
    },
    {
        "name": "B",
        "start": 112,
        "chords": ["Dm9", "G13", "Cmaj9", "Fmaj9", "Bbmaj9", "Em7b5", "A7b9", "Dm9"],
        "repeat": 2,
    },
    {
        "name": "pont",
        "start": 192,
        "chords": [
            "Dm9",
            "G13",
            "Cmaj9",
            "C7_sharp9",
            "Fmaj9",
            "Fsharp_dim7",
            "Gm7",
            "C7sus4",
            "C7",
        ],
        "repeat": 1,
    },
    {
        "name": "solo",
        "start": 240,
        "chords": ["Fmaj9", "Gm7", "Am7", "Bbmaj7", "Am7", "Dm7", "Gm7", "C13"],
        "repeat": 3,
    },
    {
        "name": "B2",
        "start": 352,
        "chords": ["Dm9", "G13", "Cmaj9", "Fmaj9", "Bbmaj9", "Em7b5", "A7b9", "Dm9"],
        "repeat": 1,
    },
    {
        "name": "outro",
        "start": 416,
        "chords": ["Fmaj9", "Gm7", "C13", "Fmaj9"],
        "repeat": 1,
    },
]
# Wait, solo section has 3 repeats of 8 chords = 24 measures = 96 beats
# 240 + 96 = 336, then B' starts at 336? But I had 352 above. Let me recalculate.
# Solo: m61-88 = 28 measures. 8-chord pattern repeated 3x = 24 measures, then need 4 more.
# Actually m61-88 = 28 measures. The pattern has 8 chords = 8 measures.
# 28 / 8 = 3.5 repeats. Hmm this doesn't divide evenly.
# Let me check the structure again: "Sax solo | 61-88 | Fmaj9 | Gm7 | Am7 | Bbmaj7 | Am7 | Dm7 | Gm7 | C13"
# That's 8 measures/chords. 61-88 is 28 measures. 28/8 = 3.5.
# Hmm, either 3 full repeats (24 measures) + 4 more, or 2 full repeats + something else.
# Let me just do 3 full repeats (24 measures = m61-84) and then the last 4 measures might be a turnaround.
# Actually let me re-read more carefully. "Sax solo | 61-88" with 8 chords. That's 28 measures of the same 8-bar progression. Let me do 3 repeats (24 measures) which leaves 4 measures. The last 4 of the solo could be the same pattern's last 4 chords: Am7 Dm7 Gm7 C13. Or I'll just do 3.5 repeats.
# For simplicity, let me do 3.5 repeats (28 measures = 3 full passes + first 4 chords).

sections = [
    {
        "name": "intro",
        "start": 0,
        "chords": ["Fmaj9", "Em7b5", "A7_sharp9", "Dm9", "Gm7", "C13", "Fmaj9", "F6_9"],
        "repeat": 1,
    },
    {
        "name": "A",
        "start": 32,
        "chords": ["Fmaj9", "Gm7", "Am7", "Bbmaj7", "Am7", "Dm7", "Gm7", "C13"],
        "repeat": 2,
    },
    {
        "name": "B",
        "start": 112,
        "chords": ["Dm9", "G13", "Cmaj9", "Fmaj9", "Bbmaj9", "Em7b5", "A7b9", "Dm9"],
        "repeat": 2,
    },
    {
        "name": "pont",
        "start": 192,
        "chords": [
            "Dm9",
            "G13",
            "Cmaj9",
            "C7_sharp9",
            "Fmaj9",
            "Fsharp_dim7",
            "Gm7",
            "C7sus4",
            "C7",
        ],
        "repeat": 1,
    },
    {
        "name": "solo",
        "start": 240,
        "chords": ["Fmaj9", "Gm7", "Am7", "Bbmaj7", "Am7", "Dm7", "Gm7", "C13"],
        "repeat": 3,
    },
    {
        "name": "solo_end",
        "start": 336,
        "chords": ["Fmaj9", "Gm7", "Am7", "Bbmaj7"],
        "repeat": 1,
    },  # last 4 of solo
    {
        "name": "B2",
        "start": 352,
        "chords": ["Dm9", "G13", "Cmaj9", "Fmaj9", "Bbmaj9", "Em7b5", "A7b9", "Dm9"],
        "repeat": 1,
    },
    {
        "name": "outro",
        "start": 416,
        "chords": ["Fmaj9", "Gm7", "C13", "Fmaj9"],
        "repeat": 1,
    },
]

# Piano - block chords (jazz voicings)
piano = []
for sec in sections:
    nc = len(sec["chords"])
    for rep in range(sec["repeat"]):
        for i, cn in enumerate(sec["chords"]):
            beat = sec["start"] + (rep * nc + i) * 4
            # Rhodes style: 4-note voicings, slightly rolled
            for p in chords[cn][:4]:  # Use first 4 notes for tighter voicings
                piano.append(
                    {
                        "pitch": p + 12,
                        "start_time": beat,
                        "duration": 3.5,
                        "velocity": 78,
                    }
                )

# Basse - walking jazz
basse_roots = {
    "Fmaj9": 41,
    "Em7b5": 40,
    "A7_sharp9": 45,
    "Dm9": 38,
    "Gm7": 43,
    "C13": 36,
    "F6_9": 41,
    "Am7": 45,
    "Bbmaj7": 46,
    "Dm7": 38,
    "G13": 43,
    "Cmaj9": 36,
    "Bbmaj9": 46,
    "A7b9": 45,
    "C7_sharp9": 36,
    "Fsharp_dim7": 42,
    "C7sus4": 36,
    "C7": 36,
}
# Fifth for walking pattern
basse_fifths = {
    "Fmaj9": 48,
    "Em7b5": 47,
    "A7_sharp9": 52,
    "Dm9": 45,
    "Gm7": 50,
    "C13": 43,
    "F6_9": 48,
    "Am7": 52,
    "Bbmaj7": 53,
    "Dm7": 45,
    "G13": 50,
    "Cmaj9": 43,
    "Bbmaj9": 53,
    "A7b9": 52,
    "C7_sharp9": 43,
    "Fsharp_dim7": 49,
    "C7sus4": 43,
    "C7": 43,
}
basse = []
for sec in sections:
    nc = len(sec["chords"])
    for rep in range(sec["repeat"]):
        for i, cn in enumerate(sec["chords"]):
            beat = sec["start"] + (rep * nc + i) * 4
            root = basse_roots[cn]
            fifth = basse_fifths[cn]
            # Walking pattern: root(1), fifth(3), with chromatic passing notes
            basse.append(
                {"pitch": root, "start_time": beat, "duration": 1.5, "velocity": 88}
            )
            basse.append(
                {
                    "pitch": root + 2,
                    "start_time": beat + 1,
                    "duration": 0.8,
                    "velocity": 82,
                }
            )
            basse.append(
                {
                    "pitch": fifth,
                    "start_time": beat + 2,
                    "duration": 1.5,
                    "velocity": 85,
                }
            )
            basse.append(
                {
                    "pitch": root + 1,
                    "start_time": beat + 3,
                    "duration": 0.8,
                    "velocity": 80,
                }
            )

# Nappes - sustained 2-note pads
pad_v = {
    "Fmaj9": [53, 57],
    "Em7b5": [52, 55],
    "A7_sharp9": [57, 60],
    "Dm9": [50, 54],
    "Gm7": [55, 58],
    "C13": [48, 52],
    "F6_9": [53, 57],
    "Am7": [57, 60],
    "Bbmaj7": [58, 62],
    "Dm7": [50, 53],
    "G13": [55, 59],
    "Cmaj9": [48, 52],
    "Bbmaj9": [58, 62],
    "A7b9": [57, 60],
    "C7_sharp9": [48, 52],
    "Fsharp_dim7": [54, 57],
    "C7sus4": [48, 53],
    "C7": [48, 52],
}
nappes = []
for sec in sections:
    nc = len(sec["chords"])
    for rep in range(sec["repeat"]):
        for i, cn in enumerate(sec["chords"]):
            beat = sec["start"] + (rep * nc + i) * 4
            for p in pad_v[cn]:
                nappes.append(
                    {"pitch": p, "start_time": beat, "duration": 3.8, "velocity": 62}
                )

# Guitare - jazz comping chords (mid-range, tight voicings)
guitar_v = {
    "Fmaj9": [60, 64, 67],
    "Em7b5": [59, 62, 66],
    "A7_sharp9": [61, 64, 67],
    "Dm9": [57, 60, 64],
    "Gm7": [58, 62, 65],
    "C13": [57, 60, 64],
    "F6_9": [60, 62, 67],
    "Am7": [60, 64, 67],
    "Bbmaj7": [58, 62, 65],
    "Dm7": [57, 60, 64],
    "G13": [59, 62, 66],
    "Cmaj9": [57, 60, 64],
    "Bbmaj9": [58, 62, 65],
    "A7b9": [60, 64, 67],
    "C7_sharp9": [57, 60, 63],
    "Fsharp_dim7": [57, 60, 63],
    "C7sus4": [57, 60, 65],
    "C7": [57, 60, 63],
}
guitare = []
for sec in sections:
    nc = len(sec["chords"])
    for rep in range(sec["repeat"]):
        for i, cn in enumerate(sec["chords"]):
            beat = sec["start"] + (rep * nc + i) * 4
            for p in guitar_v[cn]:
                guitare.append(
                    {"pitch": p, "start_time": beat, "duration": 3.5, "velocity": 72}
                )

# Sax - melody line (jazz-infused)
sax_melody = {
    "intro": [
        (0, 72, 2, 85),
        (2, 71, 1, 82),
        (3, 72, 1, 82),
        (4, 74, 1.5, 85),
        (5.5, 72, 0.5, 80),
        (6, 71, 1, 82),
        (7, 72, 1, 82),
        (8, 74, 2, 85),
        (10, 76, 1, 82),
        (11, 74, 1, 82),
        (12, 72, 2, 85),
        (14, 71, 1, 82),
        (15, 69, 1, 82),
        (16, 67, 4, 85),
    ],
    "A": [
        (0, 72, 1, 85),
        (1, 74, 1, 82),
        (2, 76, 2, 88),
        (4, 77, 2, 85),
        (6, 76, 1, 82),
        (7, 74, 1, 82),
        (8, 72, 1.5, 85),
        (9.5, 74, 0.5, 80),
        (10, 76, 2, 85),
        (12, 77, 2, 88),
        (14, 76, 1, 85),
        (15, 74, 1, 85),
        (16, 72, 4, 82),
    ],
    "B": [
        (0, 79, 2, 88),
        (2, 77, 1, 85),
        (3, 76, 1, 85),
        (4, 74, 2, 88),
        (6, 72, 1, 85),
        (7, 74, 1, 85),
        (8, 76, 2, 88),
        (10, 77, 1, 85),
        (11, 76, 1, 85),
        (12, 74, 2, 88),
        (14, 72, 1, 85),
        (15, 71, 1, 85),
        (16, 69, 4, 85),
    ],
    "pont": [
        (0, 69, 1, 85),
        (1, 71, 1, 85),
        (2, 72, 2, 88),
        (4, 74, 1.5, 85),
        (5.5, 76, 0.5, 82),
        (6, 77, 2, 88),
        (8, 79, 2, 88),
        (10, 77, 1, 85),
        (11, 76, 1, 85),
        (12, 74, 2, 88),
        (14, 72, 1, 85),
        (15, 74, 1, 85),
        (16, 76, 4, 88),
    ],
    "solo": [
        (0, 77, 1, 85),
        (1, 76, 1, 85),
        (2, 74, 1.5, 88),
        (3.5, 72, 0.5, 82),
        (4, 71, 1, 85),
        (5, 72, 1, 85),
        (6, 74, 1.5, 88),
        (7.5, 76, 0.5, 82),
        (8, 77, 2, 88),
        (10, 79, 1, 85),
        (11, 77, 1, 85),
        (12, 76, 2, 88),
        (14, 74, 1, 85),
        (15, 72, 1, 85),
        (16, 71, 4, 85),
    ],
    "B2": [
        (0, 79, 2, 88),
        (2, 77, 1, 85),
        (3, 76, 1, 85),
        (4, 74, 2, 88),
        (6, 72, 1, 85),
        (7, 74, 1, 85),
        (8, 76, 2, 88),
        (10, 77, 1, 85),
        (11, 76, 1, 85),
        (12, 74, 2, 88),
        (14, 72, 1, 85),
        (15, 71, 1, 85),
        (16, 69, 4, 85),
    ],
    "outro": [
        (0, 72, 2, 85),
        (2, 71, 1, 82),
        (3, 69, 1, 82),
        (4, 67, 2, 85),
        (6, 69, 1, 82),
        (7, 71, 1, 82),
        (8, 72, 2, 85),
        (10, 71, 1, 82),
        (11, 69, 1, 82),
        (12, 67, 4, 85),
    ],
}

sec_starts = {
    "intro": 0,
    "A": 32,
    "B": 112,
    "pont": 192,
    "solo": 240,
    "B2": 352,
    "outro": 416,
}

sax = []
for sec_name, mel in sax_melody.items():
    start = sec_starts[sec_name]
    for offset, pitch, dur, vel in mel:
        sax.append(
            {
                "pitch": pitch,
                "start_time": start + offset,
                "duration": dur,
                "velocity": vel,
            }
        )

data = {
    "piano": piano,
    "basse": basse,
    "nappes": nappes,
    "guitare": guitare,
    "sax": sax,
}
with open("notes_05.json", "w") as f:
    json.dump(data, f, indent=2)

print(f"piano: {len(piano)} notes")
print(f"basse: {len(basse)} notes")
print(f"nappes: {len(nappes)} notes")
print(f"guitare: {len(guitare)} notes")
print(f"sax: {len(sax)} notes")
