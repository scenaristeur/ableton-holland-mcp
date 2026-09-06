# AGENTS.md — Ableton Holland MCP

## Project Overview

Python-based MCP (Model Context Protocol) server for controlling Ableton Live and Surge XT synthesizer. Two MCP servers:

- **`ableton_full_mcp_server.py`** — controls Ableton Live (tracks, clips, instruments, arrangement) via TCP socket to a Remote Script, plus audio capture via VB-Cable and librosa analysis
- **`surge_osc_mcp.py`** — controls Surge XT via OSC (parameters, patches, MIDI notes), up to 8 instances

Supporting files: `capture_audio.py` (standalone CLI capture), `dashboard/app.py` (Tkinter GUI), `AbletonMCP_Remote_Script.py` (Live MIDI Remote Script in Python 2/3 hybrid).

**Single RS file:** `AbletonMCP_Remote_Script.py` is the source of truth. Deployed to `AbletonMCP/__init__.py` (and `AbletonMCPExtended/__init__.py`).

**Plugin control reference:** See [`PLUGINS.md`](PLUGINS.md) for detailed capabilities of each plugin type.

## Development Workflow

| Command | Description |
|---|---|
| `.venv/Scripts/python -m pip install -r requirements.txt` | Install dependencies |
| `.venv/Scripts/python ableton_full_mcp_server.py` | Start Ableton MCP server |
| `.venv/Scripts/python surge_osc_mcp.py` | Start Surge XT OSC server |
| `.venv/Scripts/python capture_audio.py --help` | Standalone audio capture CLI |
| `python deploy_rs.py` | Copy RS + hot-reload (restart Ableton to be safe) |

### Deploy RS — restart Ableton required
1. Edit `AbletonMCP_Remote_Script.py`
2. Run `python deploy_rs.py` (copies to both RS dirs, clears cache, sends `reload` command)
3. **Restart Ableton.** The `reload` command (`importlib.reload()`) does not reliably pick up script changes — new handlers can be missing or hang. Always restart Ableton after modifying the RS, then reconnect (MCP server auto-reconnects per command).

### Test MCP server changes (no RS change)
1. Stop server (Ctrl+C) → restart: `.venv/Scripts/python ableton_full_mcp_server.py`
2. Test via any MCP client — new tools appear automatically

### When modifying both RS and server
1. Run `python deploy_rs.py` first
2. **Restart Ableton** (applies RS changes)
3. Then restart MCP server

**Linting:** Ruff (no config file, `.ruff_cache/` exists). Run:
```
ruff check .
ruff format .
```
No test framework, no `tests/` directory, no CI, no pre-commit, no `pyproject.toml`.

## Code Style Guidelines

### Imports
Order: (1) `from __future__ import annotations`, (2) standard library, (3) third-party, (4) local. Group by category with blank lines:

```python
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import numpy as np
import librosa
import sounddevice as sd

from fastmcp import FastMCP
```

### Formatting
- 4-space indentation, no tabs
- Two blank lines before top-level functions/classes, one between class methods
- Line length: under 100 chars where readable
- Trailing commas in multi-line function calls and collections
- Use f-strings over `.format()` or `%`

### ASCII Art Section Headers
```python
# ── Session / Transport ─────────────────────────────────────────────────────
```
Use `#` comments (not `"""docstrings"""`) for internal section dividers.

### Types
- Always use `from __future__ import annotations`
- Python 3.10+ syntax: `X | None`, `dict[str, Any]`, `list[dict[str, Any]]`
- Import `Any` from `typing` for dynamic types
- Type hints on ALL function signatures (parameters and return types)

### Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Functions | `snake_case` | `get_session_info`, `capture_ableton` |
| Private helpers | `_snake_case` (leading `_`) | `_send_command`, `_read_y` |
| Classes | `PascalCase` | `AbletonMCP`, `AudioAnalyzer` |
| Constants | `UPPER_SNAKE_CASE` | `HOST`, `PORT`, `TIMEOUT`, `CABLE_DEVICE_ID` |
| Module-level private | `_UPPER_SNAKE_CASE` | `_KK_MAJOR`, `_NOTES` |
| Tool wrappers | `snake_case` with `_tool` suffix | `analyze_full_tool`, `detect_key_tool` |
| Variables | `snake_case` | `track_index`, `wav_path`, `recorded` |

