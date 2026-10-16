from __future__ import annotations
import json
import socket
import time

HOST = "127.0.0.1"
PORT = 9877
TIMEOUT = 60.0

track_names = {
    0: "Piano",
    1: "Drums",
    2: "Strings",
    3: "Bass",
    4: "Guitar",
    5: "Lead",
    6: "Organ",
    7: "Horns",
}
scene_names = {
    0: "Intro",
    1: "Couplet 1",
    2: "Refrain",
    3: "Pont",
    4: "Refrain Final",
    5: "Outro",
    6: "Couplet 2",
    7: "Build",
    8: "Refrain Reprise",
    9: "Pont 2",
    10: "Bridge",
    11: "Climax",
    12: "Solo",
    13: "Refrain Final 2",
    14: "Outro 2",
    15: "Coda",
}


def send(cmd_type, params, timeout=TIMEOUT):
    payload = {"type": cmd_type, "params": params}
    raw = json.dumps(payload).encode("utf-8")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((HOST, PORT))
        sock.sendall(raw)
        chunks = []
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                break
            chunks.append(chunk)
            try:
                json.loads(b"".join(chunks))
                break
            except json.JSONDecodeError:
                continue
        data = b"".join(chunks)
        resp = json.loads(data.decode("utf-8"))
        if resp.get("status") == "error":
            raise RuntimeError(resp.get("message", "RS error"))
        return resp.get("result", {})
    finally:
        sock.close()


with open("clip_plan.json") as f:
    plan = json.load(f)

# ── Pass 1: delete any existing clips in the 16 slots x 8 tracks grid ───────
print("Deleting existing clips...")
for slot in range(16):
    for trk in range(8):
        try:
            send("delete_session_clip", {"track_index": trk, "clip_index": slot})
        except Exception:
            pass
print("Delete pass done.\n")

ok = 0
fail = 0
for slot in sorted(plan.keys(), key=lambda x: int(x)):
    for trk in sorted(plan[slot].keys(), key=lambda x: int(x)):
        info = plan[slot][trk]
        length = info["length"]
        notes = info["notes"]
        nm = f"{scene_names[int(slot)]}"
        try:
            send(
                "create_clip",
                {"track_index": int(trk), "clip_index": int(slot), "length": length},
            )
            if notes:
                send(
                    "add_notes_to_clip",
                    {"track_index": int(trk), "clip_index": int(slot), "notes": notes},
                    timeout=120.0,
                )
            send(
                "set_clip_name",
                {"track_index": int(trk), "clip_index": int(slot), "name": nm},
            )
            ok += 1
            print(
                f"OK  slot {slot} track {trk} ({track_names[int(trk)]}) len={length} notes={len(notes)}"
            )
        except Exception as e:
            fail += 1
            print(f"FAIL slot {slot} track {trk}: {e}")
        time.sleep(0.05)

print(f"\nDONE. ok={ok} fail={fail}")
