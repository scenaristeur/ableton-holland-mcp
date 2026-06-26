# SPEC — Ableton Holland MCP v2

## 1. Contexte & Problème

Le MCP actuel permet de contrôler Ableton Live (créer des pistes, des clips, ajouter des notes MIDI, charger des instruments, naviguer dans le navigateur). Cependant, de nombreuses limitations bloquent des workflows essentiels :

| Limitation | Impact |
|---|---|
| Pas de lecture/écriture des paramètres de devices | Impossible de tweaker un cutoff, threshold, decay, etc. via MCP |
| Pas de lecture des notes MIDI existantes | Impossible d'analyser ou modifier un clip existant |
| Pas de suppression de clips | Impossible de remplacer un clip — blocage pour itérer |
| Pas d'accès aux scenes | Workflow Session View limité |
| Pas de sends/returns | Impossible de gérer les effets d'envoi |
| Pas de freeze/flatten | Impossible d'optimiser le projet à distance |
| Pas d'undo/redo | Aucune sécurité pour les opérations destructrices |
| Pas de save | Impossible de sauvegarder après modifications |

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  opencode (client MCP)                                       │
│  │                                                           │
│  ├─ Tool: get_device_parameters(...)                         │
│  ├─ Tool: set_device_parameter(...)                          │
│  ├─ ...                                                      │
└──────────┬──────────────────────────────────────────────────┘
           │ JSON-RPC (stdin/stdout)
┌──────────▼──────────────────────────────────────────────────┐
│  ableton_mcp_server.py    ← NOUVEAU                         │
│  (FastMCP Server Python)                                     │
│                                                              │
│  - Reçoit les appels MCP                                     │
│  - Les traduit en commandes JSON                             │
│  - Envoie/réçoit via socket TCP                              │
└──────────┬──────────────────────────────────────────────────┘
           │ Socket TCP (port 9877)
┌──────────▼──────────────────────────────────────────────────┐
│  AbletonMCP_Remote_Script.py   ← MODIFIÉ                    │
│  (ControlSurface Live API)                                   │
│                                                              │
│  - Reçoit les commandes JSON                                 │
│  - Les exécute via Live API (song, track, clip, device...)   │
│  - Renvoie la réponse JSON                                   │
└─────────────────────────────────────────────────────────────┘
```

### Pourquoi remplacer `uvx ableton-mcp` ?

Le package `uvx ableton-mcp` est un binaire externe non modifiable. En créant notre propre serveur MCP, on contrôle totalement les fonctionnalités, le format des données, et on peut ajouter des outils sans attendre une mise à jour du package officiel.

## 3. Spécification des nouvelles commandes (Remote Script)

### 3.1 Device Parameters

#### `get_device_parameters`
```
Request:  {"type": "get_device_parameters", "params": {"track_index": int, "device_index": int}}
Response: {"status": "success", "result": {"parameters": [
    {"name": str, "value": float, "min": float, "max": float,
     "is_quantized": bool, "value_items": [str] | null}
]}}
```

#### `set_device_parameter`
```
Request:  {"type": "set_device_parameter", "params": {"track_index": int, "device_index": int,
           "parameter_name": str, "value": float}}
