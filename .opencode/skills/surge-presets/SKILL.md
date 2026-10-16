---
name: surge-presets
description: Use when looking for a reproducible Surge XT patch by name, or when a Surge sound needs to be recreated exactly later. Covers searching patches by name, loading by absolute path without extension, and the two index files (factory and third-party). Trigger words : preset Surge, patch Surge, trouver un son, search_patches, load_patch, reproductible, factory, patches_factory.
---

# Presets Surge reproductibles

## Sources de patches reproductibles

| Source | Type |
|---|---|
| **Syntorial — Preset Recipes** | recettes pas-à-pas avec valeurs en pourcentage |
| **Jon Audio — « Can it analog? » (2023)** | recette de lead analogique : saw classique + 3 voix d'unison + filtre Vintage Ladder + FEG |
| **Idle Thoughts Music — Surge XT Oscillator Tutorial (2022)** | les 13 oscillateurs, leurs types, unison, sub, filtres |
| **Surge User Manual** | documentation officielle |
| **John Valentine — Surge patches** | patches d'auteur : trombone, trumpet, french horn, cuivres |
| **Surge XT forums** | recherche « Surge XT <instrument> patch » |

## Les patches à essayer en priorité

Ce sont des **candidats**, souvent multi-oscillateurs et gras.

### Leads

| Patch | Catégorie | Note |
|---|---|---|
| `Moogy Saw` | factory Leads | 3 saws, proche Minimoog, avec unison |
| `Classic Lead 2` | factory Leads | filtre Legacy Ladder, 3 oscillateurs |
| `Prog Rock Octave Lead` | 3rdparty (Rozzer) | lead octave, punchy |
| `Warehouse Lead` | 3rdparty (Kinsey) | lead chaud |
| `Sync Sweep Lead` | 3rdparty (Dan Maurer) | lead filtré évolutif |
| `Open Retro Lead` | 3rdparty (Vospi) | lead rétro |

### Cuivres

| Patch | Catégorie | Note |
|---|---|---|
| `Bread & Butter Synth Brass` | 3rdparty (Kinsey) Keys | cuivres doux |
| `Analog Brass` | 3rdparty (Luna) Brass | analogique |
| `Fat Brass` | 3rdparty (Luna) Brass | épais |
| `Orchestral Brass` | 3rdparty (John Valentine) | section |
| `Toto Brass` | factory Brass | cuivres 80s |
| `Synth Brass 3` | factory Brass | cuivres synthétiques |

### Basses

| Patch | Catégorie | Note |
|---|---|---|
| `Big Moog` | 3rdparty (Kuniklo) Basses | moog grasse |
| `Moogish` | 3rdparty Basses | moog |
| `FM Bass 1` | factory Basses | basse FM |
| `Rubber Bass` | — | basse funk, si présente |

### Claviers et pads

| Patch | Catégorie | Note |
|---|---|---|
| `Polymoog` | factory Polysynths | pad grave analogique |
| `MKS-70 Warm Pad` | — | pad chaud, si présent |
| `Brass Pad` | 3rdparty (Nick Moritz) Pads | pad de cuivres |
| `Soft 80s Brass` | 3rdparty (Cybersoda) Brass | cuivres doux 80s |

## ⚠️ Ces patches sont souvent sur OSC1 seul

Ils sont paramétrés sur **un seul oscillateur**. Penser à activer **OSC2, OSC3, 1x2, 2x3, le
noise** dans le mixer — en gardant en tête que 0 = actif — pour retrouver l'épaisseur annoncée.

Et **recharger un patch relose l'architecture** : après chaque `surge_load_patch`, ré-approuver les
mutes, les volumes de mixer et les LFO. Voir `surge-cpu-par-voix`.

## Si la robotisation devient compliquée

Créer une **session dédiée « création de presets »**, et sculpter chaque patch à l'oreille. C'est
plus lent une fois, mais reproductible ensuite.

## Le mapping style → patch

| Style | Direction |
|---|---|
| Funky | patches percussifs, drive, detune léger |
| Pop | leads et pads ronds, peu d'unison |
| Electronic | patches évolutifs, Sync Sweep Lead, filtres mouvants |
| Cinematic | pads larges, Polymoog, cuivres de section |

Ce mapping oriente la recherche, il ne remplace pas l'écoute.

## Chercher par nom

```
surge_search_patches(query="warm")
```

Case-insensitive, cherche dans **toutes** les catégories. Le résultat donne pour chaque patch :

- `category`
- `name`
- `path` (absolu, **sans extension**)

## Charger

```
surge_load_patch(path="C:/Program Files/Common Files/VST3/Surge Synth Team/SurgeXTData/patches_factory/Pads/Warm Pad", instance=0)
```

⚠️ **Le path ne prend pas d'extension.** Ni `.fxp`, ni rien. Et les **forward slashes sont
convertis automatiquement** en backslashes sous Windows, pour éviter que Surge affiche le chemin
complet dans sa fenêtre — je n'ai pas à m'en occuper.

## Les deux index

Les patches viennent de deux sources, et `surge_list_categories` renvoie les deux :

- `patches_factory` — les patches d'usine.
- `patches_3rdparty` — les patches de tiers.

## Instantané

```
surge_get_patch(instance=0)      patch courant
surge_incr_patch / decr_patch    patch suivant / précédent dans la catégorie
surge_random_patch(instance=0)    patch aléatoire
surge_rebuild_index()            rescanne les .fxp du disque
```

**J'utilise `random` avec précaution** : un patch aléatoire est agréable à écouter, mais il n'est
pas reproductible. Si David retient un son, je note le **nom exact** dans la fiche technique —
sinon il est perdu. Voir `fiche-technique`.

## Si un patch ne se charge pas

`surge_rebuild_index()` si l'index est périmé (patch ajouté à la main). Si le patch est trouvé
mais ne sonne pas, vérifier l'instance et son port OSC — voir `surge-cpu-par-voix`.
