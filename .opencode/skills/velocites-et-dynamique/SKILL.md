---
name: velocites-et-dynamique
description: Use when writing or reviewing MIDI note velocities in Ableton clips, or when a groove sounds flat, robotic or lifeless. Covers the velocity range per instrument role (kick, snare, hat, bass, pads, arp, lead, voice), humanisation (vary velocities and micro-timing, never rewrite the density), and why a velocity gap between sections becomes a volume hole instead of a timbral change. Trigger words : vélocité, velocity, son plat, robotique, mort, dynamique, humaniser, groove plat, écart de vélocité, trou de volume.
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

## ⚠️ Un écart de vélocité = un écart de son

**Des groupes de mesures à vélocités très différentes ne sonnent pas pareil du tout** — pas
« un peu moins fort », mais un autre timbre, une autre présence. Mesuré sur l'intro médiéval :
arpège en v42 à RMS 0.0024, thème en v118 à RMS 0.21 — **39 dB d'écart**, avec le groupe
intermédiaire totalement muet.

La cause n'est presque jamais la vélocité elle-même, mais ce à quoi elle sert :

- une **modulation vélocité → gain** dans un synthé (l'OSC de Surge par exemple) : l'écart devient
  un écart de *niveau*, et il est exponentiel, pas linéaire ;
- un **timbre différent par vélocité** (split luth / chalumeau) : là, l'écart est *timbral* et c'est
  voulu — mais il faut que les **niveaux des deux timbres soient égaux**, sinon l'effet s'entend
  comme un trou de volume, pas comme un changement d'instrument.

**La règle** : quand je sépare des sections par la vélocité, je vérifie dans **une seule capture**
que les deux groupes sortent au même niveau. Et je garde les vélocités des sections qui doivent
sonner pareil dans une **plage serrée** (écart de 10-15 max), pas 42 contre 118.

## Attention aux fichiers

`add_notes_to_clip` ne purge **pas** le clip : seules les notes de même `(pitch, start_time)` sont
mises à jour, les autres survivent. Always send the complete list, and recreate the clip to
really clear it. Voir `pieges-notes-midi`.
