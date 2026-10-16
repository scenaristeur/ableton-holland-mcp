---
name: pieges-automation
description: Use when writing any automation envelope on an Ableton clip, session or arrangement. Covers the write-once overwrite trap, why several single-target calls destroy each other on arrangement clips, the set_automation_lanes single-pass tool, the target naming format, and the value scale pitfall (insert_step uses the parameter's native range, NOT a raw 0-127). Trigger words : automation, enveloppe, volume, panning, send, set_automation_curve, set_automation_lanes, fade, crescendo, clip volume, échelle, plage, insert_step.
---

# Pièges : automation

## ⚠️ Automation en arrangement : write-once

**Les enveloppes d'un clip d'arrangement s'écrasent.** Chaque écriture remplace la précédente.

Et surtout : pour un clip MIDI d'arrangement, le clip est **reconstruit depuis un clip de session
temporaire**. Donc **plusieurs appels `set_automation_curve` s'écrasent les uns les autres** — la
seconde lane tue la première, silencieusement.

## La solution : tout écrire en un appel

```
set_automation_lanes(track_index, clip_index, lanes=[
    {"target": "volume",   "points": [{"time": 0, "value": 0.3},
                                      {"time": 32, "value": 0.6}]},
    {"target": "send_0",   "points": [{"time": 0, "value": 0.2},
                                      {"time": 32, "value": 0.5}]},
])
```

`set_automation_lanes` crée **toutes** les enveloppes sur le clip temporaire **avant** de le
dupliquer, donc chaque lane survit. C'est le seul appel à utiliser en arrangement dès qu'il y a
plus d'une cible.

## Format des points

| Champ | Valeur |
|---|---|
| `time` | en **temps (beats)**, relatif au début du clip |
| `value` | **dans la plage native du paramètre** (voir `get_device_parameters` : min/max) |

## ⚠️ L'échelle des valeurs d'automation (le piège le plus cher)

**`insert_step` prend la valeur dans la plage du paramètre, PAS un brut 0-127.**

- Un paramètre **0-1** (LP Freq, Drift, la plupart des macros) → écrire `0.3`, `0.6`, pas `40`, `65`.
  Un `40` sort de la plage → Live le **clamp** à fond → **aucune variation audible**, mais l'enveloppe
  existe (l'erreur silencieuse : on croit que c'est fait, le son ne bouge pas).
- Un paramètre **-1 à 1** (pan) → valeurs négatives possibles, centrées sur 0.
- Un paramètre en **dB** (gain de clip, `Output`) → valeurs en dB réels.
- L'échelle **0-127 n'est pas une convention générale**. Vérifier **chaque fois** la plage réelle.

### Le réflexe avant d'écrire une automation

1. `get_device_parameters(track, device)` → lire `min`/`max` du paramètre.
2. Écrire les points dans cette plage.
3. **Relire** avec `get_arrangement_clip_envelope` / `get_clip_envelope` → vérifier que les valeurs
   ont atterri dans la plage attendue (un `value` énorme type `447.744` = mauvaise échelle).

### `insert_step` = automation en escalier, pas en rampe

`insert_step(t, v, d)` crée un **step** : la valeur reste **constante** entre deux points et **saute**
au point suivant. Pour une vraie **rampe** (filtre qui s'ouvre progressivement), il faut **plusieurs
points** intermédiaires, pas juste début+fin.

### Contraste entre clips, pas sweep dans un clip

Le mouvement le plus simple (ex. arp sombre en couplet → clair en refrain) se fait par **deux clips
différents** : couplet automatisé à `0.35` (constant), refrain à `0.6` (constant). La bascule se joue
au changement de scène — pas besoin d'un sweep dans le clip.

## Noms de cible

- `volume`
- `panning`
- `send_0`, `send_1` (numéro du retour)
- `device_<index>_<NomDuParametre>` — ex. `device_1_Dry/Wet`

L'index de device est **0-based**, et le nom du paramètre doit correspondre **exactement** à ce que
`get_device_parameters` renvoie, espaces et barre oblique compris.

## Lire avant d'écrire

```
get_clip_envelope(track_index, clip_index, target)
get_arrangement_clip_envelope(track_index, clip_index, target)
debug_clip_envelopes(track_index, clip_index)
```

Si une enveloppe existe et que je ne la voyais pas, elle sera détruite. Je lis donc **avant**.

## Session ou arrangement

`is_arrangement=True` pour l'arrangement, `False` pour les slots de session. Se tromper lit ou
écrit sur le mauvais clip — et l'enveloppe créée n'est pas celle que je croyais. Voir
`pieges-indexation`.
