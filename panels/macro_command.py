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

def cut(widget, self):
    logging.info(_("Cutting continuous fiber consumables"))
    self._screen._send_action(widget, "printer.gcode.script",
                              {"script": f"SET_SERVO SERVO=my_servo ANGLE=90\n"+
                                            "G4 P800\n"+
                                            "SET_SERVO SERVO=my_servo ANGLE=0\n"+
                                            "G4 P800"})

