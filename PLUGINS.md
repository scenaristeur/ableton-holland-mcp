# PLUGINS.md — Plugin Control Reference

## Overview

This project uses two control channels for instruments/effects:
- **Remote Script API** (TCP port 9877) — for all Ableton-native devices and general Live operations
- **Surge XT OSC** (UDP, instance 0: IN 53280 / OUT 53281) — dedicated control for Surge XT

External VST/AU plugins (Analog Lab V, etc.) are loaded via the Remote Script but have **limited parameter access** — only the parameters they expose to Live's API.

---

## Current Session (2026-07-08) — Clean test session

| Track | Device | Type | Paramètres exposés |
|---|---|---|---|
| 1-MIDI | *(empty)* | MIDI | — |

---

## Control Methods

### 1. Remote Script API (TCP 9877)

**Scope:** Everything in Live that the Remote Script exposes.

**Ableton-native devices** (`InstrumentGroupDevice`, `DrumGroupDevice`, all built-in synths/effects):

| Capability | How |
|---|---|
| Load instrument/effect | `load_instrument_or_effect(track_index, uri)` |
| Read parameters | `get_device_parameters(track_index, device_index, chain_index)` |
| Set parameters | `set_device_parameter(track_index, device_index, parameter_name, value)` |
| Enable/disable device | `enable_device()` / `disable_device()` |
| Delete device | `delete_device(track_index, device_index)` |
| Preset navigation | `navigate_device_preset(track_index, device_index, direction)` |
| Drum pad info | `get_drum_pad_info(track_index, device_index)` |
| Chain info (racks) | `get_chain_info(track_index, device_index, chain_index)` |

**Browser access (loading instruments/presets):**

| Action | URI pattern | Example |
|---|---|---|
| Load native synth | `query:Synths#<Name>` | `query:Synths#Wavetable` |
| Load sound preset | `query:Sounds#<Category>:FileId_XXXX` | `query:Sounds#Bass:FileId_14913` |
| Load drum kit | `query:Drums#<Name>` | `query:Drums#Drum%20Rack` |
| Load external VST | plugins path | `plugins/VST3/Arturia/Analog Lab V` |
| Browser tree | `get_browser_tree(category_type)` | `"instruments"`, `"sounds"`, `"drums"` |
| Browse path | `get_browser_items_at_path(path)` | `"Sounds/Bass"` |

**Available native synths** (via `query:Synths#<Name>`):
- Wavetable, Analog, Drift, Operator, Collision, Electric, Tension
- Simpler, Sampler, Impulse, Drum Rack, Instrument Rack
- Drum Sampler

**Available sound categories** (via `query:Sounds#<Category>`):
- Bass, Synth Lead, Synth Keys, Pad, Piano & Keys, Strings, Brass
- Guitar & Plucked, Ambient & Evolving, Synth Misc, Synth Rhythmic
- MPE Sounds, Mallets, Winds, Percussive, Effects, Booms

### External VST/AU plugins (PluginDevice)

**Capabilities:**
- Load via `load_external_plugin(track_index, plugin_name)` (searches browser)
- List available plugins via `list_external_plugins(query, max_results, refresh_cache)`
- Navigate presets via `navigate_device_preset(track_index, device_index, direction)`
- Delete via `delete_device(track_index, device_index)`
- **Read/write parameters** via `get_device_parameters()` / `set_device_parameter()` — **but only the params the VST exposes to Live's API** (usually very few)

**Important limitation:** External VSTs like Analog Lab V expose only a limited subset of their internal parameters to Ableton's Python API. You can see what's available with `get_device_parameters(track_index, device_index)`. Most parameters (oscillator controls, filter, effects inside the VST) are **NOT accessible** via the Remote Script.

### External VST Parameter Exposure (tested 2026-07-08)

Résultat des tests de paramètres exposés par chaque VST via `get_device_parameters()`. Chargez un instrument + effets sur la même track. Supprimez les devices après test pour économiser CPU/mémoire.

#### 🟢 Excellente exposition (≥20 paramètres)

