# FICHE TECHNIQUE - Pas trop tard, Mary

**Date :** 2026-10-16
**BPM :** 94
**Signature :** 4/4
**Tonalité :** **D majeur** (convention inchangée)
**Convention Ableton :** C3 = 60 (pitch réel)
**Mise à jour :** application de la vraie montée du pré-refrain + charley ouverte correctement ringante

## Structure (11 sections - brief R&B)

| Scène | Section | Mesures | Remarques |
|---|---|---|---|
| S1 | Intro | 4 (16 temps) | Pad large, Rhodes subtil, Pluck |
| S2 | Couplet 1 | 8 (32 temps) | Batterie minimale, basse sobre, guide vocal (8èmes) |
| S3 | Pré-refrain | 8 (32 temps) | **Montée réelle** - Caisse claire en 16ème sur la mesure 8, kick creusé sur les temps 3-4 de la mesure 8, charley ouverte aux temps 2 et 4 des mesures 4 et 8, pad qui gonfle, charley ouverte nettoyée (closed retiré aux moments d'open). |
| S4 | Refrain 1 | 8 (32 temps) | Tous les instruments |
| S5 | Pont 1 | 4 (16 temps) | Dépouillement |
| S6 | Couplet 2 | 8 (32 temps) | Variante harmonique |
| S7 | Pré-refrain | 8 (32 temps) | Reprise montée |
| S8 | Refrain 2 | 8 (32 temps) | Plein + breakdown fin possible |
| S9 | Pont 2 | 8 (32 temps) | Plus long, espace |
| S10 | Refrain 3 (final) | 8 (32 temps) | Intense |
| S11 | Outro | 4 (16 temps) | Dissipation vers silence |

## Grille harmonique

### Couplet 1
`Dmaj7 – A/C# – Bm7 – G6/9 | Dmaj7 – A/C# – Em7 – A7sus4` (1 accord/mesure, 8 mesures)

### Pré-refrain (S3)
`Em7 – A7 – F#m7 – Bm7 | Em7 – A7 – Dmaj7 – A/C#` (1 accord/mesure, 8 mesures)

## Pistes

| Index | Piste | Type | Device/Kit | Remarques |
|---|---|---|---|---|
| 0 | 1-Batterie | MIDI | Selector Kit Warm (.adg) | Groove = Swing MPC 3000 16ths 57, groove_amount 0.70. **Pad 42 (charley fermée)**: Sample=96. **Pad 46 (charley ouverte)**: Sample=112 (longue queue). Closed retiré aux t=13,15,29,31,31.5 (S3). Roulement 16ème m8 + kick creusé t=30-32 (S3). |
| 1 | 2-Basse | MIDI | Analog Bass | Saturator: Bass Shaper (Type 2) Drive 0.35, D/W 1.00. |
| 2 | 3-Claviers | MIDI | E-Piano Rhodish | Saturator Soft Sine (Type 1) Drive 0.28 D/W 0.60, Auto Filter HP 0.30. |
| 3 | 4-Pad | MIDI | Warm Analog Pad | Auto Filter HP 0.30, EQ Three GainMid 0.70, vol 0.44 (monte progressivement S3). |
| 4 | 5-Pluck | MIDI | Soft Attention | Auto Filter HP 0.22, vol 0.53 pan +0.20 (intro) |
| 5 | 6-Lead | MIDI | Homebound Lead | Saturator Type 1 Drive 0.40 D/W 0.70, Auto Filter HP 0.28 |
| 6 | 7-Guide | MIDI | Blushed (Synth Lead) | Fader 0.60. Guide vocal posé en **croches** (64 notes sur 8 mesures), chaque vers chanté 2× (selon préférence). |
| 7 | 8-Audio | AUDIO | Enregistrement vocal | Fader 0.85. Uni +0.0 |

## Mesures (captures propres)

| Section | centroid (Hz) | HF>4k (%) | corps 640-1280 (%) | rms | peak | crete |
|---|---|---|---|---|---|---|
| Intro (validée, S1) | 2579 | 20.9 | 17.0 | 0.0319 | 0.199 | - |
| Couplet 1 (S2, final) | 3526 | 37.5 | 4.9 | 0.0418 | 0.2542 | 6.1 |
| Pré-refrain (S3, final) | 4074 | 43.8 | 4.6 | 0.0457 | 0.2543 | 5.6 |

**Constat S3 final :** montée réelle, anneau de la charley ouverte audible (Sample=112, closed retiré aux moments d'open), peaks sous contrôle.

## Notes de production
- Tessiture mélodie : 57–67 (A2-G3). Reste telle qu'écrite (fiche du brief) — à vérifier avec David au refrain (qui monte à 78 = F#4).
- Charley fermée : Sample 96 (measuré) — présence optimale sur ce kit.
- Charley ouverte : Sample 112 (measuré) — l'anneau sonne (boucle de la décroissance propre). Retrait du closed aux temps 2/4 mesures 4 et 8, et sur l'anticipation mesure 8 (t=29,31,31.5) + mesure 4 (t=13,15).
- Batterie S3 : caisse claire en 16ème mesure 8, kick creusé sur temps 3-4 de la mesure 8.
- Pad S3 : gonfle progressivement (velocities 58→79) sur les 8 mesures.
- Guide : version à l'ancienne préférée (croches) — appliquée au couplet et au pré-refrain.
- Geste de montée : événementiel (non graduel) — ça se sent bien maintenant.

## À faire
- Scene 4 = **Refrain 1** (8 mesures) : déployage de tous les instruments, vérifier la mélodie du refrain (tessiture 57–78).
- Audit mensuel charley ouverte : garder Sample 112 (7 autres valeurs scannées : 0/16/32/48/64/80/96 — 112 donne la plus longue queue).
- Si la basse manque de corps sur téléphone, appliquer recette Saturator (Type Medium Curve 3, Drive 0.6–0.8, D/W 1.0) comme indiqué dans mix-translation.
