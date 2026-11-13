---
name: master-chain
description: Use when finishing the mix, on the master track, or when the output clips, lacks loudness, or lacks cohesion. Covers Compressor glue then Limiter true peak, Lookahead 3 ms, Ceiling 0.95 (about -1 dB), and the rule that the master fader must stay at 0.85 (unity in this build — 1.0 is +6 dB and breaks the ceiling because the fader sits after the inserts). Trigger words : master, limiter, limiteur, glue, plafond, saturation, crête, clipping, volume final, -1 dB.
---

# Chaîne master

Deux devices, dans cet ordre. Pas trois, pas un.

## 1. Compressor glue

`query:AudioFx#Compressor`, chargé **sur le master**. Rôle : coller les éléments en un tout, pas
serrer la dynamique.

✅ **Je peux le charger moi-même** : `load_instrument_or_effect_on_master({ uri: "query:AudioFx#Compressor" })`.
(La note « time-out, demander à David » était **fausse** — corrigée le 23/10/2026, voir `pieges-browser`.)

⚠️ **Le device est ajouté en fin de chaîne**, et il n'existe **aucun outil pour réordonner ou
supprimer un device du master**. Donc **je charge le Compressor AVANT le Limiter**, jamais l'inverse.
Si l'ordre est cassé, c'est à David de glisser le device (ou de supprimer le dernier chargé pour que
je recharge la paire dans le bon ordre).

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

## Le fader master reste à 0.85 — l'unité, pas 1.0

**Le fader master est en aval des inserts.** Il doit rester à **0.85**, qui est **l'unité (0 dB)**
dans cette installation — la même échelle que les pistes (`gain-staging`). Le fader est donc
transparent et la chaîne atteint exactement son plafond.

⚠️ **Mesuré le 23/10/2026, l'ancienne note « le fader master reste à 1.0 » était fausse.** Sur le
refrain final :

| Fader master | RMS | Peak | Écrêtés |
|---|---|---|---|
| **0.85** | 0.158 | **0.936** | **0** ✅ |
| 1.00 | 0.314 | 1.000 | **196** ❌ |

1.0 = **+6 dB**. Comme le fader est *après* le limiteur, monter à 1.0 pousse tout le signal 6 dB
au-dessus du plafond de 0.95 : le limiteur ne sert plus à rien et on écrête. **Ne pas monter le
fader master pour gagner du niveau** — pour ça on remonte **les pistes**, et le limiteur suit.
Voir `gain-staging`.

## Validation

- Le master ne clip pas : peak stable, pas de plateau.
- La dynamique du morceau respire encore après le glue.
- Le plafond est atteint : c'est le but d'un limiteur.
- **Vérifié sur les deux supports** — voir `mix-translation`.
