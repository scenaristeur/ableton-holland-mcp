---
name: reverb-insert
description: Use when adding depth, space or air to a track, or when a reverb return is empty. Covers why Reverb goes in as an insert rather than a send when the returns are unused, the Dry/Wet values that keep reverb from washing the mix out, and the per-source starting values. Trigger words : reverb, réverb, profondeur, espace, air, send, retour, return track, delay, profondeur.
---

# Réverb : insert ou send

## La règle

**Reverb en insert plutôt qu'en send quand les returns sont vides.**

C'est le cas le plus fréquent : les return tracks A et B sont libres, et un send obligerait à
créer, router et régler un return pour un son qui n'a besoin que d'une présence. En insert, la
réverb est attachée à la piste et se pilote avec elle.

Dès qu'un return **est** utilisé, on passe en send — parce que là, la reverb devient un bus commun,
et c'est ça qu'on veut.

## Le Dry/Wet par défaut est trop mou

Le Reverb sort à **0.55**, ce qui noie la source. Je descends systématiquement.

| Source | Dry/Wet | Room Size |
|---|---|---|
| Lead | 0.20 | 0.45 |
| Voix | 0.18 | 0.40 |
| Nappe / clavier | 0.25 | 0.50 |
| Batterie | **pas de reverb** | — |

La réverb **mange la grosse caisse**. Ne JAMAIS en mettre sur la batterie : elle efface l'attaque.

## Vérifier par capture

Charger `query:AudioFx#Reverb`, mettre l'état transparent, **vérifier que la source reste
audible**, puis descendre le Dry/Wet. Si la piste s'éloigne trop, c'est le Room Size qu'on
réduit, pas le Dry/Wet. Voir `sculpture-sonore` pour la règle générale.
