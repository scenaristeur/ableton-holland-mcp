---
name: pieges-outils-indisponibles
description: Use when a tool fails, hangs, or returns something surprising. Covers the tools that are disabled or do not exist in this build, the ones that lie or time out, and the one-line workaround for each. Trigger words : outil échoue, ça ne marche pas, tool fails, hang, indispo, pas accessible, liste de pièges, diagnostic d'outil.
---

# Outils indisponibles ou trompeurs

## Désactivés dans ce build

| Outil | État | Alternative |
|---|---|---|
| `capture_ableton` | désactivé | `capture_and_analyze` |
| `capture_at_position` | désactivé | `capture_and_analyze` |
| `create_event` | inaccessible | écrire l'enveloppe par points |
| `control_coefficients` | inaccessible | ne pas y toucher |

**145 outils actifs** sur 147 occurrences dans le serveur (2 commentées). Si un outil n'est pas dans
cette liste, il n'existe pas.

## Trompent ou mentent

| Outil | Le piège |
|---|---|
| `get_browser_item` | time-out sur les synthés. → `get_browser_items` |
| `list_external_plugins` | renvoie des **catégories de browser**, pas des plugins |
| `load_external_plugin` | perd le segment vendor dans l'URI |
| `add_notes_to_clip` | **remplace** malgré le nom ; champ `start_time` |
| `set_arrangement_clip_notes` | **remplace** malgré le nom |
| `duplicate_clip_to_arrangement` | off by one → `duplicate_to_arrangement` |
| `set_automation_curve` | s'écrasent mutuellement en arrangement |
| `hasattr(device, "drum_pads")` | **ment** sur les kits `.adg` (InstrumentGroupDevice imbriqué) |

## Activer / désactiver un device

Le paramètre est **« Device On »**, jamais `is_enabled` seule. C'est l'erreur classique : j'appelle
`disable_device`, il rapporte un succès, et le device joue toujours.

## Mute ne réduit pas la charge

Pour l'économie de CPU : `disable_device` ou `freeze_track`. Voir `diagnostic-cpu`.

## Capture silencieuse

`CABLE_DEVICE_ID` est figé au démarrage. Si VB-Cable a changé, **redémarrer le serveur MCP** est la
seule correction. Voir `capture`.

## Appels Ableton sérialisés

Le serveur n'a pas de verrous : **jamais deux appels Ableton en parallèle.** Un par un, j'attends
le retour.

## Le reste est dans les skills dédiés

Ce skill est la carte. Le détail est ailleurs, et je le charge au besoin :

- `pieges-notes-midi` — notes MIDI
- `pieges-automation` — enveloppes
- `pieges-niveaux` — gains, positions, off by one
- `pieges-browser` — URI et chargement
- `pieges-indexation` — 0-based / 1-based

Détail de l'implémentation : `AGENTS_CODE.md`, que je n'ouvre que si un outil échoue vraiment.
