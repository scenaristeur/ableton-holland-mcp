---
name: fx-lite
description: Use when adding an audio effect to a track, return or master in this project. Lists the 18 effects actually available in Live 12 Lite, notes that EQ Eight and Drum Buss do not exist (use MEqualizer via URI, and Compressor instead), and gives the role of each effect in a mix. Trigger words : ajouter un FX, effet, réverb, delay, compresseur, saturator, EQ, limiter, Utility, AudioFx, Drum Buss, EQ Eight.
---

# Les 18 effets de Live 12 Lite

Disponibles via `query:AudioFx#<Nom>` — pas `query:Audio Effects#…`. Chargement sur une **piste** :

```
load_instrument_or_effect(track_index, "query:AudioFx#Reverb")
```

⚠️ **Sur master et return tracks, ce chargement time-out** : David dépose le device lui-même. Voir
`pieges-browser` pour l'URI exacte et les limites.

## La liste réelle

| Effet | Rôle dans le mix |
|---|---|
| **Utility** | Gain, trim, HPF, mono. L'outil le plus sous-estimé. |
| **Saturator** | Génère des harmoniques. **Indispensable sur la basse** (voir `mix-translation`). |
| **Reverb** | Profondeur, espace. En insert quand les returns sont vides. |
| **Compressor** | Dynamique, glue. **Remplace `Drum Buss`.** |
| **Limiter** | Master, true peak. |
| **EQ Three** | EQ basique, 3 bandes. Suffisant pour du carving. |
| **Channel EQ** | Variante, plus de bandes. |
| **Auto Filter** | Balayage, mouvement. |
| **Delay** | Écho, répétition. |
| **Chorus-Ensemble** | Élargissement, mouvement. |
| **Phaser-Flanger** | Modulation de phase. |
| **Redux** | Réduction destructive, couleur. |
| **Erosion** | Grain, bruit, matière. |
| **Beat Repeat** | Fragmentation rythmique. |
| **Auto Pan-Tremolo** | Mouvement stéréo. |
| **Auto Shift** | Décalage, phase. |
| **Tuner** | Accord, référence de hauteur. |
| **Audio Effect Rack** | Chaîne,FX groupé. |

## ⚠️ Ce qui n'existe pas

- **`EQ Eight` n'existe pas sur Live 12 Lite.** Pour un EQ 8 bandes : **`MEqualizer` (Melda) via
  URI**, ou `EQ Three` si le carving suffit.
- **`Drum Buss` ne répond pas à ce nom.** → utiliser `Compressor`.

Je ne cherche pas l'URI de l'un ou l'autre : c'est perdu d'avance, et David n'a ni l'un ni l'autre
dans sa production.

## Charger et vérifier

Les paramètres sont **normalisés 0-1**, et le mapping n'est pas vérifié. Donc :

1. Je lis d'abord (`get_device_parameters`) pour connaître les noms réels des paramètres.
2. Je mets la chaîne en **état transparent** et je vérifie que le son est propre et audible.
3. Je sculpte, et je recapture.

## Réverb : insert ou send

Voir `reverb-insert` pour la règle complète et les valeurs de départ.
