"""Ableton Holland MCP Server — connects to AbletonMCP Remote Script via socket."""

from __future__ import annotations

import json
import socket
import time
from typing import Any

from fastmcp import FastMCP

HOST = "127.0.0.1"
PORT = 9877
TIMEOUT = 30.0

app = FastMCP("ableton-holland-mcp")


# ── Socket helpers ──────────────────────────────────────────────────────────


def _send_command(
    cmd_type: str, params: dict[str, Any] | None = None, timeout: float = TIMEOUT
) -> dict[str, Any]:
    """Send a JSON command to the Remote Script and return the parsed response."""
    if params is None:
        params = {}
    payload = {"type": cmd_type, "params": params}
    raw = json.dumps(payload)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((HOST, PORT))
        sock.sendall(raw.encode("utf-8"))

        chunks = []
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                break
            chunks.append(chunk)
            try:
                json.loads(b"".join(chunks))
                break
            except json.JSONDecodeError:
                continue

        data = b"".join(chunks)
        if not data:
            return {"status": "error", "message": "Empty response from Remote Script"}
        response = json.loads(data.decode("utf-8"))
        if response.get("status") == "error":
            raise RuntimeError(response.get("message", "Unknown error"))
        return response.get("result", {})
    finally:
        sock.close()


def _cmd(cmd_type: str, **kwargs: Any) -> dict[str, Any]:
    """Shortcut: send a command and return the result dict."""
    return _send_command(cmd_type, kwargs)


# ── Session / Transport ─────────────────────────────────────────────────────


@app.tool()
def get_session_info() -> dict[str, Any]:
    """Get current session info: tempo, time signature, track count, playback state."""
    return _cmd("get_session_info")


@app.tool()
def get_track_info(track_index: int) -> dict[str, Any]:
    """Get detailed info about a track: name, devices, clip slots, volume, pan."""
    return _cmd("get_track_info", track_index=track_index)


@app.tool()
def set_tempo(bpm: float) -> dict[str, Any]:
    """Change the session tempo."""
    return _cmd("set_tempo", tempo=bpm)


@app.tool()
def start_playback() -> dict[str, Any]:
    """Start playback."""
    return _cmd("start_playback")


@app.tool()
def stop_playback() -> dict[str, Any]:
    """Stop playback."""
    return _cmd("stop_playback")


# ── Tracks ──────────────────────────────────────────────────────────────────


@app.tool()
def create_midi_track(index: int = -1) -> dict[str, Any]:
    """Create a new MIDI track. index=-1 adds at end."""
    return _cmd("create_midi_track", index=index)


@app.tool()
def set_track_name(track_index: int, name: str) -> dict[str, Any]:
    """Rename a track."""
    return _cmd("set_track_name", track_index=track_index, name=name)


# ── Session Clips ───────────────────────────────────────────────────────────


@app.tool()
def create_clip(
    track_index: int, clip_index: int, length: float = 4.0
) -> dict[str, Any]:
    """Create an empty MIDI clip in a session slot."""
    return _cmd(
        "create_clip", track_index=track_index, clip_index=clip_index, length=length
    )


@app.tool()
def add_notes_to_clip(
    track_index: int, clip_index: int, notes: list[dict[str, Any]]
) -> dict[str, Any]:
    """Add MIDI notes to a clip. Each note: {pitch, start_time, duration, velocity, mute}."""
    return _cmd(
        "add_notes_to_clip", track_index=track_index, clip_index=clip_index, notes=notes
    )


@app.tool()
def set_clip_name(track_index: int, clip_index: int, name: str) -> dict[str, Any]:
    """Name a session clip."""
    return _cmd(
        "set_clip_name", track_index=track_index, clip_index=clip_index, name=name
    )


@app.tool()
def fire_clip(track_index: int, clip_index: int) -> dict[str, Any]:
    """Start playing a session clip."""
    return _cmd("fire_clip", track_index=track_index, clip_index=clip_index)


@app.tool()
def stop_clip(track_index: int, clip_index: int) -> dict[str, Any]:
    """Stop a session clip."""
    return _cmd("stop_clip", track_index=track_index, clip_index=clip_index)


@app.tool()
def get_clip_notes(track_index: int, clip_index: int) -> dict[str, Any]:
    """Read all MIDI notes from a session clip."""
    return _cmd("get_clip_notes", track_index=track_index, clip_index=clip_index)


