#!/usr/bin/env python3
"""
Capture audio from Ableton at a specific arrangement position.
Orchestrates: start_playback_at (ableton-holland-mcp) + capture_ableton (music-analysis)
"""

import sys
import time
import subprocess
import json


def run_mcp_tool(server_script, tool_name, **params):
    """Call an MCP tool via the server script."""
    cmd = [
        sys.executable,
        server_script,
        "--tool",
        tool_name,
        "--params",
        json.dumps(params),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"MCP tool {tool_name} failed: {result.stderr}")
    return json.loads(result.stdout)


def capture_at_position(
    ableton_server: str,
    analysis_server: str,
    position_beats: float,
    duration_sec: float = 10.0,
    output_name: str = None,
):
    """
    Capture audio at a specific arrangement position.

    Workflow:
    1. stop_playback (ableton)
    2. switch_to_arrangement_view (ableton)
    3. start capture (analysis) - non-blocking
    4. start_playback_at (ableton) - atomic position + play
    5. wait for capture duration
    6. stop_playback (ableton)
    7. get capture result (analysis)
    """
    import threading

    capture_result = {}
    capture_error = {}

    def run_capture():
        try:
            # This blocks for duration_sec
            result = run_mcp_tool(
                analysis_server,
                "capture_ableton",
                duration=duration_sec,
                output_name=output_name,
            )
            capture_result.update(result)
        except Exception as e:
            capture_error.update({"error": str(e)})

    # 1. Stop playback
    print(f"[1/7] Stopping playback...")
    run_mcp_tool(ableton_server, "stop_playback")
    time.sleep(0.3)

    # 2. Switch to arrangement view
    print(f"[2/7] Switching to arrangement view...")
    run_mcp_tool(ableton_server, "switch_to_arrangement_view")
    time.sleep(0.3)

    # 3. Start capture in background (starts recording immediately)
    print(f"[3/7] Starting capture (duration={duration_sec}s)...")
    capture_thread = threading.Thread(target=run_capture)
    capture_thread.start()

    # Small delay to ensure capture is armed before playback starts
    time.sleep(0.2)

    # 4. Start playback at position (atomic)
    print(f"[4/7] Starting playback at {position_beats} beats...")
    result = run_mcp_tool(ableton_server, "start_playback_at", time=position_beats)
    print(f"    Returned (old state): {result}")

    # 5. Wait for capture to complete
    print(f"[5/7] Waiting for capture to complete...")
    capture_thread.join(timeout=duration_sec + 5)

    # 6. Stop playback
    print(f"[6/7] Stopping playback...")
    run_mcp_tool(ableton_server, "stop_playback")
    time.sleep(0.3)

    # 7. Verify capture result
    print(f"[7/7] Capture complete")
    if capture_error:
        raise RuntimeError(f"Capture failed: {capture_error['error']}")

    # Verify position
    info = run_mcp_tool(ableton_server, "get_session_info")
    print(f"    Final position: {info.get('current_song_time')} beats")

    capture_result["capture_position_beats"] = position_beats
    capture_result["capture_duration_sec"] = duration_sec

    return capture_result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Capture Ableton audio at arrangement position"
    )
    parser.add_argument(
        "--ableton-server",
        default="ableton_mcp_server.py",
        help="Path to ableton MCP server",
    )
    parser.add_argument(
        "--analysis-server",
        default="music_analysis_plus.py",
        help="Path to analysis MCP server",
    )
    parser.add_argument(
        "--position", type=float, required=True, help="Position in beats"
    )
    parser.add_argument(
        "--duration", type=float, default=10.0, help="Capture duration in seconds"
    )
    parser.add_argument("--output-name", help="Output file base name")
    args = parser.parse_args()

    result = capture_at_position(
        ableton_server=args.ableton_server,
        analysis_server=args.analysis_server,
        position_beats=args.position,
        duration_sec=args.duration,
        output_name=args.output_name,
    )
    print(json.dumps(result, indent=2))
