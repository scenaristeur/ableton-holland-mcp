---
name: pieges-niveaux
description: Use when setting the gain of an arrangement audio clip, or when a dB value is passed to a parameter and nothing happens. Covers that clip gain is normalised 0-1 and not dB (0.4 is unity, 0.6 is about 8 dB), that track volume is 0-1 with 0.85 as unity, and the duplicate_clip_to_arrangement off-by-one trap. Trigger words : gain du clip, set_arrangement_clip_gain, volume en dB, clip audio, duplicate_clip_to_arrangement, destination_bar, off by one, décalage.
---

# Pièges : niveaux et positions

## ⚠️ Le gain d'un clip audio est normalisé 0-1, PAS des dB

```
set_arrangement_clip_gain(track_index, clip_index, gain=0.4)   → 0 dB
set_arrangement_clip_gain(track_index, clip_index, gain=0.6)   → environ +8 dB
set_arrangement_clip_gain(track_index, clip_index, gain=6.0)   → ERREUR
```

C'est l'inverse de l'intuition : **0.4 = unity, pas 0.4 dB.** Passer une valeur en dB fait
entrer Live en attente, et l'appel échoue.

Le volume de piste est sur la même échelle normalisée, avec **0.85 = 0 dB**. Voir `gain-staging`.

## ⚠️ `duplicate_clip_to_arrangement` est off by one

Le paramètre `destination_bar` est **off by one** : ce que je demande n'est pas ce que j'obtiens.

**La solution** : utiliser l'autre outil, qui travaille en temps et est exact :

```
duplicate_to_arrangement(track_index, clip_index, destination_time)   # en temps, exact, 0-based
```

`destination_time` est en **temps (beats)**, 0-based et exact. Barres : 1 barre = 4 temps en 4/4.

Je réserve `duplicate_clip_to_arrangement` au cas où je veux *volontairement* le décalage — ce qui
n'arrive jamais.

## Mémoriser le conversions

| Besoin | Valeur |
|---|---|
| 0 dB, clip audio | 0.4 |
| +8 dB, clip audio | 0.6 |
| 0 dB, volume de piste | 0.85 |
| 1 barre (4/4) | 4 temps |
| Position arrangement | 0-based |

Table de référence plus fine du gain de clip audio :

| Gain | dB |
|---|---|
| 0.4 | 0 dB |
| 0.506 | +4.25 dB |
| 0.6 | +10.0 dB |
| 0.65 | +10.0 dB |

## Vérifier après écriture

```
get_arrangement_clips(track_index)     positions réelles
get_arrangement_clip_envelope(...)     si j'ai posé une enveloppe
```

Si ce que je vois ne correspond pas à ce que j'ai demandé, **je ne réessaie pas au hasard** : je
relis l'état, et je corrige à partir de l'état réel. Voir `pieges-indexation`.
