---
name: mix-translation
description: Use when a mix works on studio monitors but fails on a phone, in a car, or on FOH speakers, or when the low end disappears. Covers the Saturator-on-bass trick that generates virtual sub harmonics, the 150-200 Hz high-pass rule, the frequency masking map, and the two opposed targets. Trigger words : téléphone, phone, autoradio, FOH, grosse enceinte, sub, caisson, grave disparaît, multi-support, traduction, mix ne passe pas.
---

# Mix multi-support

## Les deux cibles sont opposées

| | FOH (avec sub) | Téléphone |
|---|---|---|
| Sous 150 Hz | caisson, tout s'entend | **rien** — pas de haut-parleur |
| Compression | légère possible | lourde, automatique |
| Détail | disponible | aucun |
| Stéréo | large | proche, mono à l'oreille |

C'est **la** difficulté du projet, et la source de presque tous les arbitrages.

## L'astuce du saturateur sur la basse

**C'est l'outil le plus important du mix.**

Sous 150 Hz, un téléphone ne rend rien. Ce qui passe, ce sont les **harmoniques**. Donc :

1. **Saturateur sur la basse** pour générer ces harmoniques — des « sous virtuels ».
2. La basse garde son poids sur FOH, **et** elle se fait entendre sur téléphone.

Sans ça, il faut choisir un support. Avec ça, le mix existe sur les deux.

C'est aussi pourquoi la saturation n'est pas qu'une question de couleur : c'est une question de
**traduction**. Voir `sculpture-sonore` pour la mise en place sans casser le signal.

### Réglage du Saturator basse

| Paramètre | Valeur |
|---|---|
| Type | **Medium Curve** (`3`) |
| Drive | **0.60-0.80** |
| Dry/Wet | **1.0** |

### Compression drums (le complément du côté rythme)

| Paramètre | Valeur |
|---|---|
| Threshold | `0.30` |
| Ratio | ~`4:1` |
| Attack | `0.10-0.15` |
| Model | Peak |
| Makeup | On |

## Cibles de niveau (volume balancing)

| Élément | RMS cible |
|---|---|
| Lead / voix | ~`0.07-0.10` |
| Mix complet | ~`0.17-0.25` |

## LUFS par plateforme

| Plateforme | Loudness cible |
|---|---|
| Spotify | **-14** LUFS |
| YouTube | **-13** LUFS |
| TikTok | ~**-14** LUFS |

## Passe-haut

**150-200 Hz sur tout sauf le kick et la basse.** Sur téléphone, ce grave inutile mange la place et
comprime le reste. Sur FOH, il double la grosse caisse.

## Carte de masquage

Les fréquences à surveiller, celles où les rôles se marchent dessus :

| Zone | Conflit typique |
|---|---|
| 50-100 Hz | kick vs basse |
| 200-400 Hz | clavier / nappes, zone de la chaleur |
| 1-4 kHz | présence : voix, lead, charley |
| 5-8 kHz | air, cymbales, brillance |

Le carver de cette carte s'applique à l'étape 2 — voir `carving-eq`.

## Ce que je vérifie à la fin

Le mix sur **le mix complet**, pas sur une piste solo. Puis je demande à David de l'écouter sur
**ses deux supports** avant de considérer la validation acquise. Je ne peux pas écouter moi-même :
la validation est à lui.
