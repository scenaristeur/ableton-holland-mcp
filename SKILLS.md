# SKILLS.md — Ableton Holland MCP Knowledge Base

> **User profiles & preferences** → see `preferences/David/` (choose `default.md`, `rock.md`, `reggae.md`, or create a new one)
>
> **Plugin control reference** → see [`PLUGINS.md`](PLUGINS.md) for detailed capabilities of each plugin type (native synths, external VSTs, Surge XT via OSC) and how to control them.

## Setup & Conventions

### Audio Routing (Voicemeeter + VB-Cable)

```
Ableton → Voicemeeter VAIO → A1: Enceintes (monitoring)
                            → A2: CABLE Input → CABLE Output → capture
```

Monitoring: A1 = speakers, A2 = CABLE Input (for capture). Buffer: 1024 samples.

### Remote Script Installation

Copy `AbletonMCP_Remote_Script.py` (renamed `__init__.py`) to:
```
C:\ProgramData\Ableton\Live XX\Resources\MIDI Remote Scripts\AbletonMCP\__init__.py
```
Then Options → Preferences → Link, Tempo & MIDI → Control Surface = "AbletonMCP", Input/Output = "None".

### Hot-reload (no restart)

```python
reload_script()
```
Changes apply immediately after running `deploy_rs.py`.

### Surge XT OSC Setup

Configure Surge XT with OSC **after** structuring the song with native Ableton plugins:

1. Open Surge XT in Ableton → click the **menu** button (top-left, not "S") → Settings → OSC
2. Enable OSC. Default: IN=53280, OUT=53281
3. Multiple instances: each on stride=2 (instance 1 = IN=53282, OUT=53283, etc.)
4. Max 8 instances. Server sends to Surge's IN, listens on Surge's OUT.

### Indexing Convention (CRITICAL)

**ALL track/clip/device/scene/send indices are 0-based** — matching Live's Python API.

```
track_index 0 → song.tracks[0] → first session track
clip_index 0   → clip_slots[0]  → first clip slot
device_index 0 → devices[0]     → first device
```

### Beat vs measure conversion

- 1 measure = 4 beats (in 4/4)
- `time` params in the API are in **beats**
- Convert: 1 bar = 4.0 beats, 2 bars = 8.0, 4 bars = 16.0, 6 bars = 24.0

### MIDI pitch mapping (Ableton convention: middle C = C3)

| Octave | C | D | E | F | G | A | B |
|--------|---|---|---|---|---|---|---|
| 3 | 60 | 62 | 64 | 65 | 67 | 69 | 71 |
| 2 | 48 | 50 | 52 | 53 | 55 | 57 | 59 |
| 1 | 36 | 38 | 40 | 41 | 43 | 45 | 47 |

### Track naming convention

- `1-Instrument`, `2-Instrument`, etc. (prefix with index to maintain order)

### Typical arrangement structure

- Intro (4 bars): drums only → Verse (4-8 bars): bass enters → Verse 2 (4-8 bars): + pads → Buildup/Chorus: + lead, variations → Outro: tutti or fade

### Instrument loading priority

1. Drum Rack / kits natifs Ableton (browser > drums) pour percussions
2. Synthés natifs (Wavetable, Analog, Drift, Operator) pour basses, nappes, leads
3. Packs Core Library (Piano & Keys, Strings, etc.) pour instruments acoustiques
4. Surge XT uniquement si introuvable dans les natifs

Browser URIs :
- Synthés : `query:Synths#Wavetable`, `query:Synths#Analog`, `query:Synths#Drift`
- Drums : `query:Drums#Drum%20Rack` (device), `query:Drums#FileId_XXXX` (kit)
- Sons : `query:Sounds#Piano%20&%20Keys`, `query:Sounds#Strings`
- Plugins : `plugins/VST3/Surge Synth Team/Surge XT`

---

## Workflows

### Voice Guide Methodology

1. **Analyze vocal sample** (if available):
```python
load("path/to/recording.mp3")
analyze_full(y_path)
chroma_cqt(y_path)
```

2. **Determine tessitura from spectral centroid**:

| Centroid | Range | Suggested offset |
|---|---|---|
| < 800 Hz | Low (baritone/bass) | E3–G3 |
| 800–1200 Hz | Medium (tenor) | G3–C4 |
| > 1200 Hz | High (soprano/alto/falsetto) | C4–E4 |

