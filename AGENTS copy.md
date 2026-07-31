# AGENTS.md — Ableton Holland MCP

## Project Overview

Python-based MCP (Model Context Protocol) server for controlling Ableton Live and Surge XT synthesizer. Two MCP servers:

- **`ableton_full_mcp_server.py`** — controls Ableton Live (tracks, clips, instruments, arrangement) via TCP socket to a Remote Script, plus audio capture via VB-Cable and librosa analysis
- **`surge_osc_mcp.py`** — controls Surge XT via OSC (parameters, patches, MIDI notes), up to 8 instances

Supporting files: `capture_audio.py` (standalone CLI capture), `dashboard/app.py` (Tkinter GUI), `AbletonMCP_Remote_Script.py` (Live MIDI Remote Script in Python 2/3 hybrid).

**Single RS file:** `AbletonMCP_Remote_Script.py` is the source of truth. Deployed to `AbletonMCP/__init__.py` (and `AbletonMCPExtended/__init__.py`).

**Plugin control reference:** See [`PLUGINS.md`](PLUGINS.md) for detailed capabilities of each plugin type (native synths, external VSTs, Surge XT via OSC) and how to control them.

## Development Workflow

| Command | Description |
|---|---|
| `python deploy_rs.py` | Copy RS + reload (no restart) |
| `cp ...` then `reload` cmd | Manual deploy + hot-reload |

### Deploy without restart
1. Edit `AbletonMCP_Remote_Script.py`
2. Run `python deploy_rs.py` (copies to both RS dirs, clears cache, sends `reload` command)
3. Changes apply immediately — no Ableton restart needed

### Testing MCP server changes (no RS change)

When modifying only `ableton_full_mcp_server.py` (adding/editing tool wrappers that call existing RS commands):

1. Stop the running MCP server (Ctrl+C)
2. Restart it: `.venv/Scripts/python ableton_full_mcp_server.py`
3. Test via any MCP client — the new tools appear automatically in the tool list
4. No Ableton restart or RS deploy needed

When modifying both the RS and the server:
1. First run `python deploy_rs.py` (RS changes take effect immediately)
2. Then restart the MCP server

## Setup & Commands

| Command | Description |
|---|---|---|
| `.venv/Scripts/python -m pip install -r requirements.txt` | Install dependencies |
| `.venv/Scripts/python ableton_full_mcp_server.py` | Start Ableton MCP server |
| `.venv/Scripts/python surge_osc_mcp.py` | Start Surge XT OSC server |
| `.venv/Scripts/python capture_audio.py --help` | Standalone audio capture CLI |
| `python deploy_rs.py` | Deploy RS + hot-reload without restart |

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

### Instrument Workflow

Lors de la création d'un morceau, privilégier dans cet ordre :
1. Drum Kit ou kit natif Ableton (browser > drums) pour les percussions
2. Synthés natifs Ableton (Wavetable, Analog, Drift, Operator) pour basses, nappes, leads
3. Packs Core Library (Piano & Keys, Strings, etc.) pour instruments acoustiques
4. Surge XT uniquement si un son spécifique est introuvable dans les natifs

Browser items (URI) se chargent avec `load_instrument_or_effect`:
- Synthés : `query:Synths#Wavetable`, `query:Synths#Analog`, `query:Synths#Drift`, `query:Synths#Operator`
- Drums :  `query:Drums#FileId_XXXX` (preset kit), `query:Drums#Drum%20Rack` (device)
  - **Important :** Les kits du Core Library (`Racks/Drum Racks/*.adg`) se chargent comme `InstrumentGroupDevice` (pas `DrumGroupDevice`). Ils sont pré-remplis et jouent les notes GM (36=Kick, 38=Snare, 42=HH...) immédiatement. `get_drum_pad_info` ne marche QUE sur les `DrumGroupDevice` vides.
  - **Trouver le FileId :** `get_browser_item(path="drums/<Nom>.adg")` → réponse contient `item.uri` = `query:Drums#FileId_XXXX`
