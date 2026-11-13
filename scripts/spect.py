"""Vue rapide d'une capture (ou de plusieurs) - lecture humaine.

Usage :
    python scripts/spect.py data/analyses/mon_fichier.wav [autre.wav ...]
    python scripts/spect.py --bands data/analyses/mon_fichier.wav
    python scripts/spect.py --csv data/analyses/mon_fichier.wav

Sans option : une ligne par fichier (centroide, HF, corps, RMS, crete).
Avec --bands : le profil par bande, pour voir OU ca pique.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spectrum import BAND_LABELS, coarse_class, profile  # noqa: E402


def fmt_summary(path):
    p = profile(path)
    return "%-32s %-8s centroid=%6.0f Hz  HF>4k=%5.1f%%  corps640-1280=%5.1f%%  rms=%.5f  peak=%.4f  crete=%.1f" % (
        os.path.basename(path),
        coarse_class(p["centroid_hz"]),
        p["centroid_hz"],
        p["hf4k_pct"],
        p["bands_pct"][4],
        p["rms"],
        p["peak"],
        p["crest"],
    )


def print_bands(paths):
    header = "%-32s" % "fichier"
    for label in BAND_LABELS:
        header += "%9s" % label
    print(header)
    for path in paths:
        p = profile(path)
        row = "%-32s" % os.path.basename(path)
        for value in p["bands_pct"]:
            row += "%9.1f" % value
        print(row)
    print("\nvaleurs en % de l'energie spectrale totale, par bande (Hz)")


def print_summary(paths):
    for path in paths:
        print(fmt_summary(path))


def main():
    parser = argparse.ArgumentParser(description="Mesure spectrale de captures WAV.")
    parser.add_argument("files", nargs="+", help="fichiers WAV a mesurer")
    parser.add_argument("--bands", action="store_true", help="profil par bande (voir ou ca pique)")
    args = parser.parse_args()

    if args.bands:
        print_bands(args.files)
    else:
        print_summary(args.files)


if __name__ == "__main__":
    main()
