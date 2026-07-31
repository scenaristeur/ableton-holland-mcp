---
name: ableton-mcp
description: Contrôle d'Ableton Live via MCP — déploiement du Remote Script, outils session/arrangement/pistes/clips/instruments, automation, capture audio, troubleshooting.
---

# Ableton Live MCP

## Architecture

Serveur MCP Python (`ableton_full_mcp_server.py`) communique avec Ableton via TCP à `AbletonMCP_Remote_Script.py` sur le port **9877**. Le Remote Script (`AbletonMCP_Remote_Script.py`) est la source de vérité unique, déployé vers `AbletonMCP/__init__.py` et `AbletonMCPExtended/__init__.py`.

## Lancement & Déploiement

```bash
.venv/Scripts/python ableton_full_mcp_server.py   # Serveur
python deploy_rs.py                                # Copie RS + hot-reload (sans restart)
```

Si seuls les wrappers MCP sont modifiés : Ctrl+C → relancer le serveur. Si le RS est modifié : `python deploy_rs.py` d'abord, puis restart serveur.

## Conventions d'indexation (CRITICAL)

**Tous les indices sont 0-based** — matching `song.tracks[0]` (première piste après Master).

```
track_index 0 → song.tracks[0], clip_index 0 → clip_slots[0]
device_index 0 → devices[0], scene_index 0 → scenes[0], send_index 0 → return_tracks[0]
```

## Communication

`_send_command(cmd_type, params, timeout)` envoie `{"type": "...", "params": {...}}` via TCP socket. Timeouts : `TIMEOUT=30s`, `TIMEOUT_LONG=120s`. Premier appel après démarrage peut timeout (~60s).

## Outils principaux

| Catégorie | Outils |
|---|---|
| **Session** | `get_session_info`, `set_tempo(bpm)`, `start_playback`, `stop_playback`, `start_playback_at(time)`, `set_metronome`, `set_signature` |
| **Pistes** | `create_midi_track`, `delete_track`, `duplicate_track`, `set_track_name/volume/panning/solo/mute`, `get_track_info`, `freeze_track`, `flatten_track` |
| **Clips session** | `create_clip(track, clip, length)` — **length en beats** (1 bar 4/4 = 4 beats). `add_notes_to_clip` (inclure `velocity`), `get_clip_notes`, `fire/stop/delete/duplicate`, `set_clip_name`, `quantize_clip` |
| **Clips arrangement** | `get_arrangement_clips`, `duplicate_to_arrangement`, `delete_arrangement_clip`, `create_arrangement_midi/audio_clip`, `set_arrangement_clip_gain/pitch/warp/name` |
| **Scènes** | `create_scene(index=-1)`, `fire_scene(index)` |
| **Instrus** | `load_instrument_or_effect(track, uri)`, `load_external_plugin(track, name)`, `load_drum_kit(track)`, `get/set_device_parameter`, `delete_device` |
| **Automation** | `set_automation_curve(track, clip, target, points, is_arrangement)` — step automation via `insert_step()`. **Ne pas utiliser** `create_event()` (C++ struct inaccessible). `control_coefficients` est read-only. |
| **Capture** | `capture_and_analyze(position_beats, duration_sec)` — capture VB-Cable + analyse librosa (tempo, key, centroid, rolloff, RMS). |
| **Browser** | `get_browser_tree/categories/items`, `get_browser_item`, `list_external_plugins` |
| **Master** | `get_master_track`, `set_master_volume/panning`, `load_instrument_or_effect_on_master` |

## Workflow scène par scène (CONSTRAINT)

1. Découper le morceau en sections (Intro, Couplet, Refrain, Pont...). Une section = une scène.
2. Pour chaque scène, dans l'ordre :
   - Créer le clip de chaque piste (`create_clip`, longueur = nb barres × 4)
   - Remplir les notes (`add_notes_to_clip`), **toujours avec `velocity`** (0-127)
   - Nommer les clips (`set_clip_name`)
3. Présenter la scène à l'utilisateur et attendre validation AVANT la scène suivante.
4. Passer à l'arrangement seulement quand toutes les scènes sont validées.

Vélocités recommandées : Kick 110-127, Snare 95-120, HH 60-90, Basse 85-100, Piano (nappes) 65-80, Guitare arpèges 75-95, Mélodie 80-110. **Toujours varier** les vélocités entre répétitions.

## Limitations connues
- Ne pas lancer plusieurs `capture_and_analyze` ou `load_instrument_or_effect` en parallèle
- `save_project()` non disponible — sauvegarder manuellement (Ctrl+S)
- Automation arrangement = **write-once** (session→duplicate fonctionne, lecture/modification API impossible)
- `set_arrangement_time` imprécis — utiliser `start_playback_at(time)`

## Audio capture silencieuse

Symptôme : rms ≈ 0, valeurs {−1, 0, +1}. Cause : `CABLE_DEVICE_ID` figé au démarrage. Solution : redémarrer le serveur MCP.