- Sounds : `query:Sounds#Piano%20&%20Keys`, `query:Sounds#Strings`, `query:Sounds#Pad`, etc.
- Plugins externes : `plugins/VST3/Surge Synth Team/Surge XT`

### Sculpture sonore — Workflow dès que les instrus sont chargés et les premières scènes prêtes (CONSTRAINT)

Dès que les instruments sont chargés sur les pistes et qu'au moins les premières scènes sont composées, **ne pas attendre la fin du morceau pour sculpter le son**. Itérer immédiatement :

1. **Vérifier les paramètres exposés du device** (`get_device_parameters`) — beaucoup d'instrus Live (Basic Sub Sine, Wavetable, racks) ont des macros internes à 0 qu'on peut utiliser pour ajouter présence, harmoniques, chaleur.
   - Ex. Basic Sub Sine : Over Tone (+harmoniques), Tone (brillance), Distort (saturation douce) sont souvent à 0.
2. **Ajouter des plugins audio** (Saturator, Amp, Compressor, Reverb, Drum Buss, Utility/Gain) via `load_instrument_or_effect` avec URI `query:AudioFx#<Nom>`.
   - Noms qui marchent : `Utility`, `Saturator`, `Reverb`, `Compressor`, `Limiter`
   - `Drum Buss` ne marche pas par ce nom — utiliser `Compressor` à la place.
3. **Abuser du Surge MCP** — `surge_osc_mcp.py` permet de :
   - Changer de patch (`surge_load_patch`) — chercher des variantes plus présentes/tranchantes
   - Ajuster les paramètres internes (`surge_set_param` : filter cutoff, amp volume, mixer levels, macros)
   - Explorer d'autres catégories : `surge_search_patches(query)` pour trouver des patches complémentaires
4. **Utility/Gain systématique** : si un instrument est trop faible dans le mix (vérifié par capture), lui ajouter un `Utility` (`query:AudioFx#Utility`) et monter le paramètre `Output` (0.0→1.0, valeur ~0.4 = +~10 dB).
5. **Vérifier avec captures** (`capture_and_analyze`, position aux sections clés) :
   - Mesurer les **vrais dBFS** (l'analyse MCP normalise le signal → `energy_rms` est relatif, pas absolu) avec `sf.read()` en Python direct :
     ```python
     import numpy as np, soundfile as sf
     audio, sr = sf.read("fichier.wav")
     y = np.mean(audio, axis=1) if audio.ndim > 1 else audio
     peak_dbfs = 20 * np.log10(np.max(np.abs(y)) + 1e-12)
     rms_dbfs  = 20 * np.log10(np.sqrt(np.mean(y**2)) + 1e-12)
     ```
   - Vérifier l'étendue fréquentielle (spectral centroid, rolloff) et les chevauchements (si deux instrus occupent la même bande, les rééquilibrer ou les repositionner via EQ)
6. **Itérer** : retweaker et recapturer jusqu'à satisfaction de l'utilisateur (présence, équilibre, naturel).

### Maquette en Vue Session — Workflow Scène par Scène (CONSTRAINT)

Lors de la création d'une maquette MIDI, **travailler exclusivement en Vue Session, scène par scène, et valider avec l'utilisateur à chaque étape**. Ne jamais créer d'avance tous les clips d'un morceau.

1. **Découper le morceau en sections** (Intro, Couplet, Pré-Refrain, Refrain, Pont, Refrain Final, Outro...). Une section = une scène.
2. **Étendre les slots si besoin** : une piste a 8 slots par défaut ; ajouter des scènes (`create_scene`) pour atteindre jusqu'à 16 slots. Faire ceci seulement quand nécessaire, scène par scène.
3. Pour **chaque scène**, dans l'ordre :
   - créer le clip de chaque piste instrument (via `create_clip`, longueur = nb de barres × 4 temps),
   - remplir les notes (`add_notes_to_clip`), **en spécifiant toujours la vélocité**,
   - nommer les clips (`set_clip_name`).
4. **Présenter la scène à l'utilisateur** (description de chaque piste avec le **nom du clip** correspondant + plages de vélocité + propositions d'écoute) et **attendre sa validation AVANT de passer à la scène suivante**.
5. Ne passer à l'arrangement que **quand toutes les scènes sont validées** (`duplicate_to_arrangement` ou autre méthode, après accord).

