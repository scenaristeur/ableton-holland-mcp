---
name: limites-analyse
description: Use when interpreting any number returned by the analysis tools (tempo, key, centroid, spectral values, durations), and when a capture shows clipping. Covers which figures are trustworthy and which are wrong because of a false sample rate, why a centroid change is meaningful but its absolute Hz value is not, why RMS alone never decides a mix, and why a peak at 1.0 does NOT prove saturation — only samples glued flat do. Trigger words : analyse, métriques, chiffres, hertz, BPM, centroid, key detection, tonalité, est-ce que c'est bon, RMS, peak, energy_peak, true peak, saturation, sature, clipping, écrêtage, interpréter.
---

# Limites des outils d'analyse

## Les chiffres absolus sont faux

Les durées, le BPM et les valeurs en Hz sont calculés sur une **base de temps et un sample-rate
faux** (les analyses sont codées pour `sr = 22050` alors que les captures sont à 48 kHz).

Conséquence : **« centroid 226 → 791 Hz » est un signal fiable**, parce que c'est une comparaison
à sample-rate constant. Mais **« 791 Hz » n'est pas une fréquence réelle.** Je ne présente jamais
un chiffre de ce type comme une vérité absolue, et je ne le compare jamais à une cible ni à un
autre outil.

Je m'en sers pour comparer des **tendances**, pas pour valider un mix.

## Ce qui est fiable

- La **détection de tonalité**.
- Les **niveaux** : RMS, peak, dynamic range.

## Le RMS seul ne fait pas foi

**Une basse solo à RMS 0.34 peut être inaudible dans le contexte.**

Je vérifie toujours **le mix complet**, pas la piste solo. Le solo sert à isoler et comprendre ; la
décision se prend sur l'ensemble.

## Un peak à 1.0 ne prouve PAS une saturation

`energy_peak: 1.0` est **normal** pour un mix bien masterisé : une crête légitime atteint 1.0 sans
qu'il y ait le moindre écrêtage. Prendre ce chiffre pour une saturation conduit à baisser les pistes
pour rien.

Ce qui prouve l'écrêtage, ce sont des échantillons **collés** : plusieurs d'affilée, à 1.0 exact.

```python
n_clipped = int(np.sum(np.abs(x) >= 0.9999))          # nombre d'échantillons collés
tp = np.max(np.abs(scipy.signal.resample_poly(x, 4, 1)))  # true peak, ≠ peak sur échantillon
```

Un run de plusieurs échantillons iguais à 1.0 = le signal a été **coupé**, pas simplement élevé.
Le true peak suréchantillonné dépasse le peak échantillon parce que le DAC reconstruit le signal entre
deux échantillons — c'est lui qui decides si le matériel downstream crête.

## ⚠️ Ne pas confondre moyenne et crête

Repère mesuré (Refrain, 4 pistes) : RMS **−16,6 dBFS** — marge énorme — avec 69 échantillons collés à
1.0 et un true peak à **+0,40 dBFS**. La saturation était **ponctuelle**, la moyenne était largement
saine.

Conséquence pratique : baisser une piste pour « ça sature » attaque le RMS et **affaiblit tout le
reste** sans toucher au problème. Le bon levier est un compresseur/limiteur **sur le master**, puis on
**remonte les pistes** — voir `master-chain`.

## Repères d'interprétation (ordres de grandeur)

Ces valeurs sont des **fourchettes** pour lire une capture, pas des cibles absolues :

| Métrique | Plage typique |
|---|---|
| energy_rms | 0.10-0.20 |
| Dynamic range | 10-15 |
| Centroid (relatif) | 700-900 |
| Rolloff | 1200-2500 |
| ZCR | 0.02-0.06 |

À comparer toujours à la même capture dans les mêmes conditions.

## Comment je rapporte

En **langage musical**, jamais en chiffres bruts :

- ❌ « RMS 0.12, dynamic range 8.1 »
- ✅ « la voix se fait eaten par la caisse, et le refrain n'a plus d'air »

Puis je demande validation à David, parce que je **ne prétends pas entendre**.

Voir `capture` pour la capture elle-même.
