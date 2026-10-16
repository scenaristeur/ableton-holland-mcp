---
name: master-chain
description: Use when finishing the mix, on the master track, or when the output clips, lacks loudness, or lacks cohesion. Covers Compressor glue then Limiter true peak, Lookahead 3 ms, Ceiling 0.95 (about -1 dB), and the rule that the master fader must stay at 1.0 because it sits after the inserts. Trigger words : master, limiter, limiteur, glue, plafond, saturation, crête, clipping, volume final, -1 dB.
---

# Chaîne master

Deux devices, dans cet ordre. Pas trois, pas un.

## 1. Compressor glue

`query:AudioFx#Compressor`, chargé **sur le master**. Rôle : coller les éléments en un tout, pas
serrer la dynamique.

⚠️ **Je ne peux pas le charger** : `load_instrument_or_effect_on_master` time-out. **David le dépose
lui-même**, je vérifie avec `get_master_track()` puis je règle. URI et limites : `pieges-browser`.

Je le règle **doucement** — un peu de réduction, une attaque lente, une relâche moyenne. Un master
trop compressé tue la respiration du morceau, et c'est irréversible : on ne décompresse pas.

Valeurs de départ (validation Brain Stew) : **Ratio 0.7, Threshold 0.4, Release 0.3**, avec le
compresseur en mode de réduction douce. À ajuster, pas à copier.

### ⚠️ Ses réglages d'usine écrasent le mix

Un Compressor **juste déposé** est en threshold 0.85 / ratio 0.75 (≈ 7.75:1) / attack 0.4, sans
lookahead. Ce n'est pas du glue, c'est de l'écrasage : 0.85 capte beaucoup du signal et le ratio
est trop serré. **Je règle systématiquement, je ne suppose jamais que le défaut est neutre.**

## Distinguer crête et moyenne — le piège du master qui sature

Symptôme : « ça sature, j'ai baissé la batterie et j'ai perdu le reste ».

**La moyenne n'est presque jamais en cause.** Mesuré sur un Refrain à 4 pistes : RMS **−16,6 dBFS**
(marge énorme) avec 69 échantillons collés à 1.0 et un true peak à **+0,40 dBFS**. Baisser la piste
attaque le RMS : mauvais outil, et c'est pourquoi tout le reste s'affaiblit avec.

La parade est un **compresseur/limiteur sur le master**, qui traite la crête sans toucher à la
moyenne. Après l'avoir posé, on peut **remonter les pistes** : c'est tout l'intérêt.

Vérifier avant de conclure, ne pas supposer — le code de comptage est dans `limites-analyse`, qui
détaille aussi pourquoi un peak à 1.0 ne prouve rien.

## 2. Limiter true peak

`query:AudioFx#Limiter`, **après** le compresseur.

| Paramètre | Valeur |
|---|---|
| Lookahead | **3 ms** |
| Ceiling | **0.95** (≈ **−1 dB**) |

Le lookahead de 3 ms est ce qui permet au limiteur de voir la crête avant qu'elle arrive, donc de
l'écrêter proprement au lieu de la déformer.

## Le fader master reste à 1.0

**Le fader master est en aval des inserts.** Il doit rester à **1.0** pour que la chaîne atteigne
son plafond.

C'est contre-intuitif, et c'est une erreur classique : descendre le fader master « pour baisser un
peu » casse le travail du limiteur situé avant lui, et le résultat n'est plus le mix, c'est un mix
atténué. Pour baisser le mix, on baisse **les pistes**, pas le master. Voir `gain-staging`.

## Validation

- Le master ne clip pas : peak stable, pas de plateau.
- La dynamique du morceau respire encore après le glue.
- Le plafond est atteint : c'est le but d'un limiteur.
- **Vérifié sur les deux supports** — voir `mix-translation`.
