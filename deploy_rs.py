#!/usr/bin/env python
"""Deploy RS + reload in one command."""

import socket, json, shutil, os

SRC = r"C:\Users\admin\dev\ableton-holland-mcp\AbletonMCP_Remote_Script.py"
DSTS = [
    r"C:\ProgramData\Ableton\Live 12 Lite\Resources\MIDI Remote Scripts\AbletonMCP\__init__.py",
    r"C:\ProgramData\Ableton\Live 12 Lite\Resources\MIDI Remote Scripts\AbletonMCPExtended\__init__.py",
]

for dst in DSTS:
    if not os.path.exists(os.path.dirname(dst)):
        print(f"Skipped (not found): {dst}")
        continue
    shutil.copy2(SRC, dst)
    print(f"Copied -> {dst}")
    pycache = os.path.join(os.path.dirname(dst), "__pycache__")
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