@app.tool()
def delete_session_clip(track_index: int, clip_index: int) -> dict[str, Any]:
    """Delete a clip from a session slot."""
    return _cmd("delete_session_clip", track_index=track_index, clip_index=clip_index)


@app.tool()
def delete_arrangement_clip(track_index: int, clip_index: int) -> dict[str, Any]:
    """Delete a clip from the arrangement timeline (by its index in arrangement_clips list)."""
    return _cmd(
        "delete_arrangement_clip", track_index=track_index, clip_index=clip_index
    )


# ── Instruments / Effects ───────────────────────────────────────────────────


@app.tool()
def get_browser_tree(category_type: str = "all") -> dict[str, Any]:
    """Browse Ableton's browser tree. category_type: all, instruments, sounds, drums, audio_effects, midi_effects."""
    return _cmd("get_browser_tree", category_type=category_type)


@app.tool()
def get_browser_items_at_path(path: str) -> dict[str, Any]:
    """List browser items at a path like 'Instruments/Synth Lead'."""
    return _cmd("get_browser_items_at_path", path=path)


@app.tool()
def load_instrument_or_effect(track_index: int, uri: str) -> dict[str, Any]:
    """Load an instrument/effect onto a track by URI (from browser)."""
    return _cmd("load_instrument_or_effect", track_index=track_index, uri=uri)


# ── Arrangement ─────────────────────────────────────────────────────────────


@app.tool()
def switch_to_arrangement_view() -> dict[str, Any]:
    """Switch Ableton's main view to Arrangement."""
    return _cmd("switch_to_arrangement_view")


@app.tool()
def set_arrangement_time(time: float) -> dict[str, Any]:
    """Move the arrangement playhead to a beat position."""
    return _cmd("set_current_song_time", time=time)


@app.tool()
def get_arrangement_clips(track_index: int) -> dict[str, Any]:
    """List all clips in the arrangement timeline for a track."""
    return _cmd("get_arrangement_clips", track_index=track_index)


@app.tool()
def duplicate_to_arrangement(
    track_index: int, clip_index: int, destination_time: float
) -> dict[str, Any]:
    """Copy a session clip into the arrangement timeline at a beat position."""
    return _cmd(
        "duplicate_session_clip_to_arrangement",
        track_index=track_index,
        clip_index=clip_index,
        destination_time=destination_time,
    )


@app.tool()
def get_arrangement_clip_notes(track_index: int, clip_index: int) -> dict[str, Any]:
    """Read MIDI notes from an arrangement clip (by its index in the arrangement_clips list)."""
    return _cmd(
        "get_arrangement_clip_notes", track_index=track_index, clip_index=clip_index
    )


@app.tool()
def set_arrangement_clip_notes(
    track_index: int, clip_index: int, notes: list[dict[str, Any]]
) -> dict[str, Any]:
    """Replace all MIDI notes in an arrangement clip. Each note: {pitch, start_time, duration, velocity, mute}."""
    return _cmd(
        "set_arrangement_clip_notes",
        track_index=track_index,
        clip_index=clip_index,
        notes=notes,
    )


# ── Audio ───────────────────────────────────────────────────────────────────


@app.tool()
def create_audio_clip(track_index: int, clip_index: int, path: str) -> dict[str, Any]:
    """Import an audio file into an audio track's clip slot (Live 12.0.5+)."""
    return _cmd(
        "create_audio_clip", track_index=track_index, clip_index=clip_index, path=path
    )


# ── Device Parameters (NEW) ────────────────────────────────────────────────


@app.tool()
def get_device_parameters(track_index: int, device_index: int) -> dict[str, Any]:
    """Read all parameters of a device (name, value, min, max, is_quantized, value_items)."""
    return _cmd(
        "get_device_parameters", track_index=track_index, device_index=device_index
    )


@app.tool()
def set_device_parameter(
    track_index: int, device_index: int, parameter_name: str, value: float
) -> dict[str, Any]:
    """Set a device parameter value by name."""
    return _cmd(
        "set_device_parameter",
        track_index=track_index,
        device_index=device_index,
        parameter_name=parameter_name,
        value=value,
    )


# ── Scenes (NEW) ────────────────────────────────────────────────────────────


