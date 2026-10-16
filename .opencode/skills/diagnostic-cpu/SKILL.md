---
name: diagnostic-cpu
description: Use when Ableton drops out, stutters, clicks, or when a "thunder" boom is heard at the end of a bar, or when asked whether a track is too heavy. Covers why the idle CPU figure is too noisy to trust, the measure-while-playing one-solo-at-a-time method, why mute does not reduce load, and that Surge XT is almost always the culprit. Trigger words : CPU, saturation, dropout, claquement, tonnerre, saccade, ràlements, lag, trop gourmand, poids.
---

# Diagnostic CPU

## Le symptôme à surveiller

**CPU qui sature = dropout audible en fin de mesure**, un « tonnerre ». C'est le signal d'alerte en
jeu. Si David l'entend, on mesure.

## Le CPU au repos ne sert à rien

Le CPU global au repos est **trop bruité (±5 points)** pour isoler une piste. Comparer deux
lectures à l'arrêt n'a aucune valeur.

La méthode fiable :

1. **Je fais jouer la section qui pose problème.**
2. **Une piste solo à la fois**, je lis le CPU.
3. Je **gèle le coupable** et je revérifie.

C'est plus long, mais c'est la seule méthode qui isole vraiment une cause.

## Mute ne réduit pas la charge

**Muter une piste n'allège rien** : l'instrument reste chargé et continue de calculer. Pour
économiser du CPU, il faut :

- `disable_device` sur le device coûteux, ou
- `freeze_track` pour la piste.

⚠️ **Freeze bloque l'édition du clip.** Je gèle pour mesurer, je dégèle pour travailler.

## Le coupable habituel

**Surge XT est presque toujours la cause.** Voir `surge-cpu-par-voix` pour pourquoi et quoi faire.

## Outils

```
get_cpu_load()                    moyenne + pic en %, RAM du process
get_cpu_report()                  CPU et RAM globaux + diagnostic par piste
get_track_diagnostics(track_index) états des devices, RAM, drapeaux rack
```

Je ne compare jamais deux lectures prises dans des conditions de jeu différentes. Même section,
même volume, sinon la comparaison ne veut rien dire.
