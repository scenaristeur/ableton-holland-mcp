"""Surge XT OSC MCP Server.

Multi-instance support: jusqu'à 8 instances Surge XT, chacune sur des ports OSC
dédiés. Par défaut :
  - instance 0 : IN 53280 / OUT 53281
  - instance 1 : IN 53282 / OUT 53283
  - instance 2 : IN 53284 / OUT 53285
  - ...
  - instance 7 : IN 53294 / OUT 53295

Chaque instance Surge XT dans Ableton doit être configurée manuellement (Settings > OSC)
avec le port IN correspondant. L'OUT du serveur MCP doit correspondre à l'IN de Surge,
et vice-versa.

Peut être lancé indépendamment ou importé depuis ableton_full_mcp_server.py.
"""

from __future__ import annotations

import json
import os
import time
import threading
from pathlib import Path
from typing import Any

from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer

from fastmcp import FastMCP

SURGE_IP = "127.0.0.1"
BASE_PORT_IN = 53280
PORT_STRIDE = 2
MAX_INSTANCES = 8

# ── Patches index constants ─────────────────────────────────────────────────

SURGE_DATA_DIRS = [
    "C:/Program Files/Common Files/VST3/Surge Synth Team/SurgeXTData",
    os.environ.get("SURGE_XT_DATA", ""),
]
UTIL_DATA_DIR = Path(__file__).parent / "data" / "util_data"
INDEX_FILE = UTIL_DATA_DIR / "patches_index.json"

_patches_index: dict[str, dict[str, str]] | None = None


def _scan_patches() -> dict[str, dict[str, str]]:
    """Scan Surge patches directories and build category -> name -> path index."""
    index: dict[str, dict[str, str]] = {}
    for base in SURGE_DATA_DIRS:
        if not base:
            continue
        for root in ("patches_factory", "patches_3rdparty"):
            folder = Path(base) / root
            if not folder.is_dir():
                continue
            for fxp in folder.rglob("*.fxp"):
                category = fxp.parent.name
                name = fxp.stem
                if category not in index:
                    index[category] = {}
                index[category][name] = str(fxp.with_suffix(""))
    return index


def _load_patches_index() -> dict[str, dict[str, str]]:
    """Load or build the patches index, cached in JSON."""
    global _patches_index
    if _patches_index is not None:
        return _patches_index

    if INDEX_FILE.is_file():
        with open(INDEX_FILE, encoding="utf-8") as f:
            _patches_index = json.load(f)
            assert _patches_index is not None
            return _patches_index

    _patches_index = _scan_patches()
    UTIL_DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(_patches_index, f, indent=2, ensure_ascii=False)
    assert _patches_index is not None
    return _patches_index


def _rebuild_patches_index() -> dict[str, dict[str, str]]:
    """Force rebuild the patches index from disk."""
    global _patches_index
    _patches_index = _scan_patches()
    UTIL_DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(_patches_index, f, indent=2, ensure_ascii=False)
    return _patches_index


# Build the index at import time
_load_patches_index()


def _ports_for_instance(instance: int) -> tuple[int, int]:
    """Return (port_in, port_out) for a given instance index."""
    if not 0 <= instance < MAX_INSTANCES:
        raise ValueError(f"Instance must be 0..{MAX_INSTANCES - 1}")
    offset = instance * PORT_STRIDE
    return BASE_PORT_IN + offset, BASE_PORT_IN + offset + 1


# ── Per-instance state ─────────────────────────────────────────────────────

_instance_data: dict[int, dict[str, Any]] = {}
_instance_lock = threading.Lock()


