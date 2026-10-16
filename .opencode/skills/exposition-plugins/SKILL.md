---
name: exposition-plugins
description: Use when deciding which VST plugin to load for a role, when a plugin exposes too few parameters to be usable via the API, or when comparing plugins for this install. Covers the exposure table (how many parameters each installed VST exposes to Ableton), the green/yellow/red tiers, and the selection strategy. Trigger words : exposition, paramètres exposés, plugin VST, load_external_plugin, combien de paramètres, Massive X, LABS, MEqualizer, Arturia, Vital, Kontakt.
---

# Exposition des plugins VST

Tous les plugins installés ne se valent pas pour pilotage MCP : certains exposent des dizaines de
paramètres, d'autres seulement « Device On ». La table ci-dessous est la carte de ce qui est
réellement pilotable.

## Niveaux d'exposition

| Niveau | Nombre de paramètres | Usage |
|---|---|---|
| 🟢 Bon | **≥ 20** | pilotage complet, idéal |
| 🟡 Moyen | **10-19** | pilotage partiel, faisable |
| 🔴 Faible | **1** (« Device On ») | inutilisable via l'API — contourner |

## La table réelle

**🟢 ≥ 20 :**
- **MEqualizer** 53
- **LABS** 53
- **Massive X** 26
- **MSaturator** 23
- **MCompressor** 19+

**🟡 10-19 :**
- ValhallaSupermassive 19
- Raum 19
- Rev PLATE-140 16
- Vinyl 16
- Surge XT Effects 14
- Focusrite Red 2 EQ 13
- Replika 12
- Red 3 Compressor 9

**🔴 1 param (« Device On ») :**
- Analog Lab V, Acid V, Mini V3, Stage-73 V2, ARP 2600 V3, Vital, TDR Nova, **Surge XT**,
  Komplete Kontrol, Kontakt 7/8, Ozone 12 Equalizer, Reaktor 6, Trash, Splice, **MDynamicEq**.

## La stratégie de sélection

| Besoin | Choix |
|---|---|
| Instruments | **Massive X** / **LABS** (gros exposé) |
| Synthé | **Surge XT** via **OSC**, pas via l'API |
| Effets | **Melda** (MEqualizer, MSaturator, MCompressor) / **Focusrite** |
| Réverb | **Raum** / **Valhalla** / **Plate-140** / **MCharmVerb** 33 |
| Delay | **Replika** 12 |
| À éviter | Arturia sauf Plate-140, **Vital**, iZotope sauf Vinyl, **TDR Nova**, Kontakt, Reaktor |

## Règles d'usage

- Je **vérifie l'exposition avant de promettre** un pilotage. Un plugin à 1 paramètre ne se pilote
  pas par MCP.
- `load_external_plugin` perd le segment vendor dans l'URI — toujours passer par l'URI du browser.
  Voir `pieges-browser`.
- Après un test, je **supprime le device** (`delete_device`) pour ne pas accumuler.

## Relation avec Surge XT

Surge XT est **🔴 via l'API** mais pleinement pilotable **par OSC**. C'est pourquoi tout le pilotage
Surge passe par les outils `surge-*` et les skills `surge-presets` / `surge-cpu-par-voix`, jamais par
les paramètres de device Ableton.