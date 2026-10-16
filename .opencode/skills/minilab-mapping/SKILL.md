---
name: minilab-mapping
description: Use when David wants to control Ableton from the MiniLab mkII, when binding a CC to a parameter, or when inspecting existing MIDI mappings. Covers the 39 decoded controls, the example CC16 to track 1 volume, the direct vs listener-based mapping distinction, and the Ableton MIDI mappings panel. Trigger words : MiniLab, mkII, contrôleur, MIDI mapping, CC, bind, affectation, manette, knob, fader physique.
---

# Pilotage MiniLab mkII

Le mapping complet des 39 contrôles est dans `mapping_midi/README_minilab_mkII.md` — **je le lis
quand j'ai besoin de la table précise**, pas avant. Les fichiers `.minilabmk2` du même dossier
sont les exports bruts du Midi Control Center d'Arturia (format CC0).

## Le format de l'export Arturia

Chaque clé `N_C` est un contrôle `N`, champ `C` :

| Champ | Contenu |
|---|---|
| `_1` | type de message (1 = CC pot, 8 = encodeur/pad, 9 = note pad) |
| `_2` | 65 = canal système, souvent identique partout |
| `_3` | **le numéro de CC ou la note MIDI** |
| `_4` | min (0) |
| `_5` | **max (127)** |
| `_6` | mode (0 = pot absolu, 1 = toggle / on-off / pad) |
| `_17` | doublon système, présent sur pads et encodeurs |

⚠️ **L'export contient une virgule finale avant le `}`** — il faut la retirer avant `json.loads`,
sinon le fichier ne se charge pas.

## Les 14 knobs, canal 1, type CC

| Ctrl | CC | Ctrl | CC | Ctrl | CC | Ctrl | CC |
|---|---|---|---|---|---|---|---|
| 1 | 74 | 2 | 71 | 3 | 18 | 4 | 19 |
| 5 | 17 | 6 | 91 | 7 | 79 | 8 | 72 |
| 9 | 76 | 10 | **16** | 11 | 77 | 12 | 93 |
| 13 | 73 | 14 | 75 | | | | |

**CC 16 = ctrl 10**, c'est le knob utilisé pour piloter le volume. Les pads (36+) sont sur les
canaux 8 et 9, en mode toggle.

## Exemple de référence

**CC 16, canal 1 → volume de la piste 1.**

```
map_midi_control(channel=0, identifier=16, msg_type="cc",
                 target_type="track_volume", track_index=0)
```

`track_index` est **0-based** : la piste 1 est l'index 0. Voir `pieges-indexation`.

## Deux façons de mapper, et la différence compte

| Outil | Comment ça marche | Quand |
|---|---|---|
| `map_midi_control` | **listener** : le Remote Script intercepte le CC et écrit le paramètre | par défaut |
| `map_midi_control_direct` | **`connect_to()`** : Live route le message au niveau C++ | apparaît dans le panneau **Affectations MIDI** natif |

Le mapping direct est préférable quand David veut que le mapping **apparaisse et survive** dans le
panneau MIDI d'Ableton. Le listener est plus simple mais n'est pas visible dans Live.

## Lire les mappings existants

```
list_midi_mappings()
```

Renvoie par mapping : channel, type de message, identifiant (CC ou note), min, max, mode, cible.
**Attention** : cette fonction ne liste que les mappings **créés par ce script**. Les mappings
natifs d'Ableton n'y sont pas.

## Plage min / max

Par défaut `0 → 127`. Pour un paramètre bipolar comme le pan, `-1.0 → 1.0` donne un contrôle
centré, ce qui est le comportement attendu d'un knob physique. Pour un volume, `0.0 → 1.0`.

## Mode

`absolute` (la valeur du CC est la valeur) ou `relative` (la course est un incrément). Un knob
physique en mode relatif est le bon choix si le knob n'a pas de position fixe.

## Cible device

Pour contrôler un paramètre de device :

```
target_type="device_param", track_index=0, device_index=0, parameter_name="Dry/Wet"
```

Le `parameter_name` doit correspondre **exactement** à ce que renvoie `get_device_parameters`. Voir
`pieges-automation` pour le même format de nommage côté enveloppes.
