#!/usr/bin/env python3
"""
Helper to orchestrate capture_at_position via MCP tools.
Run this LOCALLY (not via MCP) - it uses the opencode tool calling mechanism.
"""
# This is a reference implementation showing the exact sequence.
# You call these tools in order from opencode:

"""
# 1. Stop playback
stop_playback()

# 2. Switch to arrangement view
switch_to_arrangement_view()

# 3. Start capture (async - returns immediately, records for 'duration' seconds)
capture_ableton(duration=10, output_name="my_capture")

# 4. Immediately start playback at position (atomic)
start_playback_at(time=16)

# 5. Wait for capture duration + small buffer
# (capture_ableton blocks for 'duration' seconds, so this is implicit)

# 6. Stop playback
stop_playback()

# 7. Analyze
analyze_full(y_path="...")
"""

# Simpler: just use the manual workflow we tested.
# The key insight: call capture_ableton FIRST, then start_playback_at.
# capture_ableton blocks for 'duration' seconds while recording.
# start_playback_at starts playback immediately.
# When capture_ableton returns, stop_playback().