Règles associées :
- Les sections musicalement identiques (Couplet 1 = Couplet 2, Refrain 1 = Refrain 2) peuvent réutiliser le même contenu, mais la mélodie peut varier (phrases A/B).
- Les clips de session inutilisés ou résiduels doivent être supprimés (`delete_session_clip`) pour garder une grille propre.
- Temps et durées des notes sont en **temps (beats)** : 1 barre 4/4 = 4 temps.

### Vélocités des notes (CONSTRAINT)

Chaque note ajoutée via `add_notes_to_clip` **doit toujours inclure un champ `velocity`** (0–127) dans son dictionnaire. Ne jamais ajouter de note sans vélocité (le défaut 100 rend le groove plat).

Principes de vélocité (toujours varier, comme un jeu réel) :
- **Batterie** : accentuer le kick, la snare et le charley sur les temps forts ; charley sur les temps faibles/& plus léger. Ex. kick 110–127, snare 100–120, charley croches 70–90. Un accent ou un fill doit ressortir (max 127).
- **Basse / Guitare** : notes d'accords/arpèges entre 75–95 avec de légères variations ; les notes de passage plus légères. La note d'attaque d'une phrase peut monter à 100–110.
- **Mélodie / Voix** : phrases accentuées 95–110, notes de passage 75–85, notes tenues 80–90. Un sommet de phrase (par ex. le Mi sur « Enfer ») à 110+.
- **Variation systématique** : même motif répété 4× doit avoir des vélocités légèrement différentes (pas de copier-coller exact) pour rester vivant.

Valeurs par défaut recommandées par rôle :
- Kick : 110–127 · Snare : 95–120 · Charley/hats : 60–90 · Crash : 110–127
- Basse (fondamentales) : 85–100 · Basse (passages) : 65–80
- Piano (nappes) : 65–80 · Piano (accents) : 85–100
- Guitare (arpèges) : 75–95 · Mélodie (phrasé) : 80–110

Lors de la présentation d'une scène à l'utilisateur, indiquer brièvement les plages de vélocité choisies par piste.

### Indexing Convention (CRITICAL)

**ALL track and clip indices are 0-based** — matching Live's Python API (`song.tracks[0]` = first track after Master). This applies to every tool parameter named `track_index`, `clip_index`, `device_index`, `chain_index`, `scene_index`, `send_index`.

```
track_index 0 → song.tracks[0] → first session track
track_index 1 → song.tracks[1] → second session track
clip_index 0   → clip_slots[0]  → first clip slot
device_index 0 → devices[0]     → first device
```

### Architecture Notes

