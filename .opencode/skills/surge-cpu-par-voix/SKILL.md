---
name: surge-cpu-par-voix
description: Use when Surge XT is loaded on a track, when CPU is too high, when a Surge patch sounds thin on a phone, or when I build a two-timbre Surge patch (scene A/B, Dual, split by velocity). Covers that Surge cost is per-voice (oscillators and unison, not max polyphony), that lowering polyphony alone does nothing, the OSC port scheme (activated by David), the mixer mute trick to find hidden oscillators, the drive/unison/filter recipe, and the verified rules for loading into a scene and splitting by velocity. Trigger words : Surge, Surge XT, CPU, polyphonie, oscillateur, unison, drive, patch chaud, instance, port OSC, scène, Dual, split, vélocité.
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

### ⚠️⚠️ RÈGLE DURE : JE NE PEUX PAS ACTIVER L'OSC

**Je n'ai aucun moyen d'activer l'OSC moi-même.** Ni par un outil MCP, ni par une action dans
Ableton, ni par un fichier de config. Le serveur OSC de Surge XT s'allume **uniquement à la main,
dans l'interface de Surge** (Settings > OSC), par **David**.

Donc, à chaque fois que je veux utiliser une instance de Surge XT :

1. **Je vérifie d'abord** que l'OSC de cette instance répond (voir le test ci-dessous).
2. **S'il ne répond pas, je demande à David de l'activer pour CETTE instance**, en nommant la
   piste et le numéro d'instance / port attendu. Et **j'attends sa réponse** avant de continuer.
3. **Je ne contourne jamais** : pas de « je laisse Surge sur son patch d'init », pas de bascule
   silencieuse vers un autre device, pas d'essai de port au hasard. Un Surge muet au milieu d'une
   scène est un défaut de production, pas un détail.

**Une activation = une instance.** Une instance déjà activée ne vaut pas pour la suivante. Si je
prévois deux instances, je demande les deux d'un coup, en une seule question (instance 0 → 53280,
instance 1 → 53282). Voir `surge-presets`.

### Le test qui prouve que l'OSC répond (et celui qui ne prouve rien)

⚠️ **Piège vérifié le 06/11/2026** : `surge_list_categories`, `surge_search_patches`,
`surge_list_patches` et `surge_load_patch` **répondent toujours**, même quand l'OSC est mort —
ils lisent le disque, pas le plugin. Ils ne prouvent donc **rien**.

Les deux seuls appels qui prouvent la connexion :

| Appel | OSC vivant | OSC mort |
|---|---|---|
| `surge_get_patch(instance=n)` | `{"patch": "<nom>"}` | `{"patch": "unknown"}` |
| `surge_query_all(instance=n)` | des centaines de paramètres | `null` |

Un `surge_load_patch` qui renvoie `{"patch": "unknown"}` signifie que **le patch n'a pas été
chargé** : l'instance joue son patch d'init. Je ne le laisse pas dans cet état.

## Scènes A/B, mode Dual, split par vélocité