3. **Create PAROLES.md**: document chord progression + annotate each lyric line with guide notes (`G3 ◷3` = note G3 held 3 beats)
   - Stay within user's tessitura (E3–B3 for David)
   - Follow chord degrees (root, 3rd, 5th) for each guide note
   - Short syllables / phrase starts: 1–3 beats → `◷3`
   - Phrase endings / keywords: 4–8 beats → `◷5` to `◷8`

4. **Create voice guide in Ableton**:
   - Load a clear guide via `load_instrument_or_effect` (Sweet Lead, Shimmer Pluck, Soft Lead)
   - Create one MIDI clip per section with guide notes
   - Name clips (`Guide - Couplet 1`, etc.)
   - Duplicate to arrangement at section positions

### Mix Translation Guide

**Problem**: mix sounds good on headphones but disappears on phone/SM/MP3.

**Core philosophy**: chaque élément doit être audible même sur des petites enceintes (téléphone, autoradio). Cela passe par :
1. **Harmoniques** : saturer les basses pour créer des partiels audibles sans subwoofer
2. **Midrange** : éviter les extrêmes (subs trop graves, aigus trop fins) — le médium = l'essentiel sur petit haut-parleur
3. **Écoute multi-support** : tester sur téléphone, autoradio, petites enceintes, pas seulement au casque

#### Harmonics Strategy (obligatoire pour translation)

| Track | Traitement | Pourquoi |
|---|---|---|
| **Bass** | Saturator (Medium Curve, Drive 0.6-0.8) | Génère des harmoniques supérieures audibles sur haut-parleur 3" |
| **Lead/Keys/Pad** | EQ bas coupé à 150-200 Hz | Enlève le mud, donne de l'air |
| **Drums** | Compressor (glue) + EQ | Colle le kit, enlève le bruit de fond |
| **FX/Drift** | Reverb + EQ | Donne de l'espace, coupe les basses inutiles |
| **Master** | Limiter (max -6 dB reduction, -1 dB ceiling) | Élève le niveau général sans écrêtage violent |

**Pourquoi Saturator sur la basse est critique** : un petit haut-parleur (< 10 cm) ne reproduit pas les fréquences < 150 Hz. La basse devient inaudible. Le Saturator crée des harmoniques dans le médium (200-1000 Hz) qui "suggèrent" la note de basse même si le fondamental est absent. Sans ça, le morceau sonne vide sur téléphone.

#### Volume Balancing Method (éprouvé sur "Holland")

1. Solo chaque piste individuellement sur une section énergétique représentative (ex: chorus final)
2. Capturer ~4 secondes avec `capture_and_analyze`
3. Noter `energy_rms` de chaque piste
4. Ajuster les volumes pour que chaque RMS soit ~0.07-0.10 pour les lead, ~0.17-0.25 pour le full mix
5. **Ne pas hésiter à monter le volume** — un mix à RMS 0.17 est sain pour l'électro (les calculs de ratio brut ne tiennent pas compte du masquage fréquentiel)
6. Vérifier le full mix RMS ~0.15-0.25 pour un rendu percutant

#### EQ Carving (prévention du masquage)

Quand plusieurs instruments jouent simultanément, ils se disputent les mêmes fréquences. Solution : créer une "niche" pour chaque instrument :

| Fréquence | Qui occupe | Qui doit être réduit |
|---|---|---|
| 50-100 Hz | Kick + Basse | Conflit : sidechain ou EQ complémentaire |
| 200-400 Hz | Basse + Keys | Keys/Pad : HPF à ~200 Hz |
| 1-4 kHz | Présence Lead | Keys/Pad : léger cut à 2 kHz |
| 5-8 kHz | Air/hats | Lead : légère atténuation |

Règle simple : **HPF à 150-200 Hz sur tous les instruments sauf kick et basse**.

#### Règles définitives pour translation multi-support

1. **Saturator on bass (mandatory)**: génère des harmoniques audibles sur petites enceintes
   - Type: Medium Curve (3), Drive: 0.60-0.80, Dry/Wet: 1.0, Color On: 1.0
