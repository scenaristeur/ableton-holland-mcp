---
name: scene-workflow
description: Workflow de création de maquette MIDI en Vue Session — scène par scène, vélocités, validation utilisateur, arrangement.
---

# Workflow Scène par Scène

## Principe

Travailler **exclusivement en Vue Session**, scène par scène. Valider chaque scène avec l'utilisateur avant de passer à la suivante. Ne jamais créer tous les clips d'un morceau d'avance.

## Étapes

1. **Découper le morceau en sections** : Intro, Couplet, Pré-Refrain, Refrain, Pont, Refrain Final, Outro... Une section = une scène.
2. **Étendre les slots si besoin** : 8 slots par défaut → `create_scene(index=-1)` pour ajouter jusqu'à 16.
3. Pour **chaque scène**, dans l'ordre :
   - Créer le clip de chaque piste instrument (`create_clip(track, slot, length)`) — **length en beats** (1 bar 4/4 = 4 beats)
   - Remplir les notes (`add_notes_to_clip`) — **toujours inclure `velocity`** (0-127)
   - Nommer les clips (`set_clip_name`)
4. **Présenter la scène** à l'utilisateur (description, nom des clips, plages de vélocité) et **attendre validation**.
5. Passer à l'arrangement seulement quand toutes les scènes sont validées.

## Règles de vélocité (CONSTRAINT)

Chaque note doit avoir un champ `velocity`. Ne jamais utiliser la valeur par défaut (100 = groove plat). Toujours varier comme un jeu réel.

| Instrument | Vélocités recommandées |
|---|---|
| Kick | 110-127 |
| Snare | 95-120 |
| Charley/HH | 60-90 (croches), 70-90 (temps forts) |
| Crash | 110-127 |
| Basse (fondamentales) | 85-100 |
| Basse (passages) | 65-80 |
| Piano (nappes) | 65-80 |
| Piano (accents) | 85-100 |
| Guitare (arpèges) | 75-95 |
| Mélodie (phrasé) | 80-110 |

Même motif répété 4× : vélocités légèrement différentes à chaque répétition.

## Passage à l'arrangement

Quand toutes les scènes sont validées : `duplicate_to_arrangement(track, clip, destination_bar)` ou l'outil `duplicate_clip_to_arrangement`. Les sections musicalement identiques peuvent réutiliser le même contenu, mais la mélodie peut varier (phrases A/B).

Supprimer les clips de session inutilisés avec `delete_session_clip` pour garder une grille propre.
