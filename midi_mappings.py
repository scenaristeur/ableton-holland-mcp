"""MIDI mappings (Affectations MIDI) router for the AbletonMCP Remote Script.

Modularize MIDI mapping logic OUT of the giant Remote Script (per the
structure-void pattern: separate module imported by the entry point).

Pattern (from midiremotescripts.structure-void.com):
    SliderElement(MIDI_CC_TYPE, channel, cc) + add_value_listener(cb)
    where cb writes to a target parameter.

This module creates SliderElement/ButtonElement listeners dynamically from a
config (e.g. the MiniLab mkII export), letting a real MIDI controller drive the
Live session in front of an audience.

Note on Python 2/3: the AbletonMCP Remote Script runs under Live 10/11 (Py2)
or Live 12 (Py3, still _Framework). Use standard imports + absolute_import.
"""

from __future__ import absolute_import, print_function, unicode_literals

try:
    from _Framework.SliderElement import SliderElement
    from _Framework.ButtonElement import ButtonElement
    from _Framework.EncoderElement import EncoderElement
    from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE
    import Live

    MapMode = Live.MidiMap.MapMode
except Exception:
    # If any framework import fails (some Live versions), degrade gracefully.
    SliderElement = None
    ButtonElement = None
    EncoderElement = None
    MIDI_CC_TYPE = MIDI_NOTE_TYPE = 0
    MapMode = None


