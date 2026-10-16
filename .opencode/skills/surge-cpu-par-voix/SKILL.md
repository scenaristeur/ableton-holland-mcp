---
name: surge-cpu-par-voix
description: Use when Surge XT is loaded on a track, when CPU is too high, or when a Surge patch sounds thin on a phone. Covers that Surge cost is per-voice (oscillators and unison, not max polyphony), that lowering polyphony alone does nothing, the OSC port scheme, the mixer mute trick to find hidden oscillators, and the drive/unison/filter recipe for a warmer patch. Trigger words : Surge, Surge XT, CPU, polyphonie, oscillateur, unison, drive, patch chaud, instance, port OSC.
---

# Surge XT : coût et réglage

## Le coût est par voix

Le coût CPU de Surge est fonction du **nombre d'oscillateurs et de l'unison du patch**, *pas* de la
polyphonie maximale.

Conséquence importante : **baisser la polyphonie max ne sert à rien.** Un patch lourd avec
polyphonie 8 coûte exactement ce qu'il coûte avec polyphonie 128. Ce qui coûte, c'est le nombre de
voix **réellement jouées** en même temps, et donc l'unison de chaque voix.

## Pour alléger

- **Changer de patch plus léger.** C'est la seule chose qui marche vraiment.
- **Réduire l'unison**, pas la polyphonie.
- **Couper des oscillateurs** dans le mixer.
- **Désactiver le device** quand la piste ne joue pas.
- **Geler** la piste, en sachant qu'on perd l'édition. Voir `diagnostic-cpu`.

## Le mixer mute (0 = actif)

Chaque oscillateur a un paramètre de volume dans le mixer. **0 = actif** dans le mixer de Surge — le
contraire de la convention Ableton.

C'est utile pour **découvrir des oscillateurs masqués** : un patch peut sonner mince alors qu'un
deuxième oscillateur existe et est éteint. Je le révèle, et je peux ajouter une **couche d'octave**
qui sert précisément au téléphone. Voir `mix-translation`.

## Le port OSC

Chaque instance se configure **à la main** dans Surge (Settings > OSC) : l'instance *n* sur le
port `53280 + 2n`.

- instance 0 → 53280
- instance 1 → 53282

Sans ça, je parle à la mauvaise instance et je pense modifier un patch que je n'ai pas sous les
yeux.

## Patch plus chaud

Pour un son « chaud », les trois leviers qui comptent :

1. **drive** — pushes l'harmonique, c'est le même principe que le saturateur sur la basse.
2. **unison** — de la largeur et du corps.
3. **filter** — contrôle le timbre. C'est le paramètre le plus musical des trois.

Mais chaque instance est du CPU. **Je structure le morceau avec du natif d'abord**, et je ne passe
à Surge que pour une couleur qu'aucun preset Drift ne donne. Voir `choix-instrument-par-role`.

## Réduire : les gains réels

Validation terrain (« Melody's Ghost ») : un patch saturant à ~100 % de CPU (`House Organ`)
retombe à **~40-46 %** en passant à `Organ 1` avec une polyphonie de **8/6**. C'est le meilleur
levier : **changer de patch**, pas râler sur la polyphonie.

## `fx/chain_bypass` : 1 vs 3

Le paramètre `fx/chain_bypass` de Surge a deux valeurs utiles, faciles à confondre :

| Valeur | Effet |
|---|---|
| `1` | **No Send FX** seulement — coupe seulement le bus d'envoi FX |
| `3` | **All FX Off** — coupe tout le chain FX |

⚠️ Pour vraiment vider le chain FX : `3`, **puis vider les slots**. Et **recharger un patch
réinstancie le chain** — il faut re-appliquer après chaque `surge_load_patch`.

## Tweaking analogique

Pour un son moins « numérique », un tableau qui marche (à ajuster à l'oreille) :

| Adresse | Plage |
|---|---|
| `osc/drift` | `0.05-0.2` |
| `osc/<n>/param6` (detune) | variable |
| `osc/<n>/param7` (voices) | variable |
| `amp/width` | variable |
| `waveshaper/drive` | `0-0.4` |
| `amp/vel_to_gain` | variable |

## ⚠️ Le piège du `play_mode`

Pour un lead mono silencieux au repos :

- **mode 5** (Mono single trigger & legato) laisse une **note fantôme → bourdon**.
- **mode 4** est le bon choix pour un lead mono qui ne résonne pas par-dessus.

Je ne pose pas un lead mono en mode 5 sans vérifier.
