# test_mapping_CC16_track1_volume - MIDI Remote Script
# Generated with midiremotescripts.structure-void.com/generator
# This generated script is yours: public domain (CC0 1.0), no restrictions.

from __future__ import absolute_import
from _Framework.ControlSurface import ControlSurface
from _Framework.SliderElement import SliderElement
from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE

class test_mapping_CC16_track1_volume(ControlSurface):

    def __init__(self, c_instance):
        super(test_mapping_CC16_track1_volume, self).__init__(c_instance)
        with self.component_guard():
            self._build()

    def _build(self):
        self._controls = []  # keep direct-mapped elements alive

        # CC 16 (ch 1) -> Volume — track · TRACK 1 (fixed)
        el_1 = SliderElement(MIDI_CC_TYPE, 0, 16)
        def _on_el_1(value):
            tracks = self.song().tracks
            if 0 < len(tracks):
                tracks[0].mixer_device.volume.value = value / 127.0
        el_1.add_value_listener(_on_el_1)
        self._controls.append(el_1)

    def disconnect(self):
        super(test_mapping_CC16_track1_volume, self).disconnect()
