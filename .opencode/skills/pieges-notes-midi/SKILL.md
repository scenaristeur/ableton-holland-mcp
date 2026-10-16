---
name: pieges-notes-midi
description: Use whenever adding, moving or writing MIDI notes into an Ableton clip. Covers the two traps that destroy work silently: the field is start_time and not start, and both add_notes_to_clip and set_arrangement_clip_notes are full replacements despite the name "add". Trigger words : add_notes_to_clip, set_arrangement_clip_notes, notes MIDI, écrire des notes, start_time, les notes disparaissent, clip vide, remplacer les notes.
---

# Pièges : notes MIDI

## ⚠️ Le champ est `start_time`, pas `start`

```
add_notes_to_clip(track_index, clip_index, [
  {"pitch": 36, "start_time": 0, "duration": 0.5, "velocity": 110}
])
```

Si j'écris `"start"`, **toutes les notes s'empilent à 0**. Le clip n'est pas vide, il est saturé
d'un accord. C'est le bug le plus silencieux du projet : rien ne signale l'erreur.

## ⚠️ « add » remplace tout

`add_notes_to_clip` et `set_arrangement_clip_notes` sont des **remplacements**, malgré le nom.

Un appel partiel **détruit** toutes les autres notes du clip. J'ajoute une basse à un clip de
batterie, j'efface la batterie.

**La règle** : je relis d'abord les notes existantes

```
get_clip_notes(track_index, clip_index)                 clip de session
get_arrangement_clip_notes(track_index, clip_index)    clip d'arrangement
```

puis j'envoie la **liste complète**, existantes + nouvelles, en un seul appel.

## Format d'une note

| Champ | Valeur |
|---|---|
| `pitch` | 0-127. **Ableton : C3 = 60** (60=C3, 64=E3, 69=A3, 71=B3) |
| `start_time` | en **temps (beats)** depuis le début du clip |
| `duration` | en temps. 1 temps = une double-croche en 4/4 |
| `velocity` | 0-127. **Dans les fiches j'écris 0-100**, voir `velocites-et-dynamique` |
| `mute` | optionnel |

## Positions

Le clip est indexé **0-based** par position, et la position dépend de l'appel
`get_arrangement_clips` ou de l'index de slot. Si le résultat ne correspond pas au clip visé, je
relis la liste avant d'écrire. Voir `pieges-indexation`.
