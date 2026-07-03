# SKILLS.md — Ableton Holland MCP Knowledge Base

> **User profiles & preferences** → see `preferences/David/` (choose `default.md`, `rock.md`, `reggae.md`, or create a new one)

## Audio Routing (Voicemeeter + VB-Cable)

```
Ableton → Voicemeeter VAIO → A1: Enceintes (monitoring)
                            → A2: CABLE Input → CABLE Output → capture
```

Monitoring: A1 = speakers, A2 = CABLE Input (for capture). Buffer: 1024 samples.

## Remote Script Installation

Copy `AbletonMCP_Remote_Script.py` (renamed `__init__.py`) to:
```
C:\ProgramData\Ableton\Live XX\Resources\MIDI Remote Scripts\AbletonMCP\__init__.py
```
Then Options → Preferences → Link, Tempo & MIDI → Control Surface = "AbletonMCP", Input/Output = "None".

## Surge XT OSC Setup

Configure Surge XT with OSC **after** structuring the song with native Ableton plugins:

1. Open Surge XT in Ableton → click the **menu** button (top-left, not "S") → Settings → OSC
2. Enable OSC. Default: IN=53280, OUT=53281
3. Multiple instances: each on stride=2 (instance 1 = IN=53282, OUT=53283, etc.)
4. Max 8 instances. Server sends to Surge's IN, listens on Surge's OUT.

## Conventions

### Track naming
- `1-Instrument`, `2-Instrument`, etc. (prefix with index to maintain order)

### Beat vs measure conversion
- User thinks in **measures (bars)**, API uses **beats**
- 1 measure = 4 beats (in 4/4)
- Always convert: 1 bar = 4.0 beats, 2 bars = 8.0, 4 bars = 16.0, 6 bars = 24.0

### MIDI pitch mapping (Ableton convention: middle C = C3)
- C3=60, D3=62, E3=64, F3=65, G3=67, A3=69, B3=71
- C2=48, D2=50, E2=52, F2=53, G2=55, A2=57, B2=59
- C1=36, D1=38, E1=40, F1=41, G1=43, A1=45, B1=47

### Typical arrangement structure
- Intro (4 bars): drums only → Verse (4-8 bars): bass enters → Verse 2 (4-8 bars): + pads → Buildup/Chorus: + lead, variations → Outro: tutti or fade

## Voice Guide Methodology

### 1. Analyze vocal sample (if available)
```python
load("path/to/recording.mp3")
analyze_full(y_path)
chroma_cqt(y_path)
```

### 2. Determine tessitura from spectral centroid
| Centroid | Range | Suggested offset |
|---|---|---|
| < 800 Hz | Low (baritone/bass) | E3–G3 |
| 800–1200 Hz | Medium (tenor) | G3–C4 |
| > 1200 Hz | High (soprano/alto/falsetto) | C4–E4 |

### 3. Create PAROLES.md with voice guide
For each song section, document:
- Chord progression
- Annotate each lyric line with guide notes: `G3 ◷3` = note G3 held 3 beats, `→` = continuation
- Stay within user's tessitura (E3–B3 for David)
- Follow chord degrees (root, 3rd, 5th) for each guide note
- Short syllables / phrase starts: 1–3 beats → `◷3`
- Phrase endings / keywords: 4–8 beats → `◷5` to `◷8`

### 4. Create voice guide in Ableton
1. Load a clear guide instrument via `load_instrument_or_effect` (Sweet Lead, Shimmer Pluck, Soft Lead — avoid instruments already used)
2. Create one MIDI clip per section with guide notes at correct `start_time`
3. Name clips (`Guide - Couplet 1`, `Guide - Refrain`, etc.)
4. Duplicate to arrangement at section positions

## Mix Translation Guide

### Problem: mix sounds good on headphones but disappears on phone/SM/MP3

### Rules
1. **Saturator on bass (mandatory)**: generates harmonics audible on small speakers
   - Type: Medium Curve (3), Drive: 0.60-0.80, Dry/Wet: 1.0, Color On: 1.0
2. **Compression on drums** (glue): Threshold: 0.30, Ratio: 0.50 (~4:1), Attack: 0.10-0.15, Model: Peak (0), Makeup: On
3. **No element under 0.70 volume** — quiet parts disappear in MP3/social compression
4. **Send reverb as glue** — 0.10-0.25 on multiple tracks unifies mix
5. **Spectral centroid target**: 700-900 Hz (balanced). < 700 = muddy, > 1000 = harsh
6. **Master Limiter** (manual, not via API): Maximizer preset, -1 dB ceiling, max -6 dB reduction

### Platform targets
| Platform | Loudness | Risks |
|---|---|---|
| Spotify | -14 LUFS | Normalization cuts extreme dynamics |
| YouTube | -13 LUFS | Aggressive compression, detail loss |
| TikTok/Insta | ~-14 LUFS | No bass, vocals saturate if too hot |
| Phone | N/A | No < 100 Hz → bass invisible |

### Verification workflow
```python
capture_and_analyze(position_beats=0, duration_sec=20)
# Check: energy_rms > 0.20, dynamic_range_db < 12,
#        spectral_centroid_hz 700-900, spectral_rolloff_hz > 1200
```
Iterate until metrics are satisfactory, then advise user to export WAV 48kHz 24-bit → MP3 320k.

## Surge XT Patch Workflow

