# Surge XT (and FX) 1.3 — OSC Specification

> **Emplacement de Surge XT dans Ableton (browser) :** Plugins → **Surge Synth Team** → **Surge XT** (VST3).
> URI : `query:Plugins#VST3:Surge%20Synth%20Team:Surge%20XT` — charger avec `load_instrument_or_effect(track_index, "<URI>")`.
> **Ne pas utiliser** `load_external_plugin()` : buggé (crash `'dict' object has no attribute 'lower'` dans `list_external_plugins`).

OSC messages use the exact (case-sensitive) entry in the **Address** column.
Form: `/<address> <value>`. Values can be:
- a float between **0.0** and **1.0** bounding the parameter range (use `.`, never `,`)
- an integer
- a boolean (0=false, 1=true)
- a file path
- contextual (int or float depending on loaded oscillator/effect)

Out-of-range values are clipped.

> **Important:** all numeric values must be sent over OSC as **floating point** numbers,
> even for int/bool typed parameters (the 'Appropriate Values' column describes how Surge uses the data).

**OSC Output:** parameter/patch/tuning/modulation changes are reported to OSC out when enabled;
floats reported 0.0-1.0 followed by a display string. Errors go to `/error`.
**Examples are shown in red** in the original and marked `ex:` here.

**Format examples:** `ex: /mnote 68 120`, `ex: /fnote 440.0 120`, `ex: /mnote 68 0`.

## Notes


| Address | Description | Value 1 | Value 2 | Value 3 |
|---|---|---|---|---|
| /mnote | MIDI-style note | note number (0 - 127) | velocity (0.0 - 127.0)* | noteID (optional, 0 - maxint)§ |
| /fnote † | frequency note | frequency (8.176 - 12543.853) | velocity (0.0 - 127.0)* | noteID (optional, 0 - maxint)§ |
| /mnote/rel | MIDI-style note release | note number (0 - 127) | release velocity (0.0 - 127.0) | noteID (optional, 0 - maxint)§ |
| /fnote/rel | frequency note release | frequency (8.176 - 12543.853) | release velocity (0.0 - 127.0) | noteID (optional, 0 - maxint)§ |
| /allnotesoff | release all current notes | (none) | (none) | (none) |
| /allsoundoff | stop all sound NOW | (none) | (none) | (none) |


## Note Expressions


| Address | Description | Value 1 | Value 2 |
|---|---|---|---|
| /ne/pitch | pitch note expression | noteID (0 - maxint)§ | pitch offset (-120.0 - 120.0: semitones) |
| /ne/volume | volume note expression | noteID (0 - maxint)§ | volume multiplier (0.0 - 4.0) |
| /ne/pan | pan note expression | noteID (0 - maxint)§ | position (0.0 - 1.0: 0.0 = left 0.5 = center 1.0 = right) |
| /ne/timbre | timbre note expression | noteID (0 - maxint)§ | timbre (0.0 - 1.0) |
| /ne/pressure | pressure note expression | noteID (0 - maxint)§ | polyphonic aftertouch (0.0 - 1.0) |


## MIDI-type controllers


| Address | Description | Value 1 | Value 2 | Value 3 |
|---|---|---|---|---|
| /pbend | pitch bend | channel (0 - 15) | pitch offset (-1.0 - 1.0) |  |
| /cc | control change | channel (0 - 15) | controller # (0 - 127) | value (0 - 127) |
| /chan_at | channel aftertouch | channel (0 - 15) | value (0 - 127) |  |
| /poly_at | polyphonic aftertouch | channel (0 - 15) | note # (0 - 127) | value (0 - 127) |


## Patches


| Address | Description | Appropriate Values |
|---|---|---|
| /patch/load | load patch | file path (absolute, no extension) |
| /patch/load_user | load patch from user patch directory | file path (relative to user patch dir, no extension, overwrites if file exists) |
| /patch/save | save patch | none: overwrites current patch or file path (absolute, no extension, overwrites if file exists) |
| /patch/save_user | save patch to user patch directory | file path (relative to user patch dir, no extension, overwrites if file exists) |
| /patch/incr | increment patch | (none) |
| /patch/decr | decrement patch | (none) |
| /patch/incr_category | increment category | (none) |
| /patch/decr_category | decrement category | (none) |
| /patch/random | choose random patch | (none) |


## Tuning


| Address | Description | Appropriate Values |
|---|---|---|
| /tuning/scl | .scl tuning file | file path (absolute or relative)* |
| /tuning/kbm | .kbm mapping file | file path (absolute or relative)* |
| /tuning/path/scl | .scl file default path | file path (absolute only) |
| /tuning/path/kbm | .kbm file default path | file path (absolute only) |


