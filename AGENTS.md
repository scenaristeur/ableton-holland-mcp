# AGENTS.md — Ableton Holland MCP

## Vue d'ensemble

Assistant de production musicale connecté à Ableton Live via deux serveurs MCP :
- **`ableton-mcp`** (uvx) — contrôle d'Ableton (pistes, clips, instruments, arrangement)
- **`music-analysis`** (`music_analysis_plus.py`) — capture audio via VB-Cable + analyse librosa

## Serveurs MCP

### ableton-mcp (démarrage)
```
"command": ["uvx", "ableton-mcp"]
```

### music-analysis (démarrage)
```
"command": [".venv/Scripts/python", "music_analysis_plus.py"]
```

## Audio Routing (Voicemeeter + VB-Cable)

```
Ableton → Voicemeeter VAIO → A1: Enceintes (monitoring)
                            → A2: CABLE Input → CABLE Output → capture
```

Monitoring : A1 = speakers, A2 = CABLE Input (pour capture)
Capture MCP écoute sur CABLE Output (sounddevice)
Buffer Voicemeeter : 1024 samples pour stabilité

## Outils Ableton MCP disponibles

### Session / Transport
| Tool | Description |
|---|---|
| `get_session_info()` | Tempo, signature, tracks, is_playing, current_song_time |
| `get_track_info(index)` | Piste : nom, clips, devices, volume, pan, mute/solo/arm |
| `set_tempo(bpm)` | Changer le tempo |
| `start_playback()` / `stop_playback()` | Démarrer/arrêter |

### Pistes
| Tool | Description |
|---|---|
| `create_midi_track(index=-1)` | Créer piste MIDI (index -1 = fin) |
| `set_track_name(index, name)` | Renommer "1-Nom", "2-Nom"... |

### Clips Session
| Tool | Description |
|---|---|
| `create_clip(track, slot, length)` | Créer clip MIDI dans un slot vide |
| `add_notes_to_clip(track, slot, notes)` | Notes : `[{pitch, start_time, duration, velocity, mute}]` |
| `set_clip_name(track, slot, name)` | Nommer un clip |
| `fire_clip(track, slot)` / `stop_clip(track, slot)` | Lancer/arrêter |

### Instruments / Effets
| Tool | Description |
|---|---|
| `load_instrument_or_effect(track, uri)` | Charger un device par URI |
| `get_browser_tree(category)` | Explorer le browser (`all`, `instruments`, `sounds`, `drums`, `audio_effects`, `midi_effects`) |
| `get_browser_items_at_path(path)` | Items à un chemin (`"Instruments/Synth"`) |

### Arrangement (Remote Script v1314+ nécessaire)
| Tool | Description |
|---|---|
| `switch_to_arrangement_view()` | Basculer en vue Arrangement |
| `set_arrangement_time(time)` | Positionner le playhead (beats) |
| `get_arrangement_clips(track)` | Lister les clips dans l'arrangement |
| `duplicate_to_arrangement(track, slot, dest_time)` | Copier clip Session → Arrangement |

### Audio
| Tool | Description |
|---|---|
| `create_audio_clip(track, slot, path)` | Importer fichier audio (Live 12.0.5+) |

## Outils Music Analysis disponibles

### Capture
| Tool | Description |
|---|---|
| `capture_ableton(duration=5)` | Capture audio depuis VB-Cable → WAV |
| `capture_and_analyze(duration=5)` | Capture + analyse complète |
| `capture_and_tempo(duration=5)` | Capture + BPM |

### Analyse
| Tool | Description |
|---|---|
| `load(path)` | Charger fichier audio |
| `tempo(y_path)` | Estimer BPM |
| `detect_key(y_path)` | Détection tonalité (Krumhansl-Kessler) |
| `analyze_energy(y_path)` | RMS, peak, dynamic range |
| `analyze_spectral(y_path)` | Centroid, rolloff, bandwidth, ZCR |
| `analyze_tuning(y_path)` | Cents offset |
| `analyze_full(y_path)` | Tout-en-un (key + energy + spectral + tuning) |
| `beat_track(y_path)` | Beat tracking |
| `chroma_cqt(y_path)` | Chromagram (12 notes) |
| `mfcc(y_path)` | Timbre spectral |

