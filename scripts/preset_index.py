"""Alimente l'index des presets : preset_index/preset_index.csv

Usage :
    python scripts/preset_index.py --famille "Guitar & Plucked" --role pluck \
        --phrase pique --fader 0.85 data/analyses/IDX_Soft_Attention.wav ...

Le nom du preset est deduit du nom de fichier : IDX_Soft_Attention.wav
  -> prefixe IDX_ retire, underscores -> espaces  -> "Soft Attention".
Un preset = une ligne. L'outil AJOUTE les lignes a la suite du CSV ; il ne
remplace pas et ne dedoublonne pas (c'est voulu : une remesure est une donnee).

Le champ --phrase est capital : sans phrase de test figee, l'index est faux.
Phrases conventionnelles : "pique" (arpège court, percussif), "tenu" (accord
tenu, soutenu). Une mesure hors protocole se marque explicitement, ex.
"clip-morceau-v0".
"""

import argparse
import csv
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spectrum import BAND_LABELS, coarse_class, profile  # noqa: E402

CSV_PATH = os.path.join("preset_index", "preset_index.csv")

COLUMNS = (
    ["date", "famille", "role", "phrase", "fader", "preset", "classe", "centroid_hz",
     "hf4k_pct", "mid_300_1200_pct"]
    + ["b_" + label for label in BAND_LABELS]
    + ["rms", "peak", "crete", "fichier"]
)


def preset_name(path, prefix):
    name = os.path.splitext(os.path.basename(path))[0]
    if prefix and name.startswith(prefix):
        name = name[len(prefix):]
    return name.replace("_", " ").strip()


def build_row(path, args):
    p = profile(path)
    row = {
        "date": datetime.date.today().isoformat(),
        "famille": args.famille,
        "role": args.role,
        "phrase": args.phrase,
        "fader": args.fader,
        "preset": preset_name(path, args.prefix),
        "classe": coarse_class(p["centroid_hz"]),
        "centroid_hz": "%.0f" % p["centroid_hz"],
        "hf4k_pct": "%.1f" % p["hf4k_pct"],
        "mid_300_1200_pct": "%.1f" % p["mid_300_1200_pct"],
        "rms": "%.5f" % p["rms"],
        "peak": "%.4f" % p["peak"],
        "crete": "%.1f" % p["crest"],
        "fichier": os.path.basename(path),
    }
    for label, value in zip(BAND_LABELS, p["bands_pct"]):
        row["b_" + label] = "%.1f" % value
    return row


def main():
    parser = argparse.ArgumentParser(description="Ajoute des mesures de presets a l'index.")
    parser.add_argument("files", nargs="+", help="WAV de capture, un par preset")
    parser.add_argument("--famille", required=True, help="ex. \"Guitar & Plucked\"")
    parser.add_argument("--role", required=True, help="ex. pluck")
    parser.add_argument("--phrase", required=True, help="ex. pique / tenu / clip-morceau-v0")
    parser.add_argument("--fader", default="", help="fader de la piste pendant la mesure")
    parser.add_argument("--prefix", default="IDX_", help="prefixe de fichier a retirer")
    parser.add_argument("--dry-run", action="store_true", help="affiche sans ecrire")
    args = parser.parse_args()

    rows = [build_row(path, args) for path in args.files]

    for row in rows:
        print("%-28s %-8s centroid=%6s Hz  HF>4k=%5s%%  corps=%5s%%  rms=%s" % (
            row["preset"], row["classe"], row["centroid_hz"],
            row["hf4k_pct"], row["b_640-1280"], row["rms"]))

    if args.dry_run:
        print("\n--dry-run : rien n'a ete ecrit.")
        return

    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    new_file = not os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        if new_file:
            writer.writeheader()
        writer.writerows(rows)
    print("\n%d ligne(s) ajoutee(s) a %s" % (len(rows), CSV_PATH))


if __name__ == "__main__":
    main()
