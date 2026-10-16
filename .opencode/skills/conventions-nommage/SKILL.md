---
name: conventions-nommage
description: Use when creating or renaming Ableton tracks, session clips, arrangement clips or drum patches in this project. Covers the index-prefixed track naming that forces session order, the S<scene> Groove/Fill clip convention, guide-vocal clip names, and the S<scene> patch format. Trigger words : nommer, renommer, nom de piste, nom de clip, ordre des pistes, nommage, patch batterie.
---

# Conventions de nommage

Le nommage n'est pas cosmétique : le préfixe d'index **force l'ordre des pistes dans la session**.
Je ne le saute jamais.

## Pistes

Format : `<index>-<Rôle>`, index en 0-based, aligné sur le template réel (8 pistes).

| Exemple | Rôle |
|---|---|
| `1-Batterie+Percs` | rythme |
| `2-Voix (talkbox)` | chant |
| `5-Basse` | basse |
| `7-Claviers` | clavier |

## Clips de session

| Type | Format | Exemple |
|---|---|---|
| Groove | `S<scene> Groove` (+ `4M` = nb mesures) | `S5 Groove`, `S7 Groove4M` |
| Fill | `S<scene> Fill<Rôle>` | `S5 FillEntrée`, `S6 FillSortie` |
| Guide vocal | `Guide - <Section>` | `Guide - Couplet 1` |

Le `S<scene>` relie le clip à sa scène dans l'arrangement. Sans lui, je ne sais plus quelle scène
est validée.

## Patches batterie

Format : `S<scene> <rôle court>` — `A1 Batt`, `A2 Basse`.

## Rappel indexation

Les **outils** sont **0-based** : `track_index 0` = première piste après Master.
Les **noms** portent l'index tel qu'il est (donc `1-` = index 0). Voir `pieges-indexation`.

## Cohérence avec la fiche

Le nom dans Ableton et le nom dans `FICHE_TECHNIQUE.md` doivent être **identiques**. Une fiche qui
contredit le nom d'une piste est une fiche fausse — je corrige la fiche, ou le nom, mais pas les deux.
