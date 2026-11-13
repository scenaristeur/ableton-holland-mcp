"""Mesure spectrale d'un WAV de capture - brique commune.

Pourquoi mesurer les fichiers et pas le tool d'analyse :
le tool normalise (il renvoie energy_peak = 1.0 quel que soit le niveau reel),
donc ses RMS et peak ne sont PAS comparables d'une capture a l'autre.
On lit donc les WAV ecrits dans data/analyses/.

Toutes les energies de bandes sont en % de l'energie spectrale totale.
"""

import numpy as np
import soundfile as sf

# Bandes de lecture (Hz). Le decoupage suit les defauts qu'on sait nommer a l'oreille :
#   > 10 kHz        -> "ca siffle / sale"
#   2,6-5,1 kHz     -> "ca pique / trop brillant"
#   1,3-2,6 kHz     -> "criard / agressif"
#   640-1280 Hz     -> "le corps"
BANDS = [
    (0, 80), (80, 160), (160, 320), (320, 640), (640, 1280),
    (1280, 2560), (2560, 5120), (5120, 10240), (10240, 20000),
]

BAND_LABELS = [
    "00-80", "80-160", "160-320", "320-640", "640-1280",
    "1280-2560", "2560-5120", "5120-10240", "10240-20000",
]


def read_mono(path):
    """Lit un WAV et le ramene en mono si besoin."""
    y, sr = sf.read(path, always_2d=False)
    if getattr(y, "ndim", 1) > 1:
        y = y.mean(axis=1)
    return y, sr


def profile(path):
    """Profil spectral complet d'un fichier de capture."""
    y, sr = read_mono(path)
    windowed = y * np.hanning(len(y))
    x = np.abs(np.fft.rfft(windowed))
    f = np.fft.rfftfreq(len(y), 1.0 / sr)
    total = float(x.sum()) or 1.0

    centroid = float((f * x).sum() / total)
    hf4k = float(x[f >= 4000].sum() / total) * 100.0
    mid = float(x[(f >= 300) & (f < 1200)].sum() / total) * 100.0
    bands = [
        float(x[(f >= lo) & (f < hi)].sum() / total) * 100.0
        for lo, hi in BANDS
    ]
    rms = float(np.sqrt(np.mean(y ** 2)))
    peak = float(np.max(np.abs(y)))
    return {
        "centroid_hz": centroid,
        "hf4k_pct": hf4k,
        "mid_300_1200_pct": mid,
        "bands_pct": bands,
        "rms": rms,
        "peak": peak,
        "crest": (peak / rms) if rms > 0 else 0.0,
        "duration_s": (len(y) / sr) if sr else 0.0,
    }


def coarse_class(centroid_hz):
    """Classe grossiere. Le centroide bouge de +/-10 % entre deux captures :
    on ne promet pas des hertz, on range en trois familles."""
    if centroid_hz < 1500:
        return "sombre"
    if centroid_hz < 3000:
        return "medium"
    return "brillant"
