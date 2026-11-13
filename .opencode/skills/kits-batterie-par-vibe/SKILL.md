---
name: kits-batterie-par-vibe
description: Use when choosing a drum kit for a song, or when a groove needs a different kit to match a vibe (rock, pop, jazz, ambient, spoken word). Covers the ~200 available .adg kits, that they already play GM directly, how to load them, and the drum pad parameter drilling needed because .adg kits load as nested InstrumentGroupDevice. Also covers creating an adapted instrument by loading a library sample onto a specific pad (e.g. a missing crash), and saving tracks by grouping perc pads onto the drum kit. Trigger words : kit, batterie, drums, kit batterie, .adg, Drum Rack, vibe batterie, quel kit, sound de batterie, ajouter un pad, pad custom, cymbale, crash, échantillon sur un pad, créer un instrument, économiser une piste, regrouper percs.
---

# Kits batterie par vibe

Environ **200 kits `.adg`** sont disponibles. Ils sont **déjà remplis** et **jouent le GM
directement** — je n'ai pas à câbler 128 pads.

## Charger un kit

```
load_drum_kit(track_index, rack_uri="query:Drums#Drum%20Rack", kit_path="...")
```

ou plus direct, si j'ai l'URI du kit :

```
load_instrument_or_effect(track_index, "query:Drums#FileId_XXXX")
```

Pour découvrir les URI : `get_browser_items(path="drums")` — **pas** `get_browser_item`, qui
time-out.

## Les kits vérifiés de David

| Vibe | Kit |
|---|---|
| Organic / warm | `Selector Kit Warm.adg` |
| Général-purpose | `Gen Purpose Kit.adg` |
| Sec / naturel | `Dry Session Kit.adg` |
| Lo-fi | `Toy LoFi Kit.adg` |
| Hybrid studio | `Recording Hybrid Kit - Damped Snare.adg` |
| Rock punchy | `Gen Purpose Kit.adg` |
| Reggae / dub | `Selector Kit Warm.adg` |

## Choisir par vibe

Le kit suit la **vibe du morceau**, pas la mode. Je demande à David si j'hésite entre deux kits
qui servent tous les deux — c'est un choix qui s'entend, pas se mesure.

Signes qui orientent le choix :

- **Sec, proche, maîtrisé** → rock / indie. Peu de réverb, kit punchy.
- **Lourd, saturé, basse = colonne vertébrale** → metal / pop Powerful. Le kit et la basse doivent
  se renforcer, pas se masquer.
- **Sensible, acoustique, respirant** → jazz PMJ, folk. Petites surfaces, beaucoup de place.
- **Lointain, noyé, sans attaque** → ambient / pièces de décor. Le kit s'éloigne, devient un
  souffle.
- **Minimal, sec, une seule grosse caisse** → spoken word. La batterie ne doit jamais passer devant
  la voix.

## Percussions

Elles se jouent sur le kit GM. Je ne crée pas de piste perc séparée sauf si la vibe l'exige
(bongos, cajon, tabla, etc.) — auquel cas c'est une piste dédiée dans le budget 8.

## ⚠️ Économiser des pistes : regrouper les pads percus sur la batterie

Budget Live Lite = **8 pistes max**. Au lieu d'une piste `Percs` dédiée, on peut regrouper les
pads percussion/cymbale désirés **sur le kit de la batterie** (les pads libres du Drum Rack).
Ça **libère une piste** dans le budget 8. On garde une piste Percs séparée seulement si la vibe
l'exige (bongos, cajon, tabla) ou si le kit batterie manque de pads libres.

## Créer / fusionner un instrument adapté en recherchant des samples