def _ensure_instance(instance: int) -> dict[str, Any]:
    """Get or create the client/server/responses for an instance."""
    with _instance_lock:
        if instance in _instance_data:
            return _instance_data[instance]

        port_in, port_out = _ports_for_instance(instance)
        client = udp_client.SimpleUDPClient(SURGE_IP, port_in)

        disp = Dispatcher()
        responses: list[tuple[str, tuple[Any, ...]]] = []
        resp_lock = threading.Lock()

        def _handler(address: str, *args: Any) -> None:
            with resp_lock:
                responses.append((address, args))

        disp.set_default_handler(_handler)
        server = ThreadingOSCUDPServer((SURGE_IP, port_out), disp)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        time.sleep(0.1)

        data = {
            "client": client,
            "server": server,
            "thread": thread,
            "responses": responses,
            "lock": resp_lock,
        }
        _instance_data[instance] = data
        return data


def osc_send(instance: int, address: str, *values: Any) -> None:
    """Send an OSC message to a specific Surge instance."""
    data = _ensure_instance(instance)
    data["client"].send_message(address, list(values) if values else [])


def osc_collect(instance: int, wait: float = 0.5) -> list[tuple[str, tuple[Any, ...]]]:
    """Collect responses from a specific Surge instance."""
    time.sleep(wait)
    data = _ensure_instance(instance)
    with data["lock"]:
        items = list(data["responses"])
        data["responses"].clear()
    return items


# ── FastMCP App ──────────────────────────────────────────────────────────────

app = FastMCP("surge-osc-mcp")


def _get_patch(instance: int) -> dict:
    """Get patch name for a specific Surge instance."""
    osc_send(instance, "/q/patch")
    for addr, args in osc_collect(instance, 0.3):
        if addr == "/patch" and args:
            name = str(args[0]).split("\\")[-1].split("/")[-1]
            return {"patch": name, "path": str(args[0])}
    return {"patch": "unknown"}


@app.tool()
def surge_get_patch(instance: int = 0) -> dict:
    """Get current patch name for a Surge XT instance (0 = first, 1 = second, etc.)."""
    return _get_patch(instance)


@app.tool()
def surge_load_patch(path: str, instance: int = 0) -> dict:
    """Load a patch by absolute file path (no extension).

    Example:
      "C:/Program Files/Common Files/VST3/Surge Synth Team/SurgeXTData/patches_factory/Templates/Init Sine"

    Note: les forward slashes sont automatiquement convertis en backslashes
    (Windows) pour éviter l'affichage du chemin complet dans Surge XT.
    """
    win_path = path.replace("/", "\\")
    osc_send(instance, "/patch/load", win_path)
    return _get_patch(instance)


@app.tool()
def surge_incr_patch(instance: int = 0) -> dict:
    """Next patch in current category for a Surge XT instance."""
    osc_send(instance, "/patch/incr")
    return _get_patch(instance)


@app.tool()
def surge_decr_patch(instance: int = 0) -> dict:
    """Previous patch in current category for a Surge XT instance."""
    osc_send(instance, "/patch/decr")
    return _get_patch(instance)


@app.tool()
def surge_random_patch(instance: int = 0) -> dict:
    """Load a random patch on a Surge XT instance."""
    osc_send(instance, "/patch/random")
    return _get_patch(instance)


@app.tool()
def surge_list_categories() -> list[str]:
    """List all available Surge XT patch categories.

    Returns category names from both patches_factory and patches_3rdparty,
    sorted alphabetically.

    Example return: ["Basses", "Drums", "Leads", "Pads", "Plucks", ...]
    """
    index = _load_patches_index()
    return sorted(index.keys())


@app.tool()
def surge_list_patches(category: str) -> list[dict]:
    """List all patches in a given Surge XT category.

    Args:
        category: Category name (e.g. "Basses", "Plucks", "Pads"). Case-sensitive.

    Returns list of {"name": "Patch Name", "path": "absolute/path/without/extension"}.
    """
    index = _load_patches_index()
    patches = index.get(category, {})
    return [{"name": name, "path": path} for name, path in sorted(patches.items())]