Response: {"status": "success", "result": {"name": str, "value": float}}
```

### 3.2 Clip Operations

#### `get_clip_notes`
```
Request:  {"type": "get_clip_notes", "params": {"track_index": int, "clip_index": int}}
Response: {"status": "success", "result": {"notes": [
    {"pitch": int, "start_time": float, "duration": float, "velocity": int, "mute": bool}
]}}
```

#### `delete_session_clip`
```
Request:  {"type": "delete_session_clip", "params": {"track_index": int, "clip_index": int}}
Response: {"status": "success", "result": {"deleted": true}}
```

#### `delete_arrangement_clip`
```
Request:  {"type": "delete_arrangement_clip", "params": {"track_index": int, "clip_index": int}}
Response: {"status": "success", "result": {"deleted": true}}
```

#### `duplicate_session_clip`
```
Request:  {"type": "duplicate_session_clip", "params": {"track_index": int, "clip_index": int, "destination_track": int | null, "destination_slot": int | null}}
Response: {"status": "success", "result": {"new_track": int, "new_slot": int}}
```

### 3.3 Scenes

#### `create_scene`
```
Request:  {"type": "create_scene", "params": {"index": int}}
Response: {"status": "success", "result": {"index": int, "name": str}}
```

#### `fire_scene`
```
Request:  {"type": "fire_scene", "params": {"index": int}}
Response: {"status": "success", "result": {"fired": true}}
```

### 3.4 Sends & Monitoring

#### `get_sends`
```
Request:  {"type": "get_sends", "params": {"track_index": int}}
Response: {"status": "success", "result": {"sends": [{"name": str, "value": float}]}}
```

#### `set_send`
```
Request:  {"type": "set_send", "params": {"track_index": int, "send_index": int, "value": float}}
Response: {"status": "success", "result": {"send_index": int, "value": float}}
```

#### `set_monitoring`
```
Request:  {"type": "set_monitoring", "params": {"track_index": int, "state": int}}
Response: {"status": "success", "result": {"monitoring_state": int}}
```

### 3.5 Project Operations

#### `freeze_track`
```
Request:  {"type": "freeze_track", "params": {"track_index": int}}
Response: {"status": "success", "result": {"frozen": bool}}
```

#### `flatten_track`
```
Request:  {"type": "flatten_track", "params": {"track_index": int}}
Response: {"status": "success", "result": {"flattened": bool}}
```

#### `save_project`
```
Request:  {"type": "save_project"}
Response: {"status": "success", "result": {"saved": true}}
```

#### `undo` / `redo`
```
Request:  {"type": "undo"} | {"type": "redo"}
Response: {"status": "success", "result": {"performed": true}}
```

### 3.6 Lecture des notes MIDI d'un clip arrangement

#### `get_arrangement_clip_notes`
```
Request:  {"type": "get_arrangement_clip_notes", "params": {"track_index": int, "arrangement_clip_index": int}}
Response: {"status": "success", "result": {"notes": [...]}}
```

Note: pour les clips arrangement, on doit d'abord les lister via `get_arrangement_clips`, puis utiliser l'index pour accéder au clip via `track.arrangement_clips[i]`.

### 3.7 Pitch MIDI effect transposition

#### `set_pitch_transposition`
```
Request:  {"type": "set_pitch_transposition", "params": {"track_index": int, "device_index": int, "semitone_offset": int}}
Response: {"status": "success", "result": {"pitch": int}}
```

Spécifique au MidiPitcher — le paramètre "Pitch" (range -24 à +24).

## 4. Plan de développement

### Phase 1 — Remote Script (backend)

1. Ajouter `_get_device_parameters()` et `_set_device_parameter()`
2. Ajouter `_get_clip_notes()`, `_delete_session_clip()`, `_delete_arrangement_clip()`, `_duplicate_session_clip()`
3. Ajouter `_create_scene()`, `_fire_scene()`
4. Ajouter `_get_sends()`, `_set_send()`, `_set_monitoring()`
5. Ajouter `_freeze_track()`, `_flatten_track()`, `_save_project()`, `_undo()`, `_redo()`
6. Ajouter `_get_arrangement_clip_notes()`
7. Enregistrer toutes les nouvelles commandes dans `_process_command()` et `main_thread_task()`

### Phase 2 — MCP Server (bridge)

1. Créer `ableton_mcp_server.py` avec FastMCP
2. Implémenter le client socket qui se connecte au Remote Script
3. Exposer chaque commande comme un outil MCP :
   - `get_device_parameters(track_index, device_index)`
   - `set_device_parameter(track_index, device_index, parameter_name, value)`
   - `get_clip_notes(track_index, clip_index)`
   - `delete_session_clip(track_index, clip_index)`
   - `delete_arrangement_clip(track_index, clip_index)`
   - `create_scene(index)`
   - `fire_scene(index)`
   - `get_sends(track_index)`
   - `set_send(track_index, send_index, value)`
   - `set_monitoring(track_index, state)`
   - `freeze_track(track_index)`
   - `flatten_track(track_index)`
   - `save_project()`
   - `undo()`
   - `redo()`
   - `set_pitch_transposition(track_index, device_index, semitone_offset)`

### Phase 3 — Configuration

1. Mettre à jour `opencode.jsonc` pour remplacer `uvx ableton-mcp` par notre serveur local
2. Tester chaque outil

## 5. Considérations techniques

### Live API disponible

Le ControlSurface donne accès à l'API Live complète :
- `song.tracks[i].devices[d].parameters[p]` → `DeviceParameter` avec `.name`, `.value`, `.min`, `.max`, `.is_quantized`, `.value_items`
- `clip.get_notes(start_time, start_pitch, end_time, end_pitch)` → tuple de notes
- `clip_slot.delete_clip()` → supprime le clip
- `track.arrangement_clips[i]` → accès aux clips arrangement
- `song.create_scene(index)`, `scene.fire()`, `scene.name`
- `track.mixer_device.sends[i].value`
- `track.current_monitoring_state`
- `track.freeze()`, `track.flatten()`
- `song.save()`, `song.undo()`

### Gestion des timeouts

Les commandes longues (freeze, flatten, save) doivent avoir un timeout plus long dans le MCP server (60s au lieu de 10s).

### Gestion des erreurs

Chaque commande doit catcher les exceptions Live spécifiques et retourner une erreur JSON claire. Les paramètres non trouvés, les index hors limites, les devices sans paramètres sont gérés individuellement.

## 6. Tests

1. `get_device_parameters` → doit retourner la liste des paramètres d'un device
2. `set_device_parameter` → doit modifier la valeur et la retourner
3. `get_clip_notes` → doit lire les notes d'un clip MIDI existant
4. `delete_session_clip` → doit supprimer le clip et confirmer
5. `create_scene` → doit créer une scene et retourner son index
6. `undo` → doit annuler la dernière opération


## 7. Future Explorations.
Voir pour combiener avec un VCVRack MCP  comme https://community.vcvrack.com/t/mcp-server-let-claude-cursor-build-and-control-your-rack-patches-live/25607