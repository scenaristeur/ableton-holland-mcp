from __future__ import annotations

import json
import socket
import time

HOST = "127.0.0.1"
PORT = 9877
TIMEOUT = 120.0


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

slots = sorted(plan.keys(), key=lambda x: int(x))

# ── Pass 1: clear any existing arrangement clips ────────────────────────────
print("Clearing arrangement...")
for trk in range(8):
    try:
        existing = send("get_arrangement_clips", {"track_index": trk}) or []
        clips = (
            existing.get("clips", existing) if isinstance(existing, dict) else existing
        )
        n = len(clips)
        for i in range(n - 1, -1, -1):
            try:
                send("delete_arrangement_clip", {"track_index": trk, "clip_index": i})
            except Exception:
                pass
    except Exception:
        pass
print("Clear done.\n")

# ── Compute cumulative start time (beats) per slot ──────────────────────────
start = {}
cursor = 0.0
for slot in slots:
    start[slot] = cursor
    # length is shared across tracks in a slot; grab from first trk
    first_trk = sorted(plan[slot].keys(), key=lambda x: int(x))[0]
    cursor += float(plan[slot][first_trk]["length"])

print("Slot start times (beats):")
for slot in slots:
    print(f"  slot {slot}: start={start[slot]:.0f}")

# ── Pass 2: duplicate each session clip to the arrangement ─────────────────
ok = 0
fail = 0
for slot in slots:
    for trk in sorted(plan[slot].keys(), key=lambda x: int(x)):
        try:
            send(
                "duplicate_session_clip_to_arrangement",
                {
                    "track_index": int(trk),
                    "clip_index": int(slot),
                    "destination_time": start[slot],
                },
            )
            ok += 1
        except Exception as e:
            fail += 1
            print(f"FAIL trk {trk} slot {slot}: {e}")
        time.sleep(0.04)

print(
    f"\nDONE. ok={ok} fail={fail}  total_beats={cursor:.0f}  (~{cursor / 4:.0f} bars)"
)
