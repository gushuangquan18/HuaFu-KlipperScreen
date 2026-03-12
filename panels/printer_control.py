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

SPEED_MODEL = {
    '50':_("Mute"),'100':_("Standard"),'124':_("Sport"),'166':_("Furious"),
}

def change_print_speed(widget, self, value):
    print_speed = re.search(r'\d+', value)
    if print_speed:
        # 提取并转换为整数
        print_speed = int(print_speed.group())
    self.print_speed = print_speed
    self._screen._send_action(widget, "printer.gcode.script", {"script": KlippyGcodes.set_speed_rate(print_speed)})
    self.labels['speed_control_model'].sel_label(SPEED_MODEL[f'print_speed'])
    for button in self.buttons["print_speed"]:
        text=button.get_label()
        if text.endswith(f"({print_speed}%)"):
            button.get_style_context().remove_class('speed_control_button')
            button.get_style_context().add_class('select_speed_control_button')
        else:
            button.get_style_context().remove_class('select_speed_control_button')
            button.get_style_context().add_class('speed_control_button')

#控制打印机XYZ轴
def move(widget, self, value):
    """

    :param self:
    :param widget:
    :param axis:    X,Y,Z
    :param direction: +,_
    :return:
    """
    axis = ''
    direction = ''
    target = self.distance
    if value == _("Raise Heater Bed"):
        target=float(target)
        axis = 'Z'
        direction = '-'
    elif value == _("Reduce Heater Bed"):
        target=float(target)
        axis = 'Z'
        direction = '+'
    else:
        target=int(target)
        axis = value[0].lower()
        direction = value[1]
    if (
            self._config.get_config()["main"].getboolean(f"invert_{axis}", False)
            and axis != "z"
    ):
        direction = "-" if direction == "+" else "+"

    dist = f"{direction}{target}"
    config_key = "move_speed_z" if axis == "z" else "move_speed_xy"
    # speed = (
    #     None
    #     if self.ks_printer_cfg is None
    #     else self.ks_printer_cfg.getint(config_key, None)
    # )
    # if speed is None:
    #     speed = self._config.get_config()["main"].getint(config_key, self.max_z_velocity)
    speed = 60 * max(1, target)
    script = f"{KlippyGcodes.MOVE_RELATIVE}\nG0 {axis}{dist} F{speed}"
    self._screen._send_action(widget, "printer.gcode.script", {"script": script})
    if self._printer.get_stat("gcode_move", "absolute_coordinates"):
        self._screen._ws.klippy.gcode_script("G90")

#更改XYZ轴每次移动的距离,并更改对应选中按钮的颜色
def change_distance(widget, self, value):
    self.distance = value
    logging.info(f"Change sport distance: {self.distance}")
    for distance_button in self.buttons["distance_button"]:
        text=distance_button.get_label()
        if text == value:
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
def change_target_temp(widget,self, name,*args):
    temp_text = self.entry[name].get_text()
    match= re.search(r'(\d+\.?\d*)',temp_text)
    temp = int(match.group(0))
    # temp = self.verify_max_temp(name,temp)
    if temp is False:
        return
    if args[0].startswith('T0'):
        #{'script': 'M104 Textruder S50'}
        self._screen._ws.klippy.set_tool_temp('extruder', temp)
    elif args[0].startswith('T1'):
        # {'script': 'M104 T1 S65'}  T1  1代表extruder
        self._screen._ws.klippy.set_tool_temp('1', temp)
    elif name.startswith("heater_bed"):
        #{'script': 'M140 S90'} S后面是温度
        self._screen._ws.klippy.set_bed_temp(temp)
    elif name.startswith("chassis"):
        #CHAMBER_HEAT TARGET=45 TOLERANCE=2
    #     name = "temperature_sensor filament_box_temp"
        self._screen._ws.klippy.set_chassis_temp(temp)
    #     self._screen._ws.klippy.set_heater_temp(name, temp)
    # elif name.startswith('temperature_fan '):
    #     self._screen._ws.klippy.set_temp_fan_temp(name, temp)
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