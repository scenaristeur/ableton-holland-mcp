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
| `python deploy_rs.py` | Copy RS + hot-reload without restart |

### Deploy RS without restart
1. Edit `AbletonMCP_Remote_Script.py`
2. Run `python deploy_rs.py` (copies to both RS dirs, clears cache, sends `reload` command)
3. No Ableton restart needed

### Test MCP server changes (no RS change)
1. Stop server (Ctrl+C) → restart: `.venv/Scripts/python ableton_full_mcp_server.py`
2. Test via any MCP client — new tools appear automatically

### When modifying both RS and server
1. Run `python deploy_rs.py` first
2. Then restart MCP server

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

## Architecture Notes
- Server communicates with Ableton via TCP on port 9877 to `AbletonMCP_Remote_Script.py`
- `_send_command()` sends JSON `{"type": "...", "params": {...}}` and returns parsed response
- Audio capture uses VB-Cable (Voicemeeter) via `sounddevice.InputStream`
- Analysis uses librosa; data saved as WAV → CSV (`.npy` not used)
- RS is Python 2/3 compatible with `try: import Queue` compat shims
- Surge OSC uses `python-osc` with `ThreadingOSCUDPServer` on ports 53281+ (stride=2)
- `create_clip(track, clip, length)` — **length is in BEATS, not bars**. 4/4: 1 bar = 4 beats
- "reload" command hot-reloads the RS via `importlib.reload()`
- Clip automation: use `insert_step(time, duration, value)`. Do NOT use `create_event()` (needs C++ struct)
- `control_coefficients` is read-only
- Automation envelopes on arrangement clips are **write-once**: session→duplicate workflow works, but reading/modifying arrangement envelopes from Python is unreliable

## Troubleshooting — Silent Audio Capture
**Symptom:** `capture_and_analyze` returns silence (rms ≈ 0, values {−1, 0, +1}).

**Cause:** `CABLE_DEVICE_ID` is a frozen index from `sd.query_devices()` at startup. If Windows audio devices change, the index points to a wrong/silent device.

**Fix:** Restart the MCP server: Ctrl+C → `.venv/Scripts/python ableton_full_mcp_server.py`. The server redetects `CABLE Output` on restart.

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
- Do NOT run `deploy_rs.py` if Ableton isn't running (safe, but reload will timeout)
