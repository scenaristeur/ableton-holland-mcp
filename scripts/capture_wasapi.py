"""Capture audio using WASAPI loopback (captures what you hear)."""

import argparse
import time
import numpy as np
import soundfile as sf
from comtypes import GUID, POINTER, CoInitialize, CoCreateInstance
from comtypes.automation import VARIANT
from ctypes import (
    c_int,
    c_uint,
    c_uint32,
    c_float,
    c_void_p,
    byref,
    sizeof,
    memmove,
    Structure,
    POINTER as CPOINTER,
)

# Windows Core Audio API GUIDs
CLSID_MMDeviceEnumerator = GUID("{BCDE0395-E52F-467C-8E3D-C4579291692E}")
IID_IMMDeviceEnumerator = GUID("{A95664D2-9614-4F35-A746-DE8DB63617E6}")
IID_IAudioClient = GUID("{1CB9AD4C-DBFA-4C32-B178-C2F568A703B2}")
IID_IAudioCaptureClient = GUID("{C8ADBD64-E71E-48A0-A4DE-185C395CD317}")
IID_IAudioRenderClient = GUID("{F294ACFC-3146-4483-A7BF-ADDCA7C260E2}")
eRender = 0
eMultimedia = 1
eConsole = 0
eCommunications = 1


class WAVEFORMATEX(Structure):
    _fields_ = [
        ("wFormatTag", c_uint),
        ("nChannels", c_uint),
        ("nSamplesPerSec", c_uint),
        ("nAvgBytesPerSec", c_uint),
        ("nBlockAlign", c_uint),
        ("wBitsPerSample", c_uint),
        ("cbSize", c_uint),
    ]


AUDCLNT_SHAREMODE_SHARED = 0
AUDCLNT_STREAMFLAGS_LOOPBACK = 0x00020000


def main():
    parser = argparse.ArgumentParser(description="Capture audio via WASAPI loopback")
    parser.add_argument("-o", "--output", default="capture_wasapi.wav")
    parser.add_argument(
        "-t",
        "--duration",
        type=float,
        default=None,
        help="Duration in seconds (default: unlimited, Ctrl+C)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="default",
        help="Device role: default, communications, multimedia",
    )
    args = parser.parse_args()

    CoInitialize()

    # Get device enumerator
    enumerator = CoCreateInstance(
        CLSID_MMDeviceEnumerator,
        IID_IMMDeviceEnumerator,
    )

    # Get default audio render device
    device = enumerator.GetDefaultAudioEndpoint(eRender, eConsole)

    # Activate IAudioClient
    client = device.Activate(IID_IAudioClient)

    # Get mix format
    fmt = client.GetMixFormat()
    print(f"Format: {fmt.nChannels}ch, {fmt.nSamplesPerSec}Hz, {fmt.wBitsPerSample}bit")

    # Initialize in loopback mode
    client.Initialize(
        AUDCLNT_SHAREMODE_SHARED,
        AUDCLNT_STREAMFLAGS_LOOPBACK,
        200000,  # 200ms buffer
        0,
        fmt,
        None,
    )

    # Get capture client
    capture_client = client.GetService(IID_IAudioCaptureClient)

    frame_size = fmt.nBlockAlign
    buffer_frames = 1024
    client.Start()

    print("Recording... Press Ctrl+C to stop.")
    if args.duration:
        print(f"Duration: {args.duration}s")

    all_audio = []
    start_time = time.time()
    try:
        while True:
            frames = None
            try:
                frames = capture_client.GetNextPacketSize()
            except Exception:
                break

            if frames > 0:
                data = capture_client.GetBuffer(frames)
                # data is (buffer_pointer, frames_available, flags, stream_position)
                buf_ptr = data[0]
                frames_avail = data[1]
                buf_size = frames_avail * frame_size
                raw = (c_uint8 * buf_size).from_address(buf_ptr)
                np_data = np.frombuffer(bytes(raw), dtype=np.int16)
                np_data = np_data.reshape(-1, fmt.nChannels)
                all_audio.append(np_data)

                capture_client.ReleaseBuffer(frames_avail)

            if args.duration and time.time() - start_time >= args.duration:
                break
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass
    finally:
        client.Stop()
        if all_audio:
            audio = np.concatenate(all_audio, axis=0)
            sf.write(args.output, audio, int(fmt.nSamplesPerSec))
            dur = len(audio) / fmt.nSamplesPerSec
            print(f"\nSaved {dur:.1f}s to {args.output}")
        else:
            print("No audio captured.")


if __name__ == "__main__":
    main()
