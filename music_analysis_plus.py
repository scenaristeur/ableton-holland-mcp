"""MCP server: capture Ableton audio via VB-Cable + analyse librosa."""

import asyncio
import os
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import sounddevice as sd
import soundfile as sf
import librosa

from mcp_music_analysis.server import (
    mcp,
    load,
    get_duration,
    tempo,
    chroma_cqt,
    mfcc,
    beat_track,
)
from mcp_music_analysis.server import download_from_url, download_from_youtube


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


def play_audio(audio, sr):
    """Play audio data through the default output device (non-blocking)."""
    sd.play(audio, sr)


def play_wav(path: str):
    """Play a WAV file through the default output device."""
    audio, sr = sf.read(path)
    play_audio(audio, sr)


@mcp.tool()
async def capture_ableton(
    duration: float = 5.0,
    output_name: str | None = None,
) -> dict:
    """
    Capture audio from Ableton Live via VB-Cable and load it for analysis.
    Requires Ableton's audio output to be set to 'CABLE Input (VB-Audio Virtual Cable)'.

    Parameters:
    - duration: Recording duration in seconds (default: 5.0)
    - output_name: Optional base name for the output file

    Returns the y_path of the loaded audio, ready for analysis with the other tools.
    """
    if output_name is None:
        output_name = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    if CABLE_DEVICE_ID is None:
        raise RuntimeError(
            "CABLE Output (VB-Audio Virtual Cable) not found among input devices. "
            "Make sure VB-Cable is installed."
        )

    wav_path = str(ANALYSES_DIR / f"{output_name}.wav")
    recorded = []
    event = asyncio.Event()

    def callback(indata, frames, time_info, status):
        if status:
            import warnings

            warnings.warn(f"Capture status: {status}")
        recorded.append(indata.copy())

    device_info = sd.query_devices(CABLE_DEVICE_ID)
    samplerate = int(device_info["default_samplerate"])

    def stop():
        event.set()

    with sd.InputStream(
        device=CABLE_DEVICE_ID,
        channels=2,
        samplerate=samplerate,
        callback=callback,
        finished_callback=stop,
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


@mcp.tool()
async def capture_and_tempo(
    duration: float = 5.0,
    hop_length: int = 512,
    start_bpm: float = 120,
) -> dict:
    """
    Capture audio from Ableton and estimate tempo in one call.
    """
    loaded = await capture_ableton(duration=duration)
    y_path = loaded["y_path"]
    bpm_result = tempo(y_path, hop_length=hop_length, start_bpm=start_bpm)
    dur = get_duration(y_path)
    bpm_value = (
        float(bpm_result[0]) if hasattr(bpm_result, "__len__") else float(bpm_result)
    )
    return {
        "duration_s": dur,
        "tempo_bpm": bpm_value,
        "y_path": y_path,
    }


@mcp.tool()
def detect_key(y_path: str) -> dict:
    """
    Detect the musical key of an audio signal using Krumhansl-Kessler algorithm.
    Takes a y_path from load() or capture_ableton().
    Returns key, mode (major/minor), and confidence score.
    """
    y = _read_y(y_path)
    sr = 22050
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    return _detect_key_from_chroma(chroma)


@mcp.tool()
async def capture_and_analyze(
    duration: float = 5.0,
) -> dict:
    """
    Capture audio from Ableton and run full analysis (tempo, beats, chroma, MFCC, key).
    Returns paths to all analysis files and detected key.
    """
    loaded = await capture_ableton(duration=duration)
    y_path = loaded["y_path"]

    dur = get_duration(y_path)
    bpm_result = tempo(y_path)
    beats_result = beat_track(y_path)
    chroma_path = chroma_cqt(y_path)
    mfcc_path = mfcc(y_path)

    bpm_value = (
        float(bpm_result[0]) if hasattr(bpm_result, "__len__") else float(bpm_result)
    )

    key_info = detect_key(y_path)

    return {
        "duration_s": dur,
        "tempo_bpm": bpm_value,
        "beat_count": len(beats_result["beats"]),
        "chroma_path": chroma_path,
        "mfcc_path": mfcc_path,
        "y_path": y_path,
        "key": key_info["key"],
        "mode": key_info["mode"],
        "key_confidence": round(key_info["confidence"], 1),
    }


if __name__ == "__main__":
    mcp.run()


def main():
    mcp.run()
