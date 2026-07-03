"""Test connected steps: can insert_step create proper automation curves?"""

import socket, json

HOST, PORT = "127.0.0.1", 9877


def send(cmd_type, **params):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    try:
        sock.connect((HOST, PORT))
        sock.sendall(json.dumps({"type": cmd_type, "params": params}).encode("utf-8"))
        raw = b""
        while True:
            chunk = sock.recv(65535)
            if not chunk:
                break
            raw += chunk
            try:
                json.loads(raw.decode("utf-8"))
                break
            except:
                continue
        return json.loads(raw.decode("utf-8"))
    finally:
        sock.close()


def dump_events(label, resp):
    result = resp.get("result", resp)
    events = result.get("target_envelope_events", []) or result.get("events", [])
    print(f"\n  {label} ({len(events)} events):")
    for e in events:
        d = e.get("display", "")
        dur = e.get("duration", "")
        dur_str = f"  dur={dur}" if dur != "" else ""
        print(f"    t={e['time']:7.4f}  v={e.get('value', 0):>8.4f}  {d}{dur_str}")
    for k in ("value_at_start", "value_at_mid", "value_at_end"):
        if k in result:
            print(f"    {k}={result[k]}")


TI, CI = 0, 0  # 0-based: track 0, clip slot 0
TARGET = "device_1_Volume"
IS_ARR = False

# Clean start: clear volume envelope
print("=== Clear envelope ===")
resp = send(
    "clear_clip_envelope",
    track_index=TI,
    clip_index=CI,
    target=TARGET,
    is_arrangement=IS_ARR,
)
print("clear:", resp.get("status"))

# First set param to a known base value (0.0 = silence)
print("\n=== Set param to 0 ===")
resp = send("set_device_parameter", track_index=TI, device_index=1, value=0.0)
print("set:", json.dumps(resp.get("result", {}), indent=2)[:200])

# Test 1: Two connected steps with duration=2.0 each
# Point at t=0, v=0 (original, already there)
# Point at t=2, v=64  → insert_step(0, 2, 0) to hold silence for 2 beats
# Then insert_step(2, 2, 64) to set volume at beat 2
print("\n=== Test 1: Two connected steps (dur=2 each) ===")
resp = send(
    "add_clip_envelope_point",
    track_index=TI,
    clip_index=CI,
    target=TARGET,
    time=0.0,
    value=0.0,
    duration=2.0,
    is_arrangement=IS_ARR,
)
print("step 1:", json.dumps(resp.get("result", {}), indent=2)[:200])
resp = send(
    "add_clip_envelope_point",
    track_index=TI,
    clip_index=CI,
    target=TARGET,
    time=2.0,
    value=64.0,
    duration=2.0,
    is_arrangement=IS_ARR,
)
print("step 2:", json.dumps(resp.get("result", {}), indent=2)[:200])
resp = send(
    "get_clip_envelope",
    track_index=TI,
    clip_index=CI,
    target=TARGET,
    is_arrangement=IS_ARR,
)
dump_events("After 2 connected steps", resp)

# Test 2: Three connected points with ramp
print("\n=== Test 2: 3-point ramp (dur=1 each) ===")
resp = send(
    "clear_clip_envelope",
    track_index=TI,
    clip_index=CI,
    target=TARGET,
    is_arrangement=IS_ARR,
)
resp = send(
    "add_clip_envelope_point",
    track_index=TI,
    clip_index=CI,
    target=TARGET,
    time=0.0,
    value=20.0,
    duration=1.0,
    is_arrangement=IS_ARR,
)
resp = send(
    "add_clip_envelope_point",
    track_index=TI,
    clip_index=CI,
    target=TARGET,
    time=1.0,
    value=60.0,
    duration=1.0,
    is_arrangement=IS_ARR,
)
resp = send(
    "add_clip_envelope_point",
    track_index=TI,
    clip_index=CI,
    target=TARGET,
    time=2.0,
    value=100.0,
    duration=1.0,
    is_arrangement=IS_ARR,
)
resp = send(
    "get_clip_envelope",
    track_index=TI,
    clip_index=CI,
    target=TARGET,
    is_arrangement=IS_ARR,
)
dump_events("3-point ramp", resp)

# Check interpolation
resp = send(
    "get_clip_envelope",
    track_index=TI,
    clip_index=CI,
    target=TARGET,
    is_arrangement=IS_ARR,
)
r = resp.get("result", {})
print(f"\n  Interpolation check:")
for bt in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
    val = r.get(
        f"value_at_{'start' if bt == 0.0 else 'mid' if bt == 2.0 else 'end'}", None
    )
    if val is not None:
        print(f"    t={bt}: {val}")
    else:
        # Read value_at_time via experiment
        pass

# Test 3: Verify with the envelope_dump for full diagnostic
print("\n=== Test 3: Envelope dump ===")
resp = send("envelope_dump", track_index=TI, clip_index=CI, is_arrangement=IS_ARR)
result = resp.get("result", {})
for pe in result.get("param_envelope_check", []):
    if pe.get("param_name") == "Volume" and pe.get("has_automation_envelope"):
        print(f"  Device={pe.get('device')} Param={pe.get('param_name')}")
        print(f"  Events: {pe.get('event_count', 0)}")
        for e in (pe.get("events") or [])[:12]:
            d = e.get("display", "")
            print(f"    t={e['time']:7.4f}  v={e['value']:>8.4f}  {d}")
        break

# Clean up: restore original
print("\n=== Clean up ===")
resp = send(
    "clear_clip_envelope",
    track_index=TI,
    clip_index=CI,
    target=TARGET,
    is_arrangement=IS_ARR,
)
print("cleared")
