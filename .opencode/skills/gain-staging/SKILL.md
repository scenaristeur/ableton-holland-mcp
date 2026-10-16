---
name: gain-staging
description: Use when a track is too quiet, too loud, weak, or buried in the mix, and before any mix balancing pass. Covers the high-pass rule (150-200 Hz on everything except kick and bass), the Utility Output trick for weak instruments, the normalised volume scale, and why the master fader sits after the inserts. Trigger words : trop fort, trop maigre, trop faible, volume, gain, pan, équilibre, disparu, enterré, gain staging, HPF, passe-haut.
---

# Gain staging et niveaux

## L'échelle est normalisée, pas en dB

Un volume de piste est un nombre **0.0 → 1.0**, où **0.85 = 0 dB**. Ce n'est pas une échelle de dB,
et je ne compare jamais un `0.4` d'un côté à un `0.4` d'un autre comme s'ils signifiaient la même
chose dans des chaînes différentes.

**Exception importante :** le gain d'un **clip audio en arrangement** est un cas à part, et c'est un
piège. Voir `pieges-niveaux`.

## Passe-haut : la règle de base

**HPF 150-200 Hz sur tout, sauf le kick et la basse.**

L'outil : `Utility` (`query:AudioFx#Utility`).

```
load_instrument_or_effect(track_index, "query:AudioFx#Utility")
set_device_parameter(track_index, device_index, "Highpass", <valeur>)
```

Je monte à 200 Hz dès que la piste a du corps dans le bas, à 150 Hz quand elle est fine (charley,
pluck, percussions aigues). Le kick et la basse ne sont **jamais** filtrés.

## Instrument faible dans le mix

`Utility` porte un paramètre **Output** : `0.4` ≈ **+10 dB**. C'est le levier le plus simple pour
remettre une piste à sa place sans toucher à l'instrument.

Mais **toujours vérifier par capture** avant de pousser. Un instrument discret à l'oreille peut
l'être parce qu'il manque d'harmoniques, pas parce qu'il est trop bas — dans ce cas c'est le
saturateur qui règle le problème, pas le volume. Voir `mix-translation`.

## Ordre de réglage

1. **Égaliser les rôles**, pas les attractions. Je place le kick et la basse d'abord, le reste se
   cale dessus.
2. **HPF** sur tout ce qui n'est pas grave.
3. **Panner** pour l'espace, avant de toucher aux volumes.
4. **Volumes** : ajustements fins, par petites touches, une piste à la fois.

## Le fader master

**Le fader master est en aval des inserts.** Il doit rester à **1.0** pour que la chaîne master
atteigne son plafond. Le descendre ne « baisse » rien proprement, ça casse le travail du limiteur
derrière. Voir `master-chain`.

## Ce que je ne fais pas

- Je ne compense pas un masquage par du volume. Je carve d'abord — voir `carving-eq`.
- Je ne monte pas une piste « pour voir » : je capture avant et après.
- Je ne présente jamais un chiffre de niveau seul comme un verdict. Je le donne **en langage
  musical** : « la voix disparaît derrière la caisse », pas « RMS 0.12 ».
