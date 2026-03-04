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

#将X Y Z轴归位
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

#更改喷嘴 腔温 热床温度
def change_target_temp(widget,self, name):
    # temp = self.verify_max_temp(name,temp)
    temp_text = self.entry[name].get_text()
    match= re.search(r'(\d+\.?\d*)',temp_text)
    temp = int(match.group(0))
    temp = True
    if temp is False:
        return
    if name.startswith('extruder'):
        self._screen._ws.klippy.set_tool_temp(self._printer.get_tool_number(name), temp)
    elif name == "heater_bed":
        self._screen._ws.klippy.set_bed_temp(temp)
    elif name.startswith('heater_generic '):
        self._screen._ws.klippy.set_heater_temp(name, temp)
    elif name.startswith('temperature_fan '):
        self._screen._ws.klippy.set_temp_fan_temp(name, temp)
    else:
        logging.info(f"Unknown heater: {name}")
        self._screen.show_popup_message(_("Unknown Heater") + " " + name)
    self._printer.set_stat(name, {"target": temp})
    if self.numpad_visible:
        self.hide_numpad()

    parameter_item = {
        "panel": "printer_control_menu",
        "icon": None
    }
    self.menu_item_clicked(widget, parameter_item)

#判断需要更改的温度是否超出限制
def verify_max_temp(self, name,temp):
    temp = int(temp)
    max_temp = int(float(self._printer.get_config_section(name)['max_temp']))
    logging.debug(f"{temp}/{max_temp}")
    if temp > max_temp:
        self._screen.show_popup_message(_("Can't set above the maximum:") + f' {max_temp}')
        return False
    return max(temp, 0)

#输入框清空
def on_digit_clicked(widget,self, num,key):
    if(num != None):
        current = self.entry[key].get_text()
        if current.endswith("℃"):
            # 插入数字到 ℃ 前
            new_text = current[:-1] + str(num) + "℃"
        else:
            new_text = current + str(num) + "℃"
        self.entry[key].set_text(new_text)
        self.entry[key].set_position(len(new_text) - 1)  # 光标停在数字末尾（℃前）
    else:
        self.entry[key].set_text("℃")