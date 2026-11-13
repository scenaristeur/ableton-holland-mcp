---
name: pieges-notes-midi
description: Use whenever adding, moving or writing MIDI notes into an Ableton clip. Covers the traps that silently corrupt clips: the field is start_time and not start, and add_notes_to_clip does NOT purge the clip (it only updates notes with the same pitch and start_time, so old notes survive). Trigger words : add_notes_to_clip, set_arrangement_clip_notes, notes MIDI, écrire des notes, start_time, les notes disparaissent, clip vide, remplacer les notes, recréer un clip.
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

## ⚠️ « add » ne purge PAS le clip (vérifié)

`add_notes_to_clip` **ne remplace que les notes qui ont le même couple `(pitch, start_time)`** :
pour celles-là, la durée et la vélocité sont mises à jour. **Toutes les autres notes du clip
survivent.**

Conséquence : réécrire une zone du clip en espérant effacer les notes de cette zone **échoue
silencieusement** — les anciennes notes restent là, et on se retrouve avec deux couches
superposées.

**Mesuré** : un clip de 178 notes, j'écris un sous-ensemble de 100 notes → le clip en contient
toujours 178. La description de l'outil MCP dit pourtant « REPLACES every existing note » : elle
est fausse, c'est le comportement mesuré qui fait foi.

⚠️ **Le `note_count` rendu par l'appel n'est pas le total du clip**, c'est le **nombre de notes
que je viens d'envoyer**. Mesuré le 23/10/2026 sur la piste 1-Batterie : j'ajoute 2 notes à un
clip de 704 → la réponse dit `note_count: 2`, et le clip en contient bien 705. Ne pas paniquer,
ne pas « restaurer » : **relire avec `get_clip_notes`** avant de conclure à une perte.

Il n'existe **aucune commande pour supprimer des notes**. Pour purger un clip :

```
delete_session_clip(track_index, clip_index)
create_clip(track_index, clip_index, length=<beats>)
set_clip_name(track_index, clip_index, "<nom>")
add_notes_to_clip(track_index, clip_index, <liste complète>)
```

Et **recréer le clip fait perdre son groove** (`get_clip_groove` avant, `set_clip_groove` après).

**La règle** : je relis d'abord les notes existantes

```
get_clip_notes(track_index, clip_index)                 clip de session
get_arrangement_clip_notes(track_index, clip_index)    clip d'arrangement
```

puis j'envoie la **liste complète**, existantes + nouvelles, en un seul appel.

## ⚠️ Petit `add_notes` plutôt que script de réécriture massive

La recette « delete → create → add » ci-dessus est un **dernier recours**, pas une méthode de
travail. Un bloc qui recalcule et renvoie 900-1 000 notes d'un coup **se fait couper en cours
d'exécution** — vécu sur « Danse tes illusions » : deux tentatives interrompues d'affilée, sans
écrire une seule note, et impossible de savoir si le clip avait été supprimé entre-temps.

Règles de travail :

- **Par défaut : `add_notes_to_clip` directement**, en petits paquets (une section, un pad, une
  mesure). Mesuré : 150-200 notes par appel passent sans problème, 880 ne passent pas.
- **Pour changer une vélocité ou une durée**, je renvoie la note avec le **même `pitch` et le même
  `start_time`** : `add_notes` met la note à jour sans toucher au reste du clip. C'est la façon
  propre de recadrer une dynamique de section sans reconstruire quoi que ce soit.
- La recette delete/create ne sert que si je dois **réellement supprimer** des notes (il n'existe
  aucun autre moyen).
- **Je ne réécris pas un clip « pour repartir propre »** : ce qui est déjà en place a été validé
  à l'oreille, et le refaire coûte une exécution.

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
