---
name: gain-staging
description: Use when a track is too quiet, too loud, weak, or buried in the mix, and before any mix balancing pass. Covers the high-pass rule done with Auto Filter (Utility has NO Highpass in this build), the Utility Output trick for weak instruments (bipolar -1..+1, 0 = unity), the normalised volume scale, and why the master fader sits after the inserts. Trigger words : trop fort, trop maigre, trop faible, volume, gain, pan, équilibre, disparu, enterré, gain staging, HPF, passe-haut, Auto Filter, Utility.
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

⚠️ **L'`Utility` de ce build n'a PAS de paramètre Highpass.** Vérifié en session : ses seuls
paramètres sont Output, Bass Mono, Bass Freq, Balance, Stereo Width, Mono, Mute, DC Filter, Channel
Mode, Left/Right Inv. La recette historique « Utility + Highpass » **ne fonctionne pas ici**. Le
passe-haut se fait avec **Auto Filter** réglé en High-pass :

```
load_instrument_or_effect(track_index, "query:AudioFx#Auto Filter")
set_device_parameter(track_index, device_index, "Filter Type", 1)   # 1 = High-pass
set_device_parameter(track_index, device_index, "Frequency", <0-1>)
set_device_parameter(track_index, device_index, "Resonance", 0.05)  # réso minimale
set_device_parameter(track_index, device_index, "Dry/Wet", 1.0)
```

`Frequency` est **normalisée 0-1 et logarithmique** (≈ 20 Hz → 20 kHz). Repères utiles :
`0.22 ≈ 90 Hz` · `0.28 ≈ 140 Hz` · `0.30 ≈ 160 Hz` · `0.35 ≈ 220 Hz`. Je monte plus haut quand la
piste a du corps dans le bas, plus bas quand elle est fine (charley, pluck, percussions aigues).
Le kick et la basse ne sont **jamais** filtrés.

Sur la **basse**, pas de passe-haut mais un **Utility → Mono** (et au besoin *Bass Mono* +
*Bass Freq*) pour garder le grave mono.

## Instrument faible dans le mix

`Utility` porte un paramètre **Output** d'échelle **bipolaire −1 → +1**, où **0 = gain neutre
(0 dB)** — c'est la valeur par défaut d'un Utility fraîchement chargé. Au-dessus de 0 la piste est
amplifiée, en dessous atténuée. C'est le levier le plus simple pour remettre une piste à sa place
sans toucher à l'instrument.

**Je ne suppose jamais un chiffre de dB** : je pousse un peu, puis je **capture** avant/après.

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
