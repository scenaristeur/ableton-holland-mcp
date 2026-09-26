"""Lengthen T6 solo notes (legato) to kill the rotary-re-trigger "siren" effect.

Recreates session clip 7 (Solo Original) with extended durations, then
re-duplicates it into the arrangement at beat 72, deleting the old clip.
"""

from __future__ import annotations
import json
import socket

HOST = "127.0.0.1"
PORT = 9877
TIMEOUT = 30.0


def send_command(cmd_type: str, params: dict) -> dict:
    payload = {"type": cmd_type, "params": params}
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)
    try:
        sock.connect((HOST, PORT))
        sock.sendall(json.dumps(payload).encode("utf-8"))
        chunks = []
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                break
            chunks.append(chunk)
            try:
                return json.loads(b"".join(chunks))
            except json.JSONDecodeError:
                continue
        return json.loads(b"".join(chunks))
    except Exception as e:
        return {"error": str(e)}
    finally:
        sock.close()


def lengthen(notes: list[dict]) -> list[dict]:
    starts = sorted({n["start_time"] for n in notes})
    for n in notes:
        later = [s for s in starts if s > n["start_time"]]
        gap = (min(later) - n["start_time"]) if later else 16.0
        if gap < 0.1:
            continue
        target = max(n["duration"] * 3.0, 0.6)
        new_dur = min(target, gap * 0.9, 3.0)
        n["duration"] = round(max(new_dur, n["duration"]), 3)
    return notes


resp = send_command("get_clip_notes", {"track_index": 6, "clip_index": 7})
notes = resp.get("result", {}).get("notes")
if not notes:
    print("ERROR: no notes:", resp)
    raise SystemExit(1)
print(f"Read {len(notes)} notes")

out = lengthen(notes)
durs = [round(n["duration"], 2) for n in out]

resp = send_command("delete_session_clip", {"track_index": 6, "clip_index": 7})
print("Deleted session clip:", resp.get("status"))

resp = send_command("create_clip", {"track_index": 6, "clip_index": 7, "length": 120.0})
print("Created clip:", resp.get("status"))

resp = send_command(
    "add_notes_to_clip", {"track_index": 6, "clip_index": 7, "notes": out}
)
print("Added notes:", resp.get("status"), f"({len(out)} notes)")

resp = send_command(
    "set_clip_name", {"track_index": 6, "clip_index": 7, "name": "Solo Original"}
)
print("Named clip:", resp.get("status"))

resp = send_command("delete_arrangement_clip", {"track_index": 6, "clip_index": 0})
print("Deleted old arrangement clip:", resp.get("status"))

resp = send_command(
    "duplicate_to_arrangement",
    {"track_index": 6, "clip_index": 7, "destination_time": 72.0},
)
print("Duplicated to arrangement @72:", resp.get("status"))

print("New durations sample:", durs[:20])