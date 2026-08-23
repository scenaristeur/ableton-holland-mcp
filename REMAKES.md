# REMAKES.md — Refaire un .mid en arrangement Live Lite

Checklist de capitalisation, validée sur « Keep Talking » (Pink Floyd). Pour TOUT nouveau remake
à partir d'un fichier `.mid`. Complète AGENTS.md et la skill `midi-remake`.

## Rappel rapide
- Server : `ableton_full_mcp_server.py` (+ Remote Script `AbletonMCP_Remote_Script.py`, port 9877).
- Utils : `prep_<song>.py` (découpage+remap drum+dédup), `inject_scene.py SCENE ATRACK`.
- Skills : `midi-remake`, `scene-workflow`, `full-mix-workflow`, `surge-osc`, `mix-translation`.

## Pièges (à lire AVANT de commencer)
| # | Piège | Solution |
|---|-------|----------|
| 1 | `add_notes_to_clip` champ = **`start_time`** (pas `start`) | sinon notes empilées à 0 |
| 2 | Fusion à l'unisson = doublons (loude/phasé) | dédupliquer via `prep_<song>.py` |
| 3 | Kit drum ≠ mappage GM source | remapper pitches (DRUM_PITCH_MAP) |
| 4 | CPU : mute ≠ désactive ; freeze bloque l'édition | `disable_device` / freezer ; dégeler pour éditer |
| 5 | Automation de device sur arrangement peu fiable | tester ; ou enveloppe sur clip session / Auto Filter |
| 6 | `destination_bar` off-by-one | `duplicate_to_arrangement` avec `destination_time` (beats) |
| 7 | Paramètres de plugin VST = mappings non vérifiés | tester par petites valeurs mesurées |
| 8 | Surge reload patch = perd l'architecture | re-approuver mute/vol/LFO, noter les tweaks |
| 9 | Basse trop grave < 70 Hz = inaudible | ancrer en E2 (~82 Hz) / saturateur, pas transposition aveugle |

## Étapes (résumé)
1. Analyser le .mid (mido) : pistes, tempo, signature, durée. Choisir la source la plus nommée.
2. Découper en sections (frontières par silences/entrées instrumentales). 1 scène = 1 section.
3. Fusionner en ≤8 pistes (familles). 1 piste = 1 instrument.
4. `prep_<song>.py` → `_scenes_notes.json` (dédup + remap drum + vélos source).
5. `create_clip(track, slot, length_beats)` (4/4 : 1 bar = 4 beats).
6. `add_notes_to_clip` (⚠️ `start_time`). Gros volumes → `inject_scene.py`.
7. Nommer les clips.
8. Tweak instrus AVANT capture (FX natifs, analyse solo track par track).
9. `duplicate_to_arrangement(..., destination_time)` vers l'arrangement.
10. Capture + analyse (RMS/centroid/rolloff/DR) par section, ajuster.
11. Validation utilisateur.
12. Mix final (`full-mix-workflow`) + master glue+limiter.
13. Vérifier sur smartphone + grosses enceintes (`mix-translation`).

## Factorisation — TOUS les instruments (métaphore groove + fills)
**Pas seulement la batterie.** Clavier/arpège, slide guitare, basse, guitare rythmique ont des
motifs répétitifs bouclables.

- `prep_<song>.py`/`prep_anycolour_group.py` analyse PAR PISTE et PAR SCÈNE : nb de patterns,
  `top xN` (mesure la plus répétée).
- **`top x>=3` → FACTORISER** : clip **groove court bouclé (1-4 mesures)** + **fills de transition**
  aux frontières. EX: keyboard x17, slide guit x12, basse x4 → accord/arpège bouclé.
- `top x1-2` + beaucoup de patterns → variations (clips longue section ok).
- Le plan `REMAKES_PLAN.md` indique par scène/piste quelles pistes factoriser.
- Placer le groove dans l'arrangement, **étendre la boucle dans l'UI** (Loop + drag).

## Par piste, les chaînes types testées (à adapter)
- **Batterie** : kit natif Selector Kit Warm (FileId_5282) + DrBuss Drive/Boom/Comp macros + pads réglés.
- **Basse** : Electric Bass Soft + Saturator Bass Shaper + glue parallèle.
- **Nappes** : Warm Analog Pad + Reverb + Auto Filter (mouvement).
- **Lead** : Surge XT (patch lead) + Delay ping-pong.
- **Claviers** : Surge XT (EP) + EQ + Saturator (à doser, le "caissette" est un piège fréquent).
- **Voix/talkbox** : Surge XT (patch voix/talkbox) sur une piste dédiée.

## Rappels Live Lite
- 8 pistes max, 16 slots. Pas d'EQ Eight (→ EQ Three), pas de Glue (→ Compressor).
- Pas de save_project() → **Ctrl+S manuel**.
- Dégeler pour éditer ; désactiver le device pour baisser le CPU.

## Fichiers utiles pour ce projet
- Fiche (état complet) : `sources/Reprises/Keep Talking/fiche_technique.md`
- Description + clip : `sources/Reprises/Keep Talking/description_youtube_soundcloud.md`,
  `prompt_clip_video*.md`, `analyse_morceau_clip.md`
