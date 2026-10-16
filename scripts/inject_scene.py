"""Inject session clip notes directly to the Ableton Remote Script over TCP.

Reads _scenes_notes.json and sends add_notes_to_clip commands for a given scene
and Ableton track, using the same JSON protocol as the MCP server (port 9877).

Usage:
    python inject_scene.py SCENE ATrack [--src SRC_MIDI_TRACK]
"""

from __future__ import annotations

import json
import socket
import sys

HOST = "127.0.0.1"
PORT = 9877
TIMEOUT = 30.0


def send(cmd_type: str, params: dict) -> dict:
    """Send one command to the Remote Script and return parsed response."""
    payload = json.dumps({"type": cmd_type, "params": params})
    with socket.create_connection((HOST, PORT), timeout=TIMEOUT) as sock:
        sock.settimeout(TIMEOUT)
        sock.sendall(payload.encode("utf-8"))
        buf = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            buf += chunk
            try:
                return json.loads(buf.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
    raise RuntimeError("connection closed before response")


def main() -> None:
    scene_key = sys.argv[1]
    atrack = int(sys.argv[2])
    notes = json.load(
        open("sources/Reprises/Keep Talking/_scenes_notes.json", encoding="utf-8")
    )
    arr = notes[scene_key][str(atrack)]
    if not arr:
        print(f"scene {scene_key} track {atrack}: 0 notes, rien a faire")
        return
    length = notes[scene_key]["length"]
    # ensure clip exists
    send(
        "create_clip",
        {"track_index": atrack, "clip_index": int(scene_key), "length": length},
    )
    # inject notes in chunks of 200
    for i in range(0, len(arr), 200):
        chunk = arr[i : i + 200]
        resp = send(
            "add_notes_to_clip",
            {"track_index": atrack, "clip_index": int(scene_key), "notes": chunk},
        )
        print(f"chunk {i}-{i + len(chunk)}: {resp}")
    print(
        f"scene {scene_key} track {atrack}: {len(arr)} notes injectees dans clip {scene_key} (len {length})"
    )


if __name__ == "__main__":
    main()
