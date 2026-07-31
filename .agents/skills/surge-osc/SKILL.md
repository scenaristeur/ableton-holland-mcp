---
name: surge-osc
description: Contrôle de Surge XT via OSC — paramètres, patches, modulation routing, MIDI notes, multi-instances jusqu'à 8.
---

# Surge XT OSC Control

## Configuration OSC

1. Ouvrir Surge XT dans Ableton → menu (top-left) → Settings → OSC
2. Activer OSC. Ports : **IN=53280, OUT=53281** (instance 0)
3. Multi-instances : stride=2 (instance 1 = IN=53282/OUT=53283, etc.). Max **8 instances**.

Le serveur MCP (`surge_osc_mcp.py`) envoie à l'IN de Surge et écoute sur l'OUT de Surge.

## Gestion des patches

```python
surge_list_categories()                          # [ "Basses", "Drums", "Leads", "Pads", ... ]
surge_list_patches("Basses")                     # [{ "name": "...", "path": "..." }, ...]
surge_search_patches(query="warm")               # recherche across ALL categories
surge_load_patch(path="C:/...without...extension", instance=0)
surge_get_patch(instance=0)                      # vérifier le patch chargé
surge_incr_patch(instance=0)                     # patch suivant dans la catégorie
surge_decr_patch(instance=0)                     # patch précédent
surge_random_patch(instance=0)                   # patch aléatoire
surge_rebuild_index()                            # rescanner les .fxp du disque
```

**Chemins :** utiliser des forward slashes (`C:/...`). Le serveur convertit automatiquement en backslashes Windows. Ne pas inclure l'extension `.fxp`.

## Paramètres OSC (via `surge_set_param`)

Adresse OSC : `/param/<scene>/<type>/<index>/<param>`

| Exemples d'adresses | Description |
|---|---|
| `/param/a/osc/1/pitch` | Oscillator 1 pitch (semitone) |
| `/param/a/osc/1/type` | Osc type : 0=Classic..11=Wavetable |
| `/param/a/filter/1/cutoff` | Filter 1 cutoff |
| `/param/a/filter/1/resonance` | Filter 1 resonance |
| `/param/a/amp/volume` | Amplifier volume |
| `/param/a/amp/pan` | Amplifier pan |
| `/param/a/waveshaper/drive` | Waveshaper drive |
| `/param/a/waveshaper/type` | Waveshaper type |
| `/param/a/mixer/osc1/volume` | Osc 1 mixer level |
| `/param/a/mixer/osc1/mute` | Osc 1 mute |
| `/param/macro/1` .. `/param/macro/8` | Macros |
| `/param/global/volume` | Global volume |
| `/param/global/polyphony_limit` | Polyphony limit |
| `/param/a/play_mode` | 0=Poly..5=Mono |
| `/param/a/feg/attack` | Filter EG attack |
| `/param/a/aeg/attack` | Amp EG attack |

## Modulation routing

```python
surge_map_modulation(mod_source, target, depth, instance=0)
surge_unmap_modulation(mod_source, target, instance=0)  # depth = 0 pour disconnecter
```

**Sources (`mod_source`) :**

| Source | Description |
|---|---|
| `a/vlfo_1/0` .. `a/vlfo_6/0` | Voice LFOs (index 0=LFO out, 1=Raw Wave, 2=EG Only) |
| `a/slfo_1/0` .. `a/slfo_6/0` | Scene LFOs |
| `a/feg` | Filter EG |
| `a/aeg` | Amp EG |
| `vel` | Velocity |
| `keytrk` | Keytrack |
| `mw` | Mod Wheel |
| `pb` | Pitch Bend |
| `rand_bi/0` | Random Bipolar |
| `rand_uni/0` | Random Unipolar |
| `macro_1` .. `macro_8` | Macros |

**Target :** adresse OSC du paramètre cible (ex: `/param/a/filter/1/cutoff`), **depth** = -1.0 à 1.0 (0 = déconnecte).

## MIDI Notes

```python
surge_note_on(pitch=60, velocity=100, instance=0)    # Note On (pitch 0-127)
surge_note_off(pitch=60, instance=0)                  # Note Off
surge_all_notes_off(instance=0)                       # Toutes notes off
```

## Dump et monitoring

```python
surge_query_all(instance=0)    # dump tous les paramètres + valeurs courantes
surge_get_param(address, instance=0)    # lire un paramètre individuel
```

## Limitations OSC connues

L'arpégiateur, la sélection de wavetable et les subtypes de filtre ne sont pas exposés via OSC. À configurer manuellement dans l'UI Surge XT.

## Style → Patch mapping

| Style | Bass | Guitar/Pluck | Pad | Lead |
|---|---|---|---|---|
| Funky | Rubber Bass, Fingered | Clean, E-Guitar | MKS-70 Warm Pad | Moogy Saw, Sine Lead |
| Pop/Organic | E-Bass, Mellow | Woody, Guitar | Subtle Comb Strings | Classic Lead 2 |
| Electronic | FM Bass 1, Digibass | Sync Pluck, FM Pluck | Flux Capacitor | Classic Lead 1, Acidofil |
| Cinematic | Sub 2, Deep End | Ambient E-Guitar | Ghost Pad, Still | Vocal Lead |
