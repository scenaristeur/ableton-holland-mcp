"""Rough staging pass (mix-en-6-etapes step 1): pans + baseline volumes.

Levels are small, reversible touches; fine-tuning comes after each instrument
is revisited. Bass (0.85) and kick level were set by ear with David.
"""
import sys
sys.path.insert(0, "scripts")
import prep_mona_ia as p

PANS = {
    0: 0.00,   # batterie
    1: 0.00,   # basse (fondation, centre)
    3: -0.30,  # EP leger a gauche
    4: 0.30,   # arp leger a droite
    5: 0.00,   # nappe (lit, centre)
    6: 0.20,   # percs subtil a droite
    7: 0.00,   # FX
}
VOL = {
    0: 0.85,   # batterie
    1: 0.85,   # basse (choisi par David)
    3: 0.80,   # EP
    4: 0.80,   # arp
    5: 0.55,   # nappe (lit, on la baisse)
    6: 0.70,   # percs
    7: 0.80,   # FX
}

for trk, pan in PANS.items():
    p.must("set_track_panning", {"track_index": trk, "panning": pan})
for trk, vol in VOL.items():
    p.must("set_track_volume", {"track_index": trk, "value": vol})

print("[staging] pans:", PANS)
print("[staging] volumes:", VOL)