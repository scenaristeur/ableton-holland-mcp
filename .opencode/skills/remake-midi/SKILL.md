---
name: remake-midi
description: Use when rebuilding a song from a .mid file, or when asked to reproduce, refaire or cover an existing piece. Covers the ordered method (analyse, factoriser, construire les scènes, mixer), the rule that groove factorisation must precede arrangement, and the validation gate at every step. Trigger words : refaire un mid, remake, .mid, reproduire un morceau, cover, reprise, Keep Talking, factoriser.
---

# Refaire un fichier `.mid`

Méthode validée sur « Keep Talking » (Pink Floyd). Voir aussi `factorisation-grooves`.

## L'ordre compte

**On factorise avant d'arranger.** C'est l'inverse de l'instinct : on veut entendre le morceau tout
de suite. Non — sans patterns factorisés, l'arrangement est du poker.

## Les étapes

1. **Analyser le `.mid`.** Tempo, signature, longueur en mesures, structure, tonalité. Je lis les
   données, je n'improvise rien.
2. **Factoriser les motifs.** Chaque percussion, chaque pattern de basse, chaque phrase de lead
   devient un pattern nommé et réutilisable. La décision se prend au **top xN**. Voir
   `factorisation-grooves`.
3. **Fusionner en 8 pistes maximum**, par famille : drums+percs, guitares, pads+strings… Puis
   dédupliquer ce qui a été fusionné à l'unisson.
4. **Poser les instruments**, en partant de la décision par rôle. Voir `choix-instrument-par-role`.
5. **Construire les scènes**, une section = une scène. Les frontières de section viennent des
   silences et des entrées instrumentales. Voir `maquette-scene-par-scene`.
6. **Poser les vélocités.** Un `.mid` importé a des vélocités plates ou arbitraires. C'est le
   premier vrai travail de groove. Voir `velocites-et-dynamique`.
7. **Sculpter** chaque son, en isolant les pistes une à une aux moments cruels. Voir
   `sculpture-sonore`.
8. **Arranger** une fois toutes les scènes validées, avec `destination_time`.
9. **Mixer** dans l'ordre des 6 étapes. Voir `mix-en-6-etapes`.

## Les 11 pièges de « Keep Talking »

Ces onze points viennent d'un remake réel. Ils ne sont pas déductibles de la méthode.

1. **`add_notes_to_clip` attend `start_time`**, pas `start`. Sinon les notes s'empilent à 0.
   Vérifier avec `get_clip_notes` après chaque injection. Voir `pieges-notes-midi`.
2. **Fusionner des pistes à l'unisson crée des doublons** → il faut dédupliquer.
3. **Un kit Core Library n'a pas le mappage GM du `.mid`** → il faut remapper les pitches des pads.
   Voir `kits-batterie-par-vibe`.
4. **Mute ne désactive pas ; freeze bloque l'édition.** Mesurer en jeu. Voir `diagnostic-cpu`.
5. **L'automation de device en arrangement n'est pas fiable.** Passer par des clips de session, ou
   vérifier par l'Auto Filter. Voir `pieges-automation`.
6. **`duplicate_to_arrangement` : toujours `destination_time` en temps**, jamais
   `destination_bar`. Voir `pieges-niveaux`.
7. **Les paramètres de plugin VST ont un mapping non vérifié** → tester par petites valeurs
   mesurées, jamais une valeur « plausible » posée d'un coup.
8. **Recharger un patch Surge relose son architecture** → il faut ré-approuver les mutes, les
   volumes de mixer et les LFO après chaque chargement.
9. **Une basse sous ~70 Hz est inaudible.** L'ancrer vers **E2 (~82 Hz)** et ajouter un saturateur
   pour les harmoniques. Voir `mix-translation`.
10. **Factoriser selon la règle du top xN**, pas à l'intuition. Voir `factorisation-grooves`.
11. **La palette réelle de Lite** : 6 instruments natifs seulement. Si le `.mid` suppose un synthé
    absent, le rendre avec Drift + sons, puis **le noter dans la fiche**. Voir `palette-live-lite`.

## Outillage du remake

Un remake prépare ses données dans un script, pas à la main :

```
prep_<song>.py                analyse mido, dédup, remap des pads, vélocités préservées
  → _scenes_notes.json        par piste / par scène
  → factorization_analysis    le « top xN » qui décide clip court ou clip long
```

Le reste du travail se fait dans Ableton, via les outils, dans l'ordre des étapes ci-dessus.

## Ce que je ne fais pas

- **Improviser un groove « à l'aveugle »** pour gagner du temps. Un contre-temps inventé structure
  tout le reste autour d'une erreur.
- **Recomposer** ce qui existe : un remake reproduit. Les écarts se corrigent avec David, pas
  seuls.
- **Passer à l'arrangement** avant que les scènes soient validées à l'oreille.

## La validation

À chaque étape, je capture, je rapporte **en langage musical**, et j'attends la validation de David
avant la suivante. Une validation par étape, pas une validation finale.

## Périmètre

Un remake concerne **un** morceau. Sa mémoire est dans
`sources/<Album>/NN - Titre/FICHE_TECHNIQUE.md` — je l'écris au fur et à mesure, sinon le morceau
n'est pas rejouable. Voir `fiche-technique`.
