import logging
import os
import pathlib
from functools import lru_cache
import json
import logging
import gi
import re

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GdkPixbuf, Gio, Gtk, Pango
from ks_includes.widgets.scroll import CustomScrolledWindow
from jinja2 import Template
from datetime import datetime
from ks_includes.screen_panel import ScreenPanel
from ks_includes.KlippyGtk import find_widget
from ks_includes.KlippyGcodes import KlippyGcodes


def bed_mesh_calibration(widget,self):
    widget.set_sensitive(False)
    self._screen.show_popup_message(_("Calibrating"), level=1)
    if self._printer.get_stat("toolhead", "homed_axes") != "xyz":
        self._screen._ws.klippy.gcode_script("G28")
    if (
            "Z_TILT_ADJUST" in self._printer.available_commands
            and not bool(self._printer.get_stat("z_tilt", "applied"))
    ):
        self._screen._ws.klippy.gcode_script("Z_TILT_ADJUST")
    if (
            "QUAD_GANTRY_LEVEL" in self._printer.available_commands
            and not bool(self._printer.get_stat("quad_gantry_level", "applied"))
    ):
        self._screen._ws.klippy.gcode_script("QUAD_GANTRY_LEVEL")
    self._screen._send_action(widget, "printer.gcode.script", {"script": "BED_MESH_CALIBRATE"})
    # self._screen._send_action(widget, "printer.gcode.script", {'script': 'SAVE_CONFIG'})

