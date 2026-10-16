---
name: palette-live-lite
description: Use when loading any instrument, effect or drum kit through the Ableton browser in this project, or when checking whether a device exists. Contains the verified Live 12 Lite palette (6 native instruments only), the 18 audio effects, the ~200 .adg kits, the 17 Sound categories, and the device-vs-sound distinction. Trigger words : charger un instrument, charger un plugin, browser, URI, preset, kit, Drum Rack, Drift, Simpler, Impulse, Wavetable, Analog, est-ce que ça existe.
---

# Palette réelle de Live 12 Lite

Vérifié **dans le browser**, pas de mémoire. Cette liste est la vérité du projet.

## Instruments natifs : 6, et pas plus

- `Drift`
- `Drum Rack`
- `Drum Sampler`
- `Impulse`
- `Instrument Rack`
- `Simpler`

⚠️ **Wavetable, Analog, Operator, Collision, Electric et Tension n'existent PAS comme devices**
dans cette installation. Ce sont des instruments Suite/Advanced. **Je ne les propose pas à David et
je ne cherche pas leur URI** — la recherche coûte un timeout à chaque fois.

## La nuance sons vs devices

Des **sons** de ces familles existent bel et bien dans `query:Sounds#…` (17 dossiers : Bass, Pad,
Strings, Mallets, Brass, Winds, Percussive, Piano & Keys, Guitar & Plucked, Synth Keys, Synth Lead,
Synth Rhythmic, Ambient & Evolving, Booms, Effects, MPE Sounds, Synth Misc).

Un preset comme « Warm Analog Pad » est donc **chargeable**. C'est un **son**, pas le synthé Analog.
Ce qui n'existe pas, c'est le device.

Conséquence pratique : je peux honnêtement dire « un pad chaud de la famille Analog » en chargeant un
preset Drift. Je ne peux pas dire « je mets Analog ».

## Ce qui existe en quantité

- **~200 kits batterie** `.adg` — déjà remplis, ils jouent le GM directement.
- **18 effets audio** — voir `fx-lite`.

## Charger une chose

```
load_instrument_or_effect(track_index, uri)
```

Pour **découvrir** les URI, **jamais** `get_browser_item` (il time-out sur les synthés) :

```
get_browser_items(path="instruments")      toute la subtree, avec les bons URI
get_browser_items(path="drums")
get_browser_items(path="audio_effects")
```

Les deux URI de base qui répondent :

- `query:Drums#Drum%20Rack` — le Drum Rack vide
- `query:Drums#FileId_XXXX` — un kit `.adg` précis

## Règle d'ordre

1. **Drift** pour tout synthé. 12 familles de presets. C'est le multis de l'install : je compose
   d'abord avec.
2. **Kits `.adg`** pour la batterie.
3. **Simpler / Impulse** pour l'échantillonné.
4. **Surge XT** en dernier recours seulement.

Voir `choix-instrument-par-role` pour la décision par rôle, et `kits-batterie-par-vibe` pour le
choix du kit.