@app.tool()
def create_scene(index: int = -1) -> dict[str, Any]:
    """Create a new scene. index=-1 adds at end."""
    return _cmd("create_scene", index=index)


@app.tool()
def fire_scene(index: int) -> dict[str, Any]:
    """Launch a scene (fires all clips in that scene row)."""
    return _cmd("fire_scene", index=index)


# ── Mixer (NEW) ─────────────────────────────────────────────────────────────


@app.tool()
def get_sends(track_index: int) -> dict[str, Any]:
    """Get all send levels for a track."""
    return _cmd("get_sends", track_index=track_index)


@app.tool()
def set_send(track_index: int, send_index: int, value: float) -> dict[str, Any]:
    """Set a send level for a track (0.0–1.0)."""
    return _cmd("set_send", track_index=track_index, send_index=send_index, value=value)


@app.tool()
def set_monitoring(track_index: int, state: int) -> dict[str, Any]:
    """Set track monitoring: 0=auto, 1=in, 2=off."""
    return _cmd("set_monitoring", track_index=track_index, state=state)


# ── Project Operations (NEW) ───────────────────────────────────────────────


@app.tool()
def freeze_track(track_index: int) -> dict[str, Any]:
    """Freeze a track (renders audio, disables editing)."""
    return _cmd("freeze_track", track_index=track_index)


@app.tool()
def flatten_track(track_index: int) -> dict[str, Any]:
    """Flatten a frozen track (commits the frozen audio)."""
    return _cmd("flatten_track", track_index=track_index)


@app.tool()
def save_project() -> dict[str, Any]:
    """Save the current Live project."""
    return _cmd("save_project")


@app.tool()
def undo() -> dict[str, Any]:
    """Undo the last action."""
    return _cmd("undo")


@app.tool()
def redo() -> dict[str, Any]:
    """Redo the last undone action."""
    return _cmd("redo")


# ── Track Management (NEW) ───────────────────────────────────────


@app.tool()
def delete_track(track_index: int) -> dict[str, Any]:
    """Delete a track from the set."""
    return _cmd("delete_track", track_index=track_index)


@app.tool()
def duplicate_track(track_index: int) -> dict[str, Any]:
    """Duplicate a track."""
    return _cmd("duplicate_track", track_index=track_index)


@app.tool()
def duplicate_clip(track_index: int, clip_index: int) -> dict[str, Any]:
    """Duplicate a session clip in place (to next empty slot)."""
    return _cmd("duplicate_clip", track_index=track_index, clip_index=clip_index)


@app.tool()
def quantize_clip(
    track_index: int,
    clip_index: int,
    amount: float = 1.0,
    quantize_to: int = 2,
) -> dict[str, Any]:
    """Quantize a MIDI clip. quantize_to: 0=1/4, 1=1/8, 2=1/16, 3=1/32. amount: 0.0–1.0."""
    return _cmd(
        "quantize_clip",
        track_index=track_index,
        clip_index=clip_index,
        amount=amount,
        quantize_to=quantize_to,
    )


@app.tool()
def select_track(track_index: int) -> dict[str, Any]:
    """Select a track in Ableton's UI."""
    return _cmd("select_track", track_index=track_index)


# ── Track / Clip Color (NEW) ─────────────────────────────────────


@app.tool()
def get_track_color(track_index: int) -> dict[str, Any]:
    """Get a track's color index (0–255)."""
    return _cmd("get_track_color", track_index=track_index)


@app.tool()
def set_track_color(track_index: int, color: int) -> dict[str, Any]:
    """Set a track's color index (0–255)."""
    return _cmd("set_track_color", track_index=track_index, color=color)


@app.tool()
def get_clip_color(track_index: int, clip_index: int) -> dict[str, Any]:
    """Get a clip's color index (0–255)."""
    return _cmd("get_clip_color", track_index=track_index, clip_index=clip_index)


@app.tool()
def set_clip_color(track_index: int, clip_index: int, color: int) -> dict[str, Any]:
    """Set a clip's color index (0–255)."""
    return _cmd(
        "set_clip_color", track_index=track_index, clip_index=clip_index, color=color
    )


# ── Transport Extras (NEW) ────────────────────────────────────────


@app.tool()
def set_metronome(value: bool) -> dict[str, Any]:
    """Toggle metronome on/off."""
    return _cmd("set_metronome", value=value)


