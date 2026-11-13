---
name: capture-plage-voix
description: Use when measuring the frequency range of a voice (or any instrument) to decide where another part can sit without masking it. Covers the solo capture procedure (mute the other tracks, restore them), several captures at different moments, reading the WAV directly, and the script scripts/analyse_plage_voix.py. Trigger words : plage de fréquence, tessiture, fondamentale, masquage, où mettre la basse, voix solo, capture voix, fréquences de la voix, ne pas surcharger.
---

# Capture de la plage de fréquences d'une voix

## Pourquoi

Pour savoir où placer la basse, les pads ou les chœurs sans écraser la voix. La réponse est une
plage en Hz, mesurée sur la voix seule, pas une impression.

## Procédure

1. **Isoler la voix.** Couper les autres pistes qui sonnent, par `set_track_mute(track_index, mute=True)`.
   Vérifier avant la capture que la clip voix joue (`get_track_info` → `clip.is_playing`). Si la
   lecture est arrêtée, relancer la clip et `start_playback`.
2. **Capturer plusieurs moments.** Pas un seul : trois positions différentes (par exemple 32, 96 et
   160 temps). Une seule capture peut tomber sur une pause ou une voyelle tenue.
   **Une capture à la fois** (voir `capture`), 10 s chacune.
3. **Rétablir les pistes.** Remettre les mutes à `False` dans tous les cas, même si une capture échoue.
4. **Lire les WAV, pas la réponse de l'outil.** Lancer le script :

   ```
   .venv\Scripts\python.exe scripts\analyse_plage_voix.py data\analyses\<nom>.wav [...]
   ```

   Il rend la fondamentale (p10 / médiane / p90) en Hz et en note, et la répartition de l'énergie
   (5 % / 50 % / 95 %). Un WAV muet est signalé en erreur.
5. **Contrôler le silence avant tout.** Si le script dit « silence », la capture n'a pas enregistré
   la voix. Ne rien conclure de ce fichier (cas réel : une capture « voix seule » était muette alors
   que l'outil annonçait un RMS de 0,34).

## Lire les résultats

- **La fondamentale** dit où la voix chante ou parle. **L'énergie** dit où elle pèse dans le mix.
  Les deux sont à lire ensemble.
- **Les notes** issues de la fondamentale utilisent la convention Ableton (C3 = 60). Une note réelle
  (fréquence) n'est pas une note Ableton : je donne toujours les deux, avec la fréquence en Hz.
- **Une tessiture écrite en notes** (fiche, profil) peut être décalée d'une octave selon la
  convention utilisée. Avant de tirer une conclusion, comparer la fréquence mesurée à la tessiture
  attendue en Hz, et demander confirmation à David si l'écart est grand.
- **Une tonalité tirée de la voix seule** reste faible (confiance souvent sous 50 %). Ne pas l'utiliser
  seule pour décider d'une tonalité.

## Ce qui ne se mesure pas

- La tonalité fiable du morceau : la mélodie n'est pas écrite en MIDI, seulement en audio.
- Le confort de David : ça se valide à l'oreille avec lui.

## Pour la basse

Une fois la plage de la voix connue, la basse se place **sous** la fondamentale de la voix, en
général 40 à 100 Hz si la voix commence vers 105 Hz. Vérifier ensuite le spectre de la basse seule
(même principe : capture de la piste isolée, puis `scripts\analyse_plage_voix.py` ou mesure du
pourcentage d'énergie sous un seuil).

Voir `carving-eq` pour le masquage et `limites-analyse` pour les chiffres de l'outil.
