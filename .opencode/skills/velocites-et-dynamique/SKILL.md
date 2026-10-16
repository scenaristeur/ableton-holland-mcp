---
name: velocites-et-dynamique
description: Use when writing or reviewing MIDI note velocities in Ableton clips, or when a groove sounds flat, robotic or lifeless. Covers the velocity range per instrument role (kick, snare, hat, bass, pads, arp, lead, voice) and humanisation (vary velocities and micro-timing, never rewrite the density). Trigger words : vélocité, velocity, son plat, robotique, mort, dynamique, humaniser, groove plat.
---

# Vélocités et dynamique

**Chaque note a une vélocité explicite.** Le défaut 100 rend tout le groove plat. Je varie toujours.

## Plages par rôle

| Rôle | Plage |
|---|---|
| Kick | 110-127 |
| Snare | 95-120 |
| Charley | 60-90 (70-90 sur les temps forts) |
| Crash | 110-127 |
| Basse — fondamentales | 85-100 |
| Basse — passages | 65-80 |
| Piano / nappes | 65-80 (accents 85-100) |
| Guitare arpèges | 75-95 |
| Mélodie phrasée | 80-110 |
| Voix — phrases accentuées | 95-110 |
| Voix — notes tenues | 80-90 |
| Voix — passages | 75-85 |

## Humaniser : varier, jamais réécrire

Un motif répété 4 fois doit avoir des vélocités **légèrement différentes** à chaque répétition.

Ce que je varie :
- la vélocité (± 5 à 15 selon le rôle),
- de **légers décalages de timing** (quelques millièmes de temps).

Ce que **je ne change jamais** : **la densité**. Retirer des notes, ajouter des notes, déplacer un
contretemps, « respirer » un pattern — tout ça détruit la groove de David. Un kick clairsemé ou un
crescendo inventé produit un faux contre-temps. Je réhumanise un pattern **existant**, je ne le
réécris pas.

## Ce qui rend un groove vivant

- **Le contraste** entre temps forts et temps faibles, plus que le niveau absolu.
- **Les variations de vélocité entre les deux drums** : un kick et un snare sur le même temps ne
  partagent pas la même vélocité.
- **La tenue** : une basse tenue à 85-100 se place différemment d'une basse jouée à 65-80.
- **La répétition imparfaite** : c'est le signal que c'est humain, pas une erreur à corriger.

## Attention aux fichiers

`add_notes_to_clip` et `set_arrangement_clip_notes` **remplacent** toutes les notes du clip, malgré
le nom « add ». Un appel partiel **détruit** les autres. Toujours envoyer la liste complète.
Voir `pieges-notes-midi`.
