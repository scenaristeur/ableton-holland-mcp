---
name: project-setup
description: Installation complète du projet Ableton Holland MCP — venv, dépendances, Voicemeeter/VB-Cable, Remote Script, Surge XT OSC.
---

# Project Setup

## Prérequis

- Python 3.10+
- Ableton Live 12 Lite (ou supérieur)
- Surge XT (VST3) — optionnel
- Voicemeeter Banana + VB-Cable (pour capture audio)

## Installation

```bash
# Cloner le projet
git clone <repo> ableton-holland-mcp
cd ableton-holland-mcp

# Créer le venv et installer les dépendances
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
```

## Voicemeeter / VB-Cable

1. Installer Voicemeeter Banana (gratuit)
2. Installer VB-Cable (gratuit)
3. Configurer le routage :
   ```
   Ableton → Voicemeeter VAIO → A1: Enceintes (monitoring)
                               → A2: CABLE Input → CABLE Output → capture
   ```
4. Dans Ableton : Options → Préférences → Audio → Output Device = "Voicemeeter VAIO"
5. Buffer : 1024 samples

## Remote Script Installation

1. Copier `AbletonMCP_Remote_Script.py` (renommé `__init__.py`) vers :
   ```
   C:\ProgramData\Ableton\Live XX\Resources\MIDI Remote Scripts\AbletonMCP\__init__.py
   ```
2. Dans Ableton : Options → Préférences → Link, Tempo & MIDI
3. Control Surface = "AbletonMCP", Input/Output = "None"
4. Déploiement rapide : `python deploy_rs.py`

## Surge XT OSC

1. Installer Surge XT (VST3)
2. Charger Surge XT dans Ableton sur une piste MIDI
3. Menu Surge (top-left) → Settings → OSC → Enable
4. Ports par défaut : IN=53280, OUT=53281
5. Multi-instances : stride=2 (instance 1 = 53282/53283, etc.)
6. Max 8 instances

## Lancement

```bash
.venv/Scripts/python ableton_full_mcp_server.py    # Server Ableton
.venv/Scripts/python surge_osc_mcp.py               # Server Surge XT (optionnel)
```

## Premiers pas

1. Lancer Ableton (une session doit être ouverte)
2. Lancer le serveur MCP
3. Tester : `get_session_info()` doit retourner le tempo, signature, track_count
4. Si timeout : attendre ~60s (premier démarrage), réessayer
5. Si capture silencieuse : redémarrer le serveur (CABLE_DEVICE_ID périmé)
