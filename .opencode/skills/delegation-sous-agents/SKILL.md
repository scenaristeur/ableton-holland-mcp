---
name: delegation-sous-agents
description: Use when a task involves reading or analysing many files, comparing documents, computing a plan, or verifying a state, and would bloat the main context. Covers what to delegate to a sub-agent, what to keep in the main context, and how to write a delegation prompt that returns only a conclusion. Trigger words : déléguer, sous-agent, sous agent, subagent, contexte, polluer, surcharger, ne pas charger, comparer, analyser plusieurs, répartir, task, toile de fond.
---

# Délégation aux sous-agents

**Je protège le contexte global.** Tout ce qui peut être isolé est confié à un sous-agent ; je ne
garde que sa conclusion. C'est une règle de posture, pas une option.

## Quand déléguer

Je délègue quand la tâche est **isolable** : elle peut tourner de bout en bout sans dépendre de la
conversation en cours, et son résultat se résume en quelques lignes.

Bonnes candidates :

- **lire / analyser plusieurs fichiers** — comparer des skills, des docs, des fiches,
- **rechercher** — grep/glob sur un périmètre large, retrouver une référence,
- **calculer un plan** — un découpage, une feuille de route, une checklist,
- **vérifier un état** — un inventaire, un diff, une cohérence,
- **rédiger une conclusion synthétique** à partir de beaucoup de matière.

## Quoi garder

Je garde dans le contexte principal :

- la **décision** (ce qu'on fait, ce qu'on change),
- la **validation** à l'oreille (le jugement musical de David),
- les **actions** qui modifient le projet ou Ableton.

Un sous-agent ne décide pas d'un choix artistique, ne touche pas à `sources/`, ne modifie pas le
set Ableton. Il observe, compare, calcule, et rapporte.

## Comment écrire la délégation

Un prompt de délégation doit dire :

1. **Ce que j'attends** — une conclusion, pas un roman.
2. **Le périmètre exact** — les fichiers à lire, les dossiers, ce qui est hors-périmètre.
3. **Le format de sortie** — un bloc par item, la synthèse à la fin.
4. **Ce que je veux en retour** — les valeurs/noms précis, pas des généralités.

Exemple de demande :

> Travail de RECHERCHE uniquement — ne pas écrire ni modifier de fichier. Compare X et Y. Pour
> chaque couple, rapporte ce qui est déjà couvert, ce qui manque (avec valeurs exactes), et une
> recommandation. Termine par une synthèse d'actions.

**Je précise toujours si le sous-agent doit écrire du code ou seulement chercher** — un sous-agent
qui ne sait pas s'il doit modifier le projet fait n'importe quoi.

## Le réflexe

Dès qu'une demande commence par « regarde / compare / analyse / vérifie / trouve / calcule », je me
demande : *est-ce que ça tient dans une page de conclusion ?* Si oui → sous-agent. Si c'est une
action (charger un son, écrire une note, lancer une capture) → je le garde et j'attends David.

## Ne pas déléguer la validation

La décision finale reste au contexte principal. Le sous-agent apporte de la matière ; c'est moi qui
décide, et c'est David qui tranche à l'oreille. Un sous-agent qui « décide » du mix ou du groove
violerait `velocites-et-dynamique` et `preferences-david`.