### Loading factory patches (preferred over tweaking Init Saw)
1. `surge_list_categories()` → pick category (Basses, Plucks, Pads, Leads, etc.)
2. `surge_list_patches("Basses")` → get patch names + paths
3. `surge_search_patches("warm")` → search all categories
4. `surge_load_patch("C:/...path...without...extension", instance=N)` → load
5. `surge_get_patch(instance=N)` → verify actual loaded patch
6. Use forward slashes `C:/...` (server auto-converts to `\`)
7. Return value may show old template name — ignore, verify with `surge_get_patch`

### Patch selection by style
| Style | Bass | Guitar/Pluck | Pad | Lead | Percs |
|---|---|---|---|---|---|
| Funky/Groovy | Rubber Bass, Fingered | Clean, E-Guitar | MKS-70 Warm Pad, Pad 3 | Moogy Saw, Sine Lead | Synth Tom 1, Drum One |
| Pop/Organic | E-Bass, Mellow | Woody, Guitar | Subtle Comb Strings, Sunday | Classic Lead 2, Soft Sync Saw | Synth Tom 2 |
| Electronic | FM Bass 1, Digibass | Sync Pluck, FM Pluck | Flux Capacitor, Xbox 1 | Classic Lead 1, Acidofil | Kick 909ish, Kick Tech 1 |
| Cinematic | Sub 2, Deep End | Ambient E-Guitar, Bell 1 | Ghost Pad, Still | Vocal Lead, FM Is Growing On Me | Verber |

## Capture & Analysis Workflow

### Solo a track and analyze
```python
set_track_solo(track_index=2)              # solo on
capture_and_analyze(position_beats=64, duration_sec=15, output_name="solo_voix")
set_track_solo(track_index=2, solo=False)   # unsolo
```

### Analyze multiple tracks together
```python
set_track_solo(track_index=0, solo=True)    # Drums
set_track_solo(track_index=1, solo=True)    # Bass
capture_and_analyze(position_beats=64, duration_sec=15, output_name="drums_bass_only")
set_track_solo(track_index=0, solo=False)
set_track_solo(track_index=1, solo=False)
```

### Capture at position
```python
# Atomic (recommended):
capture_and_analyze(position_beats=0, duration_sec=10)
capture_and_analyze(position_beats=32, duration_sec=10, output_name="couplet1")
```

### For > 20s captures, use overlapping segments
```python
capture_and_analyze(position_beats=0, duration_sec=20, output_name="part1")
capture_and_analyze(position_beats=30, duration_sec=20, output_name="part2")
# Calculate overlap: position_beats = duration_sec × (bpm / 60) - overlap_desired_beats
```

## Automation Envelope Workflow

### Set automation curve on a clip
```python
set_automation_curve(
    track_index=0,
    clip_index=0,
    target="device_1_Volume",  # or "volume", "panning", "send_0", "device_0_Device On"
    points=[
        {"time": 0.0, "value": 0},
        {"time": 2.0, "value": 64},
        {"time": 4.0, "value": 127},
    ],
    is_arrangement=False  # False = session clip, True = arrangement clip
)
```

### Parameter target format
| Target | Description | Value range |
|---|---|---|
| `"volume"` | Track mixer volume | 0.0–1.0 |
| `"panning"` | Track mixer panning | 0.0–1.0 |
| `"send_N"` | Send N (e.g. `send_0`) | 0.0–1.0 |
| `"device_N_PARAMNAME"` | Device parameter | 0–127 (raw) |

Example: `device_1_Volume` = device index 1, parameter "Volume" (Grand Piano rack in test project).

### How it works
Each value holds from its time until the next point's time (connected steps). No interpolation between values — this is Live 12's `insert_step()` API, same as Ableton Push.

For a ramp effect, add intermediate points:
```python
points = [
    {"time": 0.0, "value": 0},
    {"time": 1.0, "value": 42},
    {"time": 2.0, "value": 85},
    {"time": 3.0, "value": 127},
]
```

### Read existing automation
```python
get_clip_envelope(
    track_index=0,
    clip_index=0,
    target="device_1_Volume",
    is_arrangement=False
)
```
Returns `target_envelope_points` with `[{time, value}, ...]`.

### Hot-reload after RS changes
```python
reload_script()
```
No Ableton restart needed after updating the Remote Script.

### Value scale
- Device parameters (most): 0–127 raw
- Mixer volume/pan/sends: 0.0–1.0 normalized
- Quantized params: integer index

## Limitations & Troubleshooting

### Known limitations
- Max 8 tracks (Ableton Live Lite), max 16 scenes per track — see `preferences/David/` for full constraints
- `save_project()` is NOT available via Live 12 Lite API. Save manually (Ctrl+S).
- `set_arrangement_time(time)` is imprecise — use `start_playback_at(time)` instead (atomic seek + play)
- `load_instrument_or_effect` can timeout if server is busy. Do NOT run multiple in parallel.
- **Do NOT run multiple captures in parallel** (each does stop/seek/play/record/stop — chaining them crashes)
- **Do NOT chain create/delete track calls too fast** — space between each command to avoid crashes
- First MCP call after opencode startup may timeout (~60s)
- Arrangement API requires Remote Script v1314+, Master API requires v1414+.
- Device parameters with `is_enabled=False` are read-only (skipped)
- Quantized params (dropdown menus) take an integer index
- API writes automation curves via `insert_step()` with connected durations (step automation only, no interpolation)
- Read automation: `get_clip_envelope` returns `target_envelope_points`

### Timeout (-32001) troubleshooting
**Reference:** https://mcpcat.io/guides/fixing-mcp-error-32001-request-timeout

**Capture timeouts:** capture blocks for `duration` seconds. Keep duration ≤ 20s.
**load_instrument_or_effect timeouts:** server saturation. Wait for previous load to finish, one at a time.
**First capture timeout:** librosa JIT-compiles numba functions on first call (~5-15s). Server preloads at startup but if first capture still times out, retry — modules are cached.

### Capture returns "silence"
Check Ableton's Output Device points to "CABLE Input (VB-Audio Virtual Cable)" and playback is active.
