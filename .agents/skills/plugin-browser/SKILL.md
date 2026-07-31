---
name: plugin-browser
description: Navigation du browser Ableton pour trouver et charger instruments, effets et kits. URIs, FileIds, catégories, chemins VST.
---

# Plugin Browser — Navigation Ableton

## Principes

Le browser Ableton s'interroge via `get_browser_items`, `get_browser_tree`, `get_browser_categories`, et `get_browser_item`. Les instruments et effets se chargent via `load_instrument_or_effect(track, uri)`.

## URIs browser

### Synthés natifs
```
query:Synths#Wavetable
query:Synths#Analog
query:Synths#Drift
query:Synths#Operator
query:Synths#Electric
query:Synths#Tension
query:Synths#Collision
```

### Audio Effects (FX)
```
query:AudioFx#Utility
query:AudioFx#Saturator
query:AudioFx#Reverb
query:AudioFx#Compressor
query:AudioFx#Limiter
query:AudioFx#EQ%20Eight    # ne marche pas toujours — utiliser plugins VST à la place
```

**Drum Buss ne marche pas par ce nom.** Utiliser `Compressor` à la place.

### Packs Core Library (Sounds)
```
query:Sounds#Piano%20&%20Keys
query:Sounds#Strings
query:Sounds#Pad
query:Sounds#Guitar%20&%20Plucked
query:Sounds#Bass
query:Sounds#Synth%20Lead
query:Sounds#Synth%20Keys
```

### Drums
```
query:Drums#Drum%20Rack          # device vide — DrumGroupDevice
query:Drums#FileId_XXXX          # preset kit — InstrumentGroupDevice
```

**Important :** les kits `.adg` du Core Library se chargent comme `InstrumentGroupDevice` (pas `DrumGroupDevice`). Ils sont pré-remplis avec sons GM (36=Kick, 38=Snare, 42=HH...). `get_drum_pad_info` ne marche QUE sur les `DrumGroupDevice` vides.

### Plugins externes (VST3)
```
plugins/VST3/<Vendor>/<PluginName>
query:Plugins#VST3:<Vendor>:<PluginName>
```

### Chemins de navigation

```python
get_browser_items_at_path("Sounds/Bass")           # lister les presets
get_browser_item(path="drums/Gen Purpose Kit.adg") # trouver FileId
get_browser_categories(category_type="instruments") # all, instruments, sounds, drums, audio_effects, midi_effects
get_browser_tree(category_type="all")               # arbre complet
```

## Trouver un FileId

```python
result = get_browser_item(path="drums/<Nom>.adg")
# réponse : { "item": { "uri": "query:Drums#FileId_XXXX" } }
```

Utiliser cet URI dans `load_instrument_or_effect` pour charger le kit.

## Vérifier les plugs externes

```python
list_external_plugins(query="Surge", max_results=50, refresh_cache=False)
# refresh_cache=True pour rescanner le browser
get_browser_items(path="plugins/VST3/<Vendor>")   # lister les plugs d'un vendor
```

## Limitations

- Les sous-chemins comme `query:Sounds#Piano%20&%20Keys:FileId_XXXX` chargent des **presets**, pas des devices
- `query:Drums#Drum%20Rack` charge le device vide — utile pour construire un rack from scratch
- Pour les plugins VST3 avec nombreux paramètres, `get_device_parameters` peut ne retourner que les paramètres exposés à l'API