### Error Handling
- **`try/finally`** for resource cleanup (especially sockets)
- **`ValueError`** for invalid parameters
- **`RuntimeError`** for operational failures
- Best-effort init: silent `try/except Exception: pass` for non-critical setup
- Remote Script errors: parse `{"status": "error", "message": "..."}` response and `raise RuntimeError`
- Use `warnings.warn()` (not `print`) for non-fatal conditions inside callbacks

### Docstrings
- Module-level: triple-quoted string after shebang, describing the file
- Tool functions (`@app.tool()`): always have a descriptive docstring (becomes MCP tool description)
- Helper functions: Google-style or plain descriptive. Args/Returns sections optional.
- **No inline comments** unless explaining a non-obvious design decision

### MCP Tool Pattern
```python
app = FastMCP("server-name")

@app.tool()
def my_tool(param1: str, param2: int = 0) -> dict:
    """Description visible to LLM as tool definition."""
    ...
    return {"key": "value"}
```

## Indexing Convention (CRITICAL)
**ALL track and clip indices are 0-based** — matching Live's Python API (`song.tracks[0]` = first track after Master). This applies to every tool parameter named `track_index`, `clip_index`, `device_index`, `chain_index`, `scene_index`, `send_index`.

```
track_index 0 → song.tracks[0] → first session track
clip_index 0   → clip_slots[0]  → first clip slot
device_index 0 → devices[0]     → first device
```

**User-facing communication uses 1-BASED clip/slot numbering.** David numbers clips/slots starting at 1 in the Live UI. When reporting scene positions, slot indices, or asking the user to move clips, always translate to 1-based: `clip_index 0` = « clip 1 », `slot 4` = « slot 5 ». Tool parameters stay 0-based; only the user-facing numbers change.

## Architecture Notes
- Server communicates with Ableton via TCP on port 9877 to `AbletonMCP_Remote_Script.py`
- `_send_command()` sends JSON `{"type": "...", "params": {...}}` and returns parsed response
- Audio capture uses VB-Cable (Voicemeeter) via `sounddevice.InputStream`
- Analysis uses librosa; data saved as WAV → CSV (`.npy` not used)
- RS is Python 2/3 compatible with `try: import Queue` compat shims
- Surge OSC uses `python-osc` with `ThreadingOSCUDPServer` on ports 53281+ (stride=2)
- `create_clip(track, clip, length)` — **length is in BEATS, not bars**. 4/4: 1 bar = 4 beats
- **Arrangement audio clip `gain` is NORMALIZED 0-1, NOT dB** — despite the tool param name `gain`. Passing a dB value (>1.0) → `Gain is out of range`. Reference: 0.4=0dB, 0.506=4.25dB, 0.6=8dB, 0.65=10dB. Verify with `get_arrangement_clips` (`gain_display_string` shows dB)
- **`duplicate_clip_to_arrangement` bar param is OFF BY ONE** — `destination_bar=N` places the clip at `(N-1)*4` beats (1-based bar). `destination_bar=4` lands on beat 12 (bar 3), not bar 4 → overlaps the preceding clip. **Workaround: always use `duplicate_to_arrangement(track, clip, destination_time)` with `destination_time` in beats (0-based, exact).**
- "reload" command hot-reloads the RS via `importlib.reload()` — **unreliable**: new handlers can be missing or hang. Always restart Ableton after modifying the RS.
- Clip automation: use `insert_step(time, duration, value)`. Do NOT use `create_event()` (needs C++ struct)
- `control_coefficients` is read-only
- Automation envelopes on arrangement clips are **write-once**: session→duplicate workflow works, but reading/modifying arrangement envelopes from Python is unreliable

## Diagnostics — CPU / RAM per Track
Live's Python API **does not expose per-track CPU** (the mixer's per-track meter is unavailable). Measure per-track impact by **toggling devices and reading `get_cpu_load`, at REST (playback stopped)**. Available tools:
- `get_cpu_load()` — global CPU (avg/peak) + process RAM (MB)
- `get_cpu_report()` — global CPU+RAM **and** per-track diagnostics for all session tracks
- `get_track_diagnostics(track_index)` — device states (device_on), plugin/rack flags, RAM per track, frozen state

