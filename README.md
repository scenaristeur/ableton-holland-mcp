# Ableton Holland MCP

Capture audio en direct depuis **Ableton Live** via **VB-Cable** et analyse musicale automatique avec **librosa**.

## Architecture

```
┌─────────────────┐     Voicemeeter     ┌──────────────┐
│  Ableton Live   │────Virtual Input──▶│  Voicemeeter │
│  (audio engine) │                    │  (mixer)     │
└─────────────────┘                    └──────┬───────┘
                                              │
                          ┌───────────────────┼───────────────────┐
                          ▼                   ▼                   ▼
                   ┌────────────┐     ┌──────────────┐     ┌──────────────┐
                   │  Enceintes │     │  CABLE Input │     │  Casque /    │
                   │  (Intel)   │     │  (VB-Cable)  │     │  Focusrite   │
                   │  monitoring│     │  (capture)   │     │  (optionnel) │
                   └────────────┘     └──────┬───────┘     └──────────────┘
                                             │
                                             ▼
                                      ┌──────────────┐
                                      │ CABLE Output │
                                      │ (sounddevice)│
                                      └──────┬───────┘
                                             │
                                   ┌─────────┴─────────┐
                                   ▼                   ▼
                            ┌────────────┐     ┌──────────────┐
                            │ MCP server │     │  Dashboard   │
                            │ (opencode) │     │  (Tkinter)   │
                            └──────┬─────┘     └──────┬───────┘
                                   │                   │
                                   ▼                   ▼
                             ┌──────────────────────────┐
                             │      librosa (analyse)   │
                             └────────────┬─────────────┘
                                          ▼
                             ┌──────────────────────┐
                             │   data/analyses/     │
                             │   (.wav + .csv)      │
                             └──────────────────────┘
```

## Prérequis

