"""Quick TCP test script — connects directly to Ableton Remote Script on port 9877."""

import socket
import json
import sys
import traceback


HOST = "127.0.0.1"
PORT = 9877


def send(cmd_type: str, **params) -> dict:
    """Send a command to the Remote Script and return the parsed response."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    try:
        sock.connect((HOST, PORT))
        payload = json.dumps({"type": cmd_type, "params": params})
        sock.sendall(payload.encode("utf-8"))
        raw = sock.recv(65535).decode("utf-8")
        return json.loads(raw)
    finally:
        sock.close()


def show_events(data: dict):
    """Pretty-print envelope events."""
    result = data.get("result", data)
    events = result.get("target_envelope_events", [])
    print(f"Events: {len(events)}")
    for e in events:
        parts = [f"  t={e.get('time', '?'):7.4f}", f"v={e.get('value', '?'):>8}"]

        # duration debug fields
        for k in ("has_duration", "duration_val", "_all_attrs", "duration_getattr"):
            if k in e:
                parts.append(f"{k}={e[k]}")
        d = e.get("display", "")
        if d:
            parts.append(f"({d})")
        print("  ".join(parts))

    # value_at_time
    for k in ("value_at_start", "value_at_mid", "value_at_end"):
        if k in result:
            print(f"  {k}={result[k]}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: test_tcp.py <command> [key=val ...]")
        print("Examples:")
        print(
            "  test_tcp.py get_arrangement_clip_envelope track_index=0 clip_index=0 target=device_1_Volume is_arrangement=False"
        )
        print(
            "  test_tcp.py add_clip_envelope_point track_index=0 clip_index=0 target=device_1_Volume time=1.2 value=46 duration=0.0 is_arrangement=False"
        )
        print(
            "  test_tcp.py clear_clip_envelope track_index=0 clip_index=0 target=device_1_Volume is_arrangement=False"
        )
        sys.exit(1)

    cmd_type = sys.argv[1]
    params = {}
    for arg in sys.argv[2:]:
        if "=" in arg:
            k, v = arg.split("=", 1)
            # auto-convert types
            if v.lower() in ("true", "false"):
                v = v.lower() == "true"
            elif v.lower() == "none":
                v = None
            else:
                try:
                    if "." in v:
                        v = float(v)
                    else:
                        v = int(v)
                except ValueError:
                    pass
            params[k] = v

    try:
        resp = send(cmd_type, **params)
        if cmd_type in (
            "get_arrangement_clip_envelope",
            "get_clip_envelope",
            "envelope_dump",
            "debug_clip_envelopes",
            "experiment_envelope",
        ):
            show_events(resp)
        else:
            print(json.dumps(resp, indent=2))
    except Exception:
        traceback.print_exc()
