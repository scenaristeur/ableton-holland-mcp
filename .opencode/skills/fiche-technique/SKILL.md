---
name: fiche-technique
description: Use when writing, reading or updating a song's technical sheet (FICHE_TECHNIQUE.md) in sources/<Album>/NN - Titre/. Covers the document structure, the Ableton pitch convention C3=60, velocity scale 0-100, beats vs bars, and how to check chord names against real notes. Trigger words : fiche, fiche technique, documenter un morceau, sources/, structure du morceau, patch par piste.
---

# Fiche technique par morceau

La fiche est **la mémoire du morceau**. Si je reprends le projet dans 3 mois, c'est ce que je lis
en premier. Elle doit permettre de **rejouer le morceau sans moi**.

Format de référence : `sources/Bac/_FICHES_CONVENTIONS.md`.
Modèle le plus propre : `sources/Resonnances/02 - Marteau-Pilon/`.

## Je documente au fur et à mesure

Dès qu'une piste est mixée, sa ligne est écrite dans la fiche. **Pas à la fin** — à la fin, j'oublie
la moitié et les valeurs sont fausses.

## Structure attendue

1. **En-tête** — Tempo, Tonalité, Signature, Durée, Atmosphère, Style, Voix.
2. **Structure** — en mesures, avec l'énergie de chaque section.
3. **Grille d'accords** — accord réel + notes réelles.
4. **Pistes** — index, moteur, patch, pan, volume, chaîne FX.
5. **Clips** — nom, position, longueur, contenu.
6. **Automations** — cible, points, raison.
7. **Réglages mix** — volumes, pan, master.
8. **Notes de production** — ce qui n'est pas déductible du reste.

Fichier de chanson chantée : `PAROLES.md` à côté. Avec clip vidéo : `CLIP.md`.

## Conventions non négociables

- **Ableton : C3 = 60.** 60 = C3, 64 = E3, 69 = A3, 71 = B3. La convention scientifique (C4 = 60)
  circule dans d'anciens `PAROLES.md` et met les notes **une octave trop bas**. Je corrige.
- **`time` en temps (beats).** La structure en mesures. **Toujours écrire l'unité** à côté.
- **Vélocités 0-100** dans les fiches, même si l'API accepte 0-127.
- **Indices de piste 0-based**, alignés sur le template réel — pas sur ce que j'ai en tête.
- **Vérifier chaque accord JSON contre son nom** : Em9 = E-G-B-D-F#, Cmaj9 = C-E-G-B-D,
  Fmaj7 = F-A-C-E, Dm9 = D-F-A-C-E. Les fiches contiennent des accords mal nommés, je corrige.
- **Aucune commande MCP inventée.** Tout ce que j'écris doit être vérifiable.

## Ce que j'écris pas

- Des commandes d'outil non vérifiées, ou des noms d'outils qui n'existent pas.
- Des valeurs approximatives (« environ 0.8 ») — je donne la valeur et son unité.
- Du code. Une fiche décrit de la musique, pas une implémentation.
