---
name: pieges-browser
description: Use when loading ANY instrument, effect or kit by URI, and above all when a load FAILS or times out — including load_instrument_or_effect_on_master, which DOES work (corrected 23/10/2026 : it appends to the end of the chain, and there is no tool to reorder or delete a master device). Also covers why get_browser_item times out, the exact URI spellings (query:AudioFx# — not "query:Audio Effects#"), that load_external_plugin loses the vendor segment, and that list_external_plugins returns browser categories rather than plugins. Trigger words : load_instrument_or_effect, load_instrument_or_effect_on_master, load_instrument_or_effect_on_return_track, AudioFx, query:AudioFx#, get_browser_item, get_browser_items, time-out, timeout, ne se charge pas, rien chargé, master, return track, browser, URI, query:, charger un plugin, charger un effet, coller un device.
---

# Pièges : browser

## ⚠️ `get_browser_item` time-out sur les synthés

**Utiliser `get_browser_items`**, qui renvoie toute la subtree avec les bons URI et ne time-out pas.

```
get_browser_items(path="instruments")
get_browser_items(path="drums")
get_browser_items(path="audio_effects")
```

C'est la seule façon fiable de découvrir un URI. J'ai perdu du temps à chercher des URI
d'instruments qui **n'existent pas dans cette installation** — voir `palette-live-lite` pour la liste
réelle avant de chercher.

## Charger

```
load_instrument_or_effect(track_index, uri)
```

Puis je vérifie avec `get_track_info(track_index)` que le device est bien là. Un chargement qui
échoue en silence est pire qu'une erreur visible.

## ⚠️ L'URI des effets audio s'écrit `AudioFx`, sans espace

Le browser **affiche** « Audio Effects », mais l'URI est `query:AudioFx#…`. Pas
`query:Audio Effects#…`, pas `query:AudioFX#…`.

```
query:AudioFx#Compressor      ✅
query:AudioFx#Reverb          ✅
query:Audio Effects#Compressor ❌ timeout
```

J'ai écrit le mauvais et perdu troisEssais. Ce bon patron était **déjà écrit** dans `fx-lite` et
`master-chain` : le lire avant de charger, ou le lire **après** s'il a échoué.

Pour découvrir la liste, `get_browser_items(path="Audio Effects")` échoue aussi. Passer par :

```
get_browser_categories(category_type="audio_effects")   # → uri "query:AudioFx"
```

## ✅ `load_instrument_or_effect_on_master` MARCHE (corrigé le 23/10/2026)

**L'ancienne note « timeout, ne marche pas » était fausse.** David l'a contestée, j'ai testé :

```
load_instrument_or_effect_on_master({ uri: "query:AudioFx#Limiter" })     → {loaded:true, item_name:"Limiter"}
load_instrument_or_effect_on_master({ uri: "query:AudioFx#Compressor" })  → {loaded:true, item_name:"Compressor"}
get_master_track() → devices: ["Limiter", "Compressor"]   ✅
```

L'URI est bien `query:AudioFx#NomDuDevice`. Les anciens timeouts venaient probablement du nom
« Glue Compressor » (device qui **n'existe pas** dans Live 12 Lite — voir `fx-lite`), pas du master.

⚠️ **Le device est TOUJOURS ajouté en fin de chaîne.** Il n'existe **aucun outil pour réordonner ou
supprimer un device du master** : `delete_device` refuse le master (`track_index` -1, 8, 9 → « Track
index out of range »), et il n'y a ni `move_device` ni `insert_device`. Donc pour une chaîne à deux
devices dans l'ordre (ex. Compressor puis Limiter), **je charge le premier d'abord**.

Si l'ordre est déjà cassé, deux options, toutes deux à demander à David : glisser le device dans la
bonne position, ou **supprimer le dernier chargé** pour que je recharge la paire dans le bon ordre.
Ensuite je règle avec `get_master_device_parameters` / `set_master_device_parameter`.

Même famille d'outils sur les returns : `load_instrument_or_effect_on_return_track` — à tester avant
de dire qu'il ne marche pas.

## ⚠️ `load_external_plugin` ne marche pas de façon fiable

Il **perd le segment vendor** dans l'URI. Le plugin est trouvé, l'URI est fausse. Passer par l'URI
du browser, toujours.

## ⚠️ `list_external_plugins` ne liste pas des plugins

Cette fonction renvoie des **catégories de browser**, pas des plugins installés. Prendre son
résultat pour une liste de plugins conduit à chercher des choses qui n'existent pas.

## Ce qui est vérifié

- Instruments natifs : **6 seulement**. Voir `palette-live-lite`.
- Effets audio : **18**. Voir `fx-lite`.
- Kits `.adg` : **~200**.
- `query:Sounds#…` : 17 familles de sons, dont beaucoup de familles « Suite » existent comme
  **son** et pas comme device.
- `query:Drums#Drum%20Rack` et `query:Drums#FileId_XXXX` : les deux URI de base qui répondent.
