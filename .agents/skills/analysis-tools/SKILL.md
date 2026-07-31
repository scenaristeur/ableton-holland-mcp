---
name: analysis-tools
description: Outils d'analyse audio — capture, détection de tonalité, tempo, énergie, spectre, MFCC, chromagram. Utilisation pour le mix et la composition.
---

# Analyse Audio

## Capture

```python
capture_and_analyze(position_beats=24, duration_sec=10, output_name="couplet1")
```

Capture via VB-Cable, analyse avec librosa. Renvoie :
- **`wav_path`** — fichier WAV brut
- **`y_path`** — CSV de la forme d'onde
- **`energy_rms`** — énergie RMS (0.0-1.0, relatif)
- **`energy_peak`** — pic absolu (toujours 1.0 après normalisation)
- **`dynamic_range_db`** — plage dynamique en dB
- **`spectral_centroid_hz`** — centroid spectral (brillance)
- **`spectral_rolloff_hz`** — rolloff spectral (fréquence en dessous de laquelle est 85% de l'énergie)
- **`tempo_bpm`** — tempo estimé
- **`key`** + **`mode`** + **`key_confidence`** — tonalité détectée
- **`zero_crossing_rate`** — taux de passage par zéro (bruit vs tonal)
- **`tuning_offset_cents`** — désaccordage en cents

## Contraintes de capture

- Duration max conseillée : **20s** (la capture bloque le temps réel)
- **Ne pas lancer plusieurs captures en parallèle** — chaque capture interrompt la précédente (seek + playback)
- La première capture peut timeout (librosa JIT-compile numba ~5-15s)
- La capture ne fonctionne qu'en **Vue Arrangement** (pas Session)

## Analyse d'un fichier existant

```python
# Charger un fichier audio
load_tool(file_path="data/analyses/mon_fichier.wav") → { "y_path": "..." }

# Analyses individuelles
analyze_full_tool(y_path=...)   # tout-en-un
detect_key_tool(y_path=...)     # tonalité
tempo_tool(y_path=...)          # tempo
beat_track_tool(y_path=...)     # beats positions
chroma_cqt_tool(y_path=...)     # chromagram
mfcc_tool(y_path=...)           # MFCC
analyze_energy_tool(y_path=...) # énergie + dynamique
analyze_spectral_tool(y_path=...) # caractéristiques spectrales
analyze_tuning_tool(y_path=...)   # désaccordage
get_duration_tool(y_path=...)   # durée
```

## Interprétation des métriques

| Métrique | Faible | Équilibré | Élevé |
|---|---|---|---|
| energy_rms | < 0.05 | 0.10-0.20 | > 0.25 |
| dynamic_range_db | < 8 (écrasé) | 10-15 (sain) | > 20 (très dynamique) |
| spectral_centroid_hz | < 700 (sombre) | 700-900 (équilibré) | > 1000 (brillant/agressif) |
| spectral_rolloff_hz | < 1000 | 1200-2500 | > 3000 |
| zero_crossing_rate | < 0.02 (pur) | 0.02-0.06 | > 0.08 (bruité) |

## Mesure dBFS réelle (non normalisée)

L'analyse MCP normalise le signal (peak = 1.0). Pour mesurer les vrais dBFS :

```python
import numpy as np, soundfile as sf
audio, sr = sf.read("fichier.wav")
y = np.mean(audio, axis=1) if audio.ndim > 1 else audio
peak_dbfs = 20 * np.log10(np.max(np.abs(y)) + 1e-12)
rms_dbfs  = 20 * np.log10(np.sqrt(np.mean(y**2)) + 1e-12)
```

## Workflow de mix assisté par analyse

1. Capturer le full mix à une section représentative
2. Soloter chaque piste et capturer individuellement
3. Comparer les métriques :
   - Un instrument trop bas → augmenter volume ou ajouter Utility/Gain
   - Centroid trop bas → ajouter des harmoniques (Saturator)
   - Conflit spectral → EQ carving (voir skill mix-translation)
4. Itérer jusqu'à équilibre satisfaisant
