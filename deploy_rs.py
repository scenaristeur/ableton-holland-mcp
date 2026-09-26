#!/usr/bin/env python
"""Deploy RS + reload in one command."""

import socket, json, shutil, os

SRC = r"C:\Users\admin\dev\ableton-holland-mcp\AbletonMCP_Remote_Script.py"
MOD = r"C:\Users\admin\dev\ableton-holland-mcp\midi_mappings.py"
CFG = r"C:\Users\admin\dev\ableton-holland-mcp\midi_mappings_config.json"
DSTS = [
    r"C:\ProgramData\Ableton\Live 12 Lite\Resources\MIDI Remote Scripts\AbletonMCP",
    r"C:\Users\admin\AppData\Roaming\Ableton\Live 12.4.6\Preferences\User Remote Scripts\AbletonMCP",
    r"C:\Users\admin\AppData\Roaming\Ableton\Live 12.4.5\Preferences\User Remote Scripts\AbletonMCP",
    r"C:\Users\admin\AppData\Roaming\Ableton\Live 12.4.3\Preferences\User Remote Scripts\AbletonMCP",
    r"C:\Users\admin\Documents\Ableton\User Library\Remote Scripts\AbletonMCP",
    # NOTE: AbletonMCPExtended is an OLD Remote Script, ne PAS deployer.
]

for dst_dir in DSTS:
    if not os.path.exists(dst_dir):
        print(f"Skipped (not found): {dst_dir}")
        continue
    # __init__.py = the RS (entry point)
    init = os.path.join(dst_dir, "__init__.py")
    shutil.copy2(SRC, init)
    print(f"Copied -> {init}")
    # midi_mappings.py local module (imported by the RS)
    mod_dst = os.path.join(dst_dir, "midi_mappings.py")
    shutil.copy2(MOD, mod_dst)
    print(f"Copied -> {mod_dst}")
    # midi_mappings_config.json persistent mapping config (loaded at startup)
    cfg_dst = os.path.join(dst_dir, "midi_mappings_config.json")
    shutil.copy2(CFG, cfg_dst)
    print(f"Copied -> {cfg_dst}")
    pycache = os.path.join(dst_dir, "__pycache__")
    if os.path.isdir(pycache):
        shutil.rmtree(pycache)
        print(f"Cleared cache {pycache}")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)
try:
    sock.connect(("127.0.0.1", 9877))
    sock.sendall(json.dumps({"type": "reload", "params": {}}).encode("utf-8"))
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
    resp = json.loads(b"".join(chunks).decode("utf-8"))
    if resp.get("status") == "success":
        print("Reload: OK")
    else:
        print("Reload error:", resp.get("message"))
except Exception as e:
    print("Reload failed:", e)
finally:
    sock.close()
