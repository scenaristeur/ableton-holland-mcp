---
name: guide-vocal-paroles
description: Use when working on vocals, lyrics, a spoken-word or sung passage for David. Covers his baritone range E3-B3 (MIDI 64-71), preferred key of C#m, the spoken-sung nonchalant delivery, PAROLES.md structure, and when to flag a melody as out of range instead of forcing it. Trigger words : voix, paroles, lyrics, chanter, couplet chanté, talkbox, tessiture, mélodie vocale, guide vocal.
---

# Voix, paroles et tessiture

## Le profil de David

- **Baryton.** Tessiture comfortable : **E3-B3 = MIDI 64-71**.
- **Tonalité préférée : Do#m.**
- **Voix parlé-chanté, nonchalante.** Pas de notes tenues alignées, pas de montée dramatisée.
  Le nonchalant vient du décalage, pas de la faiblesse.

## Tessiture : convention Ableton

**C3 = 60.** Donc E3 = 64, A3 = 69, B3 = 71.

⚠️ La convention scientifique (C4 = 60) circule dans d'anciens `PAROLES.md` et met les notes
**une octave trop bas**. Vérifier avant de chanter.

## Estimer la tessiture d'une voix par le centroid

Si je n'ai pas le profil de la voix, le **centroid spectral** oriente la tessiture :

| Centroid | Voix | Tessiture (C3=60) |
|---|---|---|
| < 800 Hz | baryton | E3-G3 (60-62) |
| 800-1200 Hz | tenor | G3-C4 (62-64) |
| > 1200 Hz | soprano | C4-E4 (64-66) |

Ce n'est qu'un **repère**, à confirmer à l'oreille — voir `limites-analyse`.

## Si la mélodie sort de la tessiture

Je **signale** avec `À valider` plutôt que de forcer. Exemple : « Cette fin de phrase monte sur D4
(MIDI 62 dans la tessiture basse / 74 si on lit C4=60) — au-dessus de ta zone. Je propose de
redescendre sur B3, ou de laisser la mélodie en voix de tête. Tu choisis. »

Je ne transpose pas une mélodie hors tessiture en silence. C'est une décision musicale de David.

## PAROLES.md

Pour tout morceau chanté. Contenu :

1. Les paroles, section par section, alignées sur la structure.
2. La tessiture cible par section, en notes **avec la convention du projet** (C3 = 60).
3. Les notes de phrasé : où respirer, où insister, où laisser l'espace.
4. Les propositions de mélodie quand elles existent déjà (guide en session).

### Durées et syllabes dans le texte

Chaque syllabe porte une indication de durée (le symbole `triangN` sur la syllabe, `N` = nombre de
temps) :

- syllabes courtes, valeurs de transition : `1-3` temps,
- mots-clés, valeurs d'accent : `4-8` temps.

C'est ce qui permet de rejouer le phrasé exact sans avoir la voix de David. Si un `PAROLES.md`
existant n'a pas ces durées, je les propose en respectant les syllabes accentuées.

## Guide vocal en session

Le clip porte le nom `Guide - <Section>` (voir `conventions-nommage`). Il contient les notes de la
mélodie à chanter, avec des vélocités qui **phrasent** la ligne, pas une noteplate :

- phrases accentuées 95-110,
- notes tenues 80-90,
- passages 75-85.

## Voix parlée

Si la section est **parlée** et non chantée : le guide contient la ligne rythmique et les intonations,
pas des hauteurs. Je ne force pas une mélodie sur du spoken word.