@app.tool()
def get_metronome() -> dict[str, Any]:
    """Get metronome state."""
    return _cmd("get_metronome")


@app.tool()
def set_session_record(value: bool) -> dict[str, Any]:
    """Toggle session record on/off."""
    return _cmd("set_session_record", value=value)


@app.tool()
def get_session_record() -> dict[str, Any]:
    """Get session record state."""
    return _cmd("get_session_record")


@app.tool()
def nudge_up() -> dict[str, Any]:
    """Nudge tempo up."""
    return _cmd("nudge_up")


@app.tool()
def nudge_down() -> dict[str, Any]:
    """Nudge tempo down."""
    return _cmd("nudge_down")


@app.tool()
def set_signature(numerator: int = 4, denominator: int = 4) -> dict[str, Any]:
    """Set time signature."""
    return _cmd("set_signature", numerator=numerator, denominator=denominator)


# ── Crossfader (NEW) ─────────────────────────────────────────────


@app.tool()
def get_crossfader() -> dict[str, Any]:
    """Get master crossfader position (0.0–1.0)."""
    return _cmd("get_crossfader")


@app.tool()
def set_crossfader(value: float) -> dict[str, Any]:
    """Set master crossfader position (0.0–1.0)."""
    return _cmd("set_crossfader", value=value)


# ── Groove (NEW) ─────────────────────────────────────────────────


@app.tool()
def get_groove_amount() -> dict[str, Any]:
    """Get global groove amount (0.0–1.0)."""
    return _cmd("get_groove_amount")


@app.tool()
def set_groove_amount(amount: float) -> dict[str, Any]:
    """Set global groove amount (0.0–1.0)."""
    return _cmd("set_groove_amount", amount=amount)


# ── System / Monitoring ─────────────────────────────────────────────────────


@app.tool()
def show_message(text: str) -> dict[str, Any]:
    """Show a message in Live's status bar."""
    return _cmd("show_message", text=text)


@app.tool()
def get_cpu_load() -> dict[str, Any]:
    """Get CPU usage: average and peak percent."""
    return _cmd("get_cpu_load")


@app.tool()
def get_live_version() -> dict[str, Any]:
    """Get Live version info (version string, build ID)."""
    return _cmd("get_live_version")


@app.tool()
def get_tempo_follower() -> dict[str, Any]:
    """Get whether tempo follower is enabled."""
    return _cmd("get_tempo_follower")


@app.tool()
def set_tempo_follower(enabled: bool) -> dict[str, Any]:
    """Enable/disable the tempo follower."""
    return _cmd("set_tempo_follower", enabled=enabled)


@app.tool()
def get_control_surfaces() -> dict[str, Any]:
    """List active control surfaces."""
    return _cmd("get_control_surfaces")


# ── Track Routing ──────────────────────────────────────────────────────────


@app.tool()
def get_track_routing(track_index: int) -> dict[str, Any]:
    """Get input/output routing info for a track."""
    return _cmd("get_track_routing", track_index=track_index)


@app.tool()
def set_track_input_routing(
    track_index: int,
    routing_type: str,
    channel: str | None = None,
) -> dict[str, Any]:
    """Set input routing for a track by type name (e.g. 'Ext. In', 'Resampling')."""
    return _cmd(
        "set_track_input_routing",
        track_index=track_index,
        routing_type=routing_type,
        channel=channel,
    )


@app.tool()
def set_track_output_routing(
    track_index: int,
    routing_type: str,
    channel: str | None = None,
) -> dict[str, Any]:
    """Set output routing for a track by type name (e.g. 'Master', 'Sends Only')."""
    return _cmd(
        "set_track_output_routing",
        track_index=track_index,
        routing_type=routing_type,
        channel=channel,
    )


# ── Master Track ───────────────────────────────────────────────────────────


@app.tool()
def get_master_track() -> dict[str, Any]:
    """Get master track info: volume, pan."""
    return _cmd("get_master_track")


@app.tool()
def set_master_volume(value: float) -> dict[str, Any]:
    """Set master volume (0.0–1.0)."""
    return _cmd("set_master_volume", value=value)


@app.tool()
def set_master_panning(value: float) -> dict[str, Any]:
    """Set master panning (-1.0–1.0)."""
    return _cmd("set_master_panning", value=value)


# ── Entrypoint ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(transport="stdio")
