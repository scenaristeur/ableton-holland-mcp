# SPECS — Futures évolutions

## Sample Clip Parameters (Audio Arrangement Clips)

Ajouter l'accès aux paramètres du Sample dans la Clip View : pitch, warp, start/end.

### Remote Script — `_get_arrangement_clips` extend
Ajouter au dict clip :
```python
"pitch_coarse": clip.pitch_coarse,       # -48 to 48 semitones
"pitch_fine": clip.pitch_fine,           # -50 to 50 cents
"warp_on": clip.warp_on,                 # bool
"warp_mode": clip.warp_mode,             # enum
"start_marker": clip.start_marker,       # sample start (beats)
"end_marker": clip.end_marker,           # sample end (beats)
"loop_on": clip.looping,                 # bool
"loop_start": clip.loop_start,
"loop_end": clip.loop_end,
```

### Remote Script — Setters à ajouter
- `_set_arrangement_clip_pitch(track_index, clip_index, coarse, fine)`
- `_set_arrangement_clip_warp(track_index, clip_index, warp_on, warp_mode)`
- `_set_arrangement_clip_markers(track_index, clip_index, start_marker, end_marker)`

### MCP Server — Tools à ajouter
```python
set_arrangement_clip_pitch(track_index, clip_index, coarse, fine)
set_arrangement_clip_warp(track_index, clip_index, warp_on, warp_mode)
set_arrangement_clip_markers(track_index, clip_index, start_marker, end_marker)
```

Tests : capturer un clip isolé (solo) avant/après modification pour vérifier l'impact sur RMS/centroid.