def _note_name(note):
    """Convert a MIDI note number to a readable name (60 -> C3)."""
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return names[note % 12] + str(note // 12 - 1)


class MidiMappingRouter(object):
    """Owns live MIDI mapping SliderElements/ButtonElements + their listeners.

    Each mapping binds an incoming CC/Note (channel+identifier) to a target
    parameter (resolved lazily by a getter). Keeps elements alive to avoid GC.
    """

    def __init__(self, control_surface, config=None, log=None, config_file=None):
        # type: (object, list, object, str) -> None
        self._cs = control_surface  # the AbletonMCP(ControlSurface)
        self._log = log or (lambda *a: None)
        self._elements = []  # keep alive (anti-GC)
        self._direct_elements = []  # direct-map elements (connect_to)
        self._mappings = []  # descriptors for list_midi_mappings
        if config_file:
            self.load_config_file(config_file)
        elif config:
            self.load_config(config)

    # ── persistent config (JSON file) ─────────────────────────────────────
    def load_config_file(self, path):
        """Load mappings from a JSON file next to the RS (persistent across
        restarts). Expected shape: a list of mapping dicts; each may include
        "direct": true to use connect_to (appears in native Map panel)."""
        try:
            import json as _json

            with open(path, "r") as fh:
                data = _json.load(fh)
        except Exception as e:
            self._log("[midimap] could not load %s: %s" % (path, e))
            return
        if isinstance(data, dict):
            data = data.get("mappings", [])
        for m in data:
            try:
                if m.get("direct"):
                    self.add_direct_mapping(m)
                else:
                    self.add_mapping(m)
            except Exception as e:  # keep going, report each failure
                self._log("[midimap] error on %s: %s" % (m, e))

    # ── config loader ─────────────────────────────────────────────────────
    def load_config(self, config):
        """config: list of dicts:
        { "channel": int (0-based), "identifier": int (CC or note number),
          "msg_type": "cc"|"note", "min": float, "max": float,
          "mode": "absolute"|"toggle",
          "target": { "type": "track_volume"|"track_pan"|"device_param"|"clip_slot"|...,
                      "track_index": int, "device_index": int,
                      "parameter_name": str, "scene_index": int, ... } }
        """
        for m in config:
            try:
                if m.get("direct"):
                    self.add_direct_mapping(m)
                else:
                    self.add_mapping(m)
            except Exception as e:  # keep going, report each failure
                self._log("[midimap] error on %s: %s" % (m, e))

    # ── main entry ─────────────────────────────────────────────────────────
    def add_mapping(self, mapping):
        channel = int(mapping.get("channel", 0))
        identifier = int(mapping.get("identifier", 0))
        msg_type = mapping.get("msg_type", "cc")
        lo = float(mapping.get("min", 0.0))
        hi = float(mapping.get("max", 127.0))
        mode = mapping.get("mode", "absolute")
        target = mapping.get("target", {})

        if ButtonElement is None or SliderElement is None:
            return False
        if msg_type == "note":
            el = ButtonElement(True, MIDI_NOTE_TYPE, channel, identifier)
        else:
            el = SliderElement(MIDI_CC_TYPE, channel, identifier)

        def _make_cb(el_obj, target, lo, hi, mode):
            def _cb(value):
                self._dispatch(el_obj, value, target, lo, hi, mode)

            return _cb

        el.add_value_listener(_make_cb(el, target, lo, hi, mode))
        self._elements.append(el)

        self._mappings.append(
            {
                "channel": channel + 1,  # 1-based for UI
                "msg_type": "note" if msg_type == "note" else "cc",
                "identifier": identifier,
                "identifier_name": (
                    _note_name(identifier)
                    if msg_type == "note"
                    else ("CC%d" % identifier)
                ),
                "min": lo,
                "max": hi,
                "mode": mode,
                "target": target,
            }
        )
        return True

    # ── direct mapping (shows in Ableton "Affectations MIDI") ─────────────
    def add_direct_mapping(self, mapping):
        """Create a DIRECT mapping that appears in Live's MIDI Map panel.

        Uses _Framework.EncoderElement.connect_to(parameter): Live routes the
        incoming MIDI message straight to the parameter at the C++ level, so it
        shows up in the native 'Affectations MIDI' view (channel, CC, path,
        name, min, max). Requires a resolvable DeviceParameter.
        """
        if EncoderElement is None:
            return {"bound": False, "error": "framework map not available"}
        try:
            song = self._cs.song()
            param = self._resolve_parameter(song, mapping)
            if param is None:
                return {"bound": False, "error": "target parameter not found"}
            channel = int(mapping.get("channel", 0))
            identifier = int(mapping.get("identifier", 0))
            enc = EncoderElement(MIDI_CC_TYPE, channel, identifier, MapMode.absolute)
            enc.connect_to(param)
            self._elements.append(enc)
            self._direct_elements.append(enc)
            self._mappings.append(
                {
                    "channel": channel + 1,
                    "msg_type": "cc",
                    "identifier": identifier,
                    "identifier_name": "CC%d" % identifier,
                    "parameter_name": param.name,
                    "path": self._parameter_path(param),
                    "min": getattr(param, "min", None),
                    "max": getattr(param, "max", None),
                    "mode": "direct",
                    "target": mapping,
                }
            )
            return {"bound": True, "parameter": param.name}
        except Exception as e:
            return {"bound": False, "error": str(e)}

    def _resolve_parameter(self, song, mapping):
        target = mapping.get("target", {})
        ttype = target.get("type")
        tindex = target.get("track_index", 0)
        try:
            if ttype == "track_volume":
                return song.tracks[tindex].mixer_device.volume
            if ttype == "track_pan":
                return song.tracks[tindex].mixer_device.panning
            if ttype == "master_volume":
                return song.master_track.mixer_device.volume
            if ttype == "device_param":
                dev = song.tracks[tindex].devices[target.get("device_index", 0)]
                pname = target.get("parameter_name", "")
                for p in dev.parameters:
                    if p.name == pname:
                        return p
            return None
        except Exception:
            return None

    def _parameter_path(self, param):
        try:
            obj = param.canonical_parent
            seg = []
            while obj is not None:
                nm = getattr(obj, "name", None)
                if nm:
                    seg.insert(0, nm)
                nxt = getattr(obj, "canonical_parent", None)
                if nxt is obj:
                    break
                obj = nxt
                try:
                    if Live is not None and isinstance(obj, Live.Song.Song):
                        break
                except Exception:
                    break
            seg.append(param.name)
            return " | ".join(seg)
        except Exception:
            return param.name

    # ── dispatch ──────────────────────────────────────────────────────────
    def _dispatch(self, el, value, target, lo, hi, mode):
        # normalize incoming value (0-127) into target's native range
        try:
            song = self._cs.song()
            ttype = target.get("type")
            tindex = target.get("track_index", 0)

            # normalized 0..1
            if lo != hi:
                norm = (value - lo) / (hi - lo)
            else:
                norm = 0.0
            norm = max(0.0, min(1.0, norm))

            if ttype == "track_volume":
                tracks = song.tracks
                if 0 <= tindex < len(tracks):
                    p = tracks[tindex].mixer_device.volume
                    p.value = p.min + norm * (p.max - p.min)
            elif ttype == "track_pan":
                tracks = song.tracks
                if 0 <= tindex < len(tracks):
                    p = tracks[tindex].mixer_device.panning
                    p.value = p.min + norm * (p.max - p.min)
            elif ttype == "master_volume":
                p = song.master_track.mixer_device.volume
                p.value = p.min + norm * (p.max - p.min)
            elif ttype == "device_param":
                tracks = song.tracks
                didx = target.get("device_index", 0)
                pname = target.get("parameter_name", "")
                if 0 <= tindex < len(tracks):
                    dev = (
                        tracks[tindex].devices[didx]
                        if 0 <= didx < len(tracks[tindex].devices)
                        else None
                    )
                    if dev is not None:
                        self._set_parameter_by_name(dev, pname, lo, hi, value)
            elif ttype in ("clip_slot", "scene"):
                self._trigger_scene_slot(song, target, ttype)
            else:
                self._log("[midimap] unknown target type: %s" % ttype)
        except Exception as e:
            self._log("[midimap] dispatch error: %s" % e)

    def _set_parameter_by_name(self, device, pname, lo, hi, value):
        for p in device.parameters:
            if p.name == pname:
                # interpret raw 0-127 directly scaled to param range
                p.value = p.min + (value / 127.0) * (p.max - p.min)
                return

    def _trigger_scene_slot(self, song, target, ttype):
        si = target.get("scene_index", 0)
        ti = target.get("track_index", 0)
        if ttype == "scene":
            scenes = song.scenes
            if 0 <= si < len(scenes):
                scenes[si].fire()
        elif ttype == "clip_slot":
            tracks = song.tracks
            if 0 <= ti < len(tracks):
                slots = tracks[ti].clip_slots
                if 0 <= si < len(slots):
                    slots[si].fire()

    # ── introspection ──────────────────────────────────────────────────────
    def list_mappings(self):
        """Return descriptors (for list_midi_mappings MCP tool)."""
        return list(self._mappings)

    def clear(self):
        """Remove listeners + release, called on disconnect()."""
        for el in self._elements:
            try:
                el.remove_value_listener(self)
            except Exception:
                pass
        self._elements = []
        self._mappings = []

    @property
    def count(self):
        return len(self._mappings)
