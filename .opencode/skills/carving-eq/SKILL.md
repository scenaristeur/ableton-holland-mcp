---
name: carving-eq
description: Use when two instruments fight each other, when the low end is muddy, or when a mix lacks presence or air. Covers the frequency masking map, how to decide which track gives way, the EQ Eight -> MEqualizer substitution on Live 12 Lite, and the rule of carving before compressing. Trigger words : masquage, ça se couvre, bourdon, lourd, presence, air, EQ, carver, sculpter les fréquences.
---

# Carving : dégager l'espace

## Carver avant de compressor

Si deux pistes se marchent dessus, la compression ne le résout pas — elle **renforce** le
problème, parce qu'elle colle exactement ce qui se recouvre. Donc : EQ d'abord, dynamique ensuite.

## La carte des fréquences

| Zone | Rôles qui s'y disputent | Gagnant typique |
|---|---|---|
| 50-100 Hz | kick vs basse | la basse garde, le kick s'accommode |
| 200-400 Hz | clavier / nappes / voix | celui qui porte la **mélodie** |
| 1-4 kHz | voix, lead, charley,+guitare | la **voix** et le lead |
| 5-8 kHz | cymbales, air, brillance | personne ne gagne : c'est de l'air pour tous |

La règle qui décide : **le contenu mélodique gagne**. La nappe cède devant la lead, la basse cède
partiellement devant le kick, tout le monde cède devant la voix.

## L'outil sur Live 12 Lite

`EQ Three` suffit pour du carving simple (3 bandes). Pour un EQ 8 bandes :
**`MEqualizer` (Melda) via URI**. **`EQ Eight` n'existe pas** dans cette installation — je ne
cherche pas son URI.

## Mapping du EQ Three (normalisé)

Les réglages d'EQ Three sont **normalisés 0-1**, pas en dB :

| Position | Signification |
|---|---|
| `0.85` | **flat** (neutre) |
| `1.0` | boost maximum |
| `0.0` | coupe maximum |

- **Coupes** : linéaires entre `0` et `0.85` — je règle entre `0.0` et `0.85`.
- **Boosts** : plage utile très étroite **`[0.98 … 1.0]`**.

Donc une coupe n'est jamais `0.5`, c'est beaucoup trop profond. La zone de coupe utile est
`0.3-0.8` ; la zone de boost utile est `0.98-1.0`.

## Valeurs par piste (validation Brain Stew)

Des exemples concrets, à adapter au morceau, pas à copier :

| Piste | Zone à dégager | Valeur indicative |
|---|---|---|
| Drums | grave / bourdon | `GainLo ≈ 0.6` |
| Rhodes | corps | `GainLo ≈ 0.7` |
| Pad | aigu / air | `GainHi ≈ 0.5` |
| Basse contrebasse/Sub | rendu audible | **Saturator + `GainMid 1.0`** (pas de transposition) |

Pour la basse sub (E1-C2 = 100 % sub inaudible) : ne **pas** transposer, rendre audible par
Saturator et boost `GainMid`.

## Vérifier une coupe

1. Je capture **avant**.
2. Je fais la coupe, je capture **après**.
3. Je compare — et je juge au mix, pas sur la piste seule.

Une coupe trop large ne se remarque pas sur la piste : elle ne s'entend que quand la piste revient
dans le contexte. Le RMS du solo ne dit rien de la qualité du carving. Voir `limites-analyse`.

## La règle anti-effet

Je ne carve pas pour « brighten » le son en général. Je carve parce qu'un rôle précis empiète sur
un autre. Sans conflit identifié, pas de coupe.