- `ableton_full_mcp_server.py` communicates with Ableton via TCP to `AbletonMCP_Remote_Script.py` on port 9877
- `_send_command()` sends JSON `{"type": "...", "params": {...}}` and returns parsed response
- Audio capture uses VB-Cable (Voicemeeter virtual audio cable) via `sounddevice.InputStream`
- Analysis functions load audio from WAV → CSV (`.npy` not used), run through librosa
- The Remote Script (`AbletonMCP_Remote_Script.py`) is Python 2/3 compatible with `try: import Queue` compat shims
- Surge OSC uses `python-osc` with `ThreadingOSCUDPServer` listening on ports 53281+ (stride=2)
- Clip automation uses `insert_step(time, duration, value)` — the only write method in Live 12 Python API. `create_event()` requires a C++ struct (inaccessible). `control_coefficients` is read-only.
- Connected steps pattern: `insert_step(t_i, t_{i+1}-t_i, v_i)` creates step automation (value holds from t_i to t_{i+1}). Each step creates 2 events at boundaries (end of previous + start of next).
- Parameter targets: `"volume"`, `"panning"`, `"send_N"`, `"device_N_PARAMNAME"` (e.g. `device_1_Volume`)
- `create_clip(track_index, clip_index, length)` — **length is in BEATS, not bars**. At 4/4: 1 bar = 4 beats. So 8 bars = 32, 16 bars = 64, etc. The loop defaults to the clip length.
- **TODO**: add `set_clip_loop` command to Remote Script (set `clip.looping`, `clip.loop_start`, `clip.loop_end`)
- "reload" command hot-reloads the RS via `importlib.reload()` + `self.__class__ = new_mod.AbletonMCP`
- **IMPORTANT — Automation arrangement findings:**
  - `set_automation_curve(is_arrangement=False)` → écrit ET lit sur clips session (via `events_in_range`)
  - `duplicate_clip_to_arrangement` → copie les enveloppes dans l'arrangement (UI visible, MAIS API illisible)
  - `automation_envelope(param)` sur clip MIDI arrangement → retourne `None` (API bug, enveloppe existe)
  - `create_automation_envelope(param)` sur clip MIDI arrangement → exception (Live 12 Lite limitation)
  - Les enveloppes d'arrangement sont **write-once** : écriture OK via workflow session→duplicate, mais lecture/modification impossible depuis Python

### Troubleshooting — Capture audio silencieuse

**Symptôme** : `capture_and_analyze` (ou `capture_ableton`) renvoie des WAV **100 % silence** (rms ≈ 0, valeurs {−1, 0, +1} sur int16) et/ou des résultats d'analyse identiques à chaque capture (tempo/key aberrants = artefacts d'analyse du bruit de silence). L'audio sort pourtant bien dans les enceintes.

**Cause probable** : `CABLE_DEVICE_ID` est un **index figé au démarrage** du serveur (boucle `sd.query_devices()`). Si la liste des périphériques Windows change (branchement/retrait Focusrite, installation Voicemeeter/VB-Cable, changement de sortie dans Ableton...), l'index pointe vers un mauvais périphérique silencieux.

**Vérifier** : tester le câble avec un `sd.rec()` standalone sur chaque `CABLE Output` (MME/DirectSound/WASAPI) pendant la lecture — si un device capte le signal mais pas le serveur, l'index est périmé.

**Solution** : **redémarrer le serveur MCP** après tout changement de périphérique audio :
1. Ctrl+C sur le terminal du serveur
2. `.venv/Scripts/python ableton_full_mcp_server.py`
3. Relancer la capture

Le serveur redétecte alors `CABLE Output` (premier device MME avec entrées).

### What NOT To Do

- Do NOT create new files when editing an existing one suffices
- Do NOT add inline comments explaining obvious code
- Do NOT add emojis to source files or documentation
- Do NOT run multiple `capture_and_analyze` calls at once — même en séquence dans un même message. Chaque capture interrompt la précédente (seek + playback). Envoyer UNE SEULE capture par message, attendre la réponse, puis envoyer la suivante.
- Do NOT run multiple `load_instrument_or_effect` calls in parallel
- Do NOT modify `AbletonMCP_Remote_Script.py` without understanding Python 2/3 dual compatibility
- Do NOT guess file paths or module names — verify with the actual imports in the codebase
- Do NOT use `create_event()` — it doesn't work in Live 12 (needs C++ struct `TEnvelopeEvent`)
- Do NOT try to set `control_coefficients` — it's read-only
- Do NOT run `deploy_rs.py` if Ableton isn't running (reload will timeout — still safe, just restart)
- Do NOT use `create_event()` — it doesn't work in Live 12 (needs C++ struct `TEnvelopeEvent`)
- Do NOT try to set `control_coefficients` — it's read-only
