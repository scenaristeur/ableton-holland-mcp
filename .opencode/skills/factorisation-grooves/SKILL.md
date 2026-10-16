---
name: factorisation-grooves
description: Use when a groove feels repetitive, when the same 2 bars loop too obviously, or when building variation across a long section. Covers drum and bass factorisation, real versus timbral variation, the three levels of variation (velocity, accent, syncopation), and the anti-pattern of inventing new fills that break the pocket. Trigger words : groove, factoriser, pattern, fill, trop répétitif, variation, pocket.
---

# Factorisation des grooves

## La règle du top xN

C'est la méthode validée sur « Keep Talking », et elle est **quantitative**, pas à l'intuition.

Pour chaque piste et chaque scène, je compte combien de fois un même motif revient
(`factorization_analysis` dans `prep_<song>.py` sort ce « top xN »).

**Si top xN ≥ 3** → un **clip groove court bouclé** de 1 à 4 mesures, plus des **fills de
transition**. C'est modulaire, court à charger, économe en CPU, et rejouable.

**Sinon** → des **variations dans un clip long** couvrant toute la section.

Ce qui fait la qualité d'un groove : le nombre de variations, pas le nombre d'orchestrations.

## Factoriser tous les instruments, pas seulement la batterie

Les quatre câlins typiquement répétitifs qui méritent un clip bouclé : **clavier, pad, basse,
guitare rythmique**. Factoriser uniquement la batterie laisse des nappes de 32 temps
impossibles à nuancer.

## Factoriser avant d'arranger

Chaque percussion, chaque pattern de basse, chaque phrase de lead devient un **pattern nommé et
réutilisable**. C'est ce qui permet de varier sans redécouvrir, et c'est ce qui rend le morceau
rejouable sans moi.

## Les trois niveaux de variation

Du plus subtil au plus audible. On monte dans cet ordre.

1. **Vélocité** — les mêmes notes, des vélocités différentes. Invisible à l'analyse, évident à
   l'oreille. C'est 80 % de la variation d'un groove.
2. **Accentuation** — une note déplacée, un contretemps marqué. Le motif reste, la hiérarchie
   change.
3. **Syncopation** — on déplace une note. Le groove bouge pour de vrai.

Puis seulement, si le morceau s'y prête :

4. **Timbre** — un autre preset, un filtre qui s'ouvre sur la fin de section.
5. **Contre-chant** — une réponse mélodique. Plus coûteux, plus risqué.

## Ce qui est interdit

⚠️ **Improviser un fill.** Un fill inventé casse le pocket et structure tout le reste du morceau
autour d'une erreur. La règle :

> Je réhumanise un pattern **existant**, je ne réécris pas la densité.

Vélocités et micro-décalages : oui. Retirer des notes, ajouter des notes, déplacer un contretemps,
respirer dans le pattern : **jamais** pour « faire vivant ».

Le kick clairsemé et le crescendo inventé sont les deux erreurs classiques. Voir
`velocites-et-dynamique`.

## Remplir sans casser

Un fill doit **conduire** vers la section suivante, pas interrompre. Il part du dernier élément du
motif en cours et il arrive sur le premier temps de la nouvelle section.

Si je ne sais pas quel fill convient, je **propose deux options** à David et j'attends. Voir
`preferences-david` pour la posture : 2-3 options concrètes, pas un menu de 20.

## Nommer

Les patterns factorisés portent le nom `S<scene> Groove` et `S<scene> Fill<Rôle>`, comme tout
clip. Voir `conventions-nommage`.
