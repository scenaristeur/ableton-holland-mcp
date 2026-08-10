# Surge XT — Presets Reproductibles & Sources

Dossier de référence pour **créer/charger des presets** Surge XT. Les presets ci-dessous sont des **candidats** (souvent multi-oscillateurs / gras) à ESSAYER — activez les oscillateurs/ring/noise supplémentaires si besoin (voir skill `surge-osc`, section "Activer toute l'architecture").

## Sources internet de presets reproductibles

| Source | Type | Lien / Note |
|---|---|---|
| **Syntorial — Preset Recipes** | Recettes pas-à-pas (% valeurs) | `syntorial.com/preset-recipe` — ex. brass de "Toto Africa" : saw 100%, LP, voicing, etc. |
| **Jon Audio — "Can it analog?" (2023)** | Vidéo recette lead analog Surge | classic saw + 3 voix unison + filtre Vintage Ladder + FEG + chorus/delay/reverb |
| **Idle Thoughts Music — Surge XT Oscillator Tutorial (2022)** | Vidéo les 13 oscillateurs | `.fl` détail des types osc, unison, sub, filtres per-osc |
| **Surge User Manual** | Doc officielle | `surge-synthesizer.github.io/manual-xt` |
| **John Valentine — Surge patches** | Patches d'auteur | `johnvalentine.co.uk` — trombone/trumpet/french horn/brass analog |
| **Surge Patch Database / Forums** | Communauté | recherche "Surge XT <instrument> patch" |

---

## ~20 presets à tester (en priorité les multi-osc)

### Leads
| Patch | Catégorie | Note |
|---|---|---|
| `Moogy Saw` | factory Leads | 3 saws, minimoog-ish, unison |
| `Classic Lead 2` | factory Leads | filtre Legacy Ladder, 3 oscs |
| `Prog Rock Octave Lead` | 3rdparty (Rozzer) Leads | lead octave, punchy |
| `Warehouse Lead` | 3rdparty (Kinsey) Leads | lead chaud |
| `Sync Sweep Lead` | 3rdparty (Dan Maurer) Leads | lead filtré évolutif |
| `Open Retro Lead` | 3rdparty (Vospi) Leads | lead rétro |

### Brass / Cuivres
| Patch | Catégorie | Note |
|---|---|---|
| `Bread & Butter Synth Brass` | 3rdparty (Kinsey) Keys | brass doux (déjà utilisé) |
| `Analog Brass` | 3rdparty (Luna) Brass | analogique |
| `Fat Brass` | 3rdparty (Luna) Brass | épais |
| `Orchestral Brass` | 3rdparty (John Valentine) Brass | section |
| `Toto Brass` | factory Brass | brass 80s |
| `Synth Brass 3` | factory Brass | brass synth |

### Basses
| Patch | Catégorie | Note |
|---|---|---|
| `Big Moog` | 3rdparty (Kuniklo) Basses | moog grasse |
| `Moogy` / `Moogish` | 3rdparty Basses | moog |
| `FM Bass 1` | factory Basses | basse FM |
| `Rubber Bass` | — | basse funk (si présente) |

### Claviers / Pads
| Patch | Catégorie | Note |
|---|---|---|
| `Polymoog` | factory Polysynths | pad gravifanalogique |
| `MKS-70 Warm Pad` | — | pad chaud (si présente) |
| `Brass Pad` | 3rdparty (Nick Moritz) Pads | pad cuivres |
| `Soft 80s Brass` | 3rdparty (Cybersoda) Brass | brass doux 80s |

> Ces candidats sont souvent paramétrés sur OSC1 uniquement : **penser à activer OSC2/OSC3, 1x2, 2x3, noise** (skill `surge-osc`).

## Workflow

1. `surge_search_patches(query)` pour localiser
2. `surge_load_patch(path)` (chemin sans extension, forward slashes)
3. `surge_get_patch()` pour confirmer
4. Activer les couches mixer manquantes (mute→0, volumes)
5. Sceller par captures + écoute (voir skill `analysis-tools` / `full-mix-workflow`)

---
Si trop compliqué à robotiser, on crée une **session dédiée "création de presets"** pour sculpter chaque patch à l'oreille.
