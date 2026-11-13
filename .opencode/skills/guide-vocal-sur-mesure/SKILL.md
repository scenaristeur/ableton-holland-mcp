---
name: guide-vocal-sur-mesure
description: Use when writing or rewriting a guide vocal for David, when a guide written from a lead sheet is unsingable, or when the energy of a section must be carried by the vocal. Covers measuring his real voice first, composing in the measured zone, mapping one note per syllable, stepwise motion with one gesture per phrase, the low anchor of "je lis", late offbeats for nonchalance, the energy map per section, and the capture-compare loop between the guide and his take. Trigger words : guide vocal, tessiture, mélodie, chanter, refaire le guide, parlé-chanté, énergie, section, respiration, trop haut, chanter mieux.
---

# Guide vocal sur mesure

## Le problème que ça résout

Le guide vocal écrit depuis une lead sheet est **chantable sur le papier** et **inchantable pour
David** : les notes viennent d'une grille, pas d'une voix. Résultat : il chante à côté, ou une
octave en dessous, et le guide ne sert à rien.

Un bon guide est **composé pour sa voix**, avec ses syllabes, et il **indique l'énergie** en plus
de la hauteur.

## 1. Mesurer la voix AVANT d'écrire

Jamais de tessiture supposée. La procédure complète est dans `capture-plage-voix` :

1. prendre une **voix seule** (casque, pas de retour enceintes) ;
2. capturer, puis lire le WAV avec `scripts/analyse_plage_voix.py` ;
3. retenir la **fondamentale** (p10 / médiane / p90), pas les notes affichées.

⚠️ **Deux pièges vécus :**

- **Le bleed.** Un take enregistré avec la musique dans les enceintes contient la musique. Muter
  les pistes ne l'enlève pas : on mesure alors la basse, pas la voix. Il faut réenregistrer.
- **La conversion en hertz.** Ne jamais déduire une fréquence d'un numéro MIDI de tête : **on
  vérifie en capturant le guide seul et en le passant au même script.** Une erreur d'octave dans
  cette conversion a fait écrire un guide deux octaves trop haut.

Repère mesuré sur ce projet : voix de David **93-127 Hz, médiane 103 Hz** (G#2 environ).

## 2. Composer dans la zone mesurée

La mélodie du guide doit **recouvrir** la plage du take, avec un sommet légèrement au-dessus pour
que la voix ait de la marge.

- cible couplet : la plage mesurée, sans forcer ;
- cible refrain : **2 à 4 demi-tons au-dessus** du p90 mesuré — c'est là que naît l'énergie ;
- vérifier ensuite : capture du guide seul → script → les deux plages doivent se recouvrir.

## 3. Une note par syllabe, le texte commande

- **Une syllabe = une note.** « Quand les no-ti-fi-ca-tions percent » = huit croches.
- Les **mots-clés** (« je lis », « pas ») prennent une **valeur longue et tenue**.
- Le rythme suit le **débit de la parole**, pas la grille d'accords. C'est la grille qui s'adapte
  harmoniquement (on choisit les notes de l'accord), pas le contraire.

## 4. Le dessin mélodique

1. **Presque pas de sauts.** On avance par **secondes** (50→48→46→45). Un ou deux élans vers le
   haut par phrase suffisent : c'est ce qui distingue une ligne parlée d'une ligne chantée.
2. **Chaque phrase descend et se pose** sur une note basse tenue.
3. **Une ancre.** Dans « Je lis », les fins de phrase retombent toujours sur **la même note**
   (A2 ou G2). C'est le pilier rythmique et mental du morceau : le chanteur sait où revenir.
4. **Un seul sommet par section.** Plusieurs sommets = aucun sommet.

## 5. Le nonchalant vient du décalage

- les **contretemps légèrement en retard** (+10 à +20 ms) ;
- des **vélocités** qui phrasent : accent 94-100 en début de phrase, 80-88 à l'intérieur,
  86-92 sur la note tenue finale ;
- **jamais** de vélocité plate.

## 6. La carte d'énergie

Le guide porte **ce que la voix doit donner**, section par section. Ce tableau est la référence du
morceau ; il se vérifie ensuite au RMS par section.

| Section | Énergie | Ce que le guide demande | Vélocités |
|---|---|---|---|
| Intro | 1/10 | presque parlé, très bas | 55-70 |
| Couplet 1 | 3/10 | posé, nonchalant | 80-96 |
| Couplet 2 | 4/10 | plus tendu, une idée plus haut | 82-98 |
| Pré-refrain | 6/10 | ça monte, on pousse | 84-100 |
| Refrain | 8/10 | plein, tenu, on ouvre | 95-110 |
| Couplet 3 | 5/10 | retour au groove, plus sec | 82-96 |
| Pont | 3/10 | nu, chuchoté, longues tenues | 60-78 |
| Refrain final | 9/10 | tout donner, doublé | 100-115 |
| Outro | 2/10 | parlé | 55-70 |

**Trois leviers pour porter l'énergie** — ils ne se remplacent pas :

1. **la hauteur** (le refrain monte, le couplet reste bas) ;
2. **la longueur des notes** (détaché = tension, tenu = lâcher) ;
3. **la densité** (le pont laisse des trous, le refrain remplit).

## 7. Les deux pistes s'auto-soutiennent

Le guide MIDI et le take audio forment une boucle :

1. le guide **donne la hauteur et le rythme** ;
2. David chante dessus ;
3. on **capture le take**, on mesure (fondamentale, RMS, centroïde) ;
4. on **compare au guide** : si le take est systématiquement en dessous, le guide est trop haut —
   on le descend ; si le take est plat en énergie, les vélocités du guide ne phrasent pas assez ;
5. on **réécrit le guide**, pas le chanteur.

⚠️ Le take n'est pas une faute à corriger : c'est une **mesure**. Un premier take « pas appliqué »
ne dit rien de la voix, il dit seulement qu'il n'y avait pas de repère.

## 8. Ce que le guide ne fait pas

- Il **n'impose pas** une mélodie définitive : c'est une proposition de travail.
- Il **ne transpose pas** une mélodie hors tessiture en silence — on demande (voir
  `guide-vocal-paroles`).
- Il **ne remplace pas** l'écoute de David : la validation est à l'oreille, toujours.

## 9. Livrable

Les clips s'appellent `Guide - <Section>` (voir `conventions-nommage`), et la carte d'énergie part
dans la fiche technique du morceau (voir `fiche-technique`).
