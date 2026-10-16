---
name: project-setup
description: Use when setting up or re-installing this Ableton Holland production environment from scratch, or when a piece of the installation is broken (VB-Cable, Voicemeeter, the Remote Script, the venv, Surge XT OSC). Covers the full install: venv, Python dependencies, Voicemeeter/VB-Cable routing, the Remote Script deploy, and Surge XT OSC. Trigger words : installer, réinstaller, setup, venv, dépendances, VB-Cable, Voicemeeter, Remote Script, déploiement, machine neuve, installation.
version: "1.0.0"
category: "devops"
tags: [setup, venv, dependencies, voicemeeter, vb-cable, remote-script, surge-osc]
complexity: intermediate
risk: safe
tools: [opencode, python]
source: community
author: ableton-holland
date_added: 2025-01-15
date_updated: 2025-09-06
---
# Project Setup

## Overview

Installation complète de l'environnement Ableton Holland MCP : venv Python, dépendances, Voicemeeter/VB-Cable pour la capture audio, Remote Script déployé dans Ableton, et Surge XT OSC. À suivre sur une nouvelle machine ou après une réinstallation.

## When to Use

- Sur une nouvelle machine — initialiser venv + dépendances + Voicemeeter
- Pour déployer le Remote Script Ableton (dossier MIDI Remote Scripts)
- Pour configurer Surge XT OSC (ports, multi-instances)
- Pour vérifier qu'un server MCP tourne (`get_session_info()` doit répondre)

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
