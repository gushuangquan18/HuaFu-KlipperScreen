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


#控制耗材的弹窗
def consumables_dialog(widget,self,current_key):
    title=_("Operating consumables")
    buttons = [
        {"name": _("Edit ConSumables"), "response": 1, "style": 'dialog_edit_consumables_button'},
        {"name": _("Control Consumables"), "response": 2, "style": 'dialog_control_consumables_button'}
    ]
    if len(self._printer.get_stat("exclude_object", "objects")) > 1:
        buttons.insert(0, {"name": _("Exclude Object"), "response": Gtk.ResponseType.APPLY})
    label = Gtk.Label(hexpand=True, vexpand=True, wrap=True)
    label.set_markup(_("Please select the function you want to operate!"))
    if self.buttons['t0_extruder_consumables_control'] == widget:
        title = f'T0:{_("Operating consumables")}'
    else:
        title = f'T1:{_("Operating consumables")}'
    self._gtk.Dialog(title, buttons, label, consumables_confirm,self,widget,current_key)

#选择哪个功能
def consumables_confirm(dialog, response_id, klippy_gtk,self,*args):
    # self._gtk.remove_dialog(dialog)
    extruder = ''
    if args[1].startswith('t0'):
        self._screen._ws.klippy.gcode_script('T0')
        extruder = 'extruder'
    else:
        self._screen._ws.klippy.gcode_script('T1')
        extruder = 'extruder1'
    # change_extruder(dialog, self, extruder)
    change_extruder(None, self, extruder)
    if response_id==1:
        parameter_item = {
            "panel": 'edit_consumables',
            "select_extruder":extruder,
            "icon": None,
        }
        self.menu_item_clicked(args[0], parameter_item)
    if response_id==2:
        parameter_item = {
            "panel": 'control_consumables',
            "select_extruder":extruder,
            "icon": None,
        }
        self.menu_item_clicked(args[0], parameter_item)


def change_extruder(widget, self, extruder):

    #printer.gcode.script: {'script': 'ACTIVATE_EXTRUDER EXTRUDER=extruder1'}
    self._screen._send_action(widget, "printer.gcode.script",
                              {"script": f"ACTIVATE_EXTRUDER EXTRUDER={extruder}"})

#控制耗材挤入挤出 载入等
#挤出：method：extrude direction：+
#抽回：method：extrude direction：-
#载入：method：load_unload direction：+
#卸载：method：load_unload direction：-
def check_min_temp(widget,self , current_key):
    method = direction = ''
    if current_key.startswith('extrude_consumables'):
        method = 'extrude'
        direction = '+'
    elif current_key.startswith('retraction_consumables'):
        method = 'extrude'
        direction = '-'
    elif current_key.startswith('long_load_consumables'):
        method = 'long_load'
        direction = '+'
    elif current_key.startswith('long_unload_consumables'):
        method = 'long_load'
        direction = '-'

    # temp = float(self._printer.get_stat(self.current_extruder, 'temperature'))
    # target = float(self._printer.get_stat(self.current_extruder, 'target'))
    # min_extrude_temp = float(self._printer.config[self.current_extruder].get('min_extrude_temp', 170))
    # if temp < min_extrude_temp:
    #     if target > min_extrude_temp:
    #         self._screen._send_action(
    #             widget, "printer.gcode.script",
    #             {"script": f"M109 S{target}"}
    #         )
    if method == "extrude":
        extrude(widget,self, direction)
    elif method == "long_load":
        long_load(widget,self, direction)

def extrude(widget, self, direction):
    self._screen._ws.klippy.gcode_script(KlippyGcodes.EXTRUDE_REL)
    #printer.gcode.script: {'script': 'G1 E+10 F120'}
    self._screen._send_action(widget, "printer.gcode.script",
                              {"script": f"G1 E{direction}{self.labels['length']} F{self.labels['speed'] * 60}"})

def long_load(widget, self, direction):
    if direction == "+":
        # "G91  相对位移
        #  G1 E2150 F6000 距离是2150 速度是100mm/s  *60
        #  G90 绝对位移
        self._screen._send_action(widget, "printer.gcode.script",
                                                                {"script": "G91\n"+
                                                                           "G1 E+2150 F6000\n"+
                                                                           "G90\n"+
                                                                           "G1 E+250 F300"})
    elif direction == "-":
        # "G91  相对
        #  G1 E2150 F6000
        #  G90   距离是2150 速度是100mm/s  *60
        self._screen._send_action(widget, "printer.gcode.script",
                                                                {"script": "G1 E-200 F300\n"+
                                                                           "G91\n"+
                                                                            "G1 E-2150 F6000\n"+
                                                                            "G90"})



#更改耗材每次载入抽回的距离,并更改对应选中按钮的颜色
def change_consumables_button(widget, self, type,value):
    value = int(value)
    self.labels[type] = value
    logging.info(f"Change {type} value : {value}")
    for distance_button in self.buttons[f'{type}_button']:
        text=distance_button.get_label()
        if int(text) == value:
            distance_button.get_style_context().remove_class('distance_button')
            distance_button.get_style_context().add_class('select_distance_button')
        else:
            distance_button.get_style_context().remove_class('select_distance_button')
            distance_button.get_style_context().add_class('distance_button')


