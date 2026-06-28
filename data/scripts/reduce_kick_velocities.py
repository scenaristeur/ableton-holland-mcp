"""Reduce kick (pitch=36) velocities above 110 to 110 across all 8 drum clips."""

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


MAX = 110

for clip_idx in range(8):
    resp = send_command(
        "get_arrangement_clip_notes", {"track_index": 4, "clip_index": clip_idx}
    )
    result = resp.get("result", {})
    notes = result.get("notes", [])
    modified = 0
    for note in notes:
        if note["pitch"] == 36 and note["velocity"] > MAX:
            note["velocity"] = MAX
            modified += 1
    if modified > 0:
        resp2 = send_command(
            "set_arrangement_clip_notes",
            {"track_index": 4, "clip_index": clip_idx, "notes": notes},
        )
        r2 = resp2.get("result", {})
        print(f"Clip {clip_idx}: {modified} kicks reduced OK")
    else:
        print(f"Clip {clip_idx}: no kicks above {MAX}")
