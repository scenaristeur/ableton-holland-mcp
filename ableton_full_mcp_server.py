"""Unified Ableton + Music Analysis MCP Server.

Combines ableton_mcp_server.py + music_analysis_plus.py.
Single process, shared state, atomic tools like capture_at_position().
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import socket
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import sounddevice as sd
import soundfile as sf

from fastmcp import FastMCP


# Lazy librosa import — avoids slow numba JIT compilation at startup
# on low-resource machines. First analysis call will trigger the import.
_librosa = None


def _L() -> Any:  # noqa: E731
    global _librosa
    if _librosa is None:
        import librosa  # type: ignore[import-untyped]

        _librosa = librosa
    return _librosa


# ── Ableton MCP Helpers ─────────────────────────────────────────────────────

HOST = "127.0.0.1"
PORT = 9877
TIMEOUT = 30.0
TIMEOUT_LONG = 120.0

app = FastMCP("ableton-full-mcp")


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


# ── Music Analysis Helpers ──────────────────────────────────────────────────

DATA_DIR = Path(__file__).resolve().parent / "data"
ANALYSES_DIR = DATA_DIR / "analyses"
ANALYSES_DIR.mkdir(parents=True, exist_ok=True)

CABLE_DEVICE_ID = None
for i, d in enumerate(sd.query_devices()):
    if "CABLE Output" in d["name"] and d["max_input_channels"] > 0:
        CABLE_DEVICE_ID = i
        break

# Krumhansl-Kessler key profiles
_KK_MAJOR = np.array(
    [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
)
_KK_MINOR = np.array(
    [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
)
_NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def _read_y(y_path: str) -> np.ndarray:
    return pd.read_csv(y_path, header=None).values.flatten()


def _detect_key_from_chroma(chroma: np.ndarray) -> dict:
    chroma_mean = chroma.mean(axis=1)
    kk_major = np.array(_KK_MAJOR)
    kk_minor = np.array(_KK_MINOR)
    corr_major = np.array(
        [float(np.dot(chroma_mean, np.roll(kk_major, i))) for i in range(12)]
    )
    corr_minor = np.array(
        [float(np.dot(chroma_mean, np.roll(kk_minor, i))) for i in range(12)]
    )
    idx_major = int(np.argmax(corr_major))
    idx_minor = int(np.argmax(corr_minor))
    if corr_major[idx_major] >= corr_minor[idx_minor]:
        return {
            "key": _NOTES[idx_major],
            "mode": "major",
            "confidence": corr_major[idx_major],
        }
    return {
        "key": _NOTES[idx_minor],
        "mode": "minor",
        "confidence": corr_minor[idx_minor],
    }


# ── Music Analysis (from music_analysis_plus.py) ────────────────────────────


def load(path: str) -> dict:
    """Load audio file and return y_path."""
    audio, sr = sf.read(path)
    y = np.mean(audio, axis=1) if audio.ndim > 1 else audio
    y = _L().util.normalize(y)
    y_path = str(ANALYSES_DIR / f"{Path(path).stem}_y.csv")
    pd.DataFrame(y).to_csv(y_path, header=False, index=False)
    return {"y_path": y_path, "audio_path": path}


def get_duration(y_path: str) -> float:
    """Get duration in seconds."""
    y = _read_y(y_path)
    sr = 22050
    return len(y) / sr


def tempo(
    y_path: str,
    hop_length: int = 512,
    start_bpm: float = 120,
    max_tempo: float = 320,
    std_bpm: float = 1,
    ac_size: float = 8,
) -> tuple:
    """Estimate tempo."""
    y = _read_y(y_path)
    sr = 22050
    onset_env = _L().onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
    bpm = _L().beat.tempo(
        onset_envelope=onset_env,
        sr=sr,
        hop_length=hop_length,
        start_bpm=start_bpm,
        max_tempo=max_tempo,
    )
    return float(bpm[0]) if isinstance(bpm, np.ndarray) else float(bpm)


def beat_track(
    y_path: str,
    hop_length: int = 512,
    start_bpm: float = 120,
    tightness: int = 100,
    units: str = "frames",
) -> dict:
    """Beat tracking."""
    y = _read_y(y_path)
    sr = 22050
    onset_env = _L().onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
    frames = _L().beat.beat_track(
        onset_envelope=onset_env, sr=sr, hop_length=hop_length, start_bpm=start_bpm
    )[1]
    if units == "time":
        beats = _L().frames_to_time(frames, sr=sr, hop_length=hop_length).tolist()
    elif units == "samples":
        beats = _L().frames_to_samples(frames, hop_length=hop_length).tolist()
    else:
        beats = frames.tolist()
    return {"beats": beats, "units": units}


def chroma_cqt(
    y_path: str,
    hop_length: int = 512,
    fmin: float | None = None,
    n_chroma: int = 12,
    n_octaves: int = 7,
) -> str:
    """Compute chromagram."""
    y = _read_y(y_path)
    sr = 22050
    chroma = _L().feature.chroma_cqt(
        y=y,
        sr=sr,
        hop_length=hop_length,
        fmin=fmin,
        n_chroma=n_chroma,
        n_octaves=n_octaves,
    )
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    times = _L().frames_to_time(
        np.arange(chroma.shape[1]), sr=sr, hop_length=hop_length
    )
    data = []
    for note_idx, note in enumerate(note_names):
        for time_idx, t in enumerate(times):
            amplitude = chroma[note_idx, time_idx]
            data.append({"note": note, "time": float(t), "amplitude": float(amplitude)})
    chroma_path = str(ANALYSES_DIR / f"{Path(y_path).stem}_chroma.csv")
    pd.DataFrame(data).to_csv(chroma_path, index=False)
    return chroma_path


def mfcc(y_path: str) -> str:
    """Compute MFCC."""
    y = _read_y(y_path)
    sr = 22050
    mfcc_features = _L().feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_path = str(ANALYSES_DIR / f"{Path(y_path).stem}_mfcc.csv")
    pd.DataFrame(mfcc_features).to_csv(mfcc_path, index=False, header=False)
    return mfcc_path


def analyze_energy(y_path: str) -> dict:
    """Analyze energy and dynamics."""
    y = _read_y(y_path)
    sr = 22050
    rms = _L().feature.rms(y=y)[0]
    peak = float(np.max(np.abs(y)))
    rms_db = 20 * np.log10(np.maximum(1e-5, np.array([float(np.mean(rms))])))
    peak_db = 20 * np.log10(np.maximum(1e-5, np.array([peak])))
    dynamic_range = peak_db[0] - rms_db[0]
    return {
        "rms_mean": float(np.mean(rms)),
        "rms_max": float(np.max(rms)),
        "rms_min": float(np.min(rms)),
        "peak": peak,
        "dynamic_range_db": dynamic_range,
    }


def analyze_spectral(y_path: str) -> dict:
    """Analyze spectral characteristics."""
    y = _read_y(y_path)
    sr = 22050
    centroid = _L().feature.spectral_centroid(y=y, sr=sr)[0]
    rolloff = _L().feature.spectral_rolloff(y=y, sr=sr)[0]
    bandwidth = _L().feature.spectral_bandwidth(y=y, sr=sr)[0]
    zcr = _L().feature.zero_crossing_rate(y)[0]
    return {
        "centroid_mean": float(np.mean(centroid)),
        "centroid_std": float(np.std(centroid)),
        "rolloff_mean": float(np.mean(rolloff)),
        "rolloff_std": float(np.std(rolloff)),
        "bandwidth_mean": float(np.mean(bandwidth)),
        "zcr_mean": float(np.mean(zcr)),
        "zcr_std": float(np.std(zcr)),
    }


def analyze_tuning(y_path: str) -> dict:
    """Analyze tuning offset."""
    y = _read_y(y_path)
    sr = 22050
    chroma = _L().feature.chroma_cqt(y=y, sr=sr)
    chroma_mean = chroma.mean(axis=1)
    fft = np.abs(_L().stft(y))
    freqs = _L().fft_frequencies(sr=sr)
    spec = np.mean(fft, axis=1)
    peak_freq = freqs[np.argmax(spec)]
    a4_freq = 440.0
    cents_offset = 1200 * np.log2(peak_freq / a4_freq)
    return {"tuning_offset_cents": float(cents_offset)}


def detect_key(y_path: str) -> dict:
    """Detect key using Krumhansl-Kessler."""
    y = _read_y(y_path)
    sr = 22050
    chroma = _L().feature.chroma_cqt(y=y, sr=sr)
    return _detect_key_from_chroma(chroma)


def analyze_full(y_path: str) -> dict:
    """Run all analysis tools."""
    key = detect_key(y_path)
    energy = analyze_energy(y_path)
    spectral = analyze_spectral(y_path)
    tuning = analyze_tuning(y_path)
    dur = get_duration(y_path)
    bpm_result = tempo(y_path)
    return {
        "duration_s": dur,
        "tempo_bpm": bpm_result,
        "key": key["key"],
        "mode": key["mode"],
        "key_confidence": round(key["confidence"], 1),
        "energy_rms": energy["rms_mean"],
        "energy_peak": energy["peak"],
        "dynamic_range_db": round(energy["dynamic_range_db"], 1),
        "spectral_centroid_hz": round(spectral["centroid_mean"], 0),
        "spectral_rolloff_hz": round(spectral["rolloff_mean"], 0),
        "zero_crossing_rate": round(spectral["zcr_mean"], 4),
        "tuning_offset_cents": round(tuning["tuning_offset_cents"], 2),
    }


# ============================================================================
# ── ABLETON MCP TOOLS (original set) ────────────────────────────────────────
# ============================================================================

# ── Session / Transport ─────────────────────────────────────────────────────


@app.tool()
def reload_script() -> dict[str, Any]:
    """Reload the Remote Script module without restarting Ableton.
    Copy the updated file first, then call this to apply changes."""
    return _cmd("reload")


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
def start_playback_at(time: float) -> dict[str, Any]:
    """Set arrangement time and start playback atomically (avoids playhead jump)."""
    return _cmd("start_playback_at", time=time)


@app.tool()
def stop_playback() -> dict[str, Any]:
    """Stop playback."""
    return _cmd("stop_playback")


# ── Transport Extras ────────────────────────────────────────────────────


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


@app.tool()
def switch_to_arrangement_view() -> dict[str, Any]:
    """Switch Ableton's main view to Arrangement."""
    return _cmd("switch_to_arrangement_view")


