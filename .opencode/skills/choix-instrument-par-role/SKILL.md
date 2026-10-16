---
name: choix-instrument-par-role
description: Use when deciding which instrument or engine to load for a given musical role (bass, pad, lead, keys, plucks, texture). Covers the native-first decision order, the Drift preset families to reach for, when Simpler or Impulse is right, and when Surge XT is genuinely justified. Trigger words : quel instrument, quel son, basse, nappe, pad, lead, pluck, texture, arpège, what sound, trouver un son.
---

# Choisir un instrument par rôle

## L'ordre de décision

1. **Drift** pour tout synthé. 12 familles de presets : Bass, Pad, Strings, Mallets, Synth Lead,
   Piano & Keys, Brass, Winds, Percussive, Guitar & Plucked, Synth Keys, Synth Rhythmic, Effects.
   C'est le multis de l'install — **je compose d'abord avec**.
2. **Kits `.adg`** pour la batterie.
3. **Simpler / Impulse** pour l'échantillonné (un sample réel, une nappe de texture).
4. **Surge XT** en dernier recours, une fois le morceau structuré avec du natif.

## Par rôle

| Rôle | Premier choix | Pourquoi |
|---|---|---|
| Basse | Drift, famille **Bass** | fondamentale + harmoniques, filtrable |
| Nappe / pad | Drift, **Pad** ; **Strings** pour un orchestre | tenue, contrôlée par le filtre |
| Lead | Drift, **Synth Lead** | une seule note doit porter une mélodie |
| Clavier | Drift, **Piano & Keys** | plucké ou tenu |
| Arpège | Drift, **Guitar & Plucked** ou **Mallets** | sustain court, percussif |
| Pluck | Drift → **Guitar & Plucked** | attaque nette, decay court |
| Texture | Drift → **Ambient & Evolving** / **Effects** | mouvement sans mélodie |
| Cuivres | Drift → **Brass** | attention, ça mange vite le CPU |
| Batterie | Kit `.adg` + Drum Rack | le kit joue déjà le GM |

## Ce qui n'est pas un device

Wavetable, Analog, Operator, Collision, Electric, Tension : **absents de cette install**. Je peux
charger un *son* de la famille, pas le synthé. Voir `palette-live-lite`.

## Après le chargement : sculpter — ⚠️ réflexe automatique

**Un preset brut n'est pas un son fini, et ça s'entend immédiatement comme une maquette.** Dès que
l'instrument est posé — ou dès que j'écris des notes dessus — je fais le passage de timbre **avant**
de présenter quoi que ce soit. Ce n'est pas une option. C'est l'étape 3 de la boucle de
`maquette-scene-par-scene`.

1. `get_device_parameters(track_index, device_index)` — je lis ce qui est exposé. Beaucoup de synthés
   natifs ont des **macros internes à 0** qui servent exactement à ça (Over Tone, Tone, Distort sur
   Basic Sub Sine). Les familles Drift exposent aussi Filtre, Réso, Enveloppe, Space, Thick, Clip.
2. Je cible en priorité les tueurs de « bas de gamme » : **résonance haute** (criard),
   **Noise Gain** élevé (grésillant), **filtre trop ouvert** (aigre) ou **trop fermé** (bouché),
   **enveloppe** inadaptée au rôle.
3. Puis l'espace : envois vers les retours Reverb / Delay (voir `reverb-insert`), plutôt que de
   laisser la source sèche et collée.
4. FX, en partant d'un **état transparent** (voir `sculpture-sonore`).
5. Recapturer et itérer.

## Surge : seulement si justifié

Une instance Surge se configure **à la main** (Settings > OSC) : instance *n* sur le port
`53280 + 2n`. Un patch plus « chaud » que la référence : **drive, unison, filter**. Le mixer mute
(0 = actif) permet de découvrir des oscillateurs masqués et d'ajouter une couche d'octave pour le
téléphone.

Mais chaque instance est du CPU. **Je structure le morceau avec du natif d'abord**, et je vérifie
le coût avant d'ajouter Surge. Voir `surge-cpu-par-voix`.