| Plugin | Type | Nb params | Paramètres clés |
|---|---|---|---|
| **MEqualizer** (Melda) | EQ | **53** | 6 bandes EQ complètes (Freq/Gain/Q/Type/Harmonics), Dry/Wet, Gain, Soft sat, Preset nav |
| **LABS** (Spitfire) | Instrument | **53** | Expression, Dynamics, ADSR, Global Pan/Tune, Stereo, Mic positions (Main/Alt1-3), Delay, Distortion, Reverb, GP 1-9 |
| **MSaturator** (Melda) | Distortion | **23** | Gain, Drive, Threshold, Harmonics (2nd-5th), Compander complet (Threshold/Ratio/Attack/Release) |
| **Massive X** (NI) | Synth | **26** | Spread, Width, Cutoff, Reso, Delay, Reverb, Macros 9-16, Morpher complet (Animator, Shape, X, Y, Speed) |
| **MCompressor** (Melda) | Compressor | **19+** | Attack, Release, RMS, Threshold, Ratio, Knee, Link, Param 1-4, Preset nav |

#### 🟡 Bonne exposition (10-19 paramètres)

| Plugin | Type | Nb params | Paramètres clés |
|---|---|---|---|
| **ValhallaSupermassive** | Reverb | **19** | Mix, Delay, Feedback, Density, Width, Low/High Cut, Mod Rate/Depth, Mode |
| **Raum** (NI) | Reverb | **19** | Predelay, Feedback, Low/High Cut, Mix, Mode, Diffusion, Size, Decay, Density, Mod, Freeze |
| **Rev PLATE-140** (Arturia) | Reverb | **16** | Drive, Plate Model, Decay, Width, Blend, Pre Delay, Mod, Low/High Shelf EQ |
| **Vinyl** (iZotope) | Effect | **16** | Input/Output Gain, Mech Noise, Wear, Elec Noise, Dust, Scratch, Warp, RPM, Lo-fi |
| **Surge XT Effects** | FX | **14** | Input Channel, Delay L/R, Feedback, Mod Rate/Depth, Output Width/Mix, FX Type |
| **Focusrite Red 2 EQ** | EQ | **13** | HiPass, LowShelf (Freq/Gain), Low/HiMid (Freq/Gain/Q), HiShelf (Freq/Gain), LowPass |
| **Replika** (NI) | Delay | **12** | Time Mode, Delay Time, Mix, Feedback, Stereo, In/Out, Saturation, Lo/HiCut, Mod |
| **Focusrite Red 3 Compressor** | Compressor | **9** | InputGain, Threshold, Ratio, Attack, Release, AutoRelease, MakeUpGain, Blend |

#### 🔴 Exposition nulle (1 seul paramètre : `Device On`)

| Plugin | Type | Note |
|---|---|---|
| **Analog Lab V** (Arturia) | Synth | Quasi incontrôlable |
| **Acid V** (Arturia) | Synth | — |
| **Mini V3** (Arturia) | Synth | — |
| **Stage-73 V2** (Arturia) | EP | — |
| **ARP 2600 V3** (Arturia) | Synth | — |
| **Vital** | Synth | — |
| **TDR Nova** | EQ dyn. | — |
| **Surge XT** (VST3) | Synth | **→ Utiliser OSC** (contrôle total via `surge_osc_mcp.py`) |
| **Komplete Kontrol** (NI) | Host | — |
| **Kontakt 7/8** (NI) | Sampler | — |
| **Ozone 12 Equalizer** (iZotope) | EQ | — |
| **Reaktor 6 / Reaktor 6 FX** (NI) | Synth/FX | — |
| **Trash** (iZotope) | Distortion | — |
| **Splice INSTRUMENT** | Instrument | — |
| **MDynamicEq** (Melda) | EQ dyn. | Surprenant pour un Melda |

#### Stratégie recommandée