@app.tool()
def surge_search_patches(query: str) -> list[dict]:
    """Search Surge XT patches by name (case-insensitive).

    Searches across ALL categories. Matches if query is a substring of the patch name.

    Args:
        query: Search term (e.g. "bass", "warm", "lead")

    Returns list of {"category": "...", "name": "...", "path": "..."}.
    """
    index = _load_patches_index()
    q = query.lower()
    results = []
    for cat, patches in index.items():
        for name, path in patches.items():
            if q in name.lower():
                results.append({"category": cat, "name": name, "path": path})
    return sorted(results, key=lambda r: r["category"] + r["name"])


@app.tool()
def surge_rebuild_index() -> dict:
    """Force rebuild the patches index from disk (rescans all .fxp files)."""
    idx = _rebuild_patches_index()
    cat_count = len(idx)
    patch_count = sum(len(p) for p in idx.values())
    return {
        "status": "ok",
        "categories": cat_count,
        "patches": patch_count,
        "file": str(INDEX_FILE),
    }


@app.tool()
def surge_set_param(address: str, value: float, instance: int = 0) -> dict:
    """Set a parameter by OSC address on a Surge XT instance.

    Common addresses:
      /param/a/osc/1/pitch       /param/a/osc/2/pitch       /param/a/osc/3/pitch
      /param/a/filter/1/cutoff   /param/a/filter/1/resonance
      /param/a/filter/2/cutoff   /param/a/filter/2/resonance
      /param/a/amp/volume        /param/a/amp/pan
      /param/a/mixer/osc1/volume /param/a/mixer/osc1/mute
      /param/macro/1 .. /param/macro/8
      /param/global/volume       /param/global/polyphony_limit
      /param/a/osc/1/type       (0=Classic .. 11=Wavetable)
      /param/a/play_mode         (0=Poly .. 5=Mono)
    """
    osc_send(instance, address, value)
    osc_collect(instance, 0.1)
    return {"status": "ok", "address": address, "value": value, "instance": instance}


@app.tool()
def surge_get_param(address: str, instance: int = 0) -> dict:
    """Read a parameter value by OSC address from a Surge XT instance."""
    osc_send(instance, f"/q/{address.removeprefix('/')}")
    for addr, args in osc_collect(instance, 0.3):
        if addr == address:
            val = args[0] if args else None
            display = str(args[1]) if len(args) > 1 else ""
            return {
                "address": address,
                "value": val,
                "display": display,
                "instance": instance,
            }
        if addr == f"/doc/{address.removeprefix('/')}" and args:
            return {
                "address": address,
                "doc": " ".join(str(a) for a in args),
                "instance": instance,
            }
    return {"address": address, "value": None, "instance": instance}


@app.tool()
def surge_query_all(instance: int = 0) -> list[dict]:
    """Dump all Surge XT parameters and their current values for a specific instance."""
    osc_send(instance, "/q/all_params")
    results = []
    for addr, args in osc_collect(instance, 1.5):
        if not addr.startswith("/doc") and not addr.startswith("/patch"):
            val = args[0] if args else None
            results.append({"address": addr, "value": val})
    return results


@app.tool()
def surge_note_on(pitch: int, velocity: float = 100.0, instance: int = 0) -> dict:
    """Send a MIDI note to a Surge XT instance (pitch 0-127, velocity 0-127)."""
    if velocity == 0:
        osc_send(instance, "/mnote/rel", pitch, 0.0)
    else:
        osc_send(instance, "/mnote", pitch, velocity)
    return {"pitch": pitch, "velocity": velocity, "instance": instance}


@app.tool()
def surge_note_off(pitch: int, instance: int = 0) -> dict:
    """Release a MIDI note on a Surge XT instance."""
    osc_send(instance, "/mnote/rel", pitch, 0.0)
    return {"pitch": pitch, "instance": instance}


@app.tool()
def surge_all_notes_off(instance: int = 0) -> dict:
    """Release all current notes on a Surge XT instance."""
    osc_send(instance, "/allnotesoff")
    return {"status": "ok", "instance": instance}


if __name__ == "__main__":
    app.run(transport="stdio")
