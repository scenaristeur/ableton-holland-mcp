---
name: grooves-swing
description: Use when adding groove or swing to a whole track, when clips sound too quantised or robotic, or when an MPC/funky swing is needed. Covers loading .agr grooves from the Core Library, that groove_amount is global and affects every clip using a groove, applying the same groove to all instrument tracks for cohesion, and the Swing categories. Trigger words : groove, swing, .agr, MPC, quantise, robotique, groove_amount, funk, SP1200, cohésion rythmique.
---

# Grooves & Swing

Le swing ne s'écrit pas note par note : on charge un **groove** `.agr` et on l'applique aux clips.

## Charger un groove

URI de référence, le plus adapté au funk :

```
query:LivePacks#www.ableton.com/0:Grooves:Swing:MPC:Swing%20MPC%20Funker%2016ths%2060.agr
```

Chemin browser équivalent : `packs/Core Library/Grooves/Swing/MPC/`.

## ⚠️ `groove_amount` est GLOBAL

`set_groove_amount(0.7-0.9)` **affecte tous les clips qui ont un groove**, pas seulement un. C'est un
réglage de session, pas de clip.

Conséquences :
- **Appliquer le même groove `.agr` à toutes les pistes instrument** → cohésion. Si chaque piste a
  un groove différent, la section part en vrille.
- **Un clip recréé perd son groove** → je revérifie l'assignation après toute recréation de clip.
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

## Workflow

1. Charger `Swing MPC Funker 16ths 60.agr`.
2. L'appliquer à **toutes** les pistes instrument pour la cohésion.
3. `set_groove_amount(0.7-0.9)`.
4. Capturer et écouter.
5. **Re-vérifier après toute recréation de clip** (un clip refait perd son groove).

## Ne pas confondre

- Le **swing** (groove `.agr`, appliqué à des clips, global) ≠ la **factorisation** (réutilisation
  de patterns nommés). Voir `factorisation-grooves`.
- Le swing est une *quantisation* du timing. La **vélocité** reste du travail de `velocites-et-dynamique`.