1. **Instrument paramétrable** → Massive X (26 params) ou LABS (53 params) via Live API ; Surge XT via OSC pour contrôle total
2. **Effets** → Privilégier **Melda** (MEqualizer 53, MSaturator 23, MCompressor 19+, MCharmVerb 33) et **Focusrite** (Red 2 EQ 13, Red 3 Comp 9)
3. **Réverb** → Raum (19), ValhallaSupermassive (19), Rev PLATE-140 (16), MCharmVerb (33)
4. **Delay** → Replika (12)
5. **À éviter** → Tous les Arturia (sauf Rev PLATE-140), Vital, iZotope (sauf Vinyl), TDR Nova, Kontakt, Reaktor
6. **Nettoyage** → `delete_device(track_index, device_index)` après chaque test pour libérer CPU/mémoire

---

### 2. Surge XT via OSC (`surge_osc_mcp.py`)

**Full reference:** `docs/surge_OSC.html`

| OSC Address | Description | Values |
|---|---|---|
| **Notes** | | |
| `/mnote` | MIDI note on | pitch (0-127), vel (0-127) |
| `/mnote/rel` | MIDI note off | pitch (0-127), vel |
| `/fnote` | Frequency note | freq (8.176-12543.853), vel |
| `/allnotesoff` | All notes off | — |
| `allsoundoff` | Panic stop | — |
| **Patches** | | |
| `/patch/load` | Load patch | absolute path, no extension |
| `/patch/incr` | Next patch in category | — |
| `/patch/decr` | Previous patch in category | — |
| `/patch/random` | Random patch | — |
| `/patch/save` | Save current patch | optional path |
| **Wavetables** (when osc type = 7 or 11) | | |
| `/wavetable/<s>/osc/<n>/id` | Select wavetable by ID | int (0..N) |
| `/wavetable/<s>/osc/<n>/incr` | Next wavetable | — |
| `/wavetable/<s>/osc/<n>/decr` | Previous wavetable | — |
| **Queries** | | |
| `/q/patch` | Get current patch name | — |
| `/q/all_params` | Dump all parameter values | — |
| `/q/<param address>` | Get single parameter | — |
| `/q/wavetable/<s>/osc/<n>` | Get wavetable info | — |
| **Macros** | | |
| `/param/macro/1` .. `/param/macro/8` | Macro knobs | float 0.0-1.0 |
| **Global** | | |
| `/param/global/volume` | Master volume | float 0.0-1.0 |
| `/param/global/polyphony_limit` | Polyphony | int 2-64 |
| `/param/global/active_scene` | Scene A/B | 0 or 1 |
| `/param/global/scene_mode` | Single/split/dual | 0-3 |
| `/param/fx/chain_bypass` | FX bypass | 0-3 |
| **Scene parameters** (replace `<s>` with `a` or `b`) | | |
| **Oscillators** (replace `<n>` with 1, 2, 3) | | |
| `/param/<s>/osc/<n>/type` | Osc type | 0=Classic..11=Wavetable |
| `/param/<s>/osc/<n>/pitch` | Pitch | float 0.0-1.0 |
| `/param/<s>/osc/<n>/octave` | Octave | int -3..3 |
| `/param/<s>/osc/<n>/param1` | Morph/WT position | varies by type |
| `/param/<s>/osc/<n>/param2` | Skew Vertical | varies by type |
| `/param/<s>/osc/<n>/param3` | Saturate | varies by type |
| `/param/<s>/osc/<n>/param4` | Formant | varies by type |
| `/param/<s>/osc/<n>/param5` | Skew Horizontal | varies by type |
| `/param/<s>/osc/<n>/param6` | Unison Detune | varies by type |
| `/param/<s>/osc/<n>/param7` | Unison Voices | varies by type |
| `/param/<s>/osc/<n>/keytrack` | Keyboard tracking | bool |
| `/param/<s>/osc/<n>/retrigger` | Retrigger | bool |
| `/param/<s>/osc/fm_routing` | FM routing | 0-3 |
| `/param/<s>/osc/fm_depth` | FM depth | float 0.0-1.0 |
| `/param/<s>/osc/drift` | Osc drift | float 0.0-1.0 |
| **Filters** (replace `<n>` with 1, 2) | | |
| `/param/<s>/filter/<n>/type` | Filter type | int 0-33 |
| `/param/<s>/filter/<n>/subtype` | Filter subtype | int 0-15 |
| `/param/<s>/filter/<n>/cutoff` | Cutoff | float 0.0-1.0 |
| `/param/<s>/filter/<n>/resonance` | Resonance | float 0.0-1.0 |
| `/param/<s>/filter/<n>/feg_amount` | FEG amount | float 0.0-1.0 |
| `/param/<s>/filter/<n>/keytrack` | Keytrack | float 0.0-1.0 |
| `/param/<s>/filter/config` | Filter config | int 0-7 |
| `/param/<s>/filter/balance` | Filter balance | float 0.0-1.0 |
| `/param/<s>/filter/feedback` | Feedback | float 0.0-1.0 |
| `/param/<s>/highpass` | Highpass | float 0.0-1.0 |
| **Amplifier** | | |
| `/param/<s>/amp/volume` | Volume | float 0.0-1.0 |
| `/param/<s>/amp/pan` | Pan | float 0.0-1.0 |
| `/param/<s>/amp/width` | Width | float 0.0-1.0 |
| `/param/<s>/amp/gain` | VCA gain | float 0.0-1.0 |
| `/param/<s>/amp/vel_to_gain` | Vel→VCA gain | float 0.0-1.0 |
| **Mixer** (replace `<n>` with osc1, osc2, osc3, noise, rm1x2, rm2x3) | | |
| `/param/<s>/mixer/<n>/volume` | Volume | float 0.0-1.0 |
| `/param/<s>/mixer/<n>/mute` | Mute | bool |
| `/param/<s>/mixer/<n>/solo` | Solo | bool |
| `/param/<s>/mixer/<n>/route` | Route | 0-2 |
| `/param/<s>/mixer/prefilter_gain` | Pre-filter gain | float 0.0-1.0 |
| **Envelopes** | | |
| `/param/<s>/aeg/attack` | Amp EG attack | float 0.0-1.0 |
| `/param/<s>/aeg/decay` | Amp EG decay | float 0.0-1.0 |
| `/param/<s>/aeg/sustain` | Amp EG sustain | float 0.0-1.0 |
| `/param/<s>/aeg/release` | Amp EG release | float 0.0-1.0 |
| `/param/<s>/aeg/attack_shape` | Attack shape | 0-2 |
| `/param/<s>/aeg/decay_shape` | Decay shape | 0-2 |
| `/param/<s>/aeg/release_shape` | Release shape | 0-2 |
| `/param/<s>/aeg/mode` | Envelope mode | 0-1 |
| `/param/<s>/feg/attack` | Filter EG attack | float 0.0-1.0 |
| `/param/<s>/feg/decay` | Filter EG decay | float 0.0-1.0 |
| `/param/<s>/feg/sustain` | Filter EG sustain | float 0.0-1.0 |
| `/param/<s>/feg/release` | Filter EG release | float 0.0-1.0 |
| **Waveshaper** | | |
| `/param/<s>/waveshaper/type` | Waveshaper type | int 0-42 |
| `/param/<s>/waveshaper/drive` | Drive | float 0.0-1.0 |
| **LFOs** (replace `<n>` with 1-6 for VLFO, 1-6 for SLFO) | | |
| `/param/<s>/vlfo/<n>/type` | LFO type | int 0-9 |
| `/param/<s>/vlfo/<n>/rate` | Rate | float 0.0-1.0 |
| `/param/<s>/vlfo/<n>/phase` | Phase | float 0.0-1.0 |
| `/param/<s>/vlfo/<n>/amplitude` | Amplitude | float 0.0-1.0 |
| `/param/<s>/vlfo/<n>/deform` | Deform | float 0.0-1.0 |
| `/param/<s>/vlfo/<n>/trigger_mode` | Trigger | 0-2 |
| `/param/<s>/vlfo/<n>/unipolar` | Unipolar | bool |
| `/param/<s>/vlfo/<n>/eg/*` | LFO EG | attack/decay/sustain/release/hold/delay |
| Same structure for SLFO (scene LFOs) | | |
| **FX** (replace `<s>` with a, b, global, send; `<n>` with 1-4) | | |
| `/param/fx/<s>/<n>/type` | FX type | int 0-29 |
| `/param/fx/<s>/<n>/param1` .. `/param/fx/<s>/<n>/param12` | FX params | contextual |
| `/param/fx/<s>/<n>/deactivate` | Bypass slot | bool |
| `/param/fx/send/<n>/return` | Send return level | float 0.0-1.0 |
| **Modulation Mapping** | | |
| `/mod/<source> /param/<target> <depth>` | Map modulator→param | depth -1.0..1.0 |
| `/mod/mute/<source> /param/<target> <mute>` | Mute modulation | bool |
| **Extended options** (append to parameter address) | | |
| `<addr>/abs+` | Absolute mode | bool |
| `<addr>/enable+` | Enable | bool |
| `<addr>/tempo_sync+` | Tempo sync | bool |
| `<addr>/extend+` | Extend range | bool |
| `<addr>/deform+` | Deform | int |
| **Portamento options** | | |
| `/param/<s>/portamento/const_rate+` | Constant rate | bool |
| `/param/<s>/portamento/gliss+` | Glissando | bool |
| `/param/<s>/portamento/retrig+` | Retrigger | bool |
| `/param/<s>/portamento/curve+` | Curve | -1..1 |

