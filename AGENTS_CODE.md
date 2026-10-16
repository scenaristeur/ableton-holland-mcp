# AGENTS_CODE.md — Référence technique (code, déploiement, pièges API)

> Doc **d'ingénierie**, pas le manuel de production. Pour mon rôle et la méthode de travail,
> voir `AGENTS.md`. Je n'ouvre ce fichier que si je dois toucher au code, déployer le Remote
> Script, ou déboguer un appel qui échoue.

## What this is

Two MCP servers that drive a **running Ableton Live 12 Lite** instance and **Surge XT**:

- **`ableton_full_mcp_server.py`** (~2000 lines, 145 tools) — Ableton control + audio capture/analysis.
- **`surge_osc_mcp.py`** — Surge XT via OSC, up to 8 instances (IN 53280+2n / OUT 53281+2n).

`AbletonMCP_Remote_Script.py` (~5000 lines) is the **Remote Script** that actually runs inside
Ableton. It is the source of truth for every Ableton-side operation.

`opencode.jsonc` wires both servers to opencode, but it is **gitignored** — MCP config is local-only.

## Commands

```bash
.venv/Scripts/python ableton_full_mcp_server.py    # Ableton MCP server
.venv/Scripts/python surge_osc_mcp.py              # Surge OSC MCP server
.venv/Scripts/python dashboard/app.py              # Tkinter capture/analysis GUI
.venv/Scripts/python capture_audio.py --help       # standalone capture CLI
.venv/Scripts/python -m ruff check .               # lint  (ruff is NOT on PATH)
.venv/Scripts/python -m ruff format .              # format
```

**`requirements.txt` is incomplete — do not trust it for a fresh venv.** It omits
`fastmcp`, `librosa`, `python-osc`, `mido`, `comtypes`, `ruff` (all present in `.venv`), and lists
`plotly` / `matplotlib`, which nothing in the repo imports. Install those explicitly if you rebuild
the venv.

**No test framework, no CI, no `pyproject.toml`.** The root `test_*.py` files are **not** tests:
they are hand-run TCP probes that talk straight to the RS on port 9877 and **mutate the loaded
set** (they set device params, insert envelope points, clear envelopes; `TRACK=0`, `CLIP=0`,
`TARGET="device_1_Volume"` hardcoded). Never run them without asking — they will damage a set.
`test_tcp.py` is at least safe-ish: `python test_tcp.py <command> [k=v ...]`.

## Deploy the Remote Script — then restart Ableton

```bash
.venv/Scripts/python deploy_rs.py
```

Copies **three** files into each of 5 existing `AbletonMCP` Remote Script dirs
(`ProgramData\Ableton\Live 12 Lite\...`, several `%APPDATA%\Live 12.4.x\...`, and
`Documents\Ableton\User Library\...`):

1. `AbletonMCP_Remote_Script.py` → `__init__.py`
2. `midi_mappings.py` → same dir (imported by the RS)
3. `midi_mappings_config.json` → same dir (persistent MIDI-map config)

`AbletonMCPExtended` is **deliberately not deployed** (old script). Do not add it.

Then clears `__pycache__` and sends a `reload` command. **Restart Ableton anyway.** `reload` does
`importlib.reload()` + rebinds `self.__class__` on the live instance, which leaves the socket server
thread and client handlers as the *old* objects — new handlers go missing or hang. Restart is the
only reliable path. If Ableton isn't running, the copy still happens; the reload times out (safe).

Editing `midi_mappings.py` or `midi_mappings_config.json` **also requires `deploy_rs.py`**.

## Architecture

```
MCP tool  →  _cmd(type, **params)  →  TCP 127.0.0.1:9877  →  RS _process_command  →  Ableton API
```

- Every tool call opens a **new TCP socket** and closes it in `finally`. No pooling, no retry.
- Wire format: raw JSON, **no length prefix**. RS framing is "recv, try `json.loads`, on
  `ValueError` keep reading" — it clears the buffer after one successful parse, so **one command
  per connection**. Don't pipeline.
- Response: `{"status": "success"|"error", "result": {...}, "message": "..."}`. The client raises
  `RuntimeError(message)` on `error`, else returns `result`.
- The RS is **purely reactive** (socket thread, no timer/poll loop). State-mutating commands are
  marshalled to Ableton's main thread via a hardcoded allowlist + `schedule_message`, and the socket
  thread blocks on a response queue. Default timeout 10 s; 30 s for `set_automation_lanes`,
  60 s `create_audio_clip`, 120 s `load_instrument_or_effect` / `load_browser_item`.
