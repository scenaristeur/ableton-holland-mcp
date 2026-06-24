"""MCP server: capture Ableton audio via VB-Cable + analyse librosa."""

import asyncio
import os
import tempfile

import numpy as np
import sounddevice as sd
import soundfile as sf

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


CABLE_DEVICE_ID = None
for i, d in enumerate(sd.query_devices()):
    if "CABLE Output" in d["name"] and d["max_input_channels"] > 0:
        CABLE_DEVICE_ID = i
        break


@mcp.tool()
async def capture_ableton(
    duration: float = 5.0,
    output_name: str = None,
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
        output_name = "ableton_capture"

    if CABLE_DEVICE_ID is None:
        raise RuntimeError(
            "CABLE Output (VB-Audio Virtual Cable) not found among input devices. "
            "Make sure VB-Cable is installed."
        )

    wav_path = os.path.join(tempfile.gettempdir(), f"{output_name}.wav")
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

    return load(wav_path)


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
async def capture_and_analyze(
    duration: float = 5.0,
) -> dict:
    """
    Capture audio from Ableton and run full analysis (tempo, beats, chroma, MFCC).
    Returns paths to all analysis files.
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

    return {
        "duration_s": dur,
        "tempo_bpm": bpm_value,
        "beat_count": len(beats_result["beats"]),
        "chroma_path": chroma_path,
        "mfcc_path": mfcc_path,
        "y_path": y_path,
    }


if __name__ == "__main__":
    mcp.run()


def main():
    mcp.run()
