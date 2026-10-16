---
name: pieges-browser
description: Use when loading ANY instrument, effect or kit by URI, and above all when a load FAILS or times out — including load_instrument_or_effect_on_master, which does not work from MCP (verified), and load_instrument_or_effect_on_return_track (same suspicion). Also covers why get_browser_item times out, the exact URI spellings (query:AudioFx# — not "query:Audio Effects#"), that load_external_plugin loses the vendor segment, and that list_external_plugins returns browser categories rather than plugins. Trigger words : load_instrument_or_effect, load_instrument_or_effect_on_master, load_instrument_or_effect_on_return_track, AudioFx, query:AudioFx#, get_browser_item, get_browser_items, time-out, timeout, ne se charge pas, rien chargé, master, return track, browser, URI, query:, charger un plugin, charger un effet, coller un device.
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

## ⚠️ `load_instrument_or_effect_on_master` time-out

Le chargement d'un effet **natif sur le master** ne passe pas par MCP : trois tentatives, trois
timeouts, **master toujours vide** ensuite.

```
load_instrument_or_effect_on_master("query:AudioFx#Glue Compressor")  ❌ timeout, rien chargé
```

Le même timeout sur `get_browser_item(uri=...)` et `get_browser_items(path=...)` alors que
`get_session_info` et `get_track_info` répondent — c'est le **browser** qui est lent, pas Ableton.

**Procédure** : je demande à David de déposer le device sur le master, je vérifie avec
`get_master_track()`, puis je règle avec `get_master_device_parameters` /
`set_master_device_parameter`. Même règle probable sur les returns
(`load_instrument_or_effect_on_return_track`) : demander à David.

Ne jamais réessayer en variant l'URI : le timeout ne vient pas de l'URI.

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
