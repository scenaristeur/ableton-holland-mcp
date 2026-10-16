"""Sculpt the 4 non-FX Drift instruments by musical role (step 2, Mon IA Lisa).

Each track's device 0 is a Drift. We shape the exposed parameters per role:
  bass   -> sub + harmonic grit, dark, held
  ep     -> keys: short attack, medium decay, warm
  arp    -> pluck: saw, very fast attack, short decay, snappy filter
  pad    -> sustained, detuned, slow attack, warm + air
"""
import sys
sys.path.insert(0, "scripts")
import prep_mona_ia as p


def setp(track, **params):
    for name, val in params.items():
        p.must("set_device_parameter",
               {"track_index": track, "device_index": 0, "parameter_name": name, "value": val})


def patch(track, params):
    print(f"[sculpt] track {track} <- {params['_role']}")
    params.pop("_role")
    setp(track, **params)


patch(1, {
    "_role": "basse (sub + grit, sombre)",
    "Osc 1 On": 1.0, "Osc 1 Wave": 0.0, "Osc 1 Oct": 0.0, "Osc 1 Gain": 0.80,
    "Osc 2 On": 1.0, "Osc 2 Wave": 3.0, "Osc 2 Oct": 1.0, "Osc 2 Gain": 0.25,
    "Osc 2 Detune": 0.20,
    "Noise On": 0.0,
    "LP Freq": 0.35, "LP Res": 0.12,
    "Env 1 Attack": 0.01, "Env 1 Decay": 0.30, "Env 1 Sustain": 0.80, "Env 1 Release": 0.25,
    "Env 2 Attack": 0.05, "Env 2 Decay": 0.25, "Env 2 Sustain": 0.60, "Env 2 Release": 0.30,
    "Volume": 0.60,
})

patch(3, {
    "_role": "clav EP (attaque courte, chaud)",
    "Osc 1 On": 1.0, "Osc 1 Wave": 1.0, "Osc 1 Oct": 0.0, "Osc 1 Gain": 0.80,
    "Osc 2 On": 0.0,
    "Noise On": 0.0,
    "LP Freq": 0.60, "LP Res": 0.05,
    "Env 1 Attack": 0.01, "Env 1 Decay": 0.35, "Env 1 Sustain": 0.30, "Env 1 Release": 0.35,
    "Volume": 0.55,
})

patch(4, {
    "_role": "arp/hook (pluck, decay court)",
    "Osc 1 On": 1.0, "Osc 1 Wave": 4.0, "Osc 1 Oct": 0.0, "Osc 1 Gain": 0.80,
    "Osc 2 On": 1.0, "Osc 2 Wave": 0.0, "Osc 2 Oct": -1.0, "Osc 2 Gain": 0.30,
    "Noise On": 0.0,
    "LP Freq": 0.65, "LP Res": 0.20,
    "Env 1 Attack": 0.0, "Env 1 Decay": 0.22, "Env 1 Sustain": 0.0, "Env 1 Release": 0.18,
    "Volume": 0.55,
})

patch(5, {
    "_role": "nappe (tenue, detune, air)",
    "Osc 1 On": 1.0, "Osc 1 Wave": 1.0, "Osc 1 Oct": 0.0, "Osc 1 Gain": 0.70,
    "Osc 2 On": 1.0, "Osc 2 Wave": 1.0, "Osc 2 Detune": 0.60, "Osc 2 Gain": 0.70,
    "Noise On": 1.0, "Noise Gain": 0.15,
    "LP Freq": 0.45, "LP Res": 0.10,
    "Env 1 Attack": 0.35, "Env 1 Decay": 0.30, "Env 1 Sustain": 0.90, "Env 1 Release": 0.50,
    "Spread": 0.50, "Thickness": 0.40,
    "Volume": 0.60,
})

print("[sculpt] done: 4 Drift sculptes (basse, EP, arp, nappe)")