- **There are no locks or concurrency guards anywhere in the Ableton server.** Two overlapping
  calls race on singleton playback state. Send capture and load calls **one at a time**.

### Two transport details that bite

**`start_playback_at` ordering is load-bearing.** Live's `start_playing()` *resets*
`current_song_time` to 0, so `set_time → start_playing` never lands on the right beat. The RS
(RS:1446) does it the other way round: `song.start_playing()` **then**
`song.current_song_time = value`. The tool docstring calling it "atomic" is wrong; the RS is right.
You also cannot read the new position back from the call — poll `get_session_info()` instead.

**`save_project` is best-effort, not absent.** RS:2619 tries `application().save_current_song()`,
then `song().save()`, then `song().save_and_or_rename()`, and only then raises *"Save is not
available via the Live API in this version. Save manually (Ctrl+S)"*. Several skills claim the tool
does not exist. It exists; on Live 12 Lite it usually lands on the error, so **fall back to Ctrl+S**.

**`get_browser_item` is the wrong tool; use `get_browser_items`.** Verified live 2026-09:

- `get_browser_item` resolves a URI by **searching the tree by name, depth-first** (RS:1750 →
  `_find_browser_item_by_uri`). The handler itself is cheap (5 fields, no enumeration), so the cost
  is the walk. It uses the **default 10 s timeout**.
- Result: `query:Synths#Drum%20Rack` and `query:Synths#Instrument%20Rack` return instantly (top-level
  devices), but `query:Synths#Wavetable` and `query:Synths#Analog` **time out** — the walk is long
  *and* those devices don't exist at that level in Lite anyway.
- `get_browser_items(path=...)` does **not** walk: it returns the requested level plus each child's
  own URI, recursively for folders. One call = one whole subtree, fast. **This is the discovery tool.**
- Path vocabulary ≠ URI prefix vocabulary. `get_browser_items(path=...)` wants `instruments`,
  `sounds`, `drums`, `audio_effects`, `midi_effects`, `packs`, `plugins`… but the canonical URI
  prefix for the instruments category is `query:Synths`. A bad path returns
  `{"error": "Unknown or unavailable category", "available_categories": [...]}` — that list is
  *path* names, not URI prefixes.
- `query:Synths#Drum%20Rack` and `query:Drums#Drum%20Rack` **both** resolve, because lookup is by
  name. Don't rely on that; use the canonical prefix from `get_browser_items`.

## Live 12 Lite content (verified)

The native palette in this installation is **only** 6 instruments — Drift, Drum Rack, Drum Sampler,
Impulse, Instrument Rack, Simpler — plus 18 audio effects and ~200 `.adg` drum kits. **Wavetable,
Analog, Operator, Collision, Electric and Tension are Suite/Advanced and are absent here.** Any doc
naming them as available is wrong. Verified via `get_browser_items`; see `PLUGINS.md` for the URI
tables and `sources/` for anything song-specific.

## Indexing (CRITICAL)
**All tool params are 0-based**, matching Live's API. `track_index 0` = `song.tracks[0]` = first
track after Master. Applies to `track_index`, `clip_index`, `device_index`, `chain_index`,
`scene_index`, `send_index`.

**User-facing numbers are 1-based.** When telling David about a clip or slot, translate:
`clip_index 0` = « clip 1 ». Params stay 0-based; only prose changes.

## Verified API gotchas

- **`create_clip(track, slot, length)` — `length` is BEATS, not bars.** Undocumented in the RS; it
  passes straight to `ClipSlot.create_clip()`. In 4/4, 1 bar = 4.
- **`duplicate_clip_to_arrangement(destination_bar=N)` is off by one.** RS computes
  `(N - 1) * song.signature_numerator`, so `N=4` lands on beat 12 = bar 3 and overlaps the previous
  clip. **Use `duplicate_to_arrangement(track, clip, destination_time)`** instead — it passes beats
  through untouched (exact, 0-based). Different RS handler, not an alias.
- **Arrangement audio clip `gain` is normalized 0-1, not dB**, despite the tool param name and the
  RS docstring. Passing a dB value raises Live's own `Gain is out of range` (that string is *not* in
  this repo). Read the raw `gain` back from `get_arrangement_clips` — there is **no**
  `gain_display_string` and no dB conversion anywhere in the RS. Rough refs: 0.4 ≈ 0 dB, 0.6 ≈ 8 dB.
