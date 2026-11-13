# Index des spectres de presets

**Ce que c'est.** La réponse mesurée des presets du navigateur à une **phrase de test fixe**. Il sert
à **présélectionner** un son *avant* de charger quoi que ce soit dans le morceau — donc sans
détruire l'instrument déjà en place.

**Ce que ce n'est pas.** Un juge. « Musical » n'est pas dans les chiffres. L'index **shortliste 3
candidats** ; l'oreille tranche. Et il mesure le preset **sec** : il prédit le point de départ, pas
le son sculpté.

## Protocole (à ne pas improviser)

Une mesure n'a de sens que si toutes les autres ont été faites pareil.

| Paramètre | Valeur |
|---|---|
| Phrase de test | `pique` (arpège court, percussif) ou `tenu` (accord tenu), selon le rôle |
| Vélocité | figée dans le clip de test |
| Fader de piste | **0.85** (l'unité) — relevé dans la colonne `fader` |
| Piste | une **piste de banc d'essai**, jamais une piste du morceau |
| FX de piste | aucune (le preset garde ses FX internes s'il en a) |
| Capture | `capture_and_analyze`, 8 s, en solo |
| Mesure | `scripts/spect.py` — **jamais** le RMS du tool d'analyse (il normalise) |

Une mesure hors protocole se marque dans `phrase` (ex. `clip-morceau-v0`) : elle n'est comparable
qu'aux lignes portant la même phrase **et** le même fader.

## Lecture des colonnes

- **`classe`** : *sombre* (< 1500 Hz), *medium* (1500-3000), *brillant* (> 3000). Le centroïde bouge
  de ±10 % entre deux captures du même son : on range en familles, on ne promet pas des hertz.
- **`b_10240-20000`** : ce qui « siffle / sonne sale ».
- **`b_1280-2560`** : ce qui « crie » (criard, agressif).
- **`b_2560-5120`** : ce qui « pique » (trop brillant).
- **`b_640-1280`** : le corps.
- **`hf4k_pct`** : énergie au-dessus de 4 kHz.
- **`crete`** (peak / rms) : dureté de l'attaque — bas = mou, haut = percussif.
- **`rms`** : niveau intrinsèque du preset à fader égal — indique de combien compenser.

## Comment on alimente

```powershell
.venv\Scripts\python.exe scripts\preset_index.py --famille "Guitar & Plucked" --role pluck `
    --phrase pique --fader 0.85 --prefix IDX_ data\analyses\IDX_Soft_Attention.wav
```

Le nom du preset est déduit du nom de fichier : `IDX_Soft_Attention.wav` → **Soft Attention**.
**Convention : un `_` entre chaque mot du nom du preset** (sinon l'index écrit « SoftAttention »).

L'outil **ajoute** les lignes à la suite ; il ne remplace pas et ne dédoublonne pas — une remesure
est une donnée.

## Contenu actuel

La famille **Guitar & Plucked** est amorcée avec 6 candidats mesurés **hors protocole**
(`clip-morceau-v0`, fader 0.68, sur le clip du morceau « Pas trop tard, Mary »). Ils sont
comparables **entre eux**, et c'est ce qui a fait retenir *Soft Attention*. À remesurer au protocole
standard le jour où on retravaillera un pluck.
