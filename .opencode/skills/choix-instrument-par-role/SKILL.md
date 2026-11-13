---
name: choix-instrument-par-role
description: Use when deciding which instrument or engine to load for a given musical role (bass, pad, lead, keys, plucks, texture). Covers the native-first decision order, the Drift preset families to reach for, the measured preset audition (5-6 candidates captured and scored, never chosen by name), the preset spectral index, when Simpler or Impulse is right, and when Surge XT is genuinely justified. Trigger words : quel instrument, quel son, auditionner, tester des presets, index des spectres, mesurer un preset, basse, nappe, pad, lead, pluck, texture, arpège, what sound, trouver un son.
---

# Choisir un instrument par rôle

## L'ordre de décision

1. **Drift** pour tout synthé. 12 familles de presets : Bass, Pad, Strings, Mallets, Synth Lead,
   Piano & Keys, Brass, Winds, Percussive, Guitar & Plucked, Synth Keys, Synth Rhythmic, Effects.
   C'est le multis de l'install — **je compose d'abord avec**.
2. **Kits `.adg`** pour la batterie.
3. **Simpler / Impulse** pour l'échantillonné (un sample réel, une nappe de texture).
4. **Surge XT** en dernier recours, une fois le morceau structuré avec du natif.

## Par rôle

| Rôle | Premier choix | Pourquoi |
|---|---|---|
| Basse | Drift, famille **Bass** | fondamentale + harmoniques, filtrable |
| Nappe / pad | Drift, **Pad** ; **Strings** pour un orchestre | tenue, contrôlée par le filtre |
| Lead | Drift, **Synth Lead** | une seule note doit porter une mélodie |
| Clavier | Drift, **Piano & Keys** | plucké ou tenu |
| Arpège | Drift, **Guitar & Plucked** ou **Mallets** | sustain court, percussif |
| Pluck | Drift → **Guitar & Plucked** | attaque nette, decay court |
| Texture | Drift → **Ambient & Evolving** / **Effects** | mouvement sans mélodie |
| Cuivres | Drift → **Brass** | attention, ça mange vite le CPU |
| Batterie | Kit `.adg` + Drum Rack | le kit joue déjà le GM |

## Ce qui n'est pas un device

Wavetable, Analog, Operator, Collision, Electric, Tension : **absents de cette install**. Je peux
charger un *son* de la famille, pas le synthé. Voir `palette-live-lite`.

## Trouver LE preset : on auditionne, on ne devine pas

⚠️ **Le nom d'un preset ne dit rien de son spectre.** Vérifié : « Basic Vintage Pluck » (nom qui
promet la chaleur) sortait à **24,6 %** d'énergie au-dessus de 10 kHz — pire que le « Snappy Pluck »
qu'on remplaçait (12 %). Choisir par le nom, c'est choisir au hasard.

### La procédure — 5 à 6 candidats, mesurés

1. **Lister la famille** : `get_browser_items({path: "sounds/<Catégorie>"})`
   — ex. `"sounds/Guitar & Plucked"`. ⚠️ La forme `query:Sounds#…` renvoie **0 item** : il faut
   `sounds/<Catégorie>` (minuscules, slash). Chaque item porte son URI de chargement.
2. **Garder 5-6 candidats** choisis **par le nom** — c'est tout ce que le nom permet : viser une
   direction, pas juger.
3. **Auditionner un par un** : `load_instrument_or_effect(track_index, uri)` →
   `set_track_solo(solo: true)` → `capture_and_analyze` (4-8 s) → `set_track_solo(solo: false)`.
   **Niveau inchangé pendant toute l'audition** (les presets n'ont pas le même niveau).
4. **Mesurer les WAV** avec `scripts/spect.py` — **jamais** le RMS du tool d'analyse : il normalise.
5. **Choisir**, puis le passage de timbre (section suivante), puis le niveau.

⚠️ **Jamais sur une piste du morceau.** `load_instrument_or_effect` **remplace** l'instrument en
place : un candidat testé = le son actuel détruit, sans retour. On auditionne sur une **piste de
banc d'essai** — ou, pour un A/B à l'oreille, sur des pistes temporaires portant le même clip
(`get_clip_notes` → `create_clip` + `add_notes_to_clip`).

### L'index des presets (version légère)

Chaque famille réellement utilisée alimente `preset_index/` : la réponse des presets à une **phrase
de test fixe**. Le protocole et la lecture des colonnes vivent dans `preset_index/README.md`.

- On le remplit **au fil de l'eau**, famille par famille, quand un rôle se présente. On ne balaie
  pas les 84 plucks ni les ~200 kits d'avance.
- Il **shortliste 3 candidats sans rien charger** (donc sans rien casser) et rend le choix
  reproductible pour la fiche technique.
- Il ne décide pas : « musical » n'est pas dans les chiffres. Et il mesure le preset **sec** — le
  point de départ, pas le son sculpté.

## Après le chargement : sculpter — ⚠️ réflexe automatique

**Un preset brut n'est pas un son fini, et ça s'entend immédiatement comme une maquette.** Dès que
l'instrument est posé — ou dès que j'écris des notes dessus — je fais le passage de timbre **avant**
de présenter quoi que ce soit. Ce n'est pas une option. C'est l'étape 3 de la boucle de
`maquette-scene-par-scene`.

1. `get_device_parameters(track_index, device_index)` — je lis ce qui est exposé. Beaucoup de synthés
   natifs ont des **macros internes à 0** qui servent exactement à ça (Over Tone, Tone, Distort sur
   Basic Sub Sine). Les familles Drift exposent aussi Filtre, Réso, Enveloppe, Space, Thick, Clip.
2. Je cible en priorité les tueurs de « bas de gamme » : **résonance haute** (criard),
   **Noise Gain** élevé (grésillant), **filtre trop ouvert** (aigre) ou **trop fermé** (bouché),
   **enveloppe** inadaptée au rôle.
3. Puis l'espace : envois vers les retours Reverb / Delay (voir `reverb-insert`), plutôt que de
   laisser la source sèche et collée.
4. FX, en partant d'un **état transparent** (voir `sculpture-sonore`).
5. Recapturer et itérer.

## Surge : seulement si justifié

Une instance Surge se configure **à la main** (Settings > OSC) : instance *n* sur le port
`53280 + 2n`. Un patch plus « chaud » que la référence : **drive, unison, filter**. Le mixer mute
(0 = actif) permet de découvrir des oscillateurs masqués et d'ajouter une couche d'octave pour le
téléphone.

Mais chaque instance est du CPU. **Je structure le morceau avec du natif d'abord**, et je vérifie
le coût avant d'ajouter Surge. Voir `surge-cpu-par-voix`.
