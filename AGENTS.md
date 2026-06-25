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
5. `stop_playback()` — toujours stopper la lecture, surtout si la capture échoue

```python
# Workflow standard
stop_playback()
set_arrangement_time(0)      # remet à 0
start_playback()             # joue depuis le début
capture_ableton(duration=15) # capture immédiate
analyze_full(y_path)         # analyse
```

**Remarques sur les timeouts :**
- Si `capture_ableton` ou `capture_and_analyze` time out, réduire `duration` à ≤ 15 s.
- Ne pas lancer plusieurs `load_instrument_or_effect` en parallèle pour éviter la saturation du serveur.
- En cas de timeout persistant, consulter : https://mcpcat.io/guides/fixing-mcp-error-32001-request-timeout

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

Chargement par URI (exemple) : `load_instrument_or_effect(track, "query:Instruments#Synth...")`
Utiliser `get_browser_tree("instruments")` pour explorer les URIs disponibles.

## Profile Utilisateur: David

**Tessiture vocale** : E3–B3 (baryton/tenor confortable)
**Tonalité de référence** : Mi mineur (Em)
**Analyse de référence** : `data/tests/01- Masculiniste-Emotionnal-Indie-Rock.mp3`
- Spectral centroid : 645 Hz (timbre chaud, grave)
- Dynamic range : 81.2 dB (large — voix expressive)
- Tuning offset : -0.05 cents (juste)

**Guide Voice préféré** : Some Trumpets (instrument rack)
**Style de chant** : parlé-chanté, nonchalant et cynique (influence Gainsbourg / Desproges)

## Guide Voix & Tessiture — Méthode

Pour adapter un guide vocal à la tessiture d'un utilisateur :

### 1. Analyser un échantillon vocal
```python
# Charger un fichier MP3/WAV de l'utilisateur
load("path/to/recording.mp3")

# Analyse complète
analyze_full(y_path)  # → key, spectral_centroid, dynamic_range
chroma_cqt(y_path)    # → distribution des hauteurs
```

### 2. Déterminer la tessiture
| Spectral centroid | Tessiture | Décalage conseillé |
|---|---|---|
| < 800 Hz | Grave (baryton/basse) | E3–G3 |
| 800–1200 Hz | Medium (ténor) | G3–C4 |
| > 1200 Hz | Aigu (soprano/alto/falsetto) | C4–E4 |

### 3. Créer le guide vocal
1. Créer les clips MIDI dans la tessiture déterminée (pitch E3=40, G3=43, B3=47, etc.)
2. Suivre les **degrés de l'accord** (root, 3rd, 5th, 7th) de chaque section
3. Respecter le **phrasé des paroles** : une note par temps fort / syllabe accentuée
   - Notes de 1–3 temps pour les syllabes courtes
   - Notes de 4–5 temps pour les fins de phrase
4. Charger un instrument doux (Some Trumpets, Warm Analog Pad) via `load_instrument_or_effect`
5. Dupliquer dans l'arrangement aux positions des couplets/refrains/ponts

### 4. Notes guide par section type (Em, 89 BPM)
| Section | Grille | Guide conseillé |
|---|---|---|
| Couplet | Em7 \| Bm7 \| Am7 \| Em7 | E3→G3→B3→A3→C4→E3 (phrasé 3-5 temps) |
| Refrain | Gmaj9 \| A7#9b13 \| Em9 \| Em9 | G3→D4→A3→B3→E3→G3 (plus large) |
| Pont | Ascendant | E3→G3→A3→B3 (build-up) |
| Outro | Descendant | B3→A3→G3→E3 (fade) |

## Limitations

- Ableton Live Lite : max 8 pistes
- Pas d'API pour freeze/flatten, modifier song_length, ou lire les notes MIDI existantes
- Premier appel MCP après démarrage opencode peut timeout (~60s)
- Arrangement API nécessite Remote Script v1314+ (dans `C:\ProgramData\Ableton\Live XX\Resources\MIDI Remote Scripts\AbletonMCP\__init__.py`)
- `set_arrangement_time(time)` est imprécis : la position réelle peut différer de la valeur demandée (décalage systématique). Contournement : utiliser `start_playback()` puis régler manuellement dans Live, ou capturer à la position courante.
- `load_instrument_or_effect` peut timeout si le serveur est occupé. Réessayer en réduisant la charge (ne pas lancer plusieurs appels simultanés).
- **Pas d'API pour lire ou modifier les paramètres des devices** — `get_track_info` retourne les noms et types de devices mais pas leurs valeurs de paramètres (cutoff, resonance, threshold, ratio, etc.). Tout réglage fin doit être fait manuellement dans Live.