@app.tool()
def set_arrangement_time(time: float) -> dict[str, Any]:
    """Move the arrangement playhead to a beat position."""
    return _cmd("set_current_song_time", time=time)


@app.tool()
def create_midi_track(index: int = -1) -> dict[str, Any]:
    """Create a new MIDI track. index=-1 adds at end."""
    return _cmd("create_midi_track", index=index)


@app.tool()
def set_track_name(track_index: int, name: str) -> dict[str, Any]:
    """Rename a track."""
    return _cmd("set_track_name", track_index=track_index, name=name)


@app.tool()
def select_track(track_index: int) -> dict[str, Any]:
    """Select a track in Ableton's UI."""
    return _cmd("select_track", track_index=track_index)


@app.tool()
def create_clip(
    track_index: int, clip_index: int, length: float = 4.0
) -> dict[str, Any]:
    """Create an empty MIDI clip in a session slot."""
    return _cmd(
        "create_clip", track_index=track_index, clip_index=clip_index, length=length
    )


@app.tool()
def create_audio_clip(track_index: int, clip_index: int, path: str) -> dict[str, Any]:
    """Import an audio file into a session slot (Live 12.0.5+)."""
    return _cmd(
        "create_audio_clip",
        track_index=track_index,
        clip_index=clip_index,
        path=path,
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
def get_arrangement_clips(track_index: int) -> dict[str, Any]:
    """List all clips in the arrangement timeline for a track."""
    return _cmd("get_arrangement_clips", track_index=track_index)


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
    """Delete a clip from the arrangement timeline."""
    return _cmd(
        "delete_arrangement_clip", track_index=track_index, clip_index=clip_index
    )


@app.tool()
def get_browser_tree(category_type: str = "all") -> dict[str, Any]:
    """Browse Ableton's browser tree."""
    return _cmd("get_browser_tree", category_type=category_type)


@app.tool()
def get_browser_categories(category_type: str = "all") -> dict[str, Any]:
    """Get browser categories. category_type: all, instruments, sounds, drums, audio_effects, midi_effects."""
    return _cmd("get_browser_categories", category_type=category_type)


@app.tool()
def get_browser_items(path: str, item_type: str = "all") -> dict[str, Any]:
    """List browser items at a path. item_type: all, devices, presets, files."""
    return _cmd("get_browser_items", path=path, item_type=item_type)


@app.tool()
def get_browser_items_at_path(path: str) -> dict[str, Any]:
    """List browser items at a path."""
    return _cmd("get_browser_items_at_path", path=path)


@app.tool()
def get_browser_item(uri: str = "", path: str = "") -> dict[str, Any]:
    """Get a single browser item by URI or path."""
    return _cmd("get_browser_item", uri=uri, path=path)


@app.tool()
def load_instrument_or_effect(track_index: int, uri: str) -> dict[str, Any]:
    """Load an instrument/effect onto a track by URI."""
    return _send_command(
        "load_instrument_or_effect",
        {"track_index": track_index, "uri": uri},
        timeout=TIMEOUT_LONG,
    )


@app.tool()
def list_external_plugins(
    query: str = "",
    max_results: int = 50,
    refresh_cache: bool = False,
) -> dict[str, Any]:
    """List discovered external plugins (VST/AU), optionally filtered by name query."""
    if refresh_cache:
        _cmd("get_browser_tree", category_type="all")
    result = _cmd("get_browser_categories", category_type="all")
    plugins = result.get("categories", [])
    filtered = []
    for p in plugins:
        if query.lower() in p.lower():
            filtered.append(p)
    return {"plugins": filtered[:max_results], "total": len(filtered)}


@app.tool()
def load_external_plugin(
    track_index: int,
    plugin_name: str,
    exact_match: bool = False,
    refresh_cache: bool = False,
) -> dict[str, Any]:
    """Load an external VST/AU plugin onto a track by plugin name.
    Searches Ableton's browser for the plugin and loads it."""
    uri = f"plugins/VST3/{plugin_name}"
    if exact_match:
        pass
    return _cmd("load_browser_item", track_index=track_index, item_uri=uri)


@app.tool()
def load_drum_kit(
    track_index: int,
    rack_uri: str = "query:Drums#Drum%20Rack",
    kit_path: str = "",
) -> dict[str, Any]:
    """Load a drum rack and then load a specific drum kit into it."""
    result = _cmd("load_instrument_or_effect", track_index=track_index, uri=rack_uri)
    if kit_path:
        _cmd("get_browser_item", path=f"drums/{kit_path}")
    return result


@app.tool()
def get_device_parameters(track_index: int, device_index: int) -> dict[str, Any]:
    """Read all parameters of a device."""
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


@app.tool()
def delete_device(track_index: int, device_index: int) -> dict[str, Any]:
    """Delete a device from a track by index."""
    return _cmd(
        "delete_device",
        track_index=track_index,
        device_index=device_index,
    )


@app.tool()
def set_track_volume(track_index: int, value: float) -> dict[str, Any]:
    """Set a track's volume (0.0–1.0)."""
    return _cmd("set_track_volume", track_index=track_index, value=value)


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


@app.tool()
def delete_track(track_index: int = 0, track_name: str = "") -> dict[str, Any]:
    """Delete a track from the set by index or name."""
    if track_name and track_index == 0:
        info = _cmd("get_session_info")
        for i in range(info.get("track_count", 0)):
            t = _cmd("get_track_info", track_index=i)
            if t.get("name") == track_name:
                track_index = i
                break
    return _cmd("delete_track", track_index=track_index)


@app.tool()
def duplicate_track(track_index: int) -> dict[str, Any]:
    """Duplicate a track."""
    return _cmd("duplicate_track", track_index=track_index)


@app.tool()
def duplicate_clip(track_index: int, clip_index: int) -> dict[str, Any]:
    """Duplicate a session clip."""
    return _cmd("duplicate_clip", track_index=track_index, clip_index=clip_index)


@app.tool()
def quantize_clip(
    track_index: int, clip_index: int, quantize_to: int = 2, amount: float = 1.0
) -> dict[str, Any]:
    """Quantize a MIDI clip."""
    return _cmd(
        "quantize_clip",
        track_index=track_index,
        clip_index=clip_index,
        quantize_to=quantize_to,
        amount=amount,
    )


@app.tool()
def create_scene(index: int = -1) -> dict[str, Any]:
    """Create a new scene."""
    return _cmd("create_scene", index=index)


@app.tool()
def fire_scene(index: int) -> dict[str, Any]:
    """Launch a scene."""
    return _cmd("fire_scene", index=index)


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


@app.tool()
def freeze_track(track_index: int) -> dict[str, Any]:
    """Freeze a track."""
    return _cmd("freeze_track", track_index=track_index)


@app.tool()
def flatten_track(track_index: int) -> dict[str, Any]:
    """Flatten a frozen track."""
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


# ── Clip Envelopes (Modulation) ──────────────────────────────────────────────


@app.tool()
def get_arrangement_clip_envelope(
    track_index: int,
    clip_index: int,
    target: str = "volume",
    is_arrangement: bool = True,
) -> dict[str, Any]:
    """Read clip envelope diagnostic info.
    target: 'volume', 'panning', 'send_N', or 'device_N_PARAMNAME'
    (e.g. 'device_0_Volume' for the Volume parameter of device index 0).
    clip_index is the 0-based index from get_arrangement_clips.
    is_arrangement=True reads arrangement clips, False reads session clip slots.
    Returns exhaustive clip + envelope info."""
    return _cmd(
        "get_clip_envelope",
        track_index=track_index,
        clip_index=clip_index,
        target=target,
        is_arrangement=is_arrangement,
    )


@app.tool()
def set_automation_curve(
    track_index: int,
    clip_index: int,
    target: str = "volume",
    points: list[dict[str, Any]] = [],
    is_arrangement: bool = False,
) -> dict[str, Any]:
    """Set automation curve on a clip from a list of points.

    Each point: {'time': float (beats), 'value': float (raw 0-127)}.
    Uses connected insert_step() calls to create proper step automation.

    target: 'volume', 'panning', 'send_N', or 'device_N_PARAMNAME'
    (e.g. 'device_1_Volume' for the Volume parameter of device index 1).

    track_index is 0-based, clip_index is 0-based.
    is_arrangement=True for arrangement clips, False for session clips."""
    parsed = points or []
    return _cmd(
        "set_automation_curve",
        track_index=track_index,
        clip_index=clip_index,
        target=target,
        points=parsed,
        is_arrangement=is_arrangement,
    )


@app.tool()
def get_clip_envelope(
    track_index: int, clip_index: int, target: str = "volume"
) -> dict[str, Any]:
    """Read modulation envelope points from an arrangement clip.
    target: 'volume', 'panning', 'send_N' (e.g. 'send_0' for reverb send)."""
    return _cmd(
        "get_clip_envelope",
        track_index=track_index,
        clip_index=clip_index,
        target=target,
    )


@app.tool()
def set_clip_envelope(
    track_index: int,
    clip_index: int,
    target: str = "volume",
    points: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Set modulation envelope points on an arrangement clip.
    Each point: {'time': float, 'value': float}.
    target: 'volume', 'panning', 'send_N'."""
    if points is None:
        points = []
    return _cmd(
        "set_clip_envelope",
        track_index=track_index,
        clip_index=clip_index,
        target=target,
        points=points,
    )


@app.tool()
def set_arrangement_clip_envelope(
    track_index: int,
    clip_index: int,
    target: str = "volume",
    points: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Set modulation envelope on an arrangement clip via session-clip workaround.
    Each point: {'time': float, 'value': float}.
    target: 'volume', 'panning', 'send_N', 'device_N_PARAMNAME'."""
    if points is None:
        points = []
    return _cmd(
        "set_arrangement_clip_envelope",
        track_index=track_index,
        clip_index=clip_index,
        target=target,
        points=points,
    )


@app.tool()
def set_track_solo(track_index: int, solo: bool = True) -> dict[str, Any]:
    """Solo a track (True = solo on, False = solo off)."""
    return _cmd("set_track_solo", track_index=track_index, solo=solo)


@app.tool()
def set_track_mute(track_index: int, mute: bool = True) -> dict[str, Any]:
    """Mute a track (True = muted, False = unmuted)."""
    return _cmd("set_track_mute", track_index=track_index, mute=mute)


@app.tool()
def set_arrangement_clip_gain(
    track_index: int, clip_index: int, gain: float
) -> dict[str, Any]:
    """Set the gain (in dB) of an arrangement audio clip.
    clip_index is the 0-based index from get_arrangement_clips."""
    return _cmd(
        "set_arrangement_clip_gain",
        track_index=track_index,
        clip_index=clip_index,
        gain=gain,
    )


@app.tool()
def set_arrangement_clip_pitch(
    track_index: int, clip_index: int, coarse: int = 0, fine: int = 0
) -> dict[str, Any]:
    """Set pitch of an arrangement audio clip (coarse: ±48 semitones, fine: ±50 cents)."""
    return _cmd(
        "set_arrangement_clip_pitch",
        track_index=track_index,
        clip_index=clip_index,
        coarse=coarse,
        fine=fine,
    )


@app.tool()
def set_arrangement_clip_warp(
    track_index: int, clip_index: int, warp_on: bool = True, warp_mode: int = 0
) -> dict[str, Any]:
    """Set warp state of an arrangement audio clip.
    warp_mode: 0=beats, 1=tones, 2=textures, 3=re-pitch, 4=complex, 5=complex-pro."""
    return _cmd(
        "set_arrangement_clip_warp",
        track_index=track_index,
        clip_index=clip_index,
        warp_on=warp_on,
        warp_mode=warp_mode,
    )


@app.tool()
def set_arrangement_clip_markers(
    track_index: int, clip_index: int, start_marker: float, end_marker: float
) -> dict[str, Any]:
    """Set start/end markers of an arrangement audio clip (in beats)."""
    return _cmd(
        "set_arrangement_clip_markers",
        track_index=track_index,
        clip_index=clip_index,
        start_marker=start_marker,
        end_marker=end_marker,
    )


@app.tool()
def set_arrangement_clip_name(
    track_index: int, clip_index: int, name: str
) -> dict[str, Any]:
    """Rename an arrangement clip.
    clip_index is the 0-based index from get_arrangement_clips."""
    return _cmd(
        "set_arrangement_clip_name",
        track_index=track_index,
        clip_index=clip_index,
        name=name,
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


# ── Extended Device Management ────────────────────────────────────────────────


@app.tool()
def enable_device(
    track_index: int, device_index: int = 0, device_name: str = "", chain_index: int = 0
) -> dict[str, Any]:
    """Enable (activate) a device on a track."""
    return _cmd(
        "enable_device",
        track_index=track_index,
        device_index=device_index,
        device_name=device_name,
        chain_index=chain_index,
    )


@app.tool()
def disable_device(
    track_index: int, device_index: int = 0, device_name: str = "", chain_index: int = 0
) -> dict[str, Any]:
    """Disable (bypass) a device on a track."""
    return _cmd(
        "disable_device",
        track_index=track_index,
        device_index=device_index,
        device_name=device_name,
        chain_index=chain_index,
    )


@app.tool()
def navigate_device_preset(
    track_index: int,
    device_index: int = 1,
    chain_index: int = 0,
    direction: str = "next",
) -> dict[str, Any]:
    """Navigate device presets (next/previous)."""
    return _cmd(
        "navigate_device_preset",
        track_index=track_index,
        device_index=device_index,
        chain_index=chain_index,
        direction=direction,
    )


@app.tool()
def get_chain_info(
    track_index: int, device_index: int = 1, chain_index: int = 0
) -> dict[str, Any]:
    """List chains in a rack device, or devices within a specific chain."""
    return _cmd(
        "get_chain_info",
        track_index=track_index,
        device_index=device_index,
        chain_index=chain_index,
    )


@app.tool()
def get_drum_pad_info(track_index: int, device_index: int = 1) -> dict[str, Any]:
    """List filled drum pads in a Drum Rack."""
    return _cmd(
        "get_drum_pad_info",
        track_index=track_index,
        device_index=device_index,
    )


@app.tool()
def get_drum_pad_parameters(
    track_index: int,
    device_index: int = 1,
    note: int = 36,
    chain_index: int = 0,
    device_index_in_chain: int = 0,
) -> dict[str, Any]:
    """List parameters of a drum pad's instrument device (by MIDI note)."""
    return _cmd(
        "get_drum_pad_parameters",
        track_index=track_index,
        device_index=device_index,
        note=note,
        chain_index=chain_index,
        device_index_in_chain=device_index_in_chain,
    )


@app.tool()
def set_drum_pad_parameter(
    track_index: int,
    device_index: int = 1,
    note: int = 36,
    parameter_name: str = "Volume",
    value: float = 1.0,
    chain_index: int = 0,
    device_index_in_chain: int = 0,
) -> dict[str, Any]:
    """Set a parameter of a drum pad's instrument device (by MIDI note)."""
    return _cmd(
        "set_drum_pad_parameter",
        track_index=track_index,
        device_index=device_index,
        note=note,
        chain_index=chain_index,
        device_index_in_chain=device_index_in_chain,
        parameter_name=parameter_name,
        value=value,
    )


# ── Track Mixer Extras ──────────────────────────────────────────────────────


@app.tool()
def set_track_panning(track_index: int, panning: float) -> dict[str, Any]:
    """Set the mixer panning for a track (-1.0 to 1.0)."""
    return _cmd("set_track_panning", track_index=track_index, panning=panning)


@app.tool()
def get_track_volume(track_index: int) -> dict[str, Any]:
    """Get a track's volume and panning info.
    Volume 0.85 = 0 dB unity gain."""
    return _cmd("get_track_volume", track_index=track_index)


# ── View Control ────────────────────────────────────────────────────────────


@app.tool()
def set_ableton_view(view: str = "Arranger") -> dict[str, Any]:
    """Switch Ableton's main view. Options: Arranger, Session, Detail, Detail/Clip, Detail/DeviceChain, Browser."""
    return _cmd("set_ableton_view", view=view)


@app.tool()
def control_arrangement_view(action: str, track_index: int = 0) -> dict[str, Any]:
    """Control arrangement view: zoom_in, zoom_out, scroll_left, scroll_right, follow_on, follow_off, collapse_track, expand_track."""
    return _cmd(
        "control_arrangement_view",
        action=action,
        track_index=track_index,
    )


# ── Cue Points ──────────────────────────────────────────────────────────────


@app.tool()
def get_cue_points() -> dict[str, Any]:
    """List all cue points (locators) with bar positions."""
    return _cmd("get_cue_points")


@app.tool()
def set_song_time(bar: int = 0, beat: float = 0.0) -> dict[str, Any]:
    """Jump playback to a bar/beat position. bar is 1-based."""
    return _cmd("set_current_song_time", time=bar * 4.0 if bar > 0 else beat)


@app.tool()
def set_arrangement_loop(
    enabled: bool = True,
    start_bar: int = 0,
    end_bar: int = 0,
    start_beat: float = 0.0,
    length_beats: float = 0.0,
) -> dict[str, Any]:
    """Enable/disable arrangement loop and set region."""
    return _cmd(
        "set_arrangement_loop",
        enabled=enabled,
        start_bar=start_bar,
        end_bar=end_bar,
        start_beat=start_beat,
        length_beats=length_beats,
    )


@app.tool()
def jump_to_cue_point(direction: str = "", name: str = "") -> dict[str, Any]:
    """Jump to a cue point by direction ('next'/'prev') or name."""
    return _cmd("jump_to_cue_point", direction=direction, name=name)


@app.tool()
def create_cue_point(bar: int = 0, beat: float = 0.0, name: str = "") -> dict[str, Any]:
    """Create a cue point at bar/beat position."""
    return _cmd("create_cue_point", bar=bar, beat=beat, name=name)


@app.tool()
def delete_cue_point(bar: int = 0, beat: float = 0.0) -> dict[str, Any]:
    """Delete a cue point at bar/beat position."""
    return _cmd("delete_cue_point", bar=bar, beat=beat)


# ── Arrangement Clip Management ─────────────────────────────────────────────


@app.tool()
def create_arrangement_midi_clip(
    track_index: int,
    start_bar: int = 0,
    end_bar: int = 0,
    start_beat: float = 0.0,
    length_beats: float = 4.0,
    name: str = "",
) -> dict[str, Any]:
    """Create an empty MIDI clip in the arrangement."""
    return _cmd(
        "create_arrangement_midi_clip",
        track_index=track_index,
        start_bar=start_bar,
        end_bar=end_bar,
        start_beat=start_beat,
        length_beats=length_beats,
        name=name,
    )


@app.tool()
def create_arrangement_audio_clip(
    track_index: int,
    file_path: str,
    start_bar: int = 0,
    start_beat: float = 0.0,
) -> dict[str, Any]:
    """Place an audio file as a clip in the arrangement."""
    return _cmd(
        "create_arrangement_audio_clip",
        track_index=track_index,
        file_path=file_path,
        start_bar=start_bar,
        start_beat=start_beat,
    )


@app.tool()
def duplicate_clip_to_arrangement(
    track_index: int,
    clip_index: int,
    destination_bar: int = 0,
    destination_beat: float = 0.0,
) -> dict[str, Any]:
    """Copy a session clip to the arrangement."""
    return _cmd(
        "duplicate_clip_to_arrangement",
        track_index=track_index,
        clip_index=clip_index,
        destination_bar=destination_bar,
        destination_beat=destination_beat,
    )


# ── Automation Management ────────────────────────────────────────────────────


@app.tool()
def manage_clip_automation(
    track_index: int,
    clip_index: int = 1,
    clip_name: str = "",
    action: str = "create",
    parameter_name: str = "volume",
) -> dict[str, Any]:
    """Create or clear automation envelopes on arrangement clips."""
    return _cmd(
        "manage_clip_automation",
        track_index=track_index,
        clip_index=clip_index,
        clip_name=clip_name,
        action=action,
        parameter_name=parameter_name,
    )


@app.tool()
def add_clip_envelope_point(
    track_index: int,
    clip_index: int,
    target: str = "device_1_Volume",
    time: float = 0.0,
    value: float = 0.0,
    duration: float = 0.0,
    is_arrangement: bool = False,
) -> dict[str, Any]:
    """Write an automation point or step into a clip's envelope."""
    return _cmd(
        "add_clip_envelope_point",
        track_index=track_index,
        clip_index=clip_index,
        target=target,
        time=time,
        value=value,
        duration=duration,
        is_arrangement=is_arrangement,
    )


@app.tool()
def clear_clip_envelope(
    track_index: int,
    clip_index: int,
    target: str = "device_1_Volume",
    is_arrangement: bool = False,
) -> dict[str, Any]:
    """Clear automation envelope for a parameter on a clip."""
    return _cmd(
        "clear_clip_envelope",
        track_index=track_index,
        clip_index=clip_index,
        target=target,
        is_arrangement=is_arrangement,
    )


@app.tool()
def experiment_envelope(
    track_index: int,
    clip_index: int,
    target: str = "device_1_Volume",
    is_arrangement: bool = False,
) -> dict[str, Any]:
    """Run comprehensive envelope experiments to find working automation approaches."""
    return _cmd(
        "experiment_envelope",
        track_index=track_index,
        clip_index=clip_index,
        target=target,
        is_arrangement=is_arrangement,
    )


@app.tool()
def envelope_dump(
    track_index: int,
    clip_index: int,
    is_arrangement: bool = True,
) -> dict[str, Any]:
    """Ultra-exhaustive dump of clip envelope state."""
    return _cmd(
        "envelope_dump",
        track_index=track_index,
        clip_index=clip_index,
        is_arrangement=is_arrangement,
    )


@app.tool()
def test_create_event(
    track_index: int,
    clip_index: int,
    target: str = "device_1_Volume",
    time: float = 0.0,
    value: float = 0.0,
) -> dict[str, Any]:
    """Test various create_event signatures on the clip envelope."""
    return _cmd(
        "test_create_event",
        track_index=track_index,
        clip_index=clip_index,
        target=target,
        time=time,
        value=value,
    )


@app.tool()
def get_track_deletion_status() -> dict[str, Any]:
    """Check whether session tracks can be deleted right now."""
    return _cmd("get_track_deletion_status")


# ── Clip Envelope Debug ─────────────────────────────────────────────────────────


@app.tool()
def debug_clip_envelopes(
    track_index: int,
    clip_index: int,
    is_arrangement: bool = True,
) -> dict[str, Any]:
    """Exhaustive diagnostic of clip envelopes.
    is_arrangement=True reads arrangement clips, False reads session clip slots.
    Returns all clip properties + all automation envelopes found."""
    return _cmd(
        "debug_clip_envelopes",
        track_index=track_index,
        clip_index=clip_index,
        is_arrangement=is_arrangement,
    )


# ── Master Track ──────────────────────────────────────────────────────────────


@app.tool()
def get_master_track() -> dict[str, Any]:
    """Get master track info: volume, pan, devices."""
    return _cmd("get_master_track")


@app.tool()
def set_master_volume(value: float) -> dict[str, Any]:
    """Set master track volume (0.0–1.0)."""
    return _cmd("set_master_volume", value=value)


@app.tool()
def get_master_device_parameters(device_index: int) -> dict[str, Any]:
    """Read all parameters of a device on the master track."""
    return _cmd("get_master_device_parameters", device_index=device_index)


@app.tool()
def set_master_device_parameter(
    device_index: int, parameter_name: str, value: float
) -> dict[str, Any]:
    """Set a device parameter value on the master track."""
    return _cmd(
        "set_master_device_parameter",
        device_index=device_index,
        parameter_name=parameter_name,
        value=value,
    )


@app.tool()
def load_instrument_or_effect_on_master(uri: str) -> dict[str, Any]:
    """Load an instrument/effect onto the master track by URI."""
    return _cmd("load_browser_item_on_master", uri=uri)


@app.tool()
def set_master_panning(value: float) -> dict[str, Any]:
    """Set master panning (-1.0–1.0)."""
    return _cmd("set_master_panning", value=value)


# ── Return tracks ──────────────────────────────────────────────────────────


@app.tool()
def get_return_tracks() -> dict[str, Any]:
    """Get return tracks info: name, volume, pan, mute, devices."""
    return _cmd("get_return_tracks")


@app.tool()
def get_return_track_device_parameters(
    return_index: int, device_index: int
) -> dict[str, Any]:
    """Read all parameters of a device on a return track."""
    return _cmd(
        "get_return_track_device_parameters",
        return_index=return_index,
        device_index=device_index,
    )


@app.tool()
def set_return_track_device_parameter(
    return_index: int, device_index: int, parameter_name: str, value: float
) -> dict[str, Any]:
    """Set a device parameter value on a return track."""
    return _cmd(
        "set_return_track_device_parameter",
        return_index=return_index,
        device_index=device_index,
        parameter_name=parameter_name,
        value=value,
    )


@app.tool()
def set_return_track_volume(return_index: int, value: float) -> dict[str, Any]:
    """Set return track volume (0.0–1.0)."""
    return _cmd("set_return_track_volume", return_index=return_index, value=value)


@app.tool()
def load_instrument_or_effect_on_return_track(
    return_index: int, uri: str
) -> dict[str, Any]:
    """Load an effect onto a return track by URI (e.g. Reverb, Delay)."""
    return _cmd("load_browser_item_on_return_track", return_index=return_index, uri=uri)


# ── Crossfader ───────────────────────────────────────────────────────────


@app.tool()
def get_crossfader() -> dict[str, Any]:
    """Get master crossfader position (0.0–1.0)."""
    return _cmd("get_crossfader")


@app.tool()
def set_crossfader(value: float) -> dict[str, Any]:
    """Set master crossfader position (0.0–1.0)."""
    return _cmd("set_crossfader", value=value)


# ── Groove ───────────────────────────────────────────────────────────────


@app.tool()
def get_groove_amount() -> dict[str, Any]:
    """Get global groove amount (0.0–1.0)."""
    return _cmd("get_groove_amount")


@app.tool()
def set_groove_amount(amount: float) -> dict[str, Any]:
    """Set global groove amount (0.0–1.0)."""
    return _cmd("set_groove_amount", amount=amount)


# ── System / Monitoring ──────────────────────────────────────────────────


@app.tool()
def show_message(text: str) -> dict[str, Any]:
    """Show a message in Live's status bar."""
    return _cmd("show_message", text=text)


@app.tool()
def get_cpu_load() -> dict[str, Any]:
    """Get CPU usage: average and peak percent, plus process RAM (MB)."""
    return _cmd("get_cpu_load")


@app.tool()
def get_cpu_report() -> dict[str, Any]:
    """CPU + RAM globaux et diagnostics par piste (états devices, RAM).

    Utile pour repérer les devices gourmands (Surge, Analog Lab, Ozone, plugins).
    """
    return _cmd("get_cpu_report")


@app.tool()
def get_track_diagnostics(track_index: int) -> dict[str, Any]:
    """Per-track CPU/RAM diagnostics: device on/off states, plugin/rack flags, RAM."""
    return _cmd("get_track_diagnostics", track_index=track_index)


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


# ── Track Routing ────────────────────────────────────────────────────────


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


# ============================================================================
# ── CAPTURE + ANALYSIS TOOLS ──────────────────────────────────────────────
# ============================================================================
# ── MUSIC ANALYSIS TOOLS (with atomic capture_at_position) ──────────────────
# ============================================================================


# @app.tool()
async def capture_ableton(
    duration: float = 15.0,
    output_name: str | None = None,
) -> dict:
    """Capture audio from Ableton Live via VB-Cable."""
    if output_name is None:
        output_name = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    if CABLE_DEVICE_ID is None:
        raise RuntimeError(
            "CABLE Output (VB-Audio Virtual Cable) not found. Make sure VB-Cable is installed."
        )

    wav_path = str(ANALYSES_DIR / f"{output_name}.wav")
    recorded = []

    def callback(indata, frames, time_info, status):
        if status:
            import warnings

            warnings.warn(f"Capture status: {status}")
        recorded.append(indata.copy())

    device_info = sd.query_devices(CABLE_DEVICE_ID)
    samplerate = int(device_info["default_samplerate"])

    with sd.InputStream(
        device=CABLE_DEVICE_ID,
        channels=2,
        samplerate=samplerate,
        callback=callback,
    ):
        await asyncio.sleep(duration)

    if not recorded:
        raise RuntimeError("No audio captured from VB-Cable")

    audio = np.concatenate(recorded, axis=0)
    sf.write(wav_path, audio, samplerate)

    max_amp = np.abs(audio).max()
    if max_amp < 0.001:
        raise RuntimeError(
            "Captured audio is silence. Check that:\n"
            "1. Ableton is playing audio\n"
            "2. Audio output is set to 'CABLE Input (VB-Audio Virtual Cable)'\n"
            "3. The track is not muted"
        )

    result = load(wav_path)
    result["wav_path"] = wav_path
    return result


async def _record_wav(output_name: str, duration_sec: float) -> str | None:
    """Record from VB-Cable for duration_sec. Returns wav_path or None."""
    if CABLE_DEVICE_ID is None:
        return None
    wav_path = str(ANALYSES_DIR / f"{output_name}.wav")
    recorded = []

    def callback(indata, frames, time_info, status):
        if status:
            import warnings

            warnings.warn(f"Capture status: {status}")
        recorded.append(indata.copy())

    dev = sd.query_devices(CABLE_DEVICE_ID)
    sr = int(dev["default_samplerate"])

    with sd.InputStream(
        device=CABLE_DEVICE_ID, channels=2, samplerate=sr, callback=callback
    ):
        await asyncio.sleep(duration_sec)

    if not recorded:
        return None

    sf.write(wav_path, np.concatenate(recorded, axis=0), sr)
    return wav_path


def _ableton_stop_and_seek(position_beats: float) -> dict:
    """Stop → start_playback_at (start first, then set time)."""
    _cmd("stop_playback")
    for _ in range(30):
        if not _cmd("get_session_info").get("is_playing"):
            break
        time.sleep(0.1)

    _cmd("start_playback_at", time=position_beats)
    time.sleep(0.3)
    info = _cmd("get_session_info")

    return {
        "requested": position_beats,
        "position": info.get("current_song_time"),
        "is_playing": info.get("is_playing"),
    }


# @app.tool()
async def capture_at_position(
    position_beats: float,
    duration_sec: float = 10.0,
    output_name: str | None = None,
) -> dict:
    """
    Atomic capture at arrangement position.

    Workflow:
    stop → start_playback_at → record (blocking) → stop → load
    """
    if output_name is None:
        output_name = f"cap_{position_beats:.0f}b_{datetime.now().strftime('%H%M%S')}"

    seek = _ableton_stop_and_seek(position_beats)

    wav_path = await _record_wav(output_name, duration_sec)
    if wav_path is None:
        return {"error": "Capture failed", "seek": seek}

    _cmd("stop_playback")
    time.sleep(0.3)
    end = _cmd("get_session_info")

    result = load(wav_path)
    result["wav_path"] = wav_path
    result["position_beats"] = position_beats
    result["duration_sec"] = duration_sec
    result["seek"] = seek
    result["end_song_time"] = end.get("current_song_time")
    return result


@app.tool()
async def capture_and_analyze(
    position_beats: float = 0.0,
    duration_sec: float = 10.0,
    output_name: str | None = None,
) -> dict:
    """Capture at position and analyze in one call."""
    cap = await capture_at_position(
        position_beats=position_beats,
        duration_sec=duration_sec,
        output_name=output_name,
    )
    if "error" in cap:
        return cap
    analysis = analyze_full(cap["y_path"])
    return {**cap, **analysis}


@app.tool()
def analyze_full_tool(y_path: str) -> dict:
    """Run all analysis tools on audio."""
    return analyze_full(y_path)


@app.tool()
def analyze_energy_tool(y_path: str) -> dict:
    """Analyze energy and dynamics."""
    return analyze_energy(y_path)


@app.tool()
def analyze_spectral_tool(y_path: str) -> dict:
    """Analyze spectral characteristics."""
    return analyze_spectral(y_path)


@app.tool()
def analyze_tuning_tool(y_path: str) -> dict:
    """Analyze tuning offset."""
    return analyze_tuning(y_path)


@app.tool()
def detect_key_tool(y_path: str) -> dict:
    """Detect musical key."""
    return detect_key(y_path)


@app.tool()
def get_duration_tool(y_path: str) -> dict:
    """Get audio duration."""
    dur = get_duration(y_path)
    return {"duration_seconds": dur}


@app.tool()
def tempo_tool(y_path: str) -> dict:
    """Estimate tempo."""
    bpm = tempo(y_path)
    return {"tempo_bpm": bpm}


@app.tool()
def beat_track_tool(y_path: str) -> dict:
    """Track beats."""
    return beat_track(y_path)


@app.tool()
def chroma_cqt_tool(y_path: str) -> dict:
    """Compute chromagram."""
    path = chroma_cqt(y_path)
    return {"chroma_path": path}


@app.tool()
def mfcc_tool(y_path: str) -> dict:
    """Compute MFCC."""
    path = mfcc(y_path)
    return {"mfcc_path": path}


@app.tool()
def load_tool(file_path: str) -> dict:
    """Load audio file."""
    return load(file_path)


if __name__ == "__main__":
    # Preload librosa modules — first call to chroma/beat/tempo triggers
    # numba compilation which can take 5-15s. Do it at startup so the first
    # capture doesn't time out.
    # Wrapped in try/except with warnings suppressed so limited CPU/memory
    # doesn't block server startup or spam the console with benign warnings.
    import warnings as _warnings

    _warnings.filterwarnings("ignore", category=UserWarning, module="librosa")
    _warnings.filterwarnings("ignore", category=FutureWarning, module="librosa")
    try:
        sr = 22050
        dummy = np.zeros(sr * 1, dtype=np.float32)
        _L().feature.rms(y=dummy)[0]
        _L().feature.spectral_centroid(y=dummy, sr=sr)[0]
        _L().feature.zero_crossing_rate(dummy)[0]
        _L().feature.chroma_cqt(y=dummy, sr=sr, n_chroma=12)
        _L().beat.tempo(y=dummy, sr=sr)
        _L().feature.mfcc(y=dummy, sr=sr, n_mfcc=13)
        _L().onset.onset_strength(y=dummy, sr=sr)
    except Exception:
        pass

    app.run(transport="stdio")
