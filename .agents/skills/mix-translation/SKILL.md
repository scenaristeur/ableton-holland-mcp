---
name: mix-translation
description: Mix multi-support — techniques pour qu'un mix sonne bien sur grosses enceintes, téléphone, autoradio, Spotify/YouTube. Saturator basse, HPF, EQ carving, volume balancing, targets LUFS.
---

# Mix Translation Multi-Support

## Philosophie

Chaque élément doit être audible même sur petit haut-parleur (téléphone, autoradio). Cela passe par :
1. **Harmoniques** : saturer les basses pour créer des fréquences audibles sans subwoofer
2. **Midrange** : éviter les extrêmes — le médium = l'essentiel sur petit HP
3. **Écoute multi-support** : tester sur téléphone, autoradio, pas seulement au casque

## Règles définitives

1. **Saturator on bass (obligatoire)** — génère des harmoniques audibles sur petites enceintes (< 150 Hz invisibles sur téléphone)
   - Type: Medium Curve (3), Drive: 0.60-0.80, Dry/Wet: 1.0
2. **Compression drums** (glue) — Threshold: 0.30, Ratio: ~4:1, Attack: 0.10-0.15, Model: Peak, Makeup: On
3. **HPF 200 Hz** sur Keys, Pad, FX, guitare (tout ce qui n'a pas besoin de sub)
4. **Spectral centroid target** : 700-900 Hz (balanced). < 700 = muddy, > 1000 = harsh
5. **Master Limiter** : Input Gain modéré, Ceiling -1 dB, max -6 dB reduction
6. **Send reverb as glue** — 0.10-0.25 sur plusieurs pistes unifie le mix

## EQ Carving (prévention du masquage)

| Fréquence | Qui occupe | Qui doit être réduit |
|---|---|---|
| 50-100 Hz | Kick + Basse | Conflit : sidechain ou EQ complémentaire |
| 200-400 Hz | Basse + Keys | Keys/Pad : HPF à ~200 Hz |
| 1-4 kHz | Présence Lead | Keys/Pad : léger cut à 2 kHz |
| 5-8 kHz | Air/hats | Lead : légère atténuation |

## Volume Balancing

1. Solo chaque piste sur une section énergétique représentative
2. Capturer ~4s avec `capture_and_analyze`
3. Noter `energy_rms` de chaque piste
4. Ajuster les volumes pour RMS ~0.07-0.10 (lead), ~0.17-0.25 (full mix)
5. Full mix RMS cible : 0.15-0.25

## Plateformes cibles

| Plateforme | Loudness | Risques |
|---|---|---|
| Spotify | -14 LUFS | Normalisation coupe les extrêmes dynamiques |
| YouTube | -13 LUFS | Compression agressive, perte de détails |
| TikTok/Insta | ~-14 LUFS | Pas de basse, voix saturent si trop chaud |
| Phone speaker | N/A | Rien < 150 Hz → harmoniques basse obligatoires |
| Car stereo | variable | Bass-heavy → peut masquer le médium |

## Vérification

```python
capture_and_analyze(position_beats=0, duration_sec=20)
# Vérifier : energy_rms > 0.15, dynamic_range_db 10-15,
#           spectral_centroid_hz 700-900, spectral_rolloff_hz > 1200
```

Itérer jusqu'à satisfaction, puis exporter WAV 48kHz 24-bit → MP3 320k.
