---
name: automation-envelopes
description: Écriture et lecture d'automation sur clips Ableton — insert_step, param targets, session vs arrangement, limitations Live 12 Lite.
---

# Automation Envelopes

## Méthode d'écriture

La seule méthode fiable dans Live 12 Python API est `insert_step(time, duration, value)` sur l'enveloppe d'un automate param.

```python
set_automation_curve(
    track_index=0, clip_index=0,
    target="device_1_Volume",
    points=[{"time": 0.0, "value": 0}, {"time": 2.0, "value": 64}, {"time": 4.0, "value": 127}],
    is_arrangement=False
)
```

Chaque point crée un step : `insert_step(t_i, t_{i+1} - t_i, v_i)`. La valeur se maintient de t_i à t_{i+1}. Chaque step génère 2 événements (fin du précédent + début du suivant).

## Param targets

| Target | Description | Valeurs |
|---|---|---|
| `"volume"` | Volume de piste | 0.0-1.0 |
| `"panning"` | Panning de piste | 0.0-1.0 |
| `"send_N"` | Send N (ex: `send_0` = A-Reverb) | 0.0-1.0 |
| `"device_N_PARAMNAME"` | Paramètre de device (ex: `device_1_Volume`) | 0-127 raw |

Trouver `PARAMNAME` via `get_device_parameters(track, device)` — utiliser le `name` exact du paramètre.

## Outils disponibles

| Outil | Description |
|---|---|
| `set_automation_curve(track, clip, target, points, is_arrangement)` | Écrit une courbe complète |
| `get_arrangement_clip_envelope(track, clip, target, is_arrangement)` | Lit les points d'enveloppe (diagnostic) |
| `add_clip_envelope_point(track, clip, target, time, value, duration, is_arrangement)` | Ajoute un point individuel |
| `clear_clip_envelope(track, clip, target, is_arrangement)` | Supprime toute l'enveloppe |
| `experiment_envelope(track, clip, target)` | Diagnostic exhaustif — teste toutes les approches |

## Limitations Live 12 Lite (CRITICAL)

| Ce qui marche ✅ | Ce qui ne marche PAS ❌ |
|---|---|
| Session clips : `set_automation_curve` écrit + lit via `events_in_range()` | `automation_envelope(param)` sur clip MIDI arrangement → `None` |
| `duplicate_clip_to_arrangement` copie les enveloppes (visible UI) | `create_automation_envelope(param)` sur clip MIDI arrangement → exception |
| Lecture API des enveloppes d'arrangement → impossible |

Les enveloppes d'arrangement sont **write-once** : écriture OK via workflow session→duplicate, mais lecture/modification impossible depuis Python.

## Interdits

- **Ne pas utiliser `create_event()`** — nécessite une struct C++ `TEnvelopeEvent` inaccessible depuis Python
- **Ne pas modifier `control_coefficients`** — propriété read-only
- **Ne pas tenter de lire les enveloppes d'arrangement directement** — bug API connu
