---
name: david-prefs
description: Profil utilisateur David — tessiture baryton/tenor, préférences de production, FX chains natives par vibe (pop/rock/reggae), kits batterie recommandés.
---

# David — Profil Utilisateur

## Voix

- **Tessiture** : E3-B3 (MIDI 64-71), baryton léger / tenor comfortable
- **Tonalité référence** : Do#m (préféré), Mim (secondaire)
- **Style chant** : parlé-chanté, nonchalant & cynique (Gainsbourg, Desproges)
- **Langue** : français sauf demande explicite
- **Analyse référence** (spectral centroid : 645 Hz, warm/low timbre, DR 81.2 dB)

## Contraintes de production

- **Max 8 tracks** (Live Lite), max 16 scenes
- **D'abord les plugins natifs Ableton** (Analog, Drift, Wavetable, Electric) pour structurer, puis Surge XT via OSC si besoin
- **Drumkit pré-configuré** plutôt que construire un Drum Rack from scratch
- Structure courte préférée (~1:30-2:00)
- Style : organic pop / rock / reggae selon le profil

## Kits batterie par vibe

| Vibe | Kit recommandé |
|---|---|
| Organic / warm | `Selector Kit Warm.adg` |
| General purpose | `Gen Purpose Kit.adg` |
| Dry / natural | `Dry Session Kit.adg` |
| Lo-fi | `Toy LoFi Kit.adg` |
| Hybrid studio | `Recording Hybrid Kit - Damped Snare.adg` |

## FX Chains natives

### Default (Organic Pop)

| Piste | Chaîne |
|---|---|
| Drums | Drum Buss → Compressor → Reverb (send) |
| Bass | Amp → Compressor → Saturator |
| Piano/Keys | Reverb → Chorus → Compressor |
| Pad | Reverb → Auto Filter → Delay |
| Lead | Delay → Reverb → Auto Filter |
| Vocals | EQ Eight → Compressor → Reverb → Delay |
| Percs | Reverb (send) → Saturator |
| FX | Reverb → Delay → Grain Delay → Auto Filter |

### Rock Profile

| Piste | Chaîne |
|---|---|
| Drums | Drum Buss → Compressor → Saturator |
| Guitar | Amp → Saturator → Compressor |
| Bass | Amp → Saturator → Compressor |

### Reggae Profile

| Piste | Chaîne |
|---|---|
| Drums | Drum Buss → Reverb (spring) → Delay |
| Bass | Amp → Saturator → Compressor |
| Guitar/Keys | Chorus → Reverb → Delay |
| Vocals | EQ Eight → Compressor → Reverb → Delay |

## Héritage

Les profils `rock.md` et `reggae.md` héritent de `default.md` et ne surchargent que ce qui diffère.
