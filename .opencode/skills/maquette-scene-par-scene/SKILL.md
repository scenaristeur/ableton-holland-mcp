---
name: maquette-scene-par-scene
description: Use when starting a new song, a demo or a section in Ableton Live 12 Lite via MCP. Covers the scene-by-scene session-view loop (one section = one scene, validate each before the next), the mandatory sound-sculpt pass on every placed instrument before validating a scene, clip length in beats, the exact tool order, and the rule against building the whole track upfront. Trigger words : nouveau morceau, maquette, compose, arrange, une section, une scène, session view, fire_scene, sculpter, son brut, timbre, bas de gamme.
---

# Maquette scène par scène

**Le mode par défaut pour toute création.** Je ne construis jamais tout le morceau d'avance.

Une section = une scène. Je valide avec David scène par scène. **Je ne passe à l'arrangement que
quand toutes les scènes sont validées.**

## La boucle

1. **Je propose** la section, avec son rôle et ce que j'attends à l'oreille.
2. **Je crée** la scène : pour chaque piste, un `create_clip`, puis les notes, puis le nom.
3. **Je sculpte.** ⚠️ **Réflexe automatique, jamais sauté.** Pour **chaque instrument** que je viens
   de poser ou dont je viens d'écrire les notes, **et pour chaque device intégré** que j'ajoute
   (Saturator, Auto Filter, Reverb, Delay, Compressor, Utility…), je me pose la question « comment
   j'adapte ce son / ce device à la chanson ? » et je fais le passage de timbre avant de continuer.
   Un preset **ou un device laissé à ses valeurs par défaut** = « instru bas de gamme » garanti, et
   le rattraper plus tard coûte bien plus cher. Le détail : `sculpture-sonore`.
4. **Je présente** à David : rôle de chaque piste + nom du clip + plages de vélocité + **ce que j'ai
   sculpté**.
5. **J'attends.** Sa validation à l'oreille décide de la suite.

**Aucune scène ne se présente à David sans que chaque instrument ait eu son passage de sculpture.**
C'est une étape de production, pas un bonus de fin de projet.

## Longueurs : en temps, pas en mesures

`create_clip(track_index, clip_index, length)` prend une longueur **en temps (beats)**.
En 4/4 : 1 barre = 4, 2 barres = 8, 4 barres = 16, 8 barres = 32.

## Ordre des outils, dans l'ordre

```
1. load_instrument_or_effect(track_index, uri)        si la piste vient d'être créée
2. create_clip(track_index, clip_index, length)       pour chaque piste
3. add_notes_to_clip(track_index, clip_index, notes)  ⚠️ REMPLACE, voir skill pieges-notes-midi
4. ⚠️ SCULPTURE — pour CHAQUE instrument posé/écrit ET chaque device ajouté, non négociable :
     get_device_parameters(track_index, device_index)   → lire les paramètres exposés
     set_device_parameter(...)                           → adoucir, filtrer, espacer, régler le device
     (voir sculpture-sonore : c'est le geste qui distingue un preset d'un son de morceau,
      et un device laissé par défaut d'un device réglé pour la chanson)
5. set_clip_name(track_index, clip_index, name)
6. → présenter à David et attendre
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