**Available MCP tools for Surge (surge_osc_mcp.py):**

| Tool | Description |
|---|---|
| `surge_set_param(instance, address, value)` | Set any OSC parameter |
| `surge_get_param(instance, address)` | Read any OSC parameter |
| `surge_query_all(instance)` | Dump all current parameter values |
| `surge_get_patch(instance)` | Get current patch name |
| `surge_load_patch(instance, path)` | Load patch (absolute path, no extension) |
| `surge_incr_patch(instance)` | Next patch in category |
| `surge_decr_patch(instance)` | Previous patch in category |
| `surge_random_patch(instance)` | Random patch |
| `surge_list_categories()` | List all patch categories |
| `surge_list_patches(category)` | List patches in category |
| `surge_search_patches(query)` | Search patches by name |
| `surge_note_on(instance, pitch, velocity)` | Send MIDI note on |
| `surge_note_off(instance, pitch)` | Send MIDI note off |
| `surge_all_notes_off(instance)` | Release all notes |

---

## Loading Workflow Summary

```
1. Create MIDI track       → create_midi_track(track_index): create_midi_track
2. Set track name          → set_track_name(track_index, name)
3. Load instrument:
   - Native synth          → load_instrument_or_effect(track_index, "query:Synths#Wavetable")
   - Sound preset          → load_instrument_or_effect(track_index, "query:Sounds#Bass:FileId_XXXX")
   - Drum kit              → load_drum_kit(track_index, rack_uri, kit_path)
   - External VST          → load_external_plugin(track_index, "Plugin Name")
4. Configure:
   - Native device params  → set_device_parameter(track_index, device_index, name, value)
   - Surge XT via OSC      → surge_set_param(0, "/param/a/osc/1/cutoff", 0.7)
   - Track volume/pan      → set_track_volume / set_track_panning
```

---

## Quick Reference: Native Ableton Synths URI

| Synth | URI |
|---|---|
| Wavetable | `query:Synths#Wavetable` |
| Analog | `query:Synths#Analog` |
| Drift | `query:Synths#Drift` |
| Operator | `query:Synths#Operator` |
| Collision | `query:Synths#Collision` |
| Electric | `query:Synths#Electric` |
| Tension | `query:Synths#Tension` |
| Simpler | `query:Synths#Simpler` |
| Sampler | `query:Synths#Sampler` |
| Impulse | `query:Synths#Impulse` |
| Drum Rack | `query:Synths#Drum%20Rack` |
| Instrument Rack | `query:Synths#Instrument%20Rack` |
