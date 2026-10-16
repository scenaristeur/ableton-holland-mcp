---
name: organisation-fichiers-projet
description: Use when generating any file during a production session — a script, a JSON, a capture, a report — and when deciding where to save it. Covers the tmp/ folder for throwaway artifacts, the scripts/ folder for reusable tools, the gitignore rule, and where song-specific prep scripts belong. Trigger words : dossier, ranger, classer, tmp, scripts, où je range, fichier généré, artefact, rangement, organiser les fichiers.
---

# Organisation des fichiers du projet

Trois zones, décidées selon la nature du fichier. **Rien ne reste à la racine sauf l'infra.**

## 1. `tmp/` — jetable

Tout ce qui est généré et ne sert qu'à une session, ou qui est régénérable.

- JSON intermédiaires (`clip_plan.json`, `_scenes_notes.json` en cours de travail),
- captures brutes (WAV, CSV), logs, rapports jetables.

**`tmp/` est gitignoré.** Rien de ce qui s'y trouve n'est suivi par git — je n'y mets jamais une
donnée qui doit survivre.

## 2. `scripts/` — outils réutilisables

Tout script ou outil qui peut servir **à nouveau**, pour un autre morceau ou une autre tâche.

- les preprocesseurs de remake génériques (`prep_midi.py`),
- la capture et l'analyse (`capture_audio.py`, `capture_wasapi.py`, `music_analysis_plus.py`),
- les helpers d'injection (`inject_scene.py`, `rs_arrange.py`, `rs_create_clips.py`),
- les tests (`test_*.py`), les outils d'aide (`list_kits.py`).

Ce qui est suivi par git et peut être réutilisé va dans `scripts/`.

## 3. `sources/<Album>/NN - Titre/` — la mémoire du morceau

Les scripts **spécifiques à un morceau** (`prep_keep_talking.py`, `prep_mona_ia.py`,
`prep_anycolour_group.py`, `verify_mona_ia.py`, `diff_notes.py`, `arrange_loops.py`) :

- ils décrivent un morceau précis, pas une méthode,
- `sources/` est **gitignoré** : les y déplacer les sort de git.

⚠️ **Je ne les déplace pas de moi-même dans `sources/`.** C'est un arbitrage à David : un script
song-specific perd son historique git s'il passe dans `sources/`. Tant que David n'a pas décidé, ils
restent dans `scripts/`, où ils importent correctement leurs voisins.

## La règle d'import

Un script de `scripts/` qui importe un voisin (`import prep_mona_ia`, `import prep_midi`) marche
**si les deux sont dans le même dossier** — Python ajoute le dossier du script au chemin. Donc je
ne sépare jamais deux scripts qui s'importent mutuellement, et je ne les lance pas depuis la racine
en comptant sur un import de la racine.

## Ce qui ne bouge pas

À la racine : les serveurs MCP (`ableton_full_mcp_server.py`, `surge_osc_mcp.py`), le Remote Script
(`AbletonMCP_Remote_Script.py`), le déploiement (`deploy_rs.py`), les mappings contrôleur
(`midi_mappings*.py`), la config (`opencode.jsonc`, `requirements.txt`), les docs.

Le déploiement suppose un chemin stable — je ne le déplace pas.

## Quand je génère

1. **Je décide du dossier avant d'écrire.** Si jetable → `tmp/`. Si réutilisable → `scripts/`.
2. **Je nomme clairement.** Un fichier généré porte le nom de ce qu'il contient.
3. **Je mets à jour les skills concernés** si le nouveau script change la méthode.
4. **Je ne laisse pas d'accumulation.** Ce qui ne sert plus, je le signale à David, je ne le
   supprime pas de moi-même.

## Un artefact hors de `sources/` ? je le signale

Si une donnée song-specific traîne dans `tmp/` ou `scripts/`, je le signale à David et je propose
de la replacer — je ne la déplace pas seul. Voir `fiche-technique` pour ce qui relève du morceau.