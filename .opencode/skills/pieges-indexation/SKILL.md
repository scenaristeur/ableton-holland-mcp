---
name: pieges-indexation
description: Use when passing track_index, clip_index, device_index, return_index or scene_index, and whenever a tool acts on the wrong thing. Covers that all API indices are 0-based while conversation with David is 1-based, that a track named "1-Batterie" is index 0, and that clip indices are positional within their own list. Trigger words : index, 0-based, track_index, clip_index, device_index, scene, mauvais piste, mauvais clip, décalage d'index.
---

# Pièges : indexation

## Les outils sont 0-based, la conversation est 1-based

C'est la source de confusion la plus fréquente. Quand David dit « la piste 5 », il parle de
**`track_index 4`**.

Et le nommage porte l'index tel quel : une piste nommée `1-Batterie+Percs` est l'**index 0**, parce
que le nom a été choisi pour l'affichage humain, pas pour l'API. Voir `conventions-nommage`.

## Chaque paramètre est numéroté à part

| Paramètre | Compte sur |
|---|---|
| `track_index` | les pistes de session, **après** Master et avant les returns |
| `device_index` | les devices **de cette piste**, 0-based |
| `clip_index` (session) | l'**index de slot** dans la piste |
| `clip_index` (arrangement) | la **position dans la liste** renvoyée par `get_arrangement_clips` |
| `return_index` | les return tracks |
| `scene_index` | les scènes, 0-based : scène 1 = index 0 |

Le `clip_index` est le piège : **ce n'est pas le même numéro** en session et en arrangement. En
arrangement c'est une position, pas un slot.

## La règle qui évite les erreurs

**Je liste avant d'écrire.** Le coût d'un `get_track_info` ou `get_arrangement_clips` est nul ; le
coût d'un mauvais-indexation est un clip modifié ou détruit.

```
get_session_info()               nombre de pistes, tempo, lecture
get_track_info(track_index)      devices, slots, volume, pan
get_arrangement_clips(track_index)
```

## Après une écriture, je relis

Si l'outil ne renvoie pas le résultat attendu, je **relis l'état** au lieu de réessayer avec des
valeurs devinées. Les indices se corrigent, les données, non.
