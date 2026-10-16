"""Give the EP (track 3) more personality: electric-piano character.
Second detuned oscillator (the tine/bell shimmer), a touch of noise for the
percussive hammer attack, a bit of thickness. Kept from the working state.
"""
import sys
sys.path.insert(0, "scripts")
import prep_mona_ia as p

EP = {
    "Osc 1 Wave": 1.0, "Osc 1 Gain": 0.60, "Osc 1 Oct": 0.0,
    "Osc 2 On": 1.0, "Osc 2 Wave": 1.0, "Osc 2 Detune": 0.45,
    "Osc 2 Oct": 1.0, "Osc 2 Gain": 0.30,
    "Noise On": 1.0, "Noise Gain": 0.07,
    "LP Freq": 0.65, "LP Res": 0.05,
    "Env 1 Attack": 0.01, "Env 1 Decay": 0.30, "Env 1 Sustain": 0.28, "Env 1 Release": 0.30,
    "Thickness": 0.30,
    "Volume": 0.55,
}
for name, val in EP.items():
    p.must("set_device_parameter",
           {"track_index": 3, "device_index": 0, "parameter_name": name, "value": val})
print("[ep] caractere Rhodes: 2e osc detune, hammer, thickness")