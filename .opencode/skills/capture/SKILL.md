---
name: capture
description: Use when recording audio from Ableton to measure or verify what is playing. Covers the VB-Cable routing, why only one capture runs at a time, the capture_and_analyze tool (the two other capture tools are disabled), which moments to capture, and the mandatory RMS check. Trigger words : capture, capturer, enregistrer, mesurer, VB-Cable, VB-Cable, analyse audio, RMS, vérifier le son.
---

# Capture

## Le routage

La capture passe par **VB-Cable** : ce qui sort d'Ableton est aussi capturé. Rien à configurer à
chaque fois.

## L'outil

Un seul outil de capture est actif :

```
capture_and_analyze(position_beats, duration_sec, output_name)
```

`capture_ableton` et `capture_at_position` existent dans le serveur mais sont **désactivés**. Je ne
les appelle pas.

## Une seule capture à la fois

**Je lance une capture et j'attends la réponse** avant d'en lancer une autre. Deux captures qui se
chevauchent se battent sur la position de lecture et les deux résultats sont faux.

## Quoi capturer, et combien longtemps

Aux **moments clés** : début de couplet, refrain, pont. **5 à 10 secondes suffisent** — je n'ai pas
besoin de la pièce entière pour répondre à une question de mix.

## Toujours vérifier le RMS

**Une capture « réussie » peut être du silence.** Avant d'interpréter quoi que ce soit, je regarde
le RMS. Un RMS nul ou quasi nul signifie que le signal n'est pas passé, pas que le mix est creux.

**Le peak est toujours 1.0** : l'interface VB-Cable sature. Le peak ne m'apprend donc rien. Je
juge sur RMS, centroid, rolloff et dynamic range.

## Où commence la capture

`position_beats` ne déplace que le playhead de l'**arrangement**. L'enregistrement commence à la
**position courante du song**, pas à 0 : la réponse contient `seek.position` (en beats). Pour situer
une mesure dans le WAV capturé :

```
beat_clip = t_rec × BPM / 60 + seek.position
```

Et attention à la durée : le champ `duration_s` de la réponse est l'**étendue du song** pendant
l'enregistrement (72 s pour 36 s demandés, à cause des loops de clip session), alors que le
**fichier WAV écrit** fait la durée demandée. C'est le WAV qui fait foi.

## Si la capture est muette

`CABLE_DEVICE_ID` est **figé au démarrage**. Si VB-Cable a été ajouté ou modifié après le lancement,
la seule correction est de **redémarrer le serveur MCP**. Je ne tourne pas en rond avant ça.

Voir `limites-analyse` pour ce que les chiffres signifieront vraiment une fois la capture faite.
