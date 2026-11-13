"""Mesure la plage de fréquences d'une voix (ou d'un instrument) sur des WAV capturés.

Usage :
    .venv\\Scripts\\python.exe scripts\\analyse_plage_voix.py data\\analyses\\voix_solo_a.wav [...]

Lit le WAV lui-même (pas les chiffres renvoyés par capture_and_analyze).
Donne : fondamentale (p10 / médiane / p90), en Hz et en note,
et la répartition de l'énergie (5 % / 50 % / 95 %).
"""
import sys
import wave

import numpy as np

NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def midi_name(m):
    # Convention Ableton : C3 = 60
    m = int(round(m))
    return f"{NAMES[m % 12]}{m // 12 - 2}"


def load(path):
    w = wave.open(path, "rb")
    sr = w.getframerate()
    ch = w.getnchannels()
    d = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0
    if ch > 1:
        d = d.reshape(-1, ch).mean(axis=1)
    return d, sr


def f0_autocorr(frame, sr, fmin=75.0, fmax=450.0):
    frame = frame - frame.mean()
    n = len(frame)
    ac = np.correlate(frame, frame, mode="full")[n - 1:]
    lo = int(sr / fmax)
    hi = min(int(sr / fmin), n - 1)
    if hi <= lo or ac[0] <= 0:
        return None, 0.0
    k = np.argmax(ac[lo:hi]) + lo
    return sr / k, ac[k] / ac[0]


def analyse(path):
    x, sr = load(path)
    hop = int(0.05 * sr)
    win = int(0.08 * sr)
    starts = list(range(0, len(x) - win, hop))
    rms = np.array([np.sqrt((x[s:s + win] ** 2).mean()) for s in starts])
    if rms.max() < 1e-4:
        return {"file": path, "erreur": "silence : le WAV est muet, refaire la capture"}
    voiced = np.where(rms > max(rms.max() * 0.25, 1e-4))[0]

    f0s = []
    for i in voiced:
        f, clarity = f0_autocorr(x[starts[i]:starts[i] + win], sr)
        if f is not None and clarity > 0.6:
            f0s.append(f)

    nfft = 4096
    spec = np.zeros(nfft // 2 + 1)
    for i in voiced:
        fr = x[starts[i]:starts[i] + win]
        spec += np.abs(np.fft.rfft(fr * np.hanning(len(fr)), n=nfft)) ** 2
    freqs = np.fft.rfftfreq(nfft, 1 / sr)
    cum = np.cumsum(spec) / spec.sum()

    out = {"file": path, "trames_voisees": len(voiced), "trames_f0": len(f0s)}
    if f0s:
        f0s = np.array(f0s)
        m = 69 + 12 * np.log2(f0s / 440.0)
        for p in (10, 50, 90):
            out[f"f0_p{p}_hz"] = round(float(np.percentile(f0s, p)), 1)
            out[f"note_p{p}"] = midi_name(np.percentile(m, p))
    out["energie_5_50_95_hz"] = [round(float(freqs[np.searchsorted(cum, q)])) for q in (0.05, 0.5, 0.95)]
    return out


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(analyse(p))