Surge XT a **deux scènes** (A et B), chacune avec ses oscillateurs, filtres, enveloppes et matrice
de modulation. `/param/global/scene_mode` : `0` = Single, `2` = Dual (vérifié à l'affichage) ;
`1` = Key split, `3` = Channel split.

### Charger un patch n'atteint que la scène A

Vérifié : après `surge_load_patch`, **c'est toujours la scène A qui reçoit le patch**, même après
avoir mis `/param/global/active_scene` à 1. La scène B garde intégralement son contenu précédent.

Et **le chargement remet `scene_mode` à 0** (Single). Donc l'ordre est : je charge d'abord, je
pose `scene_mode = 2` **après** le dernier chargement.

Et recharger un patch **relose les mutes** (osc2/osc3, noise, rm1x2, rm2x3) — cf. la section mixer
mute plus haut. Je les réactive après chaque chargement.

### Copier une scène A vers une scène B

C'est le seul moyen de mettre **deux presets différents** dans les deux scènes :

1. `surge_query_all` → je garde tous les `/param/a/*` (191 params ; j'ignore les modificateurs
   `.../abs+`, `.../enable+`, `.../extend+`, `.../deform+`, `.../tempo_sync+`).
2. je charge le patch voulu dans la scène A,
3. je rejoue l'instantané sur `/param/b/<même suffixe>` — 191 `surge_set_param`, ~24 s,
4. `scene_mode = 2`.

Vérifié : scène A = `Bagpipes` (osc Twist, filtre FX Comb, aeg tenue) **et** scène B =
`Hammered Dulcimer` (3 osc String, HP OB-Xd 12 dB) dans le même patch.

### L'échelle de `amp/volume` est logarithmique

`dB ≈ 59.8 × log10(valeur)` — vérifié sur plusieurs patches :

| valeur | dB |
|---|---|
| 0.10 | -59.8 |
| 0.50 | -18.0 |
| 0.85 | -4.2 |
| 1.00 | 0 |

Un timbre réglé à 0.10 est donc **55 dB** plus faible qu'un timbre à 0.85. C'est là que se joue
l'équilibre entre deux scènes — pas dans une comparaison de valeurs brutes.

### ⚠️ `amp/vel_to_gain` est INVERSÉ

C'est le piège qui m'a coûté le plus de captures. Le paramètre n'est **pas** une quantité de
vélocité à ajouter : c'est une **atténuation en dB**, et elle va dans le sens inverse de ce qu'on
croit.

| valeur | affichage | effet |
|---|---|---|
| 0.0 | -48.00 dB | les vélocités basses sont **écrasées** |
| 0.5 | -24.00 dB | moitié de l'écrasement |
| 1.0 | 0.00 dB | **aucun effet** de la vélocité sur le gain |

**Pour que la vélocité n'agisse pas sur le gain, je mets 1.0.** Mettre 0 (par réflexe « pas
d'effet de vélocité ») écrase les notes douces de 40 dB : mesuré, un arpège en v42 est passé de
-5 dBFS à -42 dBFS, invisible, alors que le reste du patch ne changeait pas.

### ⚠️ Le sustain de l'enveloppe est aussi en dB

`aeg/sustain` = 0.85 n'est pas « presque 1 » : le gain est en dB. Mesuré, **S 0.5 → S 1.0 vaut
~12 dB**. Une enveloppe « pluck » avec un sustain à 0.5 est donc beaucoup plus faible qu'elle n'en
a l'air, et c'est là que se joue le niveau d'un timbre percussif.

### ⚠️ Le drive du waveshaper : 0.5 = unity

`waveshaper/drive` vaut **0 dB à 0.5**. En dessous, il **atténue** au lieu de saturer : drive 0.25
= -12 dB. Je ne descends jamais sous 0.5 sauf volonté d'atténuation.

### Les leviers de gain quand une scène est trop faible

Par ordre de risque :

1. **`osc/<n>/param7` = Unison Voices.** Sur l'osc String : 0.575 → 15 %, 0.75 → 50 %. +3 à 6 dB
   avec un peu de largeur. Surveiller le CPU (le coût est par voix).
2. **`waveshaper/drive`** : 0.55 → +2.4 dB, 0.65 → +7 dB, avec de la saturation.
3. **`amp/volume`** : jusqu'à 1.0 (0 dB) seulement. C'est un plafond.
4. Les niveaux de mixer : ils plafonnent aussi à 1.0 (0 dB).

Quand une scène est **structurellement** plus faible qu'une autre — j'ai mesuré **40 dB** entre le
patch Bagpipes (avec ses filtres à peigne très résonnants) et le Hammered Dulcimer, qui n'a que
15 % d'unison — le rattrapage se fait en descendant la scène forte, pas en poussant la faible.

### Le split par vélocité, et son piège

La source `vel` est **globale** : elle pilote n'importe quelle scène. Un LFO de scène, lui, ne peut
piloter que sa propre scène.

```python
surge_map_modulation(mod_source="vel",           target="/param/a/amp/volume",    depth=+0.80)
surge_map_modulation(mod_source="a/vlfo_1/0",    target="/param/a/osc/1/pitch",   depth=0.02)
surge_map_modulation(mod_source="macro_1",       target="/param/a/filter/1/cutoff", depth=0.25)
```

⚠️ **Piège majeur** : parce que `amp/volume` est logarithmique, une modulation *linéaire* de la
vélocité crée des **écarts de niveau énormes** entre deux sections. Mesuré sur l'intro : un arpège
en v42 sortait à RMS 0.006 (-44 dBFS) pendant qu'une mélodie en v118 sortait à RMS 0.43 avec
**clipping permanent** — 35 dB d'écart, et un groupe de mesures entièrement muet entre les deux.

**Des groupes de mesures à vélocités très différentes sonnent très différemment.** C'est un fait
de production, pas un réglage : si je veux des sections homogènes, je garde les vélocités dans une
plage serrée, ou je compense.

La parade :

- garder les deux bases **dans la même zone** (0.5-0.7), pour que l'écart entre les deux timbres
  reste ≤ 8-12 dB ;
- viser une **balance en dB**, pas une égalité de paramètre ;
- `amp/vel_to_gain` ajoute une **seconde** couche de vélocité → je le mets à 0 quand je pilote le
  split moi-même ;
- **mesurer chaque section dans la même capture** : c'est la seule façon de voir l'écart.

Voir `velocites-et-dynamique` pour les plages de vélocité par rôle.

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
