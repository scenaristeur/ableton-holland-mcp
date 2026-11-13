---
name: split-clavier-economie-pistes
description: Use when the 8-track Live Lite budget is full and a track is needed for audio (vocal, guitar...), or when two instrument tracks do the same job and can share one. Covers merging two instruments into one Instrument Rack with Key Zones, the Surge XT internal key split (fully scriptable), the trap of dragging a device onto an existing chain, the per-instance Surge master volume, and how to prove which chain actually plays. Trigger words : plus de piste, manque de piste, économiser une piste, split, splitter le clavier, key zone, Instrument Rack, deux chaînes, fusionner deux pistes, piste audio, 8 pistes, budget de pistes.
---

# Splitter un clavier pour économiser une piste

## Le problème

Live 12 Lite plafonne à **8 pistes**. Quand le morceau est plein et qu'il faut une piste
**audio** (voix, guitare, réverbe imprimée), on n'a plus de place. Deux issues :

1. supprimer un rôle — coûteux musicalement ;
2. **faire cohabiter deux instruments sur une seule piste**, séparés par une **Key Zone** : c'est
   la hauteur de la note qui décide quel instrument sonne.

C'est la solution à privilégier quand deux pistes font **le même métier**. Exemple validé :
**nappe (pad tenu) + orgue (accord tenu)** — elles se remplacent plus qu'elles ne s'additionnent.

## Le principe, et sa conséquence

Une Key Zone sépare les instruments **par registre**. Donc :

- l'instrument qui va dans l'aigu doit être **réécrit une octave au-dessus** ;
- l'autre garde son registre d'origine ;
- les deux partagent **le même clip** : un clip par scène et par piste, donc les notes des deux
  instruments vivent dans le même clip, séparées par la hauteur.

C'est souvent un **gain musical** : un orgue dans l'aigu traverse un refrain bien mieux qu'au
milieu du clavier.

## Méthode A — Instrument Rack à deux chaînes (interface)

⚠️ **Les Key Zones ne sont pas réglables par l'API.** Aucun outil ne les expose. C'est un geste de
David, à lui demander explicitement.

Ce que je fais : je charge les instruments, je prépare les notes dans les bons registres, je règle
les FX et les volumes. Ce qu'il fait : les deux zones.

### ⚠️ Le piège des deux chaînes

Un Instrument Rack démarre avec **une seule chaîne**. Si on glisse un device **sur la chaîne
existante**, Live le **remplace** — l'utilisateur voit « Surge écrase Organ Plush » et croit que
deux instruments sont impossibles.

Il faut créer la deuxième chaîne d'abord :

- glisser le device sur la zone vide **« Drop Area to create a new chain »**, tout en bas de la
  liste des chaînes ;
- ou **clic droit dans la zone des chaînes → « Create Chain »**, puis glisser le device dedans.

### L'ordre des chaînes n'a aucune importance

Chaîne 1 = orgue et chaîne 2 = pad, ou l'inverse : seule la **Key Zone** compte. Ne pas faire
perdre du temps à David pour réordonner.

### Les zones (exemple validé)

| Chaîne | Instrument | Zone |
|---|---|---|
| 1 | Orgue | **C4 → G8 (72 → 127)** |
| 2 | Pad | **C-2 → B3 (0 → 71)** |

Split à **C4 = 72**. Le pad garde 48-69, l'orgue est réécrit en 72-84.

## Méthode B — split interne Surge XT (tout scriptable, zéro geste)

Surge a **deux scènes** et sait les séparer au clavier. C'est le seul moyen de faire un split
**sans toucher à l'interface** :

- `scene_mode = 1` → **Key split** (`0` = Single, `2` = Dual, `3` = Channel split) ;
- charger un patch n'écrit que dans la **scène A** et **remet `scene_mode` à 0** → on charge
  d'abord, on pose `scene_mode` **après** ;
- pour mettre deux **presets différents** en A et B : instantané `surge_query_all` sur A →
  charger le second patch → rejouer l'instantané sur `/param/b/*` → `scene_mode = 1`.

Procédure complète et pièges : `surge-cpu-par-voix`. En échange, l'orgue devient un orgue Surge
(`Organ 1`, `Rotary Blue`) et non plus un preset natif.

⚠️ L'OSC doit être activé par David **pour cette instance** — je ne peux pas le faire. Voir
`surge-presets`.

## ⚠️ Le piège du volume global Surge

Deux instances du **même patch** ne sonnent pas au même niveau. Mesuré sur ce projet, la
nappe MKS-70 Warm Pad :

| Instance | `/param/global/volume` | RMS solo |
|---|---|---|
| 0 (ancienne piste) | 0.9578 | 0.172 |
| 1 (dans le rack) | **0.5507** | **0.029** |

**~15 dB d'écart** pour un patch identique. La cause n'est ni le filtre, ni la Key Zone : c'est le
**volume global de l'instance**. Je l'aligne sur l'instance de référence dès que j'installe un
instrument dans un rack.

## Vérifier que le split marche vraiment

Trois contrôles, dans cet ordre :

1. **Solo de la piste fusionnée, scène 1** (l'instrument grave) → capturer, noter RMS + centroïde.
2. **Solo de la piste fusionnée, scène de l'instrument aigu** → capturer. Les deux mesures doivent
   être **nettes et différentes** (ex. pad 0.159 / 345 Hz, orgue 0.053 / 3947 Hz).
3. **Test décisif** si un doute subsiste : couper **un seul** instrument par OSC
   (`surge_set_param("/param/a/amp/volume", 0.001)`) et recapturer. Si le son disparaît, c'est
   bien cette chaîne qui jouait. Remettre la valeur d'origine ensuite
   (`surge_get_param` avant la coupure).

Un `RMS` qui s'effondre sans que le timbre change = **niveau**, pas routage. Un `RMS` qui s'effondre
**et** un centroïde qui s'envole = il ne reste que des transitoires (voir `sculpture-sonore`).

## Après la fusion

- **Renommer** la piste avec les deux rôles : `5-Nappe/Orgue`.
- **Récupérer les FX de piste** de la piste supprimée (chorus, reverb en insert) — ils ne suivent
  pas automatiquement le rack.
- **Supprimer la piste devenue vide** avec `delete_track`, puis **renuméroter** les préfixes pour
  que l'ordre reste lisible (voir `conventions-nommage`).
- **Noter le split dans la fiche technique** : c'est une décision de production, pas un détail.

## Quand ne pas le faire

Si les deux instruments jouent **en même temps dans le même registre**, un split les casse : il
faut un rack **sans** Key Zone (les deux chaînes sur toute l'étendue) ou deux pistes. Le split ne
sert que quand les rôles sont **séparés dans le temps ou dans le registre**.