**Measurements are noisy** (~±5 pts at rest); average 3+ reads, and freeze the biggest suspect (e.g. Analog Lab V was +15 pts at rest). Hosted plugin instruments (Surge XT, Analog Lab, Ozone) keep their engine running at rest — the main CPU culprits.

### Device On/Off — use the « Device On » parameter, NOT `is_enabled`
`device.is_enabled` doesn't reliably toggle plugins. The real switch is the **« Device On » parameter**. `enable_device`/`disable_device` now set that parameter via `_device_set_enabled()` (falls back to `is_enabled` if the parameter is absent). For manual control: `set_device_parameter(..., "Device On", 1|0)`.

## Troubleshooting — Silent Audio Capture
**Symptom:** `capture_and_analyze` returns silence (rms ≈ 0, values {−1, 0, +1}).

**Cause:** `CABLE_DEVICE_ID` is a frozen index from `sd.query_devices()` at startup. If Windows audio devices change, the index points to a wrong/silent device.

**Fix:** Restart the MCP server: Ctrl+C → `.venv/Scripts/python ableton_full_mcp_server.py`. The server redetects `CABLE Output` on restart.

## Core Library Kits — Drum Rack imbriqué
**Symptom:** `get_drum_pad_info`/`get_drum_pad_parameters` échoue avec « Only drum racks can have pads! » sur un kit chargé depuis Core Library (ex. Big Break Kit).
**Cause:** les kits .adg de Core Library se chargent comme **`InstrumentGroupDevice`** dont la chain contient le vrai **`DrumGroupDevice`** (les pads vivent là, PAS à la racine du track.devices). Live définit de plus `device.drum_pads` comme propriété qui **lève** cette erreur sur un non-drum device → `hasattr()` est trompeur.
**Fix:** le RS descend désormais dans les chains via `_find_drum_rack()` (check du `class_name` contenant « Drum ») + `_try_drum_pads()` (guard try/except). Cela permet de régler le volume d'un pad individuel (`set_drum_pad_parameter(note=N, "Volume", v)`) sans toucher au rack entier. Ex. charley = note 42, snare = 38, kick = 36.

