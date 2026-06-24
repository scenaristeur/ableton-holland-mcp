# Ableton Holland MCP

Capture audio en direct depuis **Ableton Live** via **VB-Cable** et analyse musicale automatique avec **librosa**.

## Architecture

```
┌─────────────────┐     VB-Cable      ┌──────────────────┐
│  Ableton Live   │────Audio Out────▶│  CABLE Input     │
│  (audio engine) │                  │  (Virtual Cable) │
└────────┬────────┘                  └────────┬─────────┘
         │                                    │
         │  Monitoring                        ▼
         │  (Voicemeeter /              ┌──────────────────┐
         │   Windows Listen)            │  CABLE Output    │
         ▼                              │  (capture here)  │
   ┌──────────┐                         └────────┬─────────┘
   │ Focusrite│                                   │
   │ Speakers │                          ┌────────┴────────┐
   └──────────┘                          ▼                 ▼
                                  ┌────────────┐   ┌──────────────┐
                                  │ MCP server │   │  Dashboard   │
                                  │ (opencode) │   │  (Tkinter)   │
                                  └──────┬─────┘   └──────┬───────┘
                                         │                │
                                         ▼                ▼
                                   ┌──────────────────────────┐
                                   │      librosa (analyse)   │
                                   └────────────┬─────────────┘
                                                │
                                                ▼
                                   ┌──────────────────────┐
                                   │   data/analyses/     │
                                   │   (.wav + .csv)      │
                                   └──────────────────────┘
```

## Prérequis

| Logiciel | Rôle |
|---|---|
| [Ableton Live](https://www.ableton.com) 11+ | Station audio |
| [VB-Cable](https://vb-audio.com/Cable/) | Routage audio virtuel |
| Python 3.12+ | Moteur d'analyse |
| [opencode](https://opencode.ai) | CLI agent MCP |

## Installation

### 1. VB-Cable

1. Télécharger depuis [vb-audio.com/Cable](https://vb-audio.com/Cable/)
2. Lancer `VBCABLE_Setup.exe` en administrateur
3. Redémarrer Windows

### 2. Python

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configuration Ableton Live

1. **Options → Preferences → Audio**
2. Driver Type: **MME / DirectX** (pas ASIO — sinon VB-Cable est bloqué en exclusif)
3. Audio Output Device: **CABLE Input (VB-Audio Virtual Cable)**
4. Audio Input Device: **CABLE Output (VB-Audio Virtual Cable)** (optionnel)
5. Activer **"In/Out"** dans la vue Session

### 4. Configuration opencode

```json
{
  "mcp": {
    "ableton-mcp": {
      "type": "local",
      "command": ["uvx", "ableton-mcp"],
      "enabled": true
    },
    "music-analysis": {
      "type": "local",
      "command": [".venv/Scripts/python", "music_analysis_plus.py"],
      "enabled": true
    }
  }
}
```

## Outils MCP disponibles

### Capture audio

| Tool | Description |
|---|---|
| `capture_ableton(duration=5, output_name=None)` | Capture l'audio depuis Ableton via VB-Cable (sauvegarde dans `data/analyses/`) |
| `capture_and_tempo(duration=5)` | Capture + estimation du tempo |
| `capture_and_analyze(duration=5)` | Capture + analyse complète (tempo, beats, chroma, MFCC) |
| `play_audio(audio, sr)` | Joue un tableau numpy sur le périphérique par défaut |
| `play_wav(path)` | Joue un fichier WAV sur le périphérique par défaut |

### Analyse (fichier existant)

| Tool | Description |
|---|---|
| `load(file_path)` | Charge un fichier audio |
| `tempo(y_path)` | Estime le BPM |
| `beat_track(y_path)` | Détecte les temps forts |
| `chroma_cqt(y_path)` | Contenu chromatique (12 notes) |
| `mfcc(y_path)` | Timbre / texture spectrale |
| `get_duration(y_path)` | Durée en secondes |

### Ableton (via `ableton-mcp`)

| Tool | Description |
|---|---|
| `get_session_info()` | Infos session (tempo, tracks) |
| `get_track_info(index)` | Détails d'une piste |
| `create_midi_track(index)` | Nouvelle piste MIDI |
| `set_track_name(index, name)` | Renommer une piste |
| `create_clip(track, slot, length)` | Nouveau clip MIDI |
| `add_notes_to_clip(track, slot, notes)` | Ajouter des notes |
| `fire_clip(track, slot)` | Lancer un clip |
| `load_instrument(track, uri)` | Charger un instrument |

## Structure du projet

```
ableton-holland-mcp/
├── data/
│   ├── tests/             # Fichiers audio de test (.wav, .mp3)
│   └── analyses/          # Résultats d'analyse (.wav + .csv)
├── dashboard/
│   └── app.py             # Interface graphique (Tkinter + matplotlib)
├── music_analysis_plus.py # Serveur MCP personnalisé (capture + analyse)
├── capture_audio.py       # Script capture simple (sounddevice, legacy)
├── requirements.txt       # Dépendances Python
├── opencode.jsonc         # Configuration MCP pour opencode
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

### Méthode 2 : Voicemeeter (VB-Audio)

Installé séparément. Permet de router l'audio simultanément vers plusieurs sorties (Focusrite + CABLE Input) avec contrôle du mix.

```bash
# Configuration à venir après installation et redémarrage
```

*Avantage* : monitoring en temps réel, contrôle du volume, latence configurable.

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

### Itération 3 — Monitoring temps réel avec Voicemeeter

- [ ] Configurer Voicemeeter pour router Ableton → Focusrite (monitoring) + CABLE Input (capture)
- [ ] Adapter la capture MCP pour fonctionner avec ou sans Voicemeeter
- [ ] Documenter le setup final

### Itération 4 — Analyse avancée

- [ ] Détection de la tonalité / key detection (`librosa.feature.tonnetz`)
- [ ] Analyse harmonique (accords)
- [ ] Détection de genre / voix

### Itération 5 — Améliorations pipeline

- [ ] Interface web Streamlit (dashboard plus riche, graphiques interactifs Plotly)
- [ ] Streaming continu (capture + analyse en boucle, metronome visuel)
- [ ] Whisper / transcription automatique des paroles (si voix)
- [ ] Export des résultats en JSON structuré

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

### Device busy
→ Ableton est en mode ASIO. Passer en MME/DirectX dans les préférences Ableton

## Notes de version

### Itération 2 (24 juin 2026) — Stabilisation
- Capture sauvegardée dans `data/analyses/` avec timestamp
- Dashboard graphique Tkinter (capture, analyse, visualisation, playback)
- Documentation complète (README, requirements.txt, .gitignore)
- Monitoring audio : Windows Listen + Voicemeeter (en cours)
- Export WAV + CSV organisé dans `data/`

### Itération 1 (20 juin 2026) — Première version
- Serveur MCP `music_analysis_plus.py` avec capture async
- Analyse tempo, chroma CQT, MFCC, beats
- Fix timeout MCP (`async def` + `await asyncio.sleep()`)

## Licence

MIT
