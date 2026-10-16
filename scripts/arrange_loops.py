"""Assemble factored drum loops + fills into the arrangement for scenes 5-8.

Each factored scene has: a groove clip (looped N times) + optional fill clips.
We duplicate the session groove clip at each beat position across its section.

Scene layout (bar ranges read from _scenes_notes.json).
"""

from __future__ import annotations

import json
import socket
import sys

HOST = "127.0.0.1"
PORT = 9877


def send(cmd_type: str, params: dict) -> dict:
    payload = json.dumps({"type": cmd_type, "params": params})
    with socket.create_connection((HOST, PORT), timeout=60) as sock:
        sock.settimeout(60)
        sock.sendall(payload.encode("utf-8"))
        buf = b""
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                break
            buf += chunk
            try:
                return json.loads(buf.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
    raise RuntimeError("connection closed")


def arrange_loop(track, slot, start_beat, n_loops, loop_beats=4, step=0.05):
    """Duplicate the session groove clip at start_beat + k*loop_beats, n_loops times."""
    for k in range(n_loops):
        t = start_beat + k * loop_beats
        resp = send(
            "duplicate_session_clip_to_arrangement",
            {"track_index": track, "clip_index": slot, "destination_time": t},
        )
        ok = resp.get("status") == "success"
        if not ok:
            print(f"  err at {t}: {resp}")
            return
        yield t


def main() -> None:
    notes = json.load(
        open("sources/Reprises/Keep Talking/_scenes_notes.json", encoding="utf-8")
    )
    # Scene -> (section_start_beat_in_arrangement, config)
    scenes = {"5": 336.0, "6": 416.0, "7": 432.0, "8": 528.0}
    # Given by user arg: grooves to assemble as "scene:slot:loop_beats"
    for spec in sys.argv[1:]:
        parts = spec.split(":")
        scene = parts[0]
        slot = int(parts[1])
        loop_beats = int(parts[2]) if len(parts) > 2 else 4
        n_bars = 0
        arr_start = scenes[scene]
        length = notes[scene]["length"]
        n_loops = int(length // loop_beats)
        print(
            f"scene {scene}: groove slot {slot} {loop_beats}b x{n_loops} @ {arr_start}"
        )
        gen = arrange_loop(0, slot, arr_start, n_loops, loop_beats)
        count = sum(1 for _ in gen)
        print(f"  done {count}")


if __name__ == "__main__":
    main()
