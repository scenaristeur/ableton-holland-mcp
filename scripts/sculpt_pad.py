"""Sculpt the pad (track 5) toward a grandiose, floating, light bed.
Detuned triangles + wide stereo + slow swell + a touch of air.
"""
import sys
sys.path.insert(0, "scripts")
import prep_mona_ia as p

PAD = {
    "Osc 1 Wave": 1.0, "Osc 1 Gain": 0.70, "Osc 1 Oct": 0.0,
    "Osc 2 Wave": 1.0, "Osc 2 Detune": 0.70, "Osc 2 Gain": 0.70, "Osc 2 Oct": 0.0,
    "Noise Gain": 0.08,
    "LP Freq": 0.55, "LP Res": 0.08,
    "Env 1 Attack": 0.40, "Env 1 Decay": 0.30, "Env 1 Sustain": 0.90, "Env 1 Release": 0.60,
    "Spread": 0.70, "Thickness": 0.45,
    "Volume": 0.45,
}
for name, val in PAD.items():
    p.must("set_device_parameter",
           {"track_index": 5, "device_index": 0, "parameter_name": name, "value": val})
print("[pad] grandiose/planant: triangles detunes, spread 0.7, swell lent, volume 0.45")