## Production Constraints — Mix Translation
- **Every mix must be audible on BOTH big speakers (concert/FOH, sub present) AND smartphone speakers (no sub < ~150 Hz, heavy compression, no detail).** These are opposite ends: what makes sound live can be inaudible on a phone and vice-versa.
- **Run a global frequency-distribution analysis on every song** (capture via VB-Cable + spectral analysis: centroid, rolloff, band energy). The midrange (200 Hz – 4 kHz) carries intelligibility everywhere; bass content that lives only in the sub disappears on phone.
- Tactics: saturate the low end to generate harmonics (Saturator on bass = "virtual sub"); HPF everything non-kick/bass at ~150-200 Hz; master limiter ~ -1 dB ceiling; target spectral centroid ~700-900 Hz (balancé : <700 boue, >1000 agressif).
- Always verify the full mix spectrum (not just solo'd tracks) before delivery.

## Mix Discoveries — « Melody's Ghost » (2026-08-17)
- **Surge XT = le gros CPU** : le patch `House Organ` saturait à ~100% en jeu (dropouts = « tonnerre » en fins de mesures). Remplacer par un patch plus léger (**`Organ 1`**) + **poly ~8/6** → ~40-46% en jeu. Le coût est **par voix** (nombre d'osc/unison du patch), pas la polyphonie maximale — réduire l'unison d'un oscillateur suffit rarement seul.
- **CPU global inutilisable au repos pour isoler une piste** (bruité ~±5 pts). Mesure fiable : **en jeu, en solo, une piste à la fois** (Pads seul = 100%+, preuve que c'était LE coupable).
- **FX internes Surge** : `fx/chain_bypass=1` = "No Send FX" (coupe seulement les send). Pour couper TOUT, passer à **3 (All FX Off)** PUIS vider les slots (`fx/*/type=0`). Tout reload du patch réinstancie les FX → revérifier après charge.
- **Ne jamais inventer un groove drums « à l'aveugle »** : les espacements/cre-scendo improvisés (kick sparse, `pont narrac cresc`) créent un **faux contre-temps inadapté**. Réutiliser un pattern vivant existant (humanisé : vélocités variables + micro-décalages) plutôt que réécrire à l'aveugle. Humaniser = varier vélosité + léger décalage timing, PAS changer la densité.
- **`set_arrangement_clip_notes` AJOUTE des notes au lieu de remplacer** → crée des doublons. Workflow sûr : recréer un clip session (create_clip à la bonne longueur) + notes, puis `duplicate_to_arrangement`. Ne pas utiliser set_arrangement_clip_notes pour remplacer.
- **Voix baryton** : HPF ~85Hz + présence ~3-4kHz + air ~6kHz (gain léger 0.55-0.6) font monter le centroid couplet 226→791 Hz (dans la cible 700-900). Utile pour smartphone. Dosage fin à l'oreille (trop d'air = voix écrasante).

## Mix Discoveries — « Un jour avec les oiseaux » (2026-08-08)
- **Solo captures understate low drums** : Choir Drums solo RMS 0.057 but sits fine in context — don't over-boost quiet solo readings alone; verify in full mix.
- **Bird-lead tracks are top-heavy** : Lead/Alto/Tenor centroids 3210-4104 Hz. A bird-choir centrepiece naturally pushes the global centroid high (2800 Hz+). Rebalance via **cutting the low end of the pad** (EQ Three GainLo 0.5) and **boosting bass mid** (GainMid 1.0 + Saturator Medium Curve Drive 0.65 Dry/Wet 0.75) rather than attenuating the birds (the lead IS the melody).
- **ClubHouse 4-on-floor** : adding a kick on beats 2&4 (vel ~82 vs 100 on 1&3) to a funk groove instantly reads as a dance beat without rewriting the pattern — cheapest way to flip a section to disco without a full house drum rebuild.
- **Master chain (Live Lite)** : Compressor glue (Threshold 0.7 / Ratio 0.4 / Release 0.3) → Limiter True Peak (Lookahead 3 ms / Ceiling 0.95) → master fader at 1.0. Dropped global Chœur centroid 2881→2380 Hz while keeping RMS ~0.14.

## What NOT To Do
- Do NOT create new files when editing an existing one suffices
- Do NOT add inline comments explaining obvious code
- Do NOT add emojis to source files or documentation
- Do NOT run multiple `capture_and_analyze` calls at once — send one, wait for response
- Do NOT run multiple `load_instrument_or_effect` calls in parallel
- Do NOT modify `AbletonMCP_Remote_Script.py` without understanding Python 2/3 dual compatibility
- Do NOT guess file paths or module names — verify imports in the actual codebase
- Do NOT use `create_event()` — it requires a C++ struct `TEnvelopeEvent` (inaccessible)
- Do NOT set `control_coefficients` — it's read-only
- Do NOT apply a documented FX chain (§4-style or preset copies) "blind" via device parameters — plugin params are normalized 0-1 with **unverified mapping**, and preset copies can swallow the signal entirely (e.g. Saturator « Hot Tubes » Color made a vocal inaudible). Always: put the chain in a transparent state first, verify the audio is audible/clean, then sculpt by ear. Doc chains are **EXAMPLES to adapt per song**, not recipes
- Do NOT trust normalized parameter values (threshold/ratio/attack/release/plugin freqs) as physical values — no reliable mapping exists via the API; set approximate values and have the user verify by ear
- Do NOT trust `device.is_enabled` alone to toggle plugins — use the « Device On » parameter instead (see Diagnostics above)
- Do NOT invent drum grooves "blind" (sparse/cre-scendo patterns) — they create off-beat artifacts; reuse an existing humanized pattern (varying velocities + slight timing offsets) instead
- Do NOT use `set_arrangement_clip_notes` to replace existing notes — it ADDS duplicates; recreate a session clip (create_clip to correct length) + notes, then `duplicate_to_arrangement`
- Do NOT run `deploy_rs.py` if Ableton isn't running (safe, but reload will timeout)