| Logiciel | Rôle |
|---|---|---|
| [Ableton Live](https://www.ableton.com) 11+ | Station audio |
| [VB-Cable](https://vb-audio.com/Cable/) | Routage audio virtuel (capture) |
| [Voicemeeter](https://vb-audio.com/Voicemeeter/) (Vanilla ou Banana) | Mixeur virtuel (monitoring + routage) |
| Python 3.12+ | Moteur d'analyse |
| [opencode](https://opencode.ai) | CLI agent MCP |

## Installation

### 1. VB-Cable

1. Télécharger depuis [vb-audio.com/Cable](https://vb-audio.com/Cable/)
2. Lancer `VBCABLE_Setup.exe` en administrateur
3. Redémarrer Windows

### 2. Voicemeeter

1. Télécharger depuis [vb-audio.com/Voicemeeter](https://vb-audio.com/Voicemeeter/)
2. Lancer `VoicemeeterSetup.exe` en administrateur
3. Redémarrer Windows

### 3. Python

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configuration Voicemeeter

1. Lancer **Voicemeeter** (démarrer menu ou `C:\Program Files (x86)\VB\Voicemeeter\Voicemeeter.exe`)
2. Dans **Hardware Out** (colonne de droite) :
   - **A1** → choisir tes enceintes (Intel Display Audio, Focusrite...)
   - **A2** → choisir **CABLE Input (VB-Audio Virtual Cable)**
3. Dans **Virtual Input** (colonne de gauche) → laisser **Voicemeeter VAIO** par défaut
4. Régler les niveaux (A1 = monitoring, A2 = capture)

### 5. Configuration Ableton Live

1. **Options → Preferences → Audio**
2. Driver Type: **MME / DirectX**
3. Audio Output Device: **Voicemeeter Virtual Audio Cable** (ou **Voicemeeter VAIO**)
4. Audio Input Device: **CABLE Output (VB-Audio Virtual Cable)** (optionnel)
5. Activer **"In/Out"** dans la vue Session

### 6. AbletonMCP Remote Script

Le Remote Script `AbletonMCP_Remote_Script.py` (à la racine du projet) permet à `ableton-mcp` de communiquer avec Ableton Live via socket.

#### Installation

1. Copie `AbletonMCP_Remote_Script.py` et renommer dans le dossier des Remote Scripts d'Ableton :

--> "C:\ProgramData\Ableton\Live 12 Lite\Resources\MIDI Remote Scripts\AbletonMCP\__init__.py"

 copy /Y "C:\Users\admin\dev\ableton-holland-mcp\AbletonMCP_Remote_Script.py" "C:\ProgramData\Ableton\Live 12 Lite\Resources\MIDI Remote Scripts\AbletonMCP\__init__.py"


2. Lance **Ableton Live** → **Options → Preferences → Link, Tempo & MIDI**
3. Dans **Control Surface**, sélectionne **"AbletonMCP"**
4. Mets **Input** et **Output** sur **"None"**
5. Redémarre Ableton

Le script se trouve aussi dans le dépôt GitHub original : [ahujasid/ableton-mcp/AbletonMCP_Remote_Script](https://github.com/ahujasid/ableton-mcp/blob/main/AbletonMCP_Remote_Script/__init__.py)

### 7. Configuration opencode

```json
{
  "mcp": {
    "ableton-full": {
      "type": "local",
      "command": [".venv/Scripts/python", "ableton_full_mcp_server.py"],
      "enabled": true
    }
  }
}
```

Le serveur `ableton-full` (unifié) remplace les deux anciens serveurs (`ableton-mcp` + `music-analysis`). Un seul process, outils atomiques comme `capture_at_position`.

## Outils MCP disponibles (serveur unifié `ableton-full`)

### Capture audio atomique (nouveau)

| Tool | Description |
|---|---|
| `capture_at_position(position_beats, duration_sec, output_name)` | Stop → switch view → seek → play → capture (bloque `duration_sec` s) → stop → load WAV |
| `capture_and_analyze(position_beats, duration_sec, output_name)` | `capture_at_position` + analyse complète en un seul appel |
| `capture_ableton(duration, output_name)` | Capture audio depuis VB-Cable (standalone) |

### Analyse (fichier existant)

| Tool | Description |
|---|---|
| `load(file_path)` | Charge un fichier audio (fix: `np.mean` au lieu de `librosa.to_mono`) |
| `analyze_full_tool(y_path)` | Tout-en-un : key, energy, spectral, tuning, tempo |
| `analyze_energy_tool(y_path)` | RMS, peak, dynamic range |
| `analyze_spectral_tool(y_path)` | Centroid, rolloff, bandwidth, ZCR |
| `analyze_tuning_tool(y_path)` | Cents offset |
| `detect_key_tool(y_path)` | Détection tonalité (Krumhansl-Kessler) |
| `tempo_tool(y_path)` | Estime le BPM |
| `get_duration_tool(y_path)` | Durée en secondes |
| `beat_track_tool(y_path)` | Détecte les temps forts |
| `chroma_cqt_tool(y_path)` | Chromagram (12 notes) |
| `mfcc_tool(y_path)` | Timbre / texture spectrale |

### Contrôle Ableton (Session / Transport)

| Tool | Description |
|---|---|
| `get_session_info()` | Tempo, signature, tracks, is_playing, current_song_time |
| `get_track_info(index)` | Détails d'une piste (nom, clips, devices, volume, pan) |
| `set_tempo(bpm)` | Changer le tempo |
| `start_playback()` / `stop_playback()` | Démarrer/arrêter |
| `start_playback_at(time)` | **Start playback first, THEN seek** (correction : Live reset le temps au `start_playing()`) |
| `set_arrangement_time(time)` | Positionner le playhead |

### Pistes & Clips

| Tool | Description |
|---|---|
| `create_midi_track(index)` | Nouvelle piste MIDI |
| `set_track_name(index, name)` | Renommer |
| `delete_track(index)` | Supprimer |
| `duplicate_track(index)` | Dupliquer |
| `create_clip(track, slot, length)` | Nouveau clip MIDI |
| `add_notes_to_clip(track, slot, notes)` | Ajouter des notes MIDI |
| `get_clip_notes(track, slot)` | Lire les notes MIDI |
| `set_clip_name(track, slot, name)` | Nommer un clip |
| `fire_clip(track, slot)` / `stop_clip(track, slot)` | Lancer/arrêter un clip |
| `duplicate_clip(track, slot)` | Dupliquer un clip |
| `delete_session_clip(track, slot)` | Supprimer clip session |
| `delete_arrangement_clip(track, index)` | Supprimer clip arrangement |
| `quantize_clip(track, slot, amount)` | Quantifier (0.0–1.0) |
| `duplicate_to_arrangement(track, slot, dest_time)` | Copier clip Session → Arrangement |
| `get_arrangement_clips(track)` | Lister clips arrangement |

### Instruments & Effets

| Tool | Description |
|---|---|
| `get_browser_tree(category)` | Explorer le browser |
| `get_browser_items_at_path(path)` | Items à un chemin |
| `load_instrument_or_effect(track, uri)` | Charger un instrument/effet |
| `get_device_parameters(track, device)` | Lire les paramètres d'un device |
| `set_device_parameter(track, device, name, value)` | Modifier un paramètre |

### Scenes, Mixer, Projet

| Tool | Description |
|---|---|
| `create_scene(index)` / `fire_scene(index)` | Créer/lancer une scene |
| `set_track_volume(track, value)` | Volume piste (0.0–1.0) |
| `get_sends(track)` / `set_send(track, send, value)` | Envois |
| `set_monitoring(track, state)` | Monitoring (0=auto, 1=in, 2=off) |
| `freeze_track(index)` / `flatten_track(index)` | Freeze/flatten |
| `set_track_color(index, color)` / `set_clip_color(...)` | Couleurs (0–255) |
| `save_project()` | Sauvegarder (non dispo Live 12 Lite) |
| `undo()` / `redo()` | Annuler/rétablir |

## Structure du projet

```
 ableton-holland-mcp/
├── data/
│   ├── tests/             # Fichiers audio de test (.wav, .mp3)
│   ├── analyses/          # Résultats d'analyse (.wav + .csv)
│   └── scripts/           # Scripts utilitaires
├── dashboard/
│   └── app.py             # Interface graphique (Tkinter + matplotlib)
├── ableton_full_mcp_server.py    # Serveur MCP UNIFIÉ (Ableton + analyse)
├── AbletonMCP_Remote_Script.py   # Remote Script Ableton (à copier)
├── music_analysis_plus.py        # Serveur analyse standalone (legacy)
├── ableton_mcp_server.py         # Serveur Ableton standalone (legacy)
├── opencode.jsonc                # Configuration MCP
├── requirements.txt              # Dépendances Python
├── AGENTS.md
├── SPEC.md
├── .gitignore
└── README.md
```

## Écouter le monitoring audio

Quand Ableton envoie son audio vers VB-Cable → plus de son dans les enceintes. Solutions :

### Méthode 1 : Windows "Listen to this device"

1. **Panneau de configuration → Son → Enregistrement**
2. Double-clic sur **"CABLE Output (VB-Audio Virtual Cable)"**
3. Onglet **"Écouter"** → cocher **"Écouter ce périphérique"**
4. Choisir Focusrite / enceintes dans la liste déroulante
5. Appliquer

*Avantage* : sans logiciel supplémentaire. *Inconvénient* : léger décalage (latence WDM).

### Méthode 2 : Voicemeeter (recommandée)

Route l'audio d'Ableton vers plusieurs sorties simultanément.

#### Configuration

1. Lance **Voicemeeter**
2. **Hardware Out** (colonne de droite) :
   - **A1** → enceintes (Intel Display Audio, Focusrite...)
   - **A2** → **CABLE Input (VB-Audio Virtual Cable)**
3. **Virtual Input** → Ableton envoie sur **Voicemeeter VAIO**
4. Ajuste les volumes (A1 = ce que tu entends, A2 = niveau envoyé à la capture)

#### Routage final

```
Ableton → Voicemeeter VAIO → A1: Enceintes (monitoring)
                            → A2: CABLE Input → CABLE Output → capture
```

*Avantage* : monitoring temps réel, contrôle du mix, pas de latence supplémentaire.
*Remarque* : la capture MCP continue d'écouter sur **CABLE Output** — inchangé.

### Méthode 3 : Dashboard Python

Bouton **Playback** dans le dashboard après chaque capture :

```bash
python dashboard/app.py
```

### Méthode 4 : Console Python / MCP

```python
# Dans le dashboard
from dashboard.app import AudioAnalyzer
audio, sr = AudioAnalyzer.capture(device_id, duration)
AudioAnalyzer.save_audio(audio, sr, "mon_capture")

# Dans le serveur MCP
play_wav("data/analyses/mon_capture.wav")
```

## Dashboard graphique

Interface native Windows (Tkinter + matplotlib, zéro dépendance supplémentaire).

```bash
python dashboard/app.py
```

### Fonctionnalités

| Section | Contrôle |
|---|---|
| **Périphérique** | Menu déroulant pour choisir la source audio (CABLE Output, Focusrite...) |
| **Capture** | Spinbox durée (1-60s) + bouton **🎤 Capturer** |
| **Playback** | Bouton **🔊 Playback** pour réécouter la dernière capture |
| **Fichier** | **Parcourir** → sélection fichier dans `data/tests/` + **Analyser** |
| **Visualisation** | Chroma CQT (heatmap) + Waveform avec onsets (lignes rouges) |
| **Résultats** | Durée, tempo BPM, nombre d'onsets |

### Architecture du code

`dashboard/app.py` contient deux classes :
- **`AudioAnalyzer`** — capture (sounddevice), analyse (librosa), sauvegarde (soundfile)
- **`Dashboard`** — interface Tkinter, appelle `AudioAnalyzer` dans un thread séparé

## Prochaines étapes

### Itération 3 — Monitoring temps réel avec Voicemeeter ✅

- [x] Installer et configurer Voicemeeter
- [x] Router Ableton → Voicemeeter → enceintes (monitoring) + CABLE Input (capture)
- [x] Valider la capture MCP inchangée
- [x] Documenter le setup final

### Itération 4 — Analyse avancée

- [ ] Détection de la tonalité / key detection (`librosa.feature.tonnetz`)
- [ ] Analyse harmonique (accords)
- [ ] Détection de genre / voix

### Itération 5 — Améliorations pipeline

- [ ] Interface web Streamlit (dashboard plus riche, graphiques interactifs Plotly)
- [ ] Streaming continu (capture + analyse en boucle, metronome visuel)
- [ ] Whisper / transcription automatique des paroles (si voix)
- [ ] Export des résultats en JSON structuré

# A etudier 
- Customize Ableton Live with the Live API  https://www.youtube.com/watch?v=Hfq-NXEhmzs
- Ableton free packs https://www.ableton.com/en/packs/#?item_type=free
- Future Explorations. Voir pour combiener avec un VCVRack MCP  comme https://community.vcvrack.com/t/mcp-server-let-claude-cursor-build-and-control-your-rack-patches-live/25607
- autre MCP ableton : https://github.com/adamjmurray/producer-pal#readme
- https://github.com/uisato/ableton-mcp-extended


## Dépannage

### "CABLE Output not found"
→ Vérifier que VB-Cable est installé et qu'Ableton n'est pas en mode ASIO

### Capture silencieuse
→ Vérifier qu'Ableton joue bien sur la sortie "CABLE Input"
→ Vérifier que la piste n'est pas en mute/solo
→ Vérifier le volume Master

### Timeout MCP
→ Le serveur utilise `async def` + `await asyncio.sleep()` pour la capture
→ Si timeout : réduire la durée de capture ou vérifier les logs du serveur
- https://mcpcat.io/guides/fixing-mcp-error-32001-request-timeout/

### Device busy
→ Ableton est en mode ASIO. Passer en MME/DirectX dans les préférences Ableton

### Voicemeeter ne s'affiche pas dans Ableton
→ Redémarrer Voicemeeter et/ou Ableton. Vérifier que le service Voicemeeter est lancé (icône dans la barre des tâches).

### Pas de son dans les enceintes (Voicemeeter)
→ Vérifier que **A1** est bien assigné à un périphérique physique dans Voicemeeter
→ Vérifier le niveau du slider A1
→ Vérifier le bouton **Mute** sur la colonne Virtual Input

### Capture silencieuse avec Voicemeeter
→ Vérifier que **A2** pointe bien vers **CABLE Input**
→ Vérifier le niveau du slider A2
→ Vérifier que VB-Cable est installé

## Notes de version

### Itération 5 (28 juin 2026) — Serveur unifié + capture atomique
- **Serveur unifié** `ableton_full_mcp_server.py` (remplace `ableton-mcp` + `music-analysis`)
- **`capture_at_position(position, duration)`** — stop → switch → play at position → capture → stop → load
- **`capture_and_analyze(position, duration)`** — capture + analyse en un appel
- **Fix `start_playback_at`** : `start_playing()` PUIS `current_song_time = X` (Live reset le temps au démarrage)
- **Fix `load()`** : `np.mean(audio, axis=1)` au lieu de `librosa.to_mono()` (inversion canaux)
- Documentation mise à jour (README, AGENTS, SPEC)

### Itération 4 (24 juin 2026) — Remote Script arrangement
- Mise à jour du Remote Script Ableton (v1314 lignes) avec support Arrangement View
- Remote Script copié à la racine du projet (`AbletonMCP_Remote_Script.py`)
- Documentation de l'installation du Remote Script dans le README
- Commandes arrangement : `switch_to_arrangement_view`, `duplicate_to_arrangement`, `set_arrangement_time`, `get_arrangement_clips`

### Itération 3 (24 juin 2026) — Monitoring temps réel
- Voicemeeter installé et configuré (A1 = enceintes, A2 = CABLE Input)
- Monitoring en temps réel sans latence supplémentaire
- Documentation du routage Voicemeeter

### Itération 2 (24 juin 2026) — Stabilisation
- Capture sauvegardée dans `data/analyses/` avec timestamp
- Dashboard graphique Tkinter (capture, analyse, visualisation, playback)
- Documentation complète (README, requirements.txt, .gitignore)
- Export WAV + CSV organisé dans `data/`

### Itération 1 (20 juin 2026) — Première version
- Serveur MCP `music_analysis_plus.py` avec capture async
- Analyse tempo, chroma CQT, MFCC, beats
- Fix timeout MCP (`async def` + `await asyncio.sleep()`)

## Licence

MIT
