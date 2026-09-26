"""Test the new set_automation_lanes TCP command (multi-lane per clip)."""

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


print("arr clips T6:", send_command("get_arrangement_clips", {"track_index": 6}))

lanes = [
    {"target": "volume", "points": [{"time": 0, "value": 0.62}, {"time": 120, "value": 0.85}]},
    {"target": "send_1", "points": [{"time": 0, "value": 10}, {"time": 120, "value": 40}]},
]
resp = send_command(
    "set_automation_lanes",
    {"track_index": 6, "clip_index": 0, "lanes": lanes, "is_arrangement": True},
)
print("set_automation_lanes:", resp)

print("arr clips T6 after:", send_command("get_arrangement_clips", {"track_index": 6}))
print("read back:", send_command("get_clip_envelope", {"track_index": 6, "clip_index": 0, "target": "volume", "is_arrangement": True}))
