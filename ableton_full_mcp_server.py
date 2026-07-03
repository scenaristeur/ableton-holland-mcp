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
import librosa
import librosa.util

from fastmcp import FastMCP

# ── Ableton MCP Helpers ─────────────────────────────────────────────────────

HOST = "127.0.0.1"
PORT = 9877
TIMEOUT = 30.0

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
    y = librosa.util.normalize(y)
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
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
    bpm = librosa.beat.tempo(
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
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
    frames = librosa.beat.beat_track(
        onset_envelope=onset_env, sr=sr, hop_length=hop_length, start_bpm=start_bpm
    )[1]
    if units == "time":
        beats = librosa.frames_to_time(frames, sr=sr, hop_length=hop_length).tolist()
    elif units == "samples":
        beats = librosa.frames_to_samples(frames, hop_length=hop_length).tolist()
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
    chroma = librosa.feature.chroma_cqt(
        y=y,
        sr=sr,
        hop_length=hop_length,
        fmin=fmin,
        n_chroma=n_chroma,
        n_octaves=n_octaves,
    )
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    times = librosa.frames_to_time(
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
    mfcc_features = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_path = str(ANALYSES_DIR / f"{Path(y_path).stem}_mfcc.csv")
    pd.DataFrame(mfcc_features).to_csv(mfcc_path, index=False, header=False)
    return mfcc_path


def analyze_energy(y_path: str) -> dict:
    """Analyze energy and dynamics."""
    y = _read_y(y_path)
    sr = 22050
    rms = librosa.feature.rms(y=y)[0]
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
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
    bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
    zcr = librosa.feature.zero_crossing_rate(y)[0]
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
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_mean = chroma.mean(axis=1)
    fft = np.abs(librosa.stft(y))
    freqs = librosa.fft_frequencies(sr=sr)
    spec = np.mean(fft, axis=1)
    peak_freq = freqs[np.argmax(spec)]
    a4_freq = 440.0
    cents_offset = 1200 * np.log2(peak_freq / a4_freq)
    return {"tuning_offset_cents": float(cents_offset)}


def detect_key(y_path: str) -> dict:
    """Detect key using Krumhansl-Kessler."""
    y = _read_y(y_path)
    sr = 22050
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
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
def get_browser_items_at_path(path: str) -> dict[str, Any]:
    """List browser items at a path."""
    return _cmd("get_browser_items_at_path", path=path)


@app.tool()
def load_instrument_or_effect(track_index: int, uri: str) -> dict[str, Any]:
    """Load an instrument/effect onto a track by URI."""
    return _cmd("load_instrument_or_effect", track_index=track_index, uri=uri)


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
def set_track_volume(track_index: int, value: float) -> dict[str, Any]:
    """Set a track's volume (0.0–1.0)."""
    return _cmd("set_track_volume", track_index=track_index, value=value)


@app.tool()
def set_track_color(track_index: int, color: int) -> dict[str, Any]:
    """Set a track's color index (0–255)."""
    return _cmd("set_track_color", track_index=track_index, color=color)


@app.tool()
def set_clip_color(track_index: int, clip_index: int, color: int) -> dict[str, Any]:
    """Set a clip's color index (0–255)."""
    return _cmd(
        "set_clip_color", track_index=track_index, clip_index=clip_index, color=color
    )


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
    try:
        sr = 22050
        dummy = np.zeros(sr * 3, dtype=np.float32)  # 3s of silence
        _ = librosa.feature.rms(y=dummy)[0]
        _ = librosa.feature.spectral_centroid(y=dummy, sr=sr)[0]
        _ = librosa.feature.zero_crossing_rate(dummy)[0]
        _ = librosa.feature.chroma_cqt(y=dummy, sr=sr, n_chroma=12)
        _ = librosa.beat.tempo(y=dummy, sr=sr)
        _ = librosa.feature.mfcc(y=dummy, sr=sr, n_mfcc=13)
        _ = librosa.onset.onset_strength(y=dummy, sr=sr)
    except Exception:
        pass  # Preload is best-effort

    app.run(transport="stdio")