On peut **customiser ou fusionner un rack** en cherchant des échantillons dans la bibliothèque
et en les posant sur des pads libres — un seul kit devient alors la somme des sons voulus.
Ex. le crash manquant (ni Toy LoFi ni Perc Kitchen n'en ont) se retrouve sur la piste Percu.

1. **Trouver l'échantillon** : `get_browser_items(path="samples")` liste les samples audio avec
   leur URI `query:Samples#FileId_XXXX`. Filtrer par nom (cymbale → `crash` / `ride` / `cymbal` /
   `splash`). ⚠️ **La sortie est énorme** : déléguer la recherche à un sous-agent qui grep le nom,
   ne pas lire tout le fichier.
2. **Le poser sur le pad** : ⚠️ **corrigé le 31/10/2026 — c'est scriptable, contrairement à ce
   que disait cette skill.** `load_instrument_or_effect(track_index, "query:Samples#FileId_XXXX")`
   sur une piste **Drum Rack** remplace le contenu du **pad sélectionné** dans Live. Le kit, les
   autres pads et la chaîne d'effets de la piste restent intacts (vérifié : `get_drum_pad_info`
   renvoie le nouveau nom du pad, `device_count` reste à 1, tous les autres pads inchangés).
   - Le pad reçoit alors un **Simpler**, pas un DrumSampler : ses paramètres sont **Volume,
     Transpose, Detune, Fade Out, Vol < Vel, Ve Release** — il n'y a **plus** de Tune/Level/Decay.
   - Le sample arrive à **Volume -12 dB** : il faut le remonter (0 dB = plein niveau) sinon il est
     inaudible dans le mix.
   - Si le mauvais pad est visé, `undo` est la sortie.
   - **Le chargement remplace le pad sélectionné dans la vue Drum Rack de Live.** Il n'y a aucun
     paramètre de pad sur l'outil, ni aucun outil de sélection : la cible est un état de l'interface.
     Sans clic de David sur le pad voulu, le chargement part sur le pad resté sélectionné (vérifié
     le 31/10/2026 : une Bell Tambo FX a écrasé le shaker du pad 42 parce que 42 était encore
     sélectionné). Pour un pad vide (ex. E2 = note 52), même règle : David le clique, puis je charge.
   - **Aucune vérification par script n'est fiable.** `get_drum_pad_info` et `get_drum_pad_parameters`
     continuent d'afficher le nom et les paramètres du kit d'origine (le Simpler vit *dans* le groupe
     de la chaîne, invisible), et `get_chain_info` ne montre que l'`InstrumentGroupDevice` externe.
     La seule vérification est **à l'oreille** ou par une capture solo du pad (le spectre et la
     décroissance trahissent le sample : shaker ≈ 180 ms / 1,5-4 kHz, cloche = partiels longs).
   - Le sample remplace le DrumSampler **à l'intérieur** du groupe : les anciens réglages
     Tune/Level/Decay ne s'appliquent plus, et les paramètres du Simpler (Volume -12 dB au départ)
     ne sont **pas accessibles** par les outils de pad. Prévoir le réglage de volume par David ou
     compter sur les vélocités.
3. **Le déclencher** : la note du pad joue le sample. L'écrire dans le clip au **pitch de ce pad**
   (E2 = 52), via `add_notes_to_clip` ou le générateur.

⚠️ Vérifier avec `get_drum_pad_info` le pad réellement rempli après le glisser (le piège des pads
s'applique toujours) et le mappage note → son avant d'écrire les notes.

> Convention du projet : **Ableton C3 = 60**, donc **E2 = 52** (et non 40, qui est la convention
> scientifique C4=60 — interdite, voir `fiche-technique`). Toujours vérifier le pitch réel d'un
> pad avec `get_drum_pad_info` avant d'écrire une note.

## ⚠️ Le piège des pads

Les kits Core Library se chargent comme un **`InstrumentGroupDevice` imbriqué**. Donc
`hasattr(device, "drum_pads")` **ment** sur ces kits.

Le Remote Script sait descendre. Pour lire ou écrire les paramètres d'un pad, j'utilise :

```
get_drum_pad_info(track_index, device_index)              pads remplis
get_drum_pad_parameters(track_index, device_index, note)   paramètres d'un pad (par note MIDI)
set_drum_pad_parameter(track_index, device_index, note, parameter_name, value)
```

Si je veux vraiment du bas niveau sur un pad, je descends dans la chaîne :
`chain_index` et `device_index_in_chain` sont disponibles sur les outils de pad.

## ⚠️ Un kit Core Library n'est pas le mappage GM du `.mid`

Quand je refais un `.mid`, le kit `.adg` **ne contient pas** les mêmes assignations que le
General MIDI du fichier. Il faut donc **remapper les pitches des pads** : identifier où la grosse
caisse et la caisse claire sont réellement chargées dans ce kit, et y router les notes du `.mid`.

C'est un piège silencieux : les notes arrivent, le son est audible, mais c'est la mauvaise
percussion. Voir `remake-midi`.

## Réglage au mix

La grosse caisse se place contre la basse, pas au-dessus. Voir `carving-eq`.
