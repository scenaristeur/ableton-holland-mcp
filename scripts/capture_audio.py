"""Capture audio from VB-Cable and save to WAV file."""

import argparse
import sys
import time
import numpy as np
import sounddevice as sd
import soundfile as sf


def main():
    parser = argparse.ArgumentParser(description="Capture audio from VB-Cable")
    parser.add_argument(
        "-d",
        "--device",
        type=int,
        default=20,
        help="Input device index (default: 20 = CABLE Output)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="capture.wav",
        help="Output WAV file (default: capture.wav)",
    )
    parser.add_argument(
        "-t",
        "--duration",
        type=float,
        default=None,
        help="Recording duration in seconds (default: unlimited, Ctrl+C to stop)",
    )
    parser.add_argument(
        "-c", "--channels", type=int, default=2, help="Number of channels (default: 2)"
    )
    parser.add_argument(
        "--sr", type=int, default=48000, help="Sample rate (default: 48000)"
    )
    args = parser.parse_args()

    device_info = sd.query_devices(args.device)
    print(f"Device: {device_info['name']}")
    print(f"Channels: {args.channels}")
    print(f"Sample rate: {args.sr}")
    print(f"Output: {args.output}")
    if args.duration:
        print(f"Duration: {args.duration}s")
    else:
        print("Recording... Press Ctrl+C to stop.")

    recorded = []

    def callback(indata, frames, time_info, status):
        if status:
            print(status, file=sys.stderr)
        recorded.append(indata.copy())

    try:
        with sd.InputStream(
            device=args.device,
            channels=args.channels,
            samplerate=args.sr,
            callback=callback,
        ):
            if args.duration:
                time.sleep(args.duration)
            else:
                while True:
                    time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        if recorded:
            audio = np.concatenate(recorded, axis=0)
            sf.write(args.output, audio, args.sr)
            duration = len(audio) / args.sr
            print(f"\nSaved {len(audio)} samples ({duration:.1f}s) to {args.output}")
        else:
            print("No audio captured.")


if __name__ == "__main__":
    main()