## Paramètres des devices

L'API MCP actuelle **ne permet pas** de lire ou modifier les paramètres individuels d'un device (potards, boutons, sliders). `get_track_info()` liste les devices (nom, class_name) mais pas leurs paramètres internes.

### Contournements

1. **Presets browser** — Utiliser `get_browser_tree("audio_effects")` / `get_browser_items_at_path(...)` pour trouver un preset dont les réglages se rapprochent du résultat voulu, puis `load_instrument_or_effect(track, uri)`. Exemple : au lieu de régler manuellement un Auto Filter, chercher un preset "Dub Low Pass" dans le browser.

2. **Réglage manuel obligatoire** dans Live pour :
   - **Auto Filter** : mode (LPF/HPF/BPF), cutoff, resonance, LFO amount/speed
   - **Compressor** : threshold, ratio, attack, release, knee, makeup gain
   - **Channel EQ** : fréquences, gain, Q de chaque bande
   - **Reverb** : decay, pre-delay, size, diffusion, mix
   - **Delay** : tempo sync, feedback, filter, mix
   - **Saturator** : mode (A Bit Warmer, Studio Tape, etc.), drive, output
   - **Limiter** : threshold, output ceiling
   - **VST3** (ex: Surge XT) : tous les paramètres internes du plugin

3. **Workflow recommandé** :
   - Charger le device via `load_instrument_or_effect` (pour avoir le bon type d'effet)
   - Ouvrir Live et tweaker manuellement les paramètres
   - (Optionnel) Sauvegarder le réglage comme preset utilisateur dans Live pour le réutiliser

## Troubleshooting : Timeout MCP (-32001)

**Référence :** https://mcpcat.io/guides/fixing-mcp-error-32001-request-timeout

Les erreurs `MCP error -32001 (Request timed out)` surviennent principalement dans deux cas :

### 1. `capture_ableton` / `capture_and_analyze`
- **Cause :** la capture bloque pendant `duration` secondes. Si la durée est > 15-20 s, le timeout du serveur MCP peut être atteint avant la fin.
- **Solution :** utiliser `duration ≤ 15` pour la capture, puis traiter l'analyse séparément si besoin. Exemple :
  ```
  capture_ableton(duration=10)     # ne pas dépasser 15s
  analyze_full(y_path)              # analyse légère, rapide
  ```
- **Si la capture renvoie « audio is silence » :** vérifier que l'Output Device d'Ableton pointe bien sur « CABLE Input (VB-Audio Virtual Cable) » et que la lecture est active.

### 2. `load_instrument_or_effect`
- **Cause :** le serveur Ableton MCP est saturé (surtout si plusieurs appels sont lancés en parallèle ou si l'interface Live est en train de charger un preset lourd).
- **Solutions :**
  - Attendre que tout chargement précédent soit terminé avant de lancer le suivant.
  - Réduire le nombre d'appels simultanés (un seul `load_instrument_or_effect` à la fois).
  - Si le timeout persiste, redémarrer le serveur MCP (`uvx ableton-mcp`).

### 3. Règle générale
- Toujours utiliser `timeout` param si disponible (certains outils MCP acceptent `timeout` en ms dans l'appel).
- Éviter les `duration` > 30 pour les captures audio (préférer des captures courtes et successives).
- Si le problème persiste, consulter : https://mcpcat.io/guides/fixing-mcp-error-32001-request-timeout

## Remote Script Installation

Copier `AbletonMCP_Remote_Script.py` (renommé `__init__.py`) dans :
```
C:\ProgramData\Ableton\Live XX\Resources\MIDI Remote Scripts\AbletonMCP\__init__.py
```
Puis Options → Preferences → Link, Tempo & MIDI → Control Surface = "AbletonMCP", Input/Output = "None".
