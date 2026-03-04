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



#控制打印机XYZ轴
def move(widget, self, value):
    """

    :param self:
    :param widget:
    :param axis:    X,Y,Z
    :param direction: +,_
    :return:
    """

    axis = value[0].lower()
    direction = value[1]
    if (
            self._config.get_config()["main"].getboolean(f"invert_{axis}", False)
            and axis != "z"
    ):
        direction = "-" if direction == "+" else "+"

    dist = f"{direction}{self.labels["sport_distance"]}"
    config_key = "move_speed_z" if axis == "z" else "move_speed_xy"
    # speed = (
    #     None
    #     if self.ks_printer_cfg is None
    #     else self.ks_printer_cfg.getint(config_key, None)
    # )
    # if speed is None:
    #     speed = self._config.get_config()["main"].getint(config_key, self.max_z_velocity)
    speed = 60 * max(1, self.labels["sport_distance"])
    script = f"{KlippyGcodes.MOVE_RELATIVE}\nG0 {axis}{dist} F{speed}"
    self._screen._send_action(widget, "printer.gcode.script", {"script": script})
    if self._printer.get_stat("gcode_move", "absolute_coordinates"):
        self._screen._ws.klippy.gcode_script("G90")

#更改XY轴每次移动的距离,并更改对应选中按钮的颜色
def change_sprot_speed(widget, self, value):
    match= re.search(r'\d+', value)
    distance = int(match.group(0))
    self.labels["sport_distance"] = distance
    logging.info(f"Change sport distance: {self.labels["sport_distance"]}")
    for distance_button in self.labels["distance_button"]:
        text=distance_button.get_label()
        if text == f'{distance}mm':
            distance_button.get_style_context().remove_class('distance_button')
            distance_button.get_style_context().add_class('select_distance_button')
        else:
            distance_button.get_style_context().remove_class('select_distance_button')
            distance_button.get_style_context().add_class('distance_button')

#将XY轴归位
def direction_home(widget, self, value=None):
    #{'script': 'G28 X Y'}
    # {'script': 'G28 X'}
    # {'script': 'G28 Y'}
    script = ""
    if value == None:
        value = "X Y Z"
    else:
        value=value.replace("轴归位","")
    script = f'G28 {value}'
    self._screen._send_action(widget, "printer.gcode.script", {"script": script})
