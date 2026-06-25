# Plus T'as d'Argent (Moins Tu Sais Faire de Choses) — Rapport de production

**Tempo :** 89 BPM (réglé après analyse)  
**Clé :** E mineur (dorian)  
**Pistes :** 7 après suppression de la 4-Audio  

---

## Ce qui a été fait

### Session
- Création de 8 pistes MIDI (Batterie, Basse, 2× Audio, Guitare Skank, Rhodes, Lead Synth, Pad)
- Suppression de la piste « 4-Audio » (devenue index 3, mute — l'API MCP ne permet pas la suppression)
- Instruments chargés :
  - 1-Batterie : Dry Session Kit
  - 2-Basse : Dub Techno Bass (Drift)
  - 5-Guitare Skank : Guitar Electric Clean (rack)
  - 6-Rhodes : E-Piano Classic (rack)
  - 7-Lead Synth : Surge XT (VST3)
  - 8-Pad : Warm Analog Pad (rack)

### Effets chargés
| Piste | Effets |
|-------|--------|
| Batterie | Auto Filter, Compressor, Saturator |
| Basse | Channel EQ, Saturator |
| Guitare Skank | Saturator |
| Rhodes | Saturator |
| Lead Synth | Reverb, Saturator |
| Pad | Delay, Saturator |

### Clips Session créés
- **Batterie :** Couplet Beat, Refrain Beat, Pont Beat, Outro Beat, Transition Fill
- **Basse :** Couplet Bass, Refrain Bass, Pont Bass
- **Guitare Skank :** Couplet Skank, Refrain Skank
- **Rhodes :** Refrain Rhodes, Pont Rhodes
- **Lead Synth :** Refrain Lead, Solo Lead
- **Pad :** Refrain Pad, Pont Pad

### Arrangement (≈ 80 bars)
Tous les clips dupliqués de la Session vers l'Arrangement aux bonnes positions :
- Intro → Couplet 1 → Refrain 1 → Couplet 2 → Refrain 2 → Pont → Solo → Couplet 3 → Refrain final → Outro

### Transitions
- **9 fills de batterie** ajoutés 1 barre avant chaque changement de section (caisse claire 8e, kick, crash) pour fluidifier les enchaînements.

### Analyse audio (15s)
- Tempo détecté : 89.1 BPM → projet réglé à 89 BPM
- Clé : E minor ✓
- Dynamic range : 58 dB (large — compression master recommandée)
- Tuning : 0.03 cents (parfait)
- Spectral centroid : 934 Hz (dominante médium-grave, signature analogique)

---

## Suggestions manuelles (à faire dans Live)

### 1. « Analogiser » le mix
| Piste | Action |
|-------|--------|
| **Saturator (toutes pistes)** | Ouvrir chaque dispositif, mode **« A Bit Warmer »** ou **« Studio Tape »**, Drive ≈ 2‑5 dB, Output ≈ -2 dB |
| **Master** | Ajouter un **Limiter** (Audio Effect → Limiter), Threshold ≈ -6 dB, Output ≈ -0.5 dB |
| **Volume des pistes** | Monter jusqu'à RMS ≈ -12 dBFS (actuellement trop bas) |
| **Auto Filter (Batterie)** | Ajuster la fréquence de coupure (120‑150 Hz) avec LFO slow pour le caractère « dub » |
| **Compressor (Batterie)** | Threshold ≈ -18 dB, Ratio ≈ 4:1, Attack ≈ 10 ms, Release ≈ 100 ms |
| **Channel EQ (Basse)** | Coupe basse à 40 Hz, boost ≈ 3 dB à 80 Hz |
| **Reverb (Lead Synth)** | Mode « Hall », pré‑delay ≈ 30 ms, decay ≈ 2.5 s, mix ≈ 30 % |
| **Delay (Pad)** | Temps ≈ 1/8, feedback ≈ 35 %, mix ≈ 25 % |

### 2. Surge XT — Réglages du Lead Synth
Si vous gardez Surge XT, appliquez dans l'interface Live :
- **Osc1 :** Saw +1 oct, level 0.75
- **Osc2 :** Square, detune +0.02, level 0.45
- **Noise :** Enable, level 0.08
- **Filter :** LP24, cutoff ≈ 3 kHz, resonance 0.15, drive 0.10
- **Envelope 1 (AMP) :** A 0.02s, D 0.30s, S 0.70, R 0.25s
- **Envelope 2 (FILTER) :** A 0.10s, D 0.45s, S 0.60, R 0.30s
- **LFO 1 → Filter Cutoff :** Sine, sync 1/4, amount 30 %
- **FX Rack :** Reverb Hall (size 0.55, decay 2.3s, mix 0.22), Delay Stereo 1/8 (feedback 0.35, mix 0.20)

### 3. Transitions
Si besoin d'enrichir les transitions :
- Ajouter une **Auto Filter sweep** 1 barre avant les changements de section (automation manuelle du cutoff)
- Créer un **riser** (hat roll + reverb croissant) sur une piste audio dédiée

### 4. Export
1. **File → Export Audio/Video**
2. Plage d'arrangement : début (0) → fin (≈ 352 beats)
3. Format : WAV 44.1 kHz / 24-bit (ou MP3 320 kbps)

---

## Ce qu'il reste à faire

### Prioritaire
- [ ] Ajuster les paramètres des effets (Saturator, Compressor, EQ, Reverb, Delay) dans Live
- [ ] Régler **Surge XT** selon le patch ci-dessus (ou le remplacer par un instrument natif si trop complexe)
- [ ] Ajouter un **Limiter** sur le Master
- [ ] Monter le **volume des pistes** pour atteindre un RMS plus élevé

### Améliorations supplémentaires
- [ ] Créer un **send Reverb global** (return track) pour harmoniser l'espace
- [ ] Ajouter des **sweeps / risers** aux transitions (automation Auto Filter)
- [ ] Enregistrer une **prise audio vocale** ou ajouter des samples (fx dub)
- [ ] Exporter le rendu final (WAV)

### Analyse avancée
- [ ] Capturer un segment plus long (30‑60 s) pour vérifier la cohérence sur l'ensemble
- [ ] Analyser beat track / chroma CQT / MFCC pour affiner l'arrangement
- [ ] Comparer le spectre avec un morceau de référence reggae/dub

---

## Problèmes techniques rencontrés
- **Timeout MCP (-32001)** : les fonctions `capture_ableton` et `load_instrument_or_effect` peuvent timeout si la durée est longue. Solution :
  - `capture_ableton` : utiliser `duration ≤ 15 s` pour éviter le timeout
  - `load_instrument_or_effect` : réessayer si timeout
  - Voir https://mcpcat.io/guides/fixing-mcp-error-32001-request-timeout

- **set_arrangement_time imprécis** : la fonction ne positionne pas le curseur exactement à la valeur demandée (décalage systématique). Contournement : utiliser `start_playback()` puis régler ou capturer à la position courante.

- **Suppression de piste** : l'API Ableton MCP ne permet pas de supprimer une piste — la solution est de la mettre en mute et de vider ses clips (si applicable).
