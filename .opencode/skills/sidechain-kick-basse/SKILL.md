---
name: sidechain-kick-basse
description: Use when the bass pumps or muddies over the kick, when the kick and bass fight in the low end, or when a sidechain ducking effect is wanted. Covers the sidechain kick-to-bass compressor workflow, the exact routing (Drums / Post FX), the S/C parameters, and the starting values. Trigger words : sidechain, ducking, pump, kick, basse, grosse caisse, Compressor S/C, sidechain compress, esquive la basse.
---

# Sidechain kick → basse

Le sidechain fait **s'effacer la basse à chaque kick**, pour que la grosse caisse passe sans se
battre avec elle. C'est un effet à la fois fonctionnel (le kick ressort) et musical (le pump).

## Le workflow, dans l'ordre

1. **Compressor sur la basse** :

```
load_instrument_or_effect(track_index_basse, "query:AudioFx#Compressor")
```

2. **Router l'input** vers la piste Drums, en Post FX :

```
set_track_input_routing(track_index_basse, routing_type="Drums", channel="All Channels")
# + input_sub_routing = "Post FX"
```

3. **Activer le sidechain** sur le Compressor :

```
set_device_parameter(track_index_basse, device_index, "S/C On", 1)
```

## Les valeurs de départ

| Paramètre | Valeur |
|---|---|
| `S/C EQ Type` | `0` (Low Shelf) ou `5` (High pass) |
| `Ratio` | ≈ `0.9` |
| `Threshold` | ≈ `0.5` |
| `Release` | ≈ `0.35` |

Le `S/C EQ Type` sert à dire au compresseur **quelle partie du signal sidechain** déclencher :
Low Shelf si on veut réagir au grave du kick, High pass pour un sidechain plus aigu/agressif.

## Règles

- **On sculpte après le sidechain, pas avant.** Un EQ ou un saturateur posé avant change ce que le
  compresseur voit.
- **Le sidechain n'est pas un EQ.** Il règle la *relation temporelle* kick/basse ; il ne règle pas
  le masquage statique. Pour ça, voir `carving-eq`.
- Capturer et écouter : le pump doit être **discret**, pas un trou. Si la basse « halète », baisser
  le Ratio ou remonter le Threshold.

Voir `sculpture-sonore` pour la règle générale (état transparent avant de régler).