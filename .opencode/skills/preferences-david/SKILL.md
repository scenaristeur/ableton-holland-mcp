---
name: preferences-david
description: Use when making any creative or technical choice for this project, to stay aligned with David's profile. Covers who David is (baryton, C#m, native-first, not a plugin collector), his 8-track project budget, his mix targets (big FOH speakers with sub AND phone), and the fact that production skills are project-specific. Trigger words : préférences, profil de David, natives, plugins, multi-support, téléphone, grosse enceinte, FOH, budget de pistes.
---

# Préférences de David

## Qui il est musicalement

- **Baryton.** E3-B3 = MIDI 64-71. Si la mélodie sort, je signale, je ne force pas.
- **Tonalité préférée : Do#m.** Secondaire : **Em**.
- **Voix parlé-chanté, nonchalante et cynique** — influences Gainsbourg, Desproges.
- **Style : pop organique.** timbres chauds, instruments naturels, **pas d'EDM**.
- **Langue : français**, sauf demande contraire.

### Références

Pink Floyd, Morcheeba, Prince, Deep Purple, Ben Harper, indie rock français, Gainsbourg, analog pop.

Le morceau de référence pour la couleur vocale est
`data/tests/01- Masculiniste-Emotionnel-Indie-Rock.mp3` : voix chaude et basse dans le timbre,
large dans l'expression, bien accordée.

⚠️ Ses chiffres d'analyse sont à prendre comme des **tendances**, pas comme des valeurs : voir
`limites-analyse`.

## Comment il veut travailler

- **Native-first.** Ce n'est pas un collectionneur de plugins : je compose d'abord avec ce que
  l'install contient. Voir `palette-live-lite` et `choix-instrument-par-role`.
- **Une action à la fois**, validée à l'oreille. Jamais de rafale d'outils.
- **2-3 options concrètes** quand il y a un choix artistique. Pas un menu de 20.
- **Je ne prétends pas entendre.** Je dis « selon la capture » et je demande validation.

## Le mix doit sonner sur deux extrêmes

**Grosses enceinte de FOH (avec sub)** ET **téléphone** (pas de sub sous 150 Hz, compression
lourde, aucun détail). Ce sont deux cibles opposées — c'est *la* difficulté du projet.

- Sur FOH : le grave existe, la basse est ronde, la largeur compte.
- Sur téléphone : le sub disparaît, il ne reste que les harmoniques. D'où le saturateur sur la
  basse comme outil principal du mix. Voir `mix-translation`.

## Budget du projet

**8 pistes maximum, 16 scènes maximum par piste.** Une piste = un rôle. Au-delà, le mix devient
illisible et le CPU sature. Si une idée ne tient pas en 8 pistes, elle doit être un *rangement*, pas
une piste de plus.

Les return tracks (A et B) ne sont pas des pistes de production.

## Ce qui passe en premier : le natif

Un kit `.adg` déjà rempli plutôt qu'un Drum Rack câblé à la main. Voir
`kits-batterie-par-vibe`.

## Les chaînes FX historiques, corrigées

David avait des chaînes écrites pour une installation plus riche. **Elles ne sont pas applicables
telles quelles** — plusieurs devices n'existent pas ici :

| Source | Chaîne d'origine | Ce qui est réellement possible |
|---|---|---|
| Batterie | Drum Buss → Compressor → Reverb | **Compressor** → Reverb en send |
| Basse | Amp → Compressor → Saturator | **Saturator** → Compressor |
| Piano / claviers | Reverb → Chorus → Compressor | **Reverb** (insert) → Chorus → Compressor |
| Pad | Reverb → Auto Filter → Delay | **Reverb** (insert) → Auto Filter → Delay |
| Lead | Delay → Reverb → Auto Filter | **Delay** → Reverb (insert) → Auto Filter |
| Voix | EQ Eight → Compressor → Reverb → Delay | **EQ Three** → Compressor → Reverb → Delay |
| Percussions | Reverb (send) → Saturator | **Reverb** (send) → Saturator |
| FX | Reverb → Delay → Grain Delay → Auto Filter | **Reverb** → Delay → Auto Filter |

`Drum Buss`, `Amp`, `EQ Eight` et `Grain Delay` **n'existent pas** dans cette installation. Voir
`fx-lite` et `palette-live-lite`.

Et même pour une chaîne qui n'utilise que des devices existants : **on ne la colle pas telle
quelle.** Voir `sculpture-sonore`.

### Les variantes Rock / Reggae

Historiquement, David déclinait ses chaînes par style. Corrigées pour cette install :

**Rock :**
- Drums : **Compressor** → Saturator
- Guitare : **Saturator** → Compressor
- Basse : **Saturator** → Compressor

**Reggae / dub :**
- Drums : **Compressor** → Reverb (spring) → Delay
- Basse : **Saturator** → Compressor
- Guitare / claviers : Chorus → Reverb → Delay
- Voix : **EQ Three** → Compressor → Reverb → Delay

Références Rock : Pink Floyd, Deep Purple, Ben Harper, indie rock français.
Références Reggae : Morcheeba, Prince (groove).

## Native avant Surge

Surge XT est le **dernier recours** : c'est le plus gros consommateur de CPU de l'install. Je
structure le morceau avec du natif, et je ne configure une instance Surge qu'ensuite, à la main.
Voir `surge-cpu-par-voix`.

## Ces skills sont propres à ce projet

Les skills de production vivent dans `.opencode/skills/` du dépôt, pas dans `~/.agents/skills/`.
Ils décrivent **cette** installation (Live 12 Lite, 8 pistes, VB-Cable, les kits de David) et ne
sont pas réutilisables tels quels ailleurs. Les skills purement techniques et indépendants de
l'install restent au niveau utilisateur.
