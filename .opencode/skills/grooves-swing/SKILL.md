---
name: grooves-swing
description: Use when adding groove or swing to a whole track, when clips sound too quantised or robotic, or when an MPC/funky swing is needed. The MCP CAN now load a groove .agr into the Groove Pool and assign it to clips (get_grooves, load_groove, get_clip_groove, set_clip_groove, set_groove_parameter) — only removing a groove stays manual. Covers the verified tool set, the LOM limitation on removal, the micro-timing fallback baked into notes, that groove_amount is global and affects every clip using a groove, applying the same groove to all instrument tracks for cohesion, and the Swing categories. Trigger words : groove, swing, .agr, MPC, quantise, robotique, groove_amount, funk, SP1200, cohésion rythmique, Groove Pool, assigner un groove, charger un groove.
---

# Grooves & Swing

Le swing ne s'écrit pas note par note : on charge un **groove** `.agr` dans la Groove Pool et on
l'assigne aux clips. **Le MCP sait le faire** (vérifié dans ce build, 2026-10-16) — sauf le retrait.

## ✅ Le MCP PEUT charger et assigner un groove

Le module groove expose désormais (via `ableton-full`) :

| Outil | Rôle |
|---|---|
| `get_grooves()` | Liste la Groove Pool : `index`, `name`, `base`, `quantization_amount`, `timing_amount`, `velocity_amount`, `random_amount`. |
| `load_groove(uri)` | Charge un `.agr` **dans la Groove Pool**. Renvoie la pool complète + `pool_count_before/after`. |
| `get_clip_groove(track_index, clip_index, is_arrangement=False)` | Lit le groove d'un clip (`has_groove`, `groove_index`, `groove`). |
| `set_clip_groove(track_index, clip_index, groove_index, is_arrangement=False)` | Assigne un groove de la pool (par son **index**) à un clip. |
| `set_groove_parameter(groove_index, parameter_name, value)` | Règle `base`, `quantization_amount`, `timing_amount`, `velocity_amount`, `random_amount`. |
| `get_groove_amount()` / `set_groove_amount(amount)` | Montant **global** (0.0–1.0). |

**Pourquoi ça marche :** le Remote Script charge le `.agr` par le chemin **générique**
`app.browser.load_item(item)` — le même que pour un instrument. Sur un fichier de groove, Live
l'ajoute à la Groove Pool au lieu de le poser sur une piste (aucun effet de bord sur la piste).
`is_loadable` vaut `True` pour ces items.

## ⚠️ Ce que l'MCP ne peut PAS faire

- **Désassigner** un groove d'un clip : `clip.groove = None` est **rejeté** par pybind
  (`did not match C++ signature … AAbstractGroove`). `clear_clip_groove` renvoie donc
  `removed: False` + une note, **il ne retire rien**. Retrait = geste manuel de David (panneau
  Groove du clip), **ou** on neutralise le groove en mettant ses quantités à 0 via
  `set_groove_parameter` (`timing_amount=0`, `velocity_amount=0`, `quantization_amount=0`,
  `random_amount=0`).
- **Vider la Groove Pool** : `GroovePool.grooves` est en **lecture seule** dans la LOM — on peut
  *ajouter* un groove, pas en *supprimer* un. `clear_grooves` le dit honnêtement.

## Trouver l'URI d'un groove

Les `.agr` vivent dans le browser sous la catégorie **`packs`** (Core Library) :

```
get_browser_items(path="packs/Core Library/Grooves/Swing/MPC")
```

Chaque item renvoie son `uri`, de la forme :

```
query:LivePacks#www.ableton.com/0:Grooves:Swing:MPC:Swing%20MPC%20Funker%2016ths%2060.agr
```

## Workflow

1. **Trouver** le groove : `get_browser_items(path="packs/Core Library/Grooves/Swing/MPC")`.
2. **Charger** dans la pool : `load_groove(uri)` — vérifier que `pool_count_after` a augmenté.
3. **Repérer l'index** : `get_grooves()` (l'index change à chaque chargement).
4. **Assigner** aux pistes rythmiques/instrument : `set_clip_groove(track_index, clip_index, groove_index)`
   — **le même** groove partout (cohésion).
5. **Régler le montant** : `set_groove_amount(0.7-0.9)`, et/ou affiner `timing_amount` par groove.
6. Capturer et écouter.
7. **Re-vérifier après toute recréation de clip** : un clip refait perd son groove → le réassigner.

## Route de repli : le swing « cuit » dans les notes

Quand assigner un groove n'est pas souhaité, on approxime le swing **en écrivant les notes
décalées** (contretemps de 16e reculés de quelques centièmes de temps). Déjà implémenté dans les
scripts de prep : `scripts/clip_plan.py` → `humanize()` (swing + jitter). Le groove est alors **figé
dans le clip**, non réglable par le montant global.

## ⚠️ `groove_amount` est GLOBAL

`set_groove_amount(0.7-0.9)` **affecte tous les clips qui ont un groove**, pas seulement un. C'est un
réglage de session, pas de clip.

Conséquences :
- **Appliquer le même groove `.agr` à toutes les pistes instrument** → cohésion. Si chaque piste a
  un groove différent, la section part en vrille.
- **Un clip recréé perd son groove** → le réassigner avec `set_clip_groove`.
- `set_groove_amount(amount)` : 0.0 = aucun, 1.0 = maximum. La zone de travail est 0.7-0.9.

## Les catégories de Swing

| Famille | Caractère |
|---|---|
| **Basic** | swing standard |
| **Logic** | swing « Logic » |
| **MPC** | swing MPC — **Funker 16ths 55/60/70** = le plus adapté au funk |
| **Notator** | swing Notator |
| **SP 1200** | swing SP-1200, plus crunchy |

Pour du funk : **MPC Funker 16ths 60**.

## Ne pas confondre

- Le **swing** (groove `.agr`, appliqué à des clips, montant global) ≠ la **factorisation**
  (réutilisation de patterns nommés). Voir `factorisation-grooves`.
- Le swing est une *quantisation* du timing. La **vélocité** reste du travail de `velocites-et-dynamique`.