- **`set_arrangement_clip_notes` REPLACES** (it calls `clip.set_notes(tuple(...))`, RS:2735). Same
  for `add_notes_to_clip` despite its name (RS:1346 also uses `set_notes`) — it is a replace, not
  an append. There is no code path that duplicates notes.
- **Automation envelopes on arrangement MIDI clips are write-once / overwrite each other.** The RS
  rebuilds the clip from a temp session clip, so several single-target calls clobber prior lanes.
  That is why `set_automation_lanes` exists — it writes every lane on the temp clip *before*
  duplicating. **Use `set_automation_lanes`, not repeated `set_automation_curve`.**
- **Envelope writes use `insert_step(time, duration, value)`.** `create_event` is only touched by
  the `test_create_event` diagnostic probe — it needs an inaccessible C++ `TEnvelopeEvent` struct.
  **Trap:** 5 other `insert_step` call sites in the RS pass `(time, value, duration)` — arguments
  swapped. `_apply_curve` (the one behind `set_automation_curve` / `set_automation_lanes`) is the
  correct `(time, duration, value)`. Don't copy the broken sites.
- **Device on/off uses the « Device On » parameter, not `is_enabled`.** `_device_set_enabled()`
  (RS:4204) sets it and falls back to `is_enabled` only when absent. Known wart: the finder
  requires `p.is_enabled` on the parameter itself, so disabling a *disabled* device falls through to
  the unreliable path.
- **Core Library drum kits nest.** `.adg` kits load as `InstrumentGroupDevice` whose chains hold the
  real `DrumGroupDevice`. `hasattr(device, "drum_pads")` lies — Live defines it as a property that
  *raises* on non-drum devices. The RS handles this via `_find_drum_rack()` (descends chains,
  matches `class_name` containing "Drum") + `_try_drum_pads()`.
- **The RS is Python 3, not a py2/3 hybrid.** It keeps py2 shims (`import Queue as queue`,
  `__future__` imports) but also uses f-strings, which are a hard `SyntaxError` under py2. Don't
  add py2-only constructs, and don't assume the shims are load-bearing.

## Analysis numbers are on a miscalibrated sample rate

`load()` (server:150) reads the WAV and **throws away its sample rate**, writing raw samples to
`*_y.csv`. Every analysis function then hardcodes `sr = 22050` — but captures are recorded at the
device default (48000 on this machine).

Consequences — treat these outputs as **relative/comparative only**:

| Output | Status |
|---|---|
| `centroid_*`, `rolloff_*`, `bandwidth_*` | scaled by `22050 / actual_rate` (≈0.46) — **not literal Hz** |
| `tuning_offset_cents` | wrong (peak freq from `fft_frequencies(sr=22050)`) |
| `duration_s`, tempo/BPM, beat positions | stretched time axis (≈2.18×) |
| key detection, RMS/peak/dynamic_range | unaffected — safe |

So mix notes like "centroid 226→791 Hz" are internally consistent and useful for *trend* comparison
(same pipeline both times), but do **not** compare them against absolute targets or against figures
from another tool. `load()` keeps the real rate — the fix is a one-line change if you need calibrated
numbers.

## librosa must stay lazy

Import librosa through `_L()` (`server:32`), never `import librosa` at module scope — numba JIT costs
5-15 s. `__main__` already warms it on a 1 s silent buffer so the first capture doesn't time out;
keep that in place.

## Audio capture

- Input is **CABLE Output (VB-Cable)**, discovered by scanning `sd.query_devices()` **once at
  import**. If Windows audio devices change, the frozen `CABLE_DEVICE_ID` points at a wrong/silent
  device and captures come back silent — **restart the MCP server** to re-detect.
- The silence guard (`max_amp < 0.001` → error) lives only in `capture_ableton`, which is **dead
  code** (`@app.tool()` is commented out at server:1747). The live path is
  `capture_and_analyze` → `capture_at_position` (also not a tool; called internally). So a silent
  capture returns "success" with `rms ≈ 0` and values in {−1, 0, +1}. **Check RMS yourself.**
- If `CABLE_DEVICE_ID` is `None`, you get the useless `{"error": "Capture failed", ...}` — the
  helpful "VB-Cable not installed" message is in the dead function.
- WAVs + CSVs land in `data/analyses/`.

## Code conventions (repo-specific only)

