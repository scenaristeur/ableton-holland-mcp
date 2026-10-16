# SPECS — Futures évolutions

## ✅ Réalisées

- `_get_arrangement_clips` étendu avec pitch_coarse, pitch_fine, warp_on, warp_mode, start_marker, end_marker, loop_on, loop_start, loop_end
- `set_arrangement_clip_pitch(track, clip, coarse, fine)` — transposition
- `set_arrangement_clip_warp(track, clip, warp_on, warp_mode)` — warp
- `set_arrangement_clip_markers(track, clip, start_marker, end_marker)` — markers
- `create_audio_clip(track, slot, path)` — import audio WAV
- `set_track_solo(index, solo)` / `set_track_mute(index, mute)` — solo/mute
- `set_arrangement_clip_envelope` fixé pour clips audio (bypass session clip workaround)

## Idées futures

### Automation clip audio
- Lire/écrire les courbes d'automation sur les clips audio via l'API (actuellement limité)

### Paramètres sample (warp markers)
- Ajouter/modifier les warp markers individuels (pas juste start/end)
- Stretch mode par défaut

### Export
- Tool `export_audio()` pour lancer l'export d'Ableton (si l'API le permet)

### Script test plugins
- Créer un script `test_plugins.py` qui pour chaque plugin externe :
  1. Le charge sur une piste
  2. Appelle `get_device_parameters()` et enregistre le nombre + noms des paramètres
  3. Mesure la charge CPU avant/après activation
  4. Supprime la piste
  5. Génère un rapport dans `.opencode/skills/exposition-plugins/` (skill projet)
  6. Compare avec la palette réelle du projet, dans `.opencode/skills/palette-live-lite/`
- Automatiser le déploiement des résultats dans ce skill
