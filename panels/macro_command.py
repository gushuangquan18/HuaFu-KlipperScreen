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

def stop_chamber_temperature(widget, self):
    logging.info(_("Stop chamber temperature heating"))
    self._screen._send_action(widget, "printer.gcode.script",
                              {"script": f"CHAMBER_STOP"})
    # self._screen._send_action(widget, "printer.gcode.script",
    #                           {"script": f"SET_GCODE_VARIABLE MACRO=_CHAMBER_VARS VARIABLE=target_temp VALUE=0\n"+
    #                                         "SET_PIN PIN=chamber_heater5_relay VALUE=0\n"+
    #                                         "SET_PIN PIN=chamber_heater6_relay VALUE=0\n"+
    #                                         "SET_PIN PIN=chamber_heater1_relay VALUE=0"})

def clean_nozzle(widget, self):
    logging.info(_("Clean Nozzle"))
    self._screen._send_action(widget, "printer.gcode.script",
                              {"script": f"CLEAN_NOZZLE"})

def turn_on_each_detection_bed(widget, self):
    # 每次打印之前自动探测床网 只探测所打印的位置
    #BED_MESH_CALIBRATE ADAPTIVE = 1
    logging.info(_("Open Detecting the printing position on the bed net"))
    self._screen._send_action(widget, "printer.gcode.script",
                              {"script": f"BED_MESH_CALIBRATE ADAPTIVE = 1"})

def turn_off_each_detection_bed(widget, self):
    # 全床都测 打印之前不测试
    # BED_MESH_PROFILE LOAD=default
    logging.info(_("Close Detecting the printing position on the bed net"))
    self._screen._send_action(widget, "printer.gcode.script",
                              {"script": f"BED_MESH_PROFILE LOAD=default"})

