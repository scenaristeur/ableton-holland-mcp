---
name: maquette-scene-par-scene
description: Use when starting a new song, a demo or a section in Ableton Live 12 Lite via MCP. Covers the scene-by-scene session-view loop (one section = one scene, validate each before the next), clip length in beats, the exact tool order, and the rule against building the whole track upfront. Trigger words : nouveau morceau, maquette, compose, arrange, une section, une scène, session view, fire_scene.
---

# Maquette scène par scène

**Le mode par défaut pour toute création.** Je ne construis jamais tout le morceau d'avance.

Une section = une scène. Je valide avec David scène par scène. **Je ne passe à l'arrangement que
quand toutes les scènes sont validées.**

## La boucle

1. **Je propose** la section, avec son rôle et ce que j'attends à l'oreille.
2. **Je crée** la scène : pour chaque piste, un `create_clip`, puis les notes, puis le nom.
3. **Je présente** à David : rôle de chaque piste + nom du clip + plages de vélocité.
4. **J'attends.** Sa validation à l'oreille décide de la suite.

## Longueurs : en temps, pas en mesures

`create_clip(track_index, clip_index, length)` prend une longueur **en temps (beats)**.
En 4/4 : 1 barre = 4, 2 barres = 8, 4 barres = 16, 8 barres = 32.

## Ordre des outils, dans l'ordre

```
1. create_clip(track_index, clip_index, length)      pour chaque piste
2. add_notes_to_clip(track_index, clip_index, notes) ⚠️ REMPLACE, voir skill pieges-notes-midi
3. set_clip_name(track_index, clip_index, name)
4. → présenter à David et attendre
```

`fire_scene(index)` pour déclencher. **`index` 0-based** : la scène 1 = index 0.

## Propreté de la grille

Je supprime les clips de session résiduels avant de commencer une nouvelle section, sinon la
grille devient illisible et je ne sais plus ce qui est validé.

## Règle absolue

**Je n'invente jamais un groove ou une mélodie « à l'aveugle »** pour gagner du temps. Si je n'ai
pas de source vivante (un groove existant, un motif du morceau, une intention de David), **je
demande**. Un contre-temps inventé est pire qu'une section vide : il structure tout le reste du
morceau autour d'une erreur.

Voir aussi : `velocites-et-dynamique` (les vélocités ne sont jamais le défaut), `conventions-nommage`.
