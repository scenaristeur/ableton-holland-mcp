---
name: sculpture-sonore
description: Use when shaping the sound of an instrument right after loading it, or when a sound is too raw, too harsh, too synthetic, too saw-like, shrill, buzzing or grésillant, or disappears in the mix. Covers the systematic first timbre pass, the rule of sculpting from a transparent state, reading exposed parameters and unused macros, and iterating with a capture. Trigger words : sculpter le son, son brut, trop dur, trop maigre, trop synthétique, crillard, grésillant, saw, aigre, nasillard, du son, relief, macros.
---

# Sculpture sonore — dès que ça joue

**Je ne laisse pas le son brut jusqu'au mix.** Dès que les instruments sont posés, je travaille le
son. Un son brut se mixe mal, et le temps perdu à le rattraper tard est bien plus cher.

## ⚠️ Règle d'automatisme — le réflexe, à chaque fois

**Dès que je pose un instrument, dès que j'écris des notes dessus, et dès que j'ajoute un device
(Saturator, Auto Filter, Reverb, Delay, Compressor, Utility…), la question « comment j'adapte ça à
la chanson ? » se pose AVANT de présenter la scène à David.** Ce n'est pas une correction après
coup : c'est l'étape 3 de la boucle de maquette (voir `maquette-scene-par-scene`). Un preset posé
brut — **ou un device laissé à ses valeurs par défaut** — s'entend tout de suite comme un « instru
bas de gamme », et le rattraper plus tard coûte bien plus cher que de le régler tout de suite.

Concrètement, à chaque instrument **et** à chaque device neuf :
1. `get_device_parameters(track_index, device_index)` — lire les paramètres exposés. **Un device
   tout juste chargé est presque toujours à régler** (Saturator sort à Drive 0.5 / Dry/Wet 1.0,
   Auto Filter à 14 kHz, etc.).
2. Instrument : corriger les tueurs de timbre (résonance haute, Noise Gain, filtre trop ouvert ou
   fermé, enveloppe inadaptée au rôle).
3. Device : régler ses paramètres pour la chanson (type de saturation, point de coupure, dose en
   Dry/Wet, envoi/retour…), jamais « par défaut parce que ça marche ».
4. Mettre de l'espace (envois Reverb / Delay).
5. Seulement après, passer à la piste suivante.

## Premier ajustement : naturaliser le timbre

**Un instrument posé ne sonne presque jamais comme le morceau.** Les presets et les oscillateurs
par défaut sont souvent **synthétiques, crillards, grésillants, saw** — trop aigus, trop tranchants,
avec un pic de résonance qui agresse. Avant toute autre chose, je fais un **premier passage de
timbre**, systématique, dans cet ordre :

1. **Adoucir l'oscillateur.** Trop de saw = aigreur. Je mélange la forme d'onde vers une plus
   ronde (triangle / sine) ou je réduis le nombre de voix d'oscillateur qui empilent du haut. Je
   cherche du **corps**, pas du tranchant.
2. **Fermer le filtre (low-pass).** Un preset ouvre trop tôt. Je baisse la coupure pour retirer le
   grésillement au-dessus — là où « ça pique ». Le grave/le corps restent, l'agression tombe.
3. **Calmer la résonance.** Un pic étroit (resonance haute) rend le son criard. Je la réduis, ou je
   décale la coupure pour ne pas amplifier un pic musicalement inutile.
4. **Régler l'enveloppe du filtre.** Une attaque trop dure = bruit d'attaque. Une relâche trop
   courte = clic. Je donne au filtre une courbe qui ouvre/ferme selon le rôle (lent pour une nappe,
   moyen pour un lead, rapide pour un pluck).
5. **Éclaircir le bas au lieu d'éclaircir le haut.** Plutôt que d'ajouter du brillant, je dégage le
   bas (HPF 150-200 Hz, voir `gain-staging`) et je laisse le timbre naturel. Le « grandiose » vient
   du corps et de l'espace, pas du tranchant.

### La cible : naturel, grandiose, efficace

Le bon timbre, c'est celui qui **sert la chanson** :

- **naturel** — ne crie pas « synthé de démo », a de la matière, pas de grésillement,
- **grandiose** — de la largeur (léger unison/detune), du corps dans le bas, une présence qui porte
  sans piquer,
- **efficace** — il remplit son rôle (lead qui passe, nappe qui enveloppe) sans se battre avec les
  autres.

Je valide ce premier passage **à l'oreille avec David** (ou « selon la capture ») avant d'aller plus
loin. Un timbre adouci à l'aveugle peut devenir boueux — le naturel se juge en contexte.

### Si le son reste criard malgré tout

Quelques macros natifs servent exactement à ça, souvent à 0 par défaut : `Over Tone`, `Tone`,
`Distort` sur les synthés natifs. Une couche d'octave basse (ou un saturateur doux sur la basse,
voir `mix-translation`) rend le son plus profond sans le rendre aigu. Je lis les paramètres exposés
avant d'ajouter quoi que ce soit.

## La règle qui compte

⚠️ **Ne jamais coller une chaîne FX documentée telle quelle.**

Les paramètres de plugin sont normalisés 0-1, le mapping n'est pas vérifié, et un preset peut
**effacer complètement le signal**. Ça arrive : le Saturator « Hot Tubes » a rendu une voix
inaudible.

Donc, dans cet ordre :

1. **État transparent.** Je mets la chaîne en place mais neutre. Je vérifie que le son est propre
   et audible.
2. **Capture de contrôle.** Je capture, je regarde le RMS. Si le signal a disparu, je remonte.
3. **Sculpture.** Un paramètre à la fois, et je recapture entre chaque.

Les recettes des docs sont des **exemples à adapter**, pas des recettes.

## Lire les paramètres exposés

```
get_device_parameters(track_index, device_index)
```

Beaucoup de synthés natifs ont des **macros internes à 0** qui servent exactement à ça :
Over Tone, Tone, Distort sur Basic Sub Sine. Elles sont à 0 par défaut et n'apparaissent pas comme
des « presets » — ce sont des points de sculpture librement accessibles.

## Un son brut se mixe mal

Le temps perdu à rattraper un son tard coûte bien plus cher que celui passé à le sculpter tout de
suite. Et une sculpture faite à l'aveugle coûte encore plus cher qu'un son brut assumé. D'où les
trois étapes : transparent, mesuré, puis sculpté.

## La chaîne minimale par type de source

- **Batterie** : Compressor (légère) → EQ Three si besoin. Pas de réverb, elle mange la caisse.
- **Basse** : Saturator → c'est l'outil le plus important du mix, pas un effet décoratif.
- **Nappe / clavier** : EQ Three (carver) → Reverb en insert, Dry/Wet bas.
- **Lead** : EQ Three → Reverb en insert très bas (0.2 / Room Size 0.45).
- **Voix** : EQ Three (présence 1-4 kHz) → Reverb en insert bas (0.18 / Room Size 0.4).
  Jamais de réverb qui mange l'intelligibilité.

## Itérer

Sculper, recapturer, écouter le résultat rapporté, ajuster. **Un changement mesurable à la fois.**

Si le son s'améliore mais que le niveau a bougé, je **re-équilibre** — voir `gain-staging`. Un
effet qui change le gain change la place de la piste dans le mix.
