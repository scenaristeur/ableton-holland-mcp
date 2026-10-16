"""Comprehensive envelope experiments --- connects directly to Ableton RS on port 9877."""

import socket
import json
import sys
import time
import traceback

HOST = "127.0.0.1"
PORT = 9877


def send(cmd_type: str, **params) -> dict:
    """Send a command to the Remote Script and return the parsed response."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    try:
        sock.connect((HOST, PORT))
        payload = json.dumps({"type": cmd_type, "params": params})
        sock.sendall(payload.encode("utf-8"))
        raw = b""
        while True:
            try:
                chunk = sock.recv(65535)
                if not chunk:
                    break
                raw += chunk
                try:
                    json.loads(raw.decode("utf-8"))
                    break
                except json.JSONDecodeError:
                    continue
            except socket.timeout:
                break
        return json.loads(raw.decode("utf-8"))
    finally:
        sock.close()


# -- Track/clip config ---------------------------------------------
# NOTE: Sending directly to RS -> use 0-based indices
TRACK = 0  # 0-based (first track = 1-Grand Piano)
CLIP = 0  # 0-based (first clip slot, has clip)
TARGET = "device_1_Volume"  # Grand Piano Volume (device index 1 = 0-based)
IS_ARR = False  # session clip


def section(title: str):
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}")


def sub(title: str):
    print(f"\n  --- {title} ---")


# -- Step 1: Initial state -----------------------------------------
section("1. INITIAL STATE --- read envelope before any changes")

resp = send(
    "get_clip_envelope",
    track_index=TRACK,
    clip_index=CLIP,
    target=TARGET,
    is_arrangement=IS_ARR,
)
print("has_envelopes:", resp.get("result", resp).get("has_envelopes"))
print("automation_envelopes:", resp.get("result", resp).get("automation_envelopes"))
print("target_envelope_exists:", resp.get("result", resp).get("target_envelope_exists"))
events = resp.get("result", resp).get("target_envelope_events", [])
print(f"Event count: {len(events)}")
for e in events[:15]:
    disp = e.get("display", "")
    print(f"  t={e['time']:7.4f}  v={e['value']:>8}  {disp}")


# -- Step 2: Run the experiment ------------------------------------
section("2. RUNNING COMPREHENSIVE EXPERIMENT")

print("This will take ~10-20 seconds...")
resp = send(
    "experiment_envelope",
    track_index=TRACK,
    clip_index=CLIP,
    target=TARGET,
    is_arrangement=IS_ARR,
)

result = resp.get("result", resp)
exp = result.get("experiment", result)

if "error" in result:
    print(f"EXPERIMENT FAILED: {result['error']}")
    print(json.dumps(result, indent=2))
    sys.exit(1)

if "error" in exp:
    print(f"EXPERIMENT FAILED: {exp['error']}")
    sys.exit(1)

# -- Results analysis ----------------------------------------------
section("3. PARAMETER INFO")
print(json.dumps(exp.get("param", {}), indent=2))

section("4. ENVELOPE ATTRIBUTES")
attrs = exp.get("envelope_attributes", {})
for k, v in attrs.items():
    print(f"  {k}: {v}")

section("5. START STATE")
print(f"Start events: {exp.get('start_event_count')}")
print(f"Value at clip start: {exp.get('value_at_clip_start')}")

section("6. INSERT_STEP DURATION TESTS")
for t in exp.get("insert_step_duration_tests", []):
    dur = t["duration"]
    ok = t.get("ok", False)
    if ok:
        cnt = t.get("event_count", 0)
        print(f"\n  duration={dur:>6}  ->  {cnt} events")
        for e in t.get("events", []):
            dur_str = f"  dur={e.get('duration', '?')}" if "duration" in e else ""
            print(f"      t={e['time']:7.4f}  v={e['value']:>8}{dur_str}")
    else:
        print(f"\n  duration={dur:>6}  ->  ERROR: {t.get('error', '?')}")

section("7. TWO-STEP APPROACH (pre-step + step)")
ts = exp.get("two_step_test", {})
if ts.get("ok"):
    print(f"  {ts['event_count']} events:")
    for e in ts.get("events", []):
        dur_str = f"  dur={e.get('duration', '?')}" if "duration" in e else ""
        print(f"    t={e['time']:7.4f}  v={e['value']:>8}{dur_str}")

section("8. RAMP TEST (8 steps)")
rt = exp.get("ramp_test", {})
if rt.get("ok"):
    print(f"  {rt['step_count']} steps, {rt['event_count']} total events")
    for e in rt.get("events", []):
        dur_str = f"  dur={e.get('duration', '?')}" if "duration" in e else ""
        print(f"    t={e['time']:7.4f}  v={e['value']:>8}{dur_str}")

section("9. SEQUENTIAL INSERT (same time, different values)")
si = exp.get("sequential_insert_test", {})
if si.get("ok"):
    for label in ["after_first", "after_second", "after_third"]:
        phase = si.get(label, {})
        print(f"\n  {label}: {phase.get('event_count', 0)} events")
        for e in phase.get("events", []):
            dur_str = f"  dur={e.get('duration', '?')}" if "duration" in e else ""
            print(f"      t={e['time']:7.4f}  v={e['value']:>8}{dur_str}")

section("10. THREE POINTS TEST (like UI automation)")
tp = exp.get("three_points_test", {})
if tp.get("ok"):
    print(f"  {tp['event_count']} events:")
    for e in tp.get("events", []):
        dur_str = f"  dur={e.get('duration', '?')}" if "duration" in e else ""
        print(f"    t={e['time']:7.4f}  v={e['value']:>8}{dur_str}")
    print(f"\n  Interpolation:")
    for k, v in exp.get("three_points_interp", {}).items():
        print(f"    {k}: {v}")

section("11. DELETE ANCHORS APPROACH")
da = exp.get("delete_anchors_test", {})
if da.get("ok"):
    print("\n  Before delete:")
    for e in da.get("events_before", []):
        dur_str = f"  dur={e.get('duration', '?')}" if "duration" in e else ""
        print(f"    t={e['time']:7.4f}  v={e['value']:>8}{dur_str}")
    print("\n  After delete:")
    for e in da.get("events_after", []):
        dur_str = f"  dur={e.get('duration', '?')}" if "duration" in e else ""
        print(f"    t={e['time']:7.4f}  v={e['value']:>8}{dur_str}")
    print(f"\n  Values at time:")
    for k, v in da.get("values_at_time", {}).items():
        print(f"    {k}: {v}")

section("12. EVENT DEEP INSPECTION")
ed = exp.get("event_deep_inspect", {})
if "error" not in ed:
    print(f"  {ed.get('count', 0)} events")
    for ev_info in ed.get("events", []):
        print(f"\n  Event {ev_info['index']}:")
        print(f"    time  = {ev_info['time']}")
        print(f"    value = {ev_info['value']}")
        for attr_name, attr_val in ev_info.get("attrs", {}).items():
            print(f"    .{attr_name} = {attr_val}"[:120])

section("13. CONTROL COEFFICIENTS")
cc = exp.get("control_coefficients_test", [])
if cc:
    for c in cc:
        print(f"\n  Event {c.get('index')}:")
        print(f"    has_control_coefficients: {c.get('has_control_coefficients', '?')}")
        print(f"    value: {c.get('value', '?')}")
        print(f"    set_ok: {c.get('set_ok', '?')}")
        print(f"    new_value: {c.get('new_value', '?')}")

section("14. CLIP ENVELOPE PROPERTIES")
for k, v in exp.get("clip_envelope_properties", {}).items():
    print(f"  {k}: {v}")

section("15. ALL PARAM ENVELOPES")
for pe in exp.get("all_param_envelopes", []):
    print(
        f"  device={pe['device']}  param={pe['param']}  has_env={pe['has_envelope']}  has_events={pe.get('has_events')}"
    )

section("16. SUMMARY")
insert_tests = exp.get("insert_step_duration_tests", [])
for t in insert_tests:
    dur = t["duration"]
    ok = t.get("ok", False)
    if ok:
        cnt = t.get("event_count", 0)
        events_at = [(e["time"], e["value"]) for e in t.get("events", [])]
        print(f"  insert_step(t, {dur:>6}, v)  ->  {cnt} events  {events_at}")
    else:
        print(f"  insert_step(t, {dur:>6}, v)  ->  FAILED: {t.get('error', '?')}")

print(f"\n  Two-step OK:     {ts.get('ok', False)}")
print(f"  Ramp OK:         {rt.get('ok', False)}")
print(f"  Three-point OK:  {tp.get('ok', False)}")
print(f"  Delete anchors:  {da.get('ok', False)}")

print(f"\n{'=' * 80}")
print("  EXPERIMENT COMPLETE")
print(f"{'=' * 80}")