- `from __future__ import annotations` first, then stdlib / third-party / local, blank-line grouped.
- 4-space indent, 2 blank lines before top-level defs, type hints on every signature.
- Section dividers are `#` comments with box-drawing chars, not docstrings:
  `# ── Session / Transport ──────────…`
- Tool wrappers that wrap a bare analysis fn take a `_tool` suffix: `analyze_full_tool`,
  `detect_key_tool`. Tool params use the Live API names (`track_index`, `clip_index`,
  `device_index`) — keep them.
- Tool docstrings **are** the LLM-facing tool descriptions — keep them accurate (one currently lies
  about `start_playback_at` being atomic; the real ordering rationale lives in the RS).
- `ValueError` for bad params, `RuntimeError` for operational failure, `try/finally` for sockets.
  Silent `except Exception: pass` is fine for best-effort init only.
- No inline comments unless they explain a non-obvious design decision. No emojis. Docs are
  mixed FR/EN — match the surrounding file.
- Codebase has one-off project scripts at root (`clip_plan.py`, `prep_*.py`, `arrange_loops.py`,
  `inject_scene.py`, `rs_*.py`). Prefer editing an existing file over adding a new one.

## Mix / field rules

- **Every mix must work on big FOH speakers *and* phone speakers** (no sub < 150 Hz, heavy
  compression). HPF non-bass at 150-200 Hz, saturate the low end to generate harmonics
  ("virtual sub"), master limiter ≈ −1 dB. Verify the **full mix**, not soloed tracks — solo
  captures understate low drums and lead to over-boosting.
- **Surge XT is usually the CPU hog**, and the cost is **per voice** (osc/unison count), not max
  polyphony. Lowering polyphony alone rarely helps; use a lighter patch.
- **Global CPU at rest is too noisy to isolate a track** (±5 pts). Reliable method: measure **in
  playback, one track soloed at a time**. Freeze the confirmed culprit.
- **Never invent a drum groove blind.** Sparse kick or improvised crescendos create off-beat
  artifacts. Reuse an existing humanized pattern (varying velocities + slight timing offsets) —
  humanize timing/velocity, never density.
- **Don't apply a documented FX chain or preset copy blindly.** Plugin params are normalized 0-1
  with unverified mapping, and a preset can swallow the signal entirely. Put the chain in a
  transparent state, confirm audio is clean, then sculpt by ear. Normalized values (threshold,
  ratio, attack, freqs) are **not** physical values — set approximations and have David verify.

## Known-broken / misleading tools

- `list_external_plugins` calls `get_browser_categories` and returns **browser categories**, not
  plugins. `refresh_cache` is a no-op.
- `get_browser_items(item_type=...)` — the RS ignores `item_type`; only `path` is used.
- `get_arrangement_clip_envelope` / `get_clip_envelope` both hit `get_clip_envelope`; the latter
  omits `is_arrangement` and so behaves differently for the same command.
- `set_arrangement_time` / `set_song_time` both hit `set_current_song_time`; `set_song_time` hardcodes
  4 beats/bar and its `beat` fallback is unreachable.
- RS never touches `control_coefficients` — the read-only rule is enforced by absence of code.

## Reference files

- `PLUGINS.md` — per-plugin-type control capabilities.
- `README.md` — Voicemeeter/VB-Cable routing setup, monitoring workarounds, troubleshooting.
- Skills in `~/.agents/skills/` carry the long-form field knowledge: `ableton-mcp`,
  `anti-patterns`, `automation-envelopes`, `full-mix-workflow`, `mix-translation`, `plugin-browser`,
  `plugin-exposure`, `scene-workflow`, `surge-osc`, `david-prefs`, `midi-remake`, `analysis-tools`.
  **Load the relevant one instead of re-deriving it here** — song-by-song mix logs live there.

## What NOT to do

- Do NOT edit the RS without running `deploy_rs.py` **and** restarting Ableton.
- Do NOT send overlapping `capture_and_analyze` or `load_instrument_or_effect` calls.
- Do NOT use `create_event` for envelopes, or set `control_coefficients`.
- Do NOT use `duplicate_clip_to_arrangement` with `destination_bar` — off by one.
- Do NOT `import librosa` at module scope.
- Do NOT run the root `test_*.py` scripts without asking; they mutate the loaded set.
- Do NOT trust absolute Hz / duration / BPM from the analysis tools (see sample-rate section).
- Do NOT toggle plugins via `is_enabled`; use the « Device On » parameter.
