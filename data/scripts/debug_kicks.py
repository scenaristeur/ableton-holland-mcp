"""Debug: read clip 0 and print kick velocities."""

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


resp = send_command("get_arrangement_clip_notes", {"track_index": 4, "clip_index": 0})
print(f"Response keys: {list(resp.keys())}")
notes = resp.get("notes", [])
print(f"Note count: {len(notes)}")
for n in notes[:5]:
    print(f"  pitch={n['pitch']} vel={n['velocity']} type={type(n['velocity'])}")

kicks = [n for n in notes if n["pitch"] == 36]
print(f"Kick count: {len(kicks)}")
high_kicks = [n for n in kicks if n["velocity"] > 110]
print(f"Kicks > 110: {len(high_kicks)}")
for k in high_kicks:
    print(f"  vel={k['velocity']} at t={k['start_time']}")
