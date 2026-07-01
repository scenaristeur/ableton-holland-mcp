# AGENTS.md — Ableton Holland MCP

## Vue d'ensemble

Assistant de production musicale connecté à Ableton Live via un **serveur MCP unifié** :
- **`ableton-full`** (`ableton_full_mcp_server.py`) — contrôle d'Ableton (pistes, clips, instruments, arrangement) + capture audio via VB-Cable + analyse librosa
- **`surge-osc`** (`surge_osc_mcp.py`) — contrôle de Surge XT via OSC (paramètres, patches, notes)

## Serveur MCP

### ablebon-full (démarrage) — local
```
"command": [".venv/Scripts/python", "ableton_full_mcp_server.py"]
```

### surge-osc (démarrage) — local
```
"command": [".venv/Scripts/python", "surge_osc_mcp.py"]
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
| `start_playback_at(time)` | Positionner ET démarrer atomiquement (évite le saut de playhead) |
| `set_metronome(value)` / `get_metronome()` | Métronome on/off |
| `set_session_record(value)` / `get_session_record()` | Session record on/off |
| `nudge_up()` / `nudge_down()` | Nudge tempo fin |
| `set_signature(numerator, denominator)` | Signature rythmique |

### Pistes
| Tool | Description |
|---|---|
| `create_midi_track(index=-1)` | Créer piste MIDI (index -1 = fin) |
| `set_track_name(index, name)` | Renommer "1-Nom", "2-Nom"... |
| `freeze_track(index)` | Freeze une piste |
| `flatten_track(index)` | Flatten une piste frozen |
| `delete_track(index)` | Supprimer une piste |
| `duplicate_track(index)` | Dupliquer une piste |
| `select_track(index)` | Sélectionner une piste (UI focus) |
| `get_track_color(index)` / `set_track_color(index, color)` | Couleur piste (0–255) |

### Clips Session
| Tool | Description |
|---|---|
| `create_clip(track, slot, length)` | Créer clip MIDI dans un slot vide |
| `add_notes_to_clip(track, slot, notes)` | Notes : `[{pitch, start_time, duration, velocity, mute}]` |
| `set_clip_name(track, slot, name)` | Nommer un clip |
| `fire_clip(track, slot)` / `stop_clip(track, slot)` | Lancer/arrêter |
| `get_clip_notes(track, slot)` | Lire les notes MIDI d'un clip |
| `delete_session_clip(track, slot)` | Supprimer un clip session |
| `delete_arrangement_clip(track, index)` | Supprimer un clip arrangement |
| `duplicate_clip(track, slot)` | Dupliquer un clip (slot libre suivant) |
| `quantize_clip(track, slot, amount)` | Quantifier (0.0–1.0) |
| `get_clip_color(track, slot)` / `set_clip_color(track, slot, color)` | Couleur clip (0–255) |

### Instruments / Effets
| Tool | Description |
|---|---|
| `load_instrument_or_effect(track, uri)` | Charger un device par URI |
| `get_browser_tree(category)` | Explorer le browser (`all`, `instruments`, `sounds`, `drums`, `audio_effects`, `midi_effects`) |
| `get_browser_items_at_path(path)` | Items à un chemin (`"Instruments/Synth"`) |

### Device Parameters (NEW)
| Tool | Description |
|---|---|
| `get_device_parameters(track, device)` | Lire tous les paramètres d'un device (nom, valeur, min, max, quantized) |
| `set_device_parameter(track, device, parameter_name, value)` | Modifier la valeur d'un paramètre |

### Arrangement (Remote Script v1314+ nécessaire)
| Tool | Description |
|---|---|
| `switch_to_arrangement_view()` | Basculer en vue Arrangement |
| `set_arrangement_time(time)` | Positionner le playhead (beats) |
| `get_arrangement_clips(track)` | Lister les clips dans l'arrangement |
| `duplicate_to_arrangement(track, slot, dest_time)` | Copier clip Session → Arrangement |
| `get_arrangement_clip_notes(track, index)` | Lire notes MIDI d'un clip arrangement |

### Audio
| Tool | Description |
|---|---|
| `create_audio_clip(track, slot, path)` | Importer fichier audio (Live 12.0.5+) |

### Scenes (NEW)
| Tool | Description |
|---|---|
| `create_scene(index=-1)` | Créer une scene |
| `fire_scene(index)` | Lancer une scene |

### Mixer (NEW)
| Tool | Description |
|---|---|
| `get_sends(track)` | Lire les niveaux d'envoi |
| `set_send(track, send_index, value)` | Régler un envoi |
| `set_monitoring(track, state)` | Monitoring : 0=auto, 1=in, 2=off |

### Crossfader (NEW)
| Tool | Description |
|---|---|
| `get_crossfader()` | Lire la position du crossfader master (0.0–1.0) |
| `set_crossfader(value)` | Positionner le crossfader master |

### Groove (NEW)
| Tool | Description |
|---|---|
| `get_groove_amount()` | Lire le groove global (0.0–1.0) |
| `set_groove_amount(amount)` | Régler le groove global |

### Project (NEW)
| Tool | Description |
|---|---|
| `save_project()` | Sauvegarder le projet (non disponible dans Live 12 Lite — sauvegarder manuellement) |
| `undo()` / `redo()` | Annuler/rétablir |

## Outils Surge XT (OSC)

### Patches
| Tool | Description |
|---|---|
| `surge_get_patch(instance=0)` | Nom du patch actuel pour l'instance N |
| `surge_load_patch(path, instance=0)` | Charger un patch (path absolu sans extension) |
| `surge_incr_patch(instance=0)` / `surge_decr_patch(instance=0)` | Patch suivant/précédent |
| `surge_random_patch(instance=0)` | Patch aléatoire |

### Paramètres
| Tool | Description |
|---|---|
| `surge_get_param(address, instance=0)` | Lire un paramètre (ex: `/param/a/filter/1/cutoff`) |
| `surge_set_param(address, value, instance=0)` | Modifier un paramètre (0.0–1.0) |
| `surge_query_all(instance=0)` | Dumper tous les paramètres |

### Notes
| Tool | Description |
|---|---|
| `surge_note_on(pitch, velocity, instance=0)` | Note MIDI on |
| `surge_note_off(pitch, instance=0)` | Note MIDI off |
| `surge_all_notes_off(instance=0)` | Couper toutes les notes |

### Adresses OSC courantes
```
/param/a/osc/1/pitch       /param/a/osc/2/pitch       /param/a/osc/3/pitch
/param/a/osc/1/type        /param/a/osc/1/param1..7   (morph, skew, saturate, etc.)
/param/a/filter/1/cutoff   /param/a/filter/1/resonance
/param/a/filter/2/cutoff   /param/a/filter/2/resonance
/param/a/amp/volume        /param/a/amp/pan           /param/a/amp/gain
/param/a/mixer/osc1/volume /param/a/mixer/osc1/mute   /param/a/mixer/noise/volume
/param/macro/1..8          /param/global/volume        /param/global/polyphony_limit
/param/a/play_mode         /param/a/osc/fm_depth       /param/a/waveshaper/drive
```

**Note :** `surge_load_patch` convertit automatiquement les `/` en `\` (Windows) pour éviter l'affichage du chemin complet dans Surge XT. L'OSC doit être activé dans Surge XT (Settings → OSC → Enable). Par défaut port IN 53280, OUT 53281. Jusqu'à 8 instances Surge XT supportées (ports : 53280-53295, stride=2).

### Configuration OSC dans Surge XT

1. Ouvrir Surge XT dans Ableton
2. Cliquer sur le logo **"S"** en haut à gauche → **Settings** → **OSC**
3. Cocher **Enable OSC**
4. Configurer les ports :
   - **Port (IN)** : port sur lequel Surge écoute (le serveur MCP y envoie)
   - **Port (OUT)** : port sur lequel Surge envoie ses réponses (le serveur MCP écoute)
5. Par défaut : IN=53280, OUT=53281
6. Pour plusieurs instances : chaque instance sur une paire différente (ex: instance 1 = IN=53282, OUT=53283)

### Paramètres FX OSC
Surge XT intègre 4 slots FX par chaîne (A/B), accessibles via :
```
/param/fx/a/1/type       /param/fx/a/1/param1..12
/param/fx/a/2/type       /param/fx/a/2/param1..12
/param/fx/b/1/type       /param/fx/b/1/param1..12
/param/fx/send/1..4/type /param/fx/send/1..4/param1..12
/param/fx/global/1..4/type /param/fx/global/1..4/param1..12
```
`type=0` = pas d'effet, `type>=1` = effet sélectionné selon l'index.

## Outils Music Analysis disponibles

### Capture
| Tool | Description |
|---|---|
| `capture_ableton(duration=5)` | Capture audio depuis VB-Cable → WAV |
| `capture_at_position(position, duration, output_name)` | **Atomique** : stop → switch → start_playback_at → capture → stop → load |
| `capture_and_analyze(position, duration, output_name)` | Capture + analyse complète en un appel |

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
**Important :** `set_arrangement_time` retourne des valeurs obsolètes (lit l'ancienne position). Toujours vérifier avec `get_session_info`.  
**Important :** `start_playback_at(time)` combine positionnement + lecture atomiquement. `start_playing()` PUIS `current_song_time = X` (Live reset le temps au démarrage).

#### Workflow standard (capture depuis le début)

```python
# Atomic : stop → seek → play → capture → stop → load → analyze
capture_and_analyze(position_beats=0, duration_sec=10)
```

#### Workflow capture à une position précise (ex: couplet à beat 32)

```python
# Atomic : tout en un appel
capture_and_analyze(position_beats=32, duration_sec=10, output_name="couplet1")
```

#### Workflow manuel (pas à pas si besoin)

```python
stop_playback()
switch_to_arrangement_view()
start_playback_at(desired_time)          # ex: 32
get_session_info()                       # vérifier position
capture_ableton(duration=N)              # capturer (bloquant)
stop_playback()
analyze_full(y_path)
```

**Remarques sur les timeouts :**
- `capture_at_position` et `capture_and_analyze` bloquent `duration_sec` secondes (le temps de capture). Avec le timeout MCP à 600s (config), les captures jusqu'à 60s passent.
- Ne pas lancer plusieurs `load_instrument_or_effect` en parallèle pour éviter la saturation du serveur.
- En cas de timeout persistant, consulter : https://mcpcat.io/guides/fixing-mcp-error-32001-request-timeout

## Conventions

### Nommage pistes
- `1-Instrument`, `2-Instrument`, etc. (maintient l'ordre dans Ableton)

### Conventions de mesure
**L'utilisateur parle en mesures (barres), pas en beats.** Dans Ableton, l'affichage principal est en mesures. Convertir systématiquement :
- 1 mesure = 4 beats (en 4/4)
- Les `start_time` des notes MIDI sont en beats (l'API MCP utilise des beats)
- Quand tu parles à l'utilisateur, utilise **toujours les mesures**

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

## Préférences Production

### Contraintes techniques
- **Max 8 pistes** (Ableton Live Lite)
- **Max 16 scènes** par piste (session view)
- **Plugins natifs Ableton uniquement** (Analog, Drift, Wavetable, Electric, Drum Rack, Simpler, effets natifs)
- **Drumkit pré-existant** (Drum Rack avec kit .adg existant — privilégier un kit déjà prêt plutôt que de le construire)
- Pas de limite de jouabilité — gammes riches, harmonies complexes, emprunts modaux bienvenus

### Choix créatifs par défaut
- **Français** sauf demande contraire
- **Voix : parlé-chanté**, tessiture E3–B3
- **Tonalité de prédilection : C#m** (nouveau), sinon Em
- **Structure courte** privilégiée (~1m30-2m) sauf demande contraire
- **Pop organique** — instruments aux timbres chauds, drums naturels, pas d'EDM
- **Styles de référence :** indie rock français, Gainsbourg, pop analogique

### Drum kits recommandés (par vibe)
| Vibe | Kit |
|---|---|
| Organique / chaud | `Selector Kit Warm.adg` |
| Généraliste | `Gen Purpose Kit.adg` |
| Sec / naturel | `Dry Session Kit.adg` |
| Lo-fi | `Toy LoFi Kit.adg` |
| Hybride studio | `Recording Hybrid Kit - Damped Snare.adg` |

### Chaîne FX natives recommandées
- **Drums :** Drum Buss → Compressor → Reverb (send)
- **Basse :** Amp → Compressor → Saturator
- **Piano/Keys :** Reverb → Chorus → Compressor
- **Pad :** Reverb → Auto Filter → Delay
- **Lead :** Delay → Reverb → Auto Filter
- **Voix :** EQ Eight → Compressor → Reverb → Delay
- **Percs :** Reverb (send) → Saturator
- **FX :** Reverb → Delay → Grain Delay → Auto Filter

## Guide Voix & Tessiture — Méthode Générique

### 0. Scanner le projet
Avant de commencer :
1. Lire le dossier `sources/<nom_projet>/` pour identifier les éléments existants (paroles brutes, accords, structure, instrument souhaité)
2. Lister les chansons à produire et leur ordre
3. Proposer à l'utilisateur la création des fichiers de chaque chanson :
   - `PAROLES.md` (paroles + guide voix détaillé)
   - Fichier structure (accords, tempo, arrangement)
4. Attendre la validation de l'utilisateur avant de créer les fichiers

### 1. Analyser un échantillon vocal (si disponible)
```python
load("path/to/recording.mp3")
analyze_full(y_path)
chroma_cqt(y_path)
```

### 2. Déterminer la tessiture
| Spectral centroid | Tessiture | Décalage conseillé |
|---|---|---|
| < 800 Hz | Grave (baryton/basse) | E3–G3 |
| 800–1200 Hz | Medium (ténor) | G3–C4 |
| > 1200 Hz | Aigu (soprano/alto/falsetto) | C4–E4 |

### 3. Créer le fichier PAROLES.md avec guide voix
Pour chaque section de la chanson (couplet, refrain, pont, etc.) :

1. **Identifier la grille d'accords** de chaque section
2. **Annoter chaque ligne de paroles** avec les notes guides :
   - Une note par temps fort / syllabe accentuée
   - Notation : `G3 ◷3` = note G3 tenue 3 temps
   - `→` poursuite sur la même note ou enchaînement
3. **Rester dans la tessiture** de l'utilisateur (E3–B3 pour David)
4. **Suivre les degrés de l'accord** (root, 3rd, 5th) pour chaque note guide
   - Sur un accord de G : G3 (root), B3 (3rd), D4 (5th)
   - Sur un accord de Em : E3 (root), G3 (b3rd), B3 (5th)
   - Sur un accord de C : C4 (root), E3 (3rd), G3 (5th)
   - Sur un accord de Am : A3 (root), C4 (b3rd), E3 (5th)
5. **Durées de notes** :
   - Syllabes courtes / début de phrase : 1–3 temps (souvent `◷3`)
   - Fins de phrase / mots clés : 4–8 temps (`◷5` à `◷8`)
6. **Ajouter un tableau de correspondance** pitch → note en fin de fichier

### 4. Créer le guide vocal dans Ableton
1. Charger un instrument guide clair (Sweet Lead, Shimmer Pluck, Soft Lead, etc.) via `load_instrument_or_effect` — éviter les instruments déjà utilisés dans la production
2. Créer un clip MIDI par section, avec les notes du guide placées aux start_time correspondant aux temps forts
3. Nommer chaque clip (`Guide - Couplet 1`, `Guide - Refrain`, etc.)
4. Dupliquer dans l'arrangement aux positions des sections correspondantes

### 5. Exemple de guide voix (format PAROLES.md)
```markdown
## Couplet (8 mesures)