## Workflows types

### Créer une piste instrument
```
create_midi_track → set_track_name → load_instrument_or_effect (URI browser)
```

### Créer et remplir un clip
```
create_clip(track, slot, length) → add_notes_to_clip → set_clip_name → fire_clip
```

### Construire un arrangement
```
switch_to_arrangement_view → duplicate_to_arrangement × N → get_arrangement_clips → start_playback
```

### Analyser le mix (workflow obligatoire)
**Important :** Sans loop dans l'arrangement, Ableton ne boucle pas — le playhead avance jusqu'à la fin et s'arrête. Toujours faire :

1. `stop_playback()` — stopper la lecture
2. `set_arrangement_time(0)` — remettre le playhead au début (ou `set_arrangement_time(8)` si 0 ne fonctionne pas)
3. `start_playback()` — lancer la lecture
4. **Immédiatement** `capture_ableton(duration=N)` — capturer pendant que le son joue

```python
# Workflow standard
stop_playback()
set_arrangement_time(0)      # remet à 0
start_playback()             # joue depuis le début
capture_ableton(duration=15) # capture immédiate
analyze_full(y_path)         # analyse
```

## Conventions

### Nommage pistes
- `1-Instrument`, `2-Instrument`, etc. (maintient l'ordre dans Ableton)

### Durées clip (100 BPM, 4/4)
- 1 barre = 4.0 beats
- 2 barres = 8.0 beats
- 4 barres = 16.0 beats
- 6 barres = 24.0 beats

### Notes MIDI (pitch)
- C4 = 60, D4 = 62, E4 = 64, F4 = 65, G4 = 67, A4 = 69, B4 = 71
- C3 = 48, D3 = 50, E3 = 52, F3 = 53, G3 = 55, A3 = 57, B3 = 59
- C2 = 36, D2 = 38, E2 = 40, F2 = 41, G2 = 43, A2 = 45, B2 = 47

### Structure arrangement type
- Intro (4 barres) : drums seuls
- Verse (4-8 barres) : entrée basse
- Verse 2 (4-8 barres) : + pads
- Buildup / Chorus : + lead, variations
- Outro : tutti ou fade

## Plugins installés

- **Surge XT** (VST3) — synthé open-source puissant
- **Surge XT Effects** (VST3)
- **Kontakt 7 & 8** (VST3)
- **Massive X** (VST3)
- **Reaktor 6** (VST3)
- **Guitar Rig 7**
- **ValhallaSupermassive** (VST3) — reverb/delay spatial
- **Raum** (NI) — reverb
- **Replika** (NI) — delay
- **Supercharger** (NI) — compression

Chargement par URI (exemple) : `load_instrument_or_effect(track, "query:Instruments#Synth...")`
Utiliser `get_browser_tree("instruments")` pour explorer les URIs disponibles.

## Limitations

- Ableton Live Lite : max 8 pistes
- Pas d'API pour freeze/flatten, modifier song_length, ou lire les notes MIDI existantes
- Premier appel MCP après démarrage opencode peut timeout (~60s)
- Arrangement API nécessite Remote Script v1314+ (dans `C:\ProgramData\Ableton\Live XX\Resources\MIDI Remote Scripts\AbletonMCP\__init__.py`)

## Remote Script Installation

Copier `AbletonMCP_Remote_Script.py` (renommé `__init__.py`) dans :
```
C:\ProgramData\Ableton\Live XX\Resources\MIDI Remote Scripts\AbletonMCP\__init__.py
```
Puis Options → Preferences → Link, Tempo & MIDI → Control Surface = "AbletonMCP", Input/Output = "None".
