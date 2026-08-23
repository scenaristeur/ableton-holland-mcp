# Mapping MIDI — MiniLab mkII (Arturia) — décodage export Midi Control Center

Fichiers sources :
- `Analog Lab 2026_08_07 11.00.11.minilabmk2`
- `Analog Lab 2026_08_07_2 11.00.11.minilabmk2`

(Export JSON « Midi Control Center » d'Arturia, device **MiniLab mkII**, v1.1.2.
Fichier CC0 — généré via le générateur midiremotescripts.structure-void.com pour l'outil.)

## Format du JSON Arturia
Chaque clé `N_C` : contrôle `N`, champ `C`. Champs :
- `_1` : type message (1 = CC pot, 8 = ? encoders/pads, 9 = note pads)
- `_2` : 65 = canal ? (système) — souvent le même (canal MIDI ?)
- `_3` : le numéro CC ou la note MIDI
- `_4` : **min** (0)
- `_5` : **max** (127)
- `_6` : mode (0 = pot absolu, 1 = toggle / on-off / pad)
- `_17` : ? (doublon système, présent sur pads/encoders)

⚠️ L'export a un **trailing comma** avant la `}` — retirer avant `json.loads`.

## Contrôles décodés (39 au total)

### Knobs / pots (canal 1, type CC) — field1=1
| Ctrl | CC | Min-Max | Mode | Ctrl | CC | Min-Max | Mode |
|---|---|---|---|---|---|---|---|
| 1 | 74 | 0-127 | pot | 9 | 76 | 0-127 | pot |
| 2 | 71 | 0-127 | pot | 10 | **16** | 0-127 | pot |
| 3 | 18 | 0-127 | pot | 11 | 77 | 0-127 | pot |
| 4 | 19 | 0-127 | pot | 12 | 93 | 0-127 | pot |
| 5 | 17 | 0-127 | pot | 13 | 73 | 0-127 | pot |
| 6 | 91 | 0-127 | pot | 14 | 75 | 0-127 | pot |
| 7 | 79 | 0-127 | pot | 8 | 72 | 0-127 | pot |

### Pads (canal 9/8, type note/pad) — field1=8/9, field6=1 (toggle)
Ce sont les **pads batterie** (notes 36+) et les pads d'encoders.

## Conséquence pour l'implémentation
- Pour « contrôler en direct la session », on utilisera les CC des knobs ci-dessus (ex. **CC16** = ctrl10 = pot), canal 1.
- L'export nous dit les **min/max** (0-127) et le **mode** (pot absolu vs toggle) que le clavier
  envoie → indispensable pour bien intercepter.
- Le clavier MiniLab mkII envoie les CC sur le **port MIDI** qui lui est assigné ; le Remote Script
  doit être sur le même port d'entrée.

## Exemple de mapping généré (CC16 → Track 1 Volume)
`mapping_midi/test_mapping_CC16_track1_volume/` — pattern de référence :
```python
from _Framework.SliderElement import SliderElement
from _Framework.InputControlElement import MIDI_CC_TYPE
el_1 = SliderElement(MIDI_CC_TYPE, 0, 16)   # CC16, canal 0 (1-based: ch1)
def _on_el_1(value):
    tracks = self.song().tracks
    if 0 < len(tracks):
        tracks[0].mixer_device.volume.value = value / 127.0
el_1.add_value_listener(_on_el_1)
self._controls.append(el_1)                 # garde l'element en vie
```

## Références
- Génération : https://midiremotescripts.structure-void.com/generator/
- Docs : https://midiremotescripts.structure-void.com/
- Généré = domaine public (CC0). Le générateur/doc = © Julien Bayle / Structure Void (CC BY-NC-SA 4.0).