2. **Compression on drums** (glue): Threshold: 0.30, Ratio: 0.50 (~4:1), Attack: 0.10-0.15, Model: Peak (0), Makeup: On
3. **No element under audible volume** — un élément trop bas disparaît sur MP3/compression social media. Laisser le volume monter si le mix global reste sous 0 dB crête.
4. **HPF 200 Hz** sur Keys, Pad, FX (tout ce qui n'a pas besoin de sub)
5. **Send reverb as glue** — 0.10-0.25 sur plusieurs pistes unifie le mix
6. **Spectral centroid target**: 700-900 Hz (balanced). < 700 = muddy, > 1000 = harsh
7. **Master Limiter** (manual, not via API): Maximizer preset, -1 dB ceiling, max -6 dB reduction

**Platform targets**:

| Platform | Loudness | Risks |
|---|---|---|
| Spotify | -14 LUFS | Normalization cuts extreme dynamics |
| YouTube | -13 LUFS | Aggressive compression, detail loss |
| TikTok/Insta | ~-14 LUFS | No bass, vocals saturate if too hot |
| Phone speaker | N/A | No < 150 Hz → bass harmonics mandatory |
| Car stereo | varies | Bass-heavy → peut masquer le médium |

**Verification**:
```python
capture_and_analyze(position_beats=0, duration_sec=20)
# Check: energy_rms > 0.15, dynamic_range_db 10-15,
#        spectral_centroid_hz 700-900, spectral_rolloff_hz > 1200
```
Iterate until metrics satisfactory, then advise user to export WAV 48kHz 24-bit → MP3 320k.

**Charger des plugins via MCP** (EQ Three, Saturator, Compressor) :
> **Note Live Lite :** EQ Eight n'existe PAS sur Live Lite (réservé Standard/Suite). Utiliser **EQ Three** (3 bandes : Lo/Mid/Hi, gains ±15 dB) ou **MEqualizer** (VST tiers, déjà en place sur les pistes voix).
```python
# Charger un EQ Three sur une piste (Live Lite, remplace EQ Eight)
load_instrument_or_effect(track_index=N, uri="query:AudioFx#EQ%20Three")
# Charger un Saturator
load_instrument_or_effect(track_index=N, uri="query:AudioFx#Saturator")
# Charger un Compressor
load_instrument_or_effect(track_index=N, uri="query:AudioFx#Compressor")
# Charger un Reverb (send/return ou directement sur piste)
load_instrument_or_effect(track_index=N, uri="query:AudioFx#Reverb")
```

### Audio Process Chain Methodology (FX Chains & Device Params)

**Règle n°1 : les chaînes documentées (ex. §4 des fiches chansons) sont des EXEMPLES, PAS des recettes.** Chaque chanson / chaque prise demande des réglages différents. Ne jamais appliquer une chaîne ou un preset « à l'aveugle » via les paramètres devices.

**Procédure (éprouvée sur « Rouge », août 2026) :**
1. Poser la chaîne en état **transparent** (EQ neutralisé, comp léger ou off, saturation Drive 0 / Color off).
2. **Vérifier que l'audio s'entend proprement** AVANT de sculpter.
   - Retour d'expérience « Rouge » : le **Saturator** a littéralement *effacé* la voix (quasi silence) à **Drive 0 + Dry/Wet 100 %** avec type « Soft Sine / Hot Tubes » + Color On — pas « sombre », mais zéro signal audible.
   - Recette éprouvée pour une voix « grattée » sans l'effacer : Type **Analog Clip**, Drive ≈ −3 dB (norm ~0.46), Dry/Wet ≈ 35 % (norm ~0.33), **Color off**, Post Clip **Soft**, Output 1.0.
3. Sculpter ensuite à l'oreille, section par section (couplet sec, refrain large), jamais à l'aveugle.

**Limite API :** les paramètres devices (plugins et natifs) sont exposés en **normalisé 0-1 sans mapping physique fiable** → ne pas traiter `threshold`, `ratio`, `attack`, `release`, fréquences EQ comme des valeurs Hz/dB réelles. Les valeurs écrites sont des approximations : à faire valider à l'oreille par l'utilisateur.

**Ancre normalisée (Compressor natif) :** ratio 0.50 ≈ 4:1, attack 0.10–0.15 ≈ attaque rapide, threshold 0.30 = glue forte. Servir d'ancrage, doser selon l'entrée réelle.

**Gain staging d'abord :** des clips audio chauds (+12/+14 dB) + Makeup auto sur-compressent ; poser un gain de tête propre avant tout traitement (Utility ou gain de clip).

### Surge XT Patch Workflow

1. `surge_list_categories()` → pick category (Basses, Plucks, Pads, Leads, etc.)
2. `surge_list_patches("Basses")` → get patch names + paths
3. `surge_search_patches("warm")` → search all categories
4. `surge_load_patch("C:/...path...without...extension", instance=N)` → load
5. `surge_get_patch(instance=N)` → verify actual loaded patch
6. Use forward slashes `C:/...` (server auto-converts to `\`)
7. Return value may show old template name — ignore, verify with `surge_get_patch`

**Modulation routing** via `surge_map_modulation`:

```python
surge_map_modulation(
    mod_source="a/vlfo_1/0",       # LFO source
    target="/param/a/filter/1/cutoff",  # target param
    depth=0.4,                      # -1.0 to 1.0 (0 = disconnect)
    instance=0,
)
```

Sources disponibles :
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
| `rand_bi/0` | Random Bipolar (Uniform) |
| `rand_uni/0` | Random Unipolar (Uniform) |
| `macro_1` .. `macro_8` | Macros |

Déconnecter : `surge_unmap_modulation(mod_source, target, instance)`

**Limitations OSC connues** : arpégiateur, wavetable selection, et filter subtypes non exposés via OSC. À configurer manuellement dans l'UI Surge XT.

**Patch selection by style**:

| Style | Bass | Guitar/Pluck | Pad | Lead | Percs |
|---|---|---|---|---|---|
| Funky | Rubber Bass, Fingered | Clean, E-Guitar | MKS-70 Warm Pad, Pad 3 | Moogy Saw, Sine Lead | Synth Tom 1, Drum One |
| Pop/Organic | E-Bass, Mellow | Woody, Guitar | Subtle Comb Strings, Sunday | Classic Lead 2, Soft Sync Saw | Synth Tom 2 |
| Electronic | FM Bass 1, Digibass | Sync Pluck, FM Pluck | Flux Capacitor, Xbox 1 | Classic Lead 1, Acidofil | Kick 909ish, Kick Tech 1 |
| Cinematic | Sub 2, Deep End | Ambient E-Guitar, Bell 1 | Ghost Pad, Still | Vocal Lead, FM Is Growing On Me | Verber |

### Capture & Solo Analysis

**Single track solo**:
```python
set_track_solo(track_index=2)              # solo on
capture_and_analyze(position_beats=64, duration_sec=15, output_name="solo_voix")
set_track_solo(track_index=2, solo=False)   # unsolo
```

**Multiple tracks together**:
```python
set_track_solo(track_index=0, solo=True)    # Drums
set_track_solo(track_index=1, solo=True)    # Bass
capture_and_analyze(position_beats=64, duration_sec=15, output_name="drums_bass_only")
set_track_solo(track_index=0, solo=False)
set_track_solo(track_index=1, solo=False)
```

**Capture at position**:
```python
capture_and_analyze(position_beats=0, duration_sec=10)
capture_and_analyze(position_beats=32, duration_sec=10, output_name="couplet1")
```

**For > 20s captures, use overlapping segments**:
```python
capture_and_analyze(position_beats=0, duration_sec=20, output_name="part1")
capture_and_analyze(position_beats=30, duration_sec=20, output_name="part2")
```

### Automation Envelope Workflow

**Set automation curve**:
```python
set_automation_curve(
    track_index=0,
    clip_index=0,
    target="device_1_Volume",  # or "volume", "panning", "send_0"
    points=[
        {"time": 0.0, "value": 0},
        {"time": 2.0, "value": 64},
        {"time": 4.0, "value": 127},
    ],
    is_arrangement=False  # False = session, True = arrangement
)
```

**Parameter target reference**:

| Target | Description | Value range |
|---|---|---|
| `"volume"` | Track mixer volume | 0.0–1.0 |
| `"panning"` | Track mixer panning | 0.0–1.0 |
| `"send_N"` | Send N (e.g. `send_0`) | 0.0–1.0 |
| `"device_N_PARAMNAME"` | Device parameter | 0–127 (raw) |

**Read existing automation**:
```python
get_clip_envelope(track_index=0, clip_index=0, target="device_1_Volume", is_arrangement=False)
```

**Add individual points**:
```python
add_clip_envelope_point(track_index=0, clip_index=0, target="device_1_Volume", time=2.0, value=64, duration=0, is_arrangement=False)
```

**Clear envelope**:
```python
clear_clip_envelope(track_index=0, clip_index=0, target="device_1_Volume", is_arrangement=False)
```

**Live 12 Lite automation API limitations**:

| Ce qui marche ✅ | Ce qui ne marche PAS ❌ |
|---|---|
| Session clips : `set_automation_curve` écrit + lit via `events_in_range()` | `automation_envelope(param)` sur clip MIDI arrangement → `None` |
| `duplicate_clip_to_arrangement` copie les enveloppes (visible UI) | `create_automation_envelope(param)` sur clip MIDI arrangement → exception |
| Lecture API des enveloppes d'arrangement → impossible |

### Device Management

**Enable/disable**:
```python
enable_device(track_index=0, device_index=1)
disable_device(track_index=0, device_index=1, device_name="EQ Three")
```

**Navigate presets**:
```python
navigate_device_preset(track_index=0, device_index=1, direction="next")
navigate_device_preset(track_index=0, device_index=1, direction="previous")
```

**Inspect chains**:
```python
get_chain_info(track_index=0, device_index=1)              # list chains
get_chain_info(track_index=0, device_index=1, chain_index=1)  # devices in chain
```

**Drum pads**:
```python
get_drum_pad_info(track_index=0, device_index=1)  # list filled pads
```

### View Control

```python
set_ableton_view("Arranger")           # Arranger, Session, Detail, Detail/Clip, Detail/DeviceChain, Browser
control_arrangement_view("zoom_in")    # zoom_in, zoom_out, scroll_left, scroll_right
control_arrangement_view("follow_on")  # follow_on, follow_off
control_arrangement_view("collapse_track", track_index=2)
```

### Cue Points

```python
get_cue_points()
create_cue_point(bar=9, name="Verse 1")
jump_to_cue_point(name="Verse 1")
jump_to_cue_point(direction="next")
delete_cue_point(bar=9)
```

### Routing

```python
get_track_routing(track_index=0)
set_track_input_routing(track_index=0, routing_type="Ext. In", channel="1")
set_track_output_routing(track_index=0, routing_type="Sends Only")
```

### Arrangement Loop

```python
set_arrangement_loop(enabled=True, start_bar=1, end_bar=17)
```

### Audio Clip Parameters (warp / gain / pitch / markers)

Les paramètres du panneau clip audio (warp, gain, pitch, markers) s'accèdent sur les **clips d'arrangement** via `get_arrangement_clips` puis les setters dédiés :

```python
clips = get_arrangement_clips(track_index=7)   # clip_index = index 0-based dans la liste
set_arrangement_clip_gain(track_index=7, clip_index=0, gain=0.65)
set_arrangement_clip_pitch(track_index=7, clip_index=0, coarse=0, fine=0)
set_arrangement_clip_warp(track_index=7, clip_index=0, warp_on=True, warp_mode=0)
set_arrangement_clip_markers(track_index=7, clip_index=0, start_marker=..., end_marker=...)
set_arrangement_clip_name(track_index=7, clip_index=0, name="Audio 6")
```

**⚠️ Le gain clip est NORMALISÉ 0-1, PAS en dB** — alors que le paramètre du wrapper s'appelle `gain` et que Live affiche `gain_display_string` en dB. Références mesurées :

| Normalisé | dB affiché |
|---|---|
| 0.4 | 0.00 dB |
| 0.506 | 4.25 dB |
| 0.6 | 8.00 dB |
| 0.65 | 10.0 dB |

- Passer une valeur en dB (> 1.0) → erreur `Gain is out of range` (l'API Live rejette tout `clip.gain` > 1.0).
- `get_arrangement_clips` retourne `gain` (normalisé) + `gain_display_string` (dB) pour vérifier.
- Exemple réel (Brain Stew, 2026) : pour compenser une voix qui baissait au milieu, gain clip 0.506 → **0.65** (4.25 → 10 dB) + Limiter en fin de chaîne.

---

## Limitations & Troubleshooting

### Known limitations

- Max 8 tracks (Ableton Live Lite), max 16 scenes per track
- `save_project()` NOT available via Live 12 Lite API. Save manually (Ctrl+S).
- `set_arrangement_time(time)` is imprecise — use `start_playback_at(time)` instead
- `load_instrument_or_effect` can timeout if server is busy. **Do NOT run multiple in parallel.**
- **Do NOT run multiple captures in parallel** (each does stop/seek/play/record/stop)
- **CPU hog constaté (Rouge, 2026) :** Surge XT coûte ~+35 points de CPU en lecture, même sur une piste MUTÉE (le device tourne quand même). Si un VST/device sature le CPU : `get_cpu_load` pendant la lecture, `disable_device` un par un pour isoler. Piste guide = outil de prod → disabler Surge XT après enregistrement. Freeze/Flatten les Drum Racks lourds.
- **Do NOT chain create/delete track calls too fast**
- First MCP call after startup may timeout (~60s)
- Device parameters with `is_enabled=False` are read-only (skipped)
- Quantized params (dropdown menus) take an integer index
- API writes automation curves via `insert_step()` with connected durations (step automation only)

### Timeout (-32001) troubleshooting

**Reference:** https://mcpcat.io/guides/fixing-mcp-error-32001-request-timeout

**Capture timeouts:** capture blocks for `duration` seconds. Keep duration ≤ 20s.
**load_instrument_or_effect timeouts:** server saturation. Wait for previous load to finish.
**First capture timeout:** librosa JIT-compiles numba functions on first call (~5-15s). Retry after startup.

### Capture returns "silence"

Check Ableton's Output Device points to "CABLE Input (VB-Audio Virtual Cable)" and playback is active.

---

## Song: "Masculinisme" — Structure finale v3

Order: **Rock (128) → Montée (128) → Trap (128)** — tout à 128 BPM, pas de changement de tempo

| Section | Mesures | Tracks actifs | Paroles | Énergie |
|---|---|---|---|---|
| Intro | 1-6 | Drums + Basse | — | Faible |
| Couplet 1 (Rock) | 7-14 | Pads + Drums + Basse + Voix | "Hé mec, fais gaffe..." | Moyenne |
| Refrain 1 (Rock) | 15-24 | Pads + Drums + Basse + Voix | "Oui, je sais..." | Haute |
| Couplet 2 (Montée) | 25-36 | Pads + Drums + Basse + Voix + Arp (m.33) | "Tu sais, c'est pas nouveau..." | Croissante |
| Build-up | 37-40 | Pads (E9 hold) + Basse (tenue) + Drums (build) + Arp (riser) | — | Très haute |
| Montée Refrain | 41-48 | Pads + Drums + Basse + Arp + Voix | "Oui, je sais..." | Maximale |
| Couplet 3 (Trap) | 49-56 | Drums trap + 808 + Trap Pads + Arp + Voix | "Si ça colle, essayez..." | Climax |
| Pont (Trap) | 57-64 | Drums trap + 808 + Trap Pads + Arp + Voix | "Quand ça ne colle pas..." | Climax |
| Refrain (Trap) | 65-72 | Drums trap + 808 + Trap Pads + Arp + Voix | "Oui, je sais..." | Apogée |
| Outro | 73-76 | Pads + Basse + Arp (fade) | "Tu es un explorateur..." | Descente |

### Track mapping

| Track | Name | Instrument | Usage |
|---|---|---|---|
| 0 | 1-Pads | E-Piano Wurli | Rock chords + Montée + build E9 hold |
| 1 | 2-Drums | Vintage Funky GT | Rock rhythm → Montée build → Trap drums |
| 2 | 3-Basse | JX Chorus Bass | Rock bass → held E build → 808 sub |
| 3 | 4-Voix | Audio track | Vocals (to record) |
| 4 | 5-Trap Pads | Say It Bass Lead | Trap nappes only (Fmaj7→Dm9) |
| 5 | 6-FX | Audio track | Crash samples (manual import) |
| 6 | 7-Arp | Classic Club Saw + Arpeggiator | Montée arp (m.33) + riser → Trap arp |
| 7 | 8-Guide vocal | (load instrument manually) | Guide chant MIDI avec notes guides |
