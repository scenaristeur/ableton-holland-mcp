# AGENTS.md — Ableton Holland MCP

## Project Overview

Python-based MCP (Model Context Protocol) server for controlling Ableton Live and Surge XT synthesizer. Two MCP servers:

- **`ableton_full_mcp_server.py`** — controls Ableton Live (tracks, clips, instruments, arrangement) via TCP socket to a Remote Script, plus audio capture via VB-Cable and librosa analysis
- **`surge_osc_mcp.py`** — controls Surge XT via OSC (parameters, patches, MIDI notes), up to 8 instances

Supporting files: `capture_audio.py` (standalone CLI capture), `dashboard/app.py` (Tkinter GUI), `AbletonMCP_Remote_Script.py` (Live MIDI Remote Script in Python 2/3 hybrid).

## Setup & Commands

| Command | Description |
|---|---|
| `.venv/Scripts/python -m pip install -r requirements.txt` | Install dependencies |
| `.venv/Scripts/python ableton_full_mcp_server.py` | Start Ableton MCP server |
| `.venv/Scripts/python surge_osc_mcp.py` | Start Surge XT OSC server |
| `.venv/Scripts/python capture_audio.py --help` | Standalone audio capture CLI |

**Linting:** Ruff has been run manually before (`.ruff_cache/` exists) but no config file. Run with:
```
ruff check .
ruff format .
```
No test framework is set up. No `tests/` directory exists. No CI, no pre-commit, no `pyproject.toml`.

## Code Style Guidelines

### Imports

Order: (1) `from __future__ import annotations`, (2) standard library, (3) third-party, (4) local. Group by category with blank lines between:

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
- Line length: not strictly enforced, but keep under 100 chars where readable
- Trailing commas in multi-line function calls and collections
- Use f-strings over `.format()` or `%`

### ASCII Art Section Headers

Separate major sections with commented header lines:

```python
# ── Session / Transport ─────────────────────────────────────────────────────
```

Use `#` comments (not `"""docstrings"""`) for internal section dividers.

### Types

- Always use `from __future__ import annotations` at top of file
- Use Python 3.10+ syntax: `X | None`, `dict[str, Any]`, `list[dict[str, Any]]`
- Import `Any` from `typing` for dynamic types
- Type hints on all function signatures (parameters and return types)

```python
def _send_command(
    cmd_type: str, params: dict[str, Any] | None = None, timeout: float = TIMEOUT
) -> dict[str, Any]:
```

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

- **`try/finally`** to guarantee resource cleanup (especially sockets):
  ```python
  sock = socket.socket(...)
  try:
      sock.connect(...)
      ...
  finally:
      sock.close()
  ```
- **`ValueError`** for invalid parameters: `raise ValueError(f"Instance must be 0..{MAX_INSTANCES - 1}")`
- **`RuntimeError`** for operational failures: `raise RuntimeError("CABLE Output not found...")`
- **Best-effort init** with silent `try/except Exception: pass` for non-critical setup
- Remote Script errors: parse `{"status": "error", "message": "..."}` response and `raise RuntimeError`
- Use `warnings.warn()` (not `print`) for non-fatal conditions inside callbacks

### Docstrings

- Module-level: triple-quoted string immediately after shebang line, describing the file
- Tool functions (`@app.tool()`): always have a descriptive docstring (becomes the MCP tool description)
- Helper functions: Google-style or plain descriptive sentences. Args/Returns sections optional.
- **No inline comments** unless explaining a non-obvious design decision

### MCP Tool Pattern

MCP tools use the `fastmcp` library (`FastMCP` class):

```python
app = FastMCP("server-name")

@app.tool()
def my_tool(param1: str, param2: int = 0) -> dict:
    """Description visible to LLM as tool definition."""
    ...
    return {"key": "value"}
```

### Architecture Notes

- `ableton_full_mcp_server.py` communicates with Ableton via TCP to `AbletonMCP_Remote_Script.py` on port 9877
- `_send_command()` sends JSON `{"type": "...", "params": {...}}` and returns parsed response
- Audio capture uses VB-Cable (Voicemeeter virtual audio cable) via `sounddevice.InputStream`
- Analysis functions load audio from WAV → CSV (`.npy` not used), run through librosa
- The Remote Script (`AbletonMCP_Remote_Script.py`) is Python 2/3 compatible with `try: import Queue` compat shims
- Surge OSC uses `python-osc` with `ThreadingOSCUDPServer` listening on ports 53281+ (stride=2)

### What NOT To Do

- Do NOT create new files when editing an existing one suffices
- Do NOT add inline comments explaining obvious code
- Do NOT add emojis to source files or documentation
- Do NOT run multiple audio captures in parallel (they block the server)
- Do NOT run multiple `load_instrument_or_effect` calls in parallel
- Do NOT modify `AbletonMCP_Remote_Script.py` without understanding Python 2/3 dual compatibility
- Do NOT guess file paths or module names — verify with the actual imports in the codebase