*Accords : G | Em | C | D*

**Mes. 1-2 (G) :** `G3 ◷3` Texte sur le→`B3 ◷5` temps fort de la phrase

**Mes. 3-4 (Em) :** `E3 ◷3` Deuxième ligne→`B3 ◷5` du couplet

**Mes. 5-6 (C) :** `C4 ◷3` Troisième phrase→`G3 ◷5` qui se termine

**Mes. 7-8 (D) :** `A3 ◷3` Dernière ligne du→`F#3 ◷5` couplet en descente
```

## Limitations

- **Captures audio : ne JAMAIS lancer plusieurs captures en parallèle.** Chaque capture fait stop/seek/play/record/stop. Lancer `capture_and_analyze` ou `capture_ableton` une par une, attendre la réponse avant la suivante.
- Ableton Live Lite : max 8 pistes
- `save_project()` n'est **pas disponible** via l'API Live 12 Lite (ni `Song.save()`, ni `Application.save_current_song()`). Sauvegarder manuellement (Ctrl+S).
- Premier appel MCP après démarrage opencode peut timeout (~60s)
- Arrangement API nécessite Remote Script v1314+ (dans `C:\ProgramData\Ableton\Live XX\Resources\MIDI Remote Scripts\AbletonMCP\__init__.py`)
- `set_arrangement_time(time)` est imprécis : la position réelle peut différer de la valeur demandée (décalage systématique). Contournement : utiliser `start_playback_at(time)` qui combine positionnement + démarrage atomiquement.
- `start_playback_at(time)` : `start_playing()` reset `current_song_time` à 0. L'ordre correct est `start_playing()` PUIS `current_song_time = X` (dans `AbletonMCP_Remote_Script.py`).
- `load_instrument_or_effect` peut timeout si le serveur est occupé. Réessayer en réduisant la charge (ne pas lancer plusieurs appels simultanés).
- Pour déployer le Remote Script, le copier manuellement dans le dossier Ableton pendant qu'Ableton est fermé.

## Paramètres des devices

L'API MCP **permet maintenant** de lire et modifier les paramètres individuels d'un device :
- `get_device_parameters(track, device)` — lit tous les paramètres (nom, valeur, min, max, quantifié)
- `set_device_parameter(track, device, parameter_name, value)` — modifie la valeur

### Limites connues

- Les paramètres `is_enabled=False` (certains params hérités ou dépendants) sont en lecture seule (skippés)
- Les paramètres quantifiés (menus déroulants) prennent un index entier
- L'API ne permet pas de lire/écrire les **courbes d'automation** — seulement les valeurs statiques
- Les devices VST3 peuvent exposer leurs paramètres différemment selon l'implémentation

### Contournements (quand l'API ne suffit pas)

1. **Presets browser** — Utiliser `get_browser_tree("audio_effects")` / `get_browser_items_at_path(...)` pour trouver un preset dont les réglages se rapprochent du résultat voulu, puis `load_instrument_or_effect(track, uri)`.
2. Pour des réglages très fins (automation, routing), ouvrir Live manuellement.

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
