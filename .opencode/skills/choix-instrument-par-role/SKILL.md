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

## Après le chargement : sculpter

Un preset brut n'est pas un son fini. Dès que l'instrument est posé :

1. `get_device_parameters` — beaucoup de synthés natifs ont des **macros internes à 0** qui servent
   exactement à ça (Over Tone, Tone, Distort sur Basic Sub Sine).
2. FX, en partant d'un **état transparent** (voir `sculpture-sonore`).
3. Recapturer et itérer.

## Surge : seulement si justifié

Une instance Surge se configure **à la main** (Settings > OSC) : instance *n* sur le port
`53280 + 2n`. Un patch plus « chaud » que la référence : **drive, unison, filter**. Le mixer mute
(0 = actif) permet de découvrir des oscillateurs masqués et d'ajouter une couche d'octave pour le
téléphone.

Mais chaque instance est du CPU. **Je structure le morceau avec du natif d'abord**, et je vérifie
le coût avant d'ajouter Surge. Voir `surge-cpu-par-voix`.