## Wavetables


### Replace '<s>' with 'a' or 'b' (scene) and <n> with '1' through '3'
                                   (oscillator #)


| Address | Description | Appropriate Values |
|---|---|---|
| /wavetable/<s>/osc/<n>/id | select wavetable by id | int (0 - # of wavetables)* |
| /wavetable/<s>/osc/<n>/incr | increment wavetable |  |
| /wavetable/<s>/osc/<n>/decr | decrement wavetable |  |


## Queries


### Replace '<s>' with 'a' or 'b' (scene) and <n> with '1' through '3'
                                   (oscillator #)


| Address | Description | Action |
|---|---|---|
| /q/patch | request current patch | Sends the full path (minus extension) of the current patch to OSC out |
| /q/all_params | request all parameters | Sends a dump of all parameters and their values, extended options (if any), and /doc messages to OSC out |
| /q/<parameter address> | request one parameter | Sends one parameter's value, extended options (if any), and /doc message to OSC out |
| /q/all_mods | request all modulation mappings | Sends a dump of all active modulation mappings and 'muted' status to OSC out |
| /q/mod/<modulation mapping> | request one modulation mapping's depth | Sends one modulations mapping's depth to OSC out |
| /q/mod/mute/<modulation mapping> | request one modulation mapping's mute status | Sends one modulation's mute status to OSC out |
| /q/wavetable/<s>/osc/<n> | request wavetable info for specified scene and oscillator | Sends id and name of specified wavetable to OSC out |
| /q/tuning/scl | request current tuning | Sends full path (minus extension) of current .scl tuning to OSC out |
| /q/tuning/kbm | request current keyboard mapping | Sends full path (minus extension) of current .kbm mapping to OSC out |


## Parameters


## Control Group: Macros


| Address | Description | Appropriate Values |
|---|---|---|
| /param/macro/1 | macro 1 | float (0.0 - 1.0) |
| /param/macro/2 | macro 2 | float (0.0 - 1.0) |
| /param/macro/3 | macro 3 | float (0.0 - 1.0) |
| /param/macro/4 | macro 4 | float (0.0 - 1.0) |
| /param/macro/5 | macro 5 | float (0.0 - 1.0) |
| /param/macro/6 | macro 6 | float (0.0 - 1.0) |
| /param/macro/7 | macro 7 | float (0.0 - 1.0) |
| /param/macro/8 | macro 8 | float (0.0 - 1.0) |


## Control Group: Global


### Replace '<s>' with 'a' or 'b' (scene)


| Address | Parameter Name | Appropriate Values |
|---|---|---|
| /param/<s>/amp/gain | VCA Gain | float (0.0 to 1.0) |
| /param/<s>/amp/pan | Pan | float (0.0 to 1.0) |
| /param/<s>/amp/vel_to_gain | Velocity > VCA Gain | float (0.0 to 1.0) |
| /param/<s>/amp/volume | Volume | float (0.0 to 1.0) |
| /param/<s>/amp/width | Width | float (0.0 to 1.0) |
| /param/<s>/filter/2/link_resonance | Link Resonance | boolean (0 or 1) |
| /param/<s>/filter/2/offset_mode | Filter 2 Offset Mode | boolean (0 or 1) |
| /param/<s>/filter/balance | Filter Balance | float (0.0 to 1.0) |
| /param/<s>/filter/config | Filter Configuration | integer (0 to 7) |
| /param/<s>/filter/feedback | Feedback | float (0.0 to 1.0) |
| /param/<s>/filter/keytrack_root | Keytrack Root Key | integer (0 to 127) |
| /param/<s>/highpass | Highpass | float (0.0 to 1.0) |
| /param/<s>/mixer/noise/color | Noise Color | float (0.0 to 1.0) |
| /param/<s>/octave | Octave | integer (-3 to 3) |
| /param/<s>/osc/drift | Osc Drift | float (0.0 to 1.0) |
| /param/<s>/osc/fm_depth | FM Depth | float (0.0 to 1.0) |
| /param/<s>/osc/fm_routing | FM Routing | integer (0 to 3) |
| /param/<s>/pitch | Pitch | float (0.0 to 1.0) |
| /param/<s>/pitchbend_down | Pitch Bend Down Range | integer (0 to 24) |
| /param/<s>/pitchbend_up | Pitch Bend Up Range | integer (0 to 24) |
| /param/<s>/play_mode | Play Mode | integer (0 to 5) |
| /param/<s>/portamento | Portamento | float (0.0 to 1.0) |
| /param/<s>/send/1/level | Send FX 1 Level | float (0.0 to 1.0) |
| /param/<s>/send/2/level | Send FX 2 Level | float (0.0 to 1.0) |
| /param/<s>/send/3/level | Send FX 3 Level | float (0.0 to 1.0) |
| /param/<s>/send/4/level | Send FX 4 Level | float (0.0 to 1.0) |
| /param/<s>/waveshaper/drive | Waveshaper Drive | float (0.0 to 1.0) |
| /param/<s>/waveshaper/type | Waveshaper Type | integer (0 to 42) |
| /param/fx/chain_bypass | FX Chain Bypass | integer (0 to 3) |
| /param/fx/send/1/return | Send FX 1 Return | float (0.0 to 1.0) |
| /param/fx/send/2/return | Send FX 2 Return | float (0.0 to 1.0) |
| /param/fx/send/3/return | Send FX 3 Return | float (0.0 to 1.0) |
| /param/fx/send/4/return | Send FX 4 Return | float (0.0 to 1.0) |
| /param/global/active_scene | Active Scene | integer (0 to 1) |
| /param/global/character | Character | integer (0 to 2) |
| /param/global/polyphony_limit | Polyphony Limit | integer (2 to 64) |
| /param/global/scene_mode | Scene Mode | integer (0 to 3) |
| /param/global/split_point | Split Point | integer (0 to 127) |
| /param/global/volume | Global Volume | float (0.0 to 1.0) |


## Control Group: Oscillators


### Replace '<s>' with 'a' or 'b' (scene) and <n> with '1' through '3'
                                   (oscillator #)


| Address | Parameter Name | Appropriate Values |
|---|---|---|
| /param/<s>/osc/<n>/keytrack | Osc <n> Keytrack | boolean (0 or 1) |
| /param/<s>/osc/<n>/octave | Osc <n> Octave | integer (-3 to 3) |
| /param/<s>/osc/<n>/param1 | Osc <n> Morph | (contextual) |
| /param/<s>/osc/<n>/param2 | Osc <n> Skew Vertical | (contextual) |
| /param/<s>/osc/<n>/param3 | Osc <n> Saturate | (contextual) |
| /param/<s>/osc/<n>/param4 | Osc <n> Formant | (contextual) |
| /param/<s>/osc/<n>/param5 | Osc <n> Skew Horizontal | (contextual) |
| /param/<s>/osc/<n>/param6 | Osc <n> Unison Detune | (contextual) |
| /param/<s>/osc/<n>/param7 | Osc <n> Unison Voices | (contextual) |
| /param/<s>/osc/<n>/pitch | Osc <n> Pitch | float (0.0 to 1.0) |
| /param/<s>/osc/<n>/retrigger | Osc <n> Retrigger | boolean (0 or 1) |
| /param/<s>/osc/<n>/type | Osc <n> Type | integer (0 to 11) |


## Control Group: Filters


### Replace '<s>' with 'a' or 'b' (scene) and '<n>' with '1' or '2' (filter
                                   #)


| Address | Parameter Name | Appropriate Values |
|---|---|---|
| /param/<s>/filter/<n>/cutoff | Filter <n> Cutoff | float (0.0 to 1.0) |
| /param/<s>/filter/<n>/feg_amount | Filter <n> FEG Mod Amount | float (0.0 to 1.0) |
| /param/<s>/filter/<n>/keytrack | Filter <n> Keytrack | float (0.0 to 1.0) |
| /param/<s>/filter/<n>/resonance | Filter <n> Resonance | float (0.0 to 1.0) |
| /param/<s>/filter/<n>/subtype | Filter <n> Subtype | integer (0 to 15) |
| /param/<s>/filter/<n>/type | Filter <n> Type | integer (0 to 33) |


## Control Group: Envelopes


### Replace '<s>' with 'a' or 'b' (scene)


| Address | Parameter Name | Appropriate Values |
|---|---|---|
| /param/<s>/aeg/attack | Amp EG Attack | float (0.0 to 1.0) |
| /param/<s>/aeg/attack_shape | Amp EG Attack Shape | integer (0 to 2) |
| /param/<s>/aeg/decay | Amp EG Decay | float (0.0 to 1.0) |
| /param/<s>/aeg/decay_shape | Amp EG Decay Shape | integer (0 to 2) |
| /param/<s>/aeg/mode | Amp EG Envelope Mode | integer (0 to 1) |
| /param/<s>/aeg/release | Amp EG Release | float (0.0 to 1.0) |
| /param/<s>/aeg/release_shape | Amp EG Release Shape | integer (0 to 2) |
| /param/<s>/aeg/sustain | Amp EG Sustain | float (0.0 to 1.0) |
| /param/<s>/feg/attack | Filter EG Attack | float (0.0 to 1.0) |
| /param/<s>/feg/attack_shape | Filter EG Attack Shape | integer (0 to 2) |
| /param/<s>/feg/decay | Filter EG Decay | float (0.0 to 1.0) |
| /param/<s>/feg/decay_shape | Filter EG Decay Shape | integer (0 to 2) |
| /param/<s>/feg/mode | Filter EG Envelope Mode | integer (0 to 1) |
| /param/<s>/feg/release | Filter EG Release | float (0.0 to 1.0) |
| /param/<s>/feg/release_shape | Filter EG Release Shape | integer (0 to 2) |
| /param/<s>/feg/sustain | Filter EG Sustain | float (0.0 to 1.0) |


## Control Group: FX


### Replace '<s>' with 'a', 'b', 'global' or 'send' and '<n>' with '1'
                                   through '4' (slot #)


| Address | Parameter Name | Appropriate Values |
|---|---|---|
| /param/fx/<s>/<n>/param1 | FX <s><n> Param 1 | (contextual) |
| /param/fx/<s>/<n>/param2 | FX <s><n> Param 2 | (contextual) |
| /param/fx/<s>/<n>/param3 | FX <s><n> Param 3 | (contextual) |
| /param/fx/<s>/<n>/param4 | FX <s><n> Param 4 | (contextual) |
| /param/fx/<s>/<n>/param5 | FX <s><n> Param 5 | (contextual) |
| /param/fx/<s>/<n>/param6 | FX <s><n> Param 6 | (contextual) |
| /param/fx/<s>/<n>/param7 | FX <s><n> Param 7 | (contextual) |
| /param/fx/<s>/<n>/param8 | FX <s><n> Param 8 | (contextual) |
| /param/fx/<s>/<n>/param9 | FX <s><n> Param 9 | (contextual) |
| /param/fx/<s>/<n>/param10 | FX <s><n> Param 10 | (contextual) |
| /param/fx/<s>/<n>/param11 | FX <s><n> Param 11 | (contextual) |
| /param/fx/<s>/<n>/param12 | FX <s><n> Param 12 | (contextual) |
| /param/fx/<s>/<n>/type | FX <s><n> FX Type | int (0 = off; 1 - 29: fx type) |
| /param/fx/<s>/<n>/deactivate | (FX slot Deactivate) | boolean (0 or 1) 1 = deactivated |


## Control Group: Mixer


### Replace '<s>' with 'a' or 'b' (scene) and <n> with '1' through '3'
                                   (oscillator #)


| Address | Parameter Name | Appropriate Values |
|---|---|---|
| /param/<s>/mixer/noise/mute | Noise Mute | boolean (0 or 1) |
| /param/<s>/mixer/noise/route | Noise Route | integer (0 to 2) |
| /param/<s>/mixer/noise/solo | Noise Solo | boolean (0 or 1) |
| /param/<s>/mixer/noise/volume | Noise Volume | float (0.0 to 1.0) |
| /param/<s>/mixer/osc<n>/mute | Osc <n> Mute | boolean (0 or 1) |
| /param/<s>/mixer/osc<n>/route | Osc <n> Route | integer (0 to 2) |
| /param/<s>/mixer/osc<n>/solo | Osc <n> Solo | boolean (0 or 1) |
| /param/<s>/mixer/osc<n>/volume | Osc <n> Volume | float (0.0 to 1.0) |
| /param/<s>/mixer/prefilter_gain | Pre-Filter Gain | float (0.0 to 1.0) |
| /param/<s>/mixer/rm1x2/mute | Ring Modulation 1x2 Mute | boolean (0 or 1) |
| /param/<s>/mixer/rm1x2/route | Ring Modulation 1x2 Route | integer (0 to 2) |
| /param/<s>/mixer/rm1x2/solo | Ring Modulation 1x2 Solo | boolean (0 or 1) |
| /param/<s>/mixer/rm1x2/volume | Ring Modulation 1x2 Volume | float (0.0 to 1.0) |
| /param/<s>/mixer/rm2x3/mute | Ring Modulation 2x3 Mute | boolean (0 or 1) |
| /param/<s>/mixer/rm2x3/route | Ring Modulation 2x3 Route | integer (0 to 2) |
| /param/<s>/mixer/rm2x3/solo | Ring Modulation 2x3 Solo | boolean (0 or 1) |
| /param/<s>/mixer/rm2x3/volume | Ring Modulation 2x3 Volume | float (0.0 to 1.0) |


## Control Group: Modulators


### Replace '<s>' with 'a' or 'b' (scene) and '<n>' with '1' through '6' (lfo
                                   #)


| Address | Parameter Name | Appropriate Values |
|---|---|---|
| /param/<s>/slfo/<n>/amplitude | Scene LFO <n> Amplitude | float (0.0 to 1.0) |
| /param/<s>/slfo/<n>/deform | Scene LFO <n> Deform | float (0.0 to 1.0) |
| /param/<s>/slfo/<n>/eg/attack | Scene LFO <n> Attack | float (0.0 to 1.0) |
| /param/<s>/slfo/<n>/eg/decay | Scene LFO <n> Decay | float (0.0 to 1.0) |
| /param/<s>/slfo/<n>/eg/delay | Scene LFO <n> Delay | float (0.0 to 1.0) |
| /param/<s>/slfo/<n>/eg/hold | Scene LFO <n> Hold | float (0.0 to 1.0) |
| /param/<s>/slfo/<n>/eg/release | Scene LFO <n> Release | float (0.0 to 1.0) |
| /param/<s>/slfo/<n>/eg/sustain | Scene LFO <n> Sustain | float (0.0 to 1.0) |
| /param/<s>/slfo/<n>/phase | Scene LFO <n> Phase | float (0.0 to 1.0) |
| /param/<s>/slfo/<n>/rate | Scene LFO <n> Rate | float (0.0 to 1.0) |
| /param/<s>/slfo/<n>/trigger_mode | Scene LFO <n> Trigger Mode | integer (0 to 2) |
| /param/<s>/slfo/<n>/type | Scene LFO <n> Type | integer (0 to 9) |
| /param/<s>/slfo/<n>/unipolar | Scene LFO <n> Unipolar | boolean (0 or 1) |
| /param/<s>/vlfo/<n>/amplitude | LFO <n> Amplitude | float (0.0 to 1.0) |
| /param/<s>/vlfo/<n>/deform | LFO <n> Deform | float (0.0 to 1.0) |
| /param/<s>/vlfo/<n>/eg/attack | LFO <n> Attack | float (0.0 to 1.0) |
| /param/<s>/vlfo/<n>/eg/decay | LFO <n> Decay | float (0.0 to 1.0) |
| /param/<s>/vlfo/<n>/eg/delay | LFO <n> Delay | float (0.0 to 1.0) |
| /param/<s>/vlfo/<n>/eg/hold | LFO <n> Hold | float (0.0 to 1.0) |
| /param/<s>/vlfo/<n>/eg/release | LFO <n> Release | float (0.0 to 1.0) |
| /param/<s>/vlfo/<n>/eg/sustain | LFO <n> Sustain | float (0.0 to 1.0) |
| /param/<s>/vlfo/<n>/phase | LFO <n> Phase | float (0.0 to 1.0) |
| /param/<s>/vlfo/<n>/rate | LFO <n> Rate | float (0.0 to 1.0) |
| /param/<s>/vlfo/<n>/trigger_mode | LFO <n> Trigger Mode | integer (0 to 2) |
| /param/<s>/vlfo/<n>/type | LFO <n> Type | integer (0 to 9) |
| /param/<s>/vlfo/<n>/unipolar | LFO <n> Unipolar | boolean (0 or 1) |


## Parameter Extended Options


### Replace '<parameter address>' with full parameter address (as
                                   above) and '<s>' with 'a' or 'b' (scene).

Some parameters, (sometimes only in certain contexts), may have the following
                                   extended options:


| Address | Description | Appropriate Values |
|---|---|---|
| <parameter address>/abs+ | absolute | boolean (0 or 1) |
| <parameter address>/enable+ | enable | boolean (0 or 1) |
| <parameter address>/tempo_sync+ | tempo sync | boolean (0 or 1) |
| <parameter address>/extend+ | extend range | boolean (0 or 1) |
| <parameter address>/deform+ | deform type OR modern osc option bitmask | integer (0 to 3) OR bitmask |
| /param/<s>/portamento/const_rate+ | portamento constant rate | boolean (0 or 1) |
| /param/<s>/portamento/gliss+ | portamento glissando | boolean (0 or 1) |
| /param/<s>/portamento/retrig+ | portamento retrigger at scale degrees | boolean (0 or 1) |
| /param/<s>/portamento/curve+ | portamento curve | int (-1:log, 0:linear, or 1:exponential) |


## Parameter Documentation


### Sent to OSC client whenever a parameter is queried using '/q/param' or
                                   '/q/all_params'.

Some parameters provide different functionality depending on other parameters.
                                   For instance, changing oscillator types, filter types or effects types will
                                   alter the descriptions and value types of their related parameters.

The '/doc/' prefix indicates documentation for a given parameter.
                                   There are two kinds of documentation, each with a different message structure.

A parameter documentation message is structured like this:


| /doc/<parameter address> | description | type | minimum value | maximum value |
|---|---|---|---|---|

Such a message might look like this:

A parameter extended options documentation message is structured like this:


| /doc/<parameter address>/ext | option 1 | option 2 | option 3 | option 4 etc... |
|---|---|---|---|---|

Such a message might look like this:


## Modulation Mapping

Modulation Mapping messages are constructed by selecting one of the '/mod' source
                                   addresses
                                   listed below (with an appropriate index value, if necessary) and adding a target
                                   address selected
                                   from the '/param' addresses listed above, then specifying a depth (-1.0 - 1.0).
                                   If both the source and target addresses are scene-specific (a or b), the scenes must
                                   match.

Send a depth of  0  to disconnect a modulator from its target.

Not all parameters can be modulated by all mod. sources. If a given combination is
                                   not possible an error will be reported to OSC out.


## Modulation Mapping: Sources


### Replace '<s>' with 'a' or 'b' (scene) and '<n>' with '1' through '6' (lfo
                                   #)


| Address | Description | <index>=0 | <index>=1 | <index>=2 |
|---|---|---|---|---|
| /mod/vel | Velocity |  |  |  |
| /mod/rel_vel | Release Velocity |  |  |  |
| /mod/keytrk | Keytrack |  |  |  |
| /mod/<s>/lowest_key | Lowest Key |  |  |  |
| /mod/<s>/highest_key | Highest Key |  |  |  |
| /mod/<s>/latest_key | Latest Key |  |  |  |
| /mod/pat | Polyphonic Aftertouch |  |  |  |
| /mod/at | Channel Aftertouch |  |  |  |
| /mod/mw | Modulation Wheel |  |  |  |
| /mod/breath | Breath |  |  |  |
| /mod/expr | Expression |  |  |  |
| /mod/sus | Sustain Pedal |  |  |  |
| /mod/pb | Pitch Bend |  |  |  |
| /mod/timbre | Timbre |  |  |  |
| /mod/alt_bi | Alternate Bipolar |  |  |  |
| /mod/alt_uni | Alternate Unipolar |  |  |  |
| /mod/rand_bi/<index> | Random Bipolar | (Uniform) | (Normal) |  |
| /mod/rand_uni/<index> | Random Unipolar | (Uniform) | (Half Normal) |  |
| /mod/<s>/feg | Filter EG |  |  |  |
| /mod/<s>/aeg | Amp EG |  |  |  |
| /mod/<s>/vlfo_<n>/<index> | Voice LFO <n>† | (Voice LFO <n>) | (Raw Waveform) | (EG Only) |
| /mod/<s>/slfo_<n>/<index> | Scene LFO <n>† | (Scene LFO <n>) | (Raw Waveform) | (EG Only) |
| /mod/macro_1 | Macro 1 |  |  |  |
| /mod/macro_2 | Macro 2 |  |  |  |
| /mod/macro_3 | Macro 3 |  |  |  |
| /mod/macro_4 | Macro 4 |  |  |  |
| /mod/macro_5 | Macro 5 |  |  |  |
| /mod/macro_6 | Macro 6 |  |  |  |
| /mod/macro_7 | Macro 7 |  |  |  |
| /mod/macro_8 | Macro 8 |  |  |  |


## Modulation Mapping: Muting


### Replace '/mod/...' with '/mod/mute/...' in the modulation-to-parameter mapping
                                   convention described above,
                                   using a value of 0 to set muting  off , or 1 to set muting  on .

Surge FX supports external OSC control of the twelve standard FX parameters.


## Surge FX parameters 1-12


### Replace '<index>' with '1' through '12'


| Address | Description | Appropriate Values |
|---|---|---|
| /fx/param/<index> | Change FX parameter <index> | float (0.0 to 1.0) |

