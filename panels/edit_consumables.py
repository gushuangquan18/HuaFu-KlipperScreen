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
def consumables_dialog(widget,self):
    title=_("Operating consumables")
    buttons = [
        {"name": _("Edit ConSumables"), "response": 1, "style": 'waring_button'},
        {"name": _("Control Consumables"), "response": 2, "style": 'dialog_cancel'}
    ]
    if len(self._printer.get_stat("exclude_object", "objects")) > 1:
        buttons.insert(0, {"name": _("Exclude Object"), "response": Gtk.ResponseType.APPLY})
    label = Gtk.Label(hexpand=True, vexpand=True, wrap=True)
    label.set_markup(_("Please select the function you want to operate!"))
    if self.labels['t0_extruder_consumables_control'] == widget:
        title = f'左喷嘴:{_("Operating consumables")}'
    else:
        title = f'右喷嘴:{_("Operating consumables")}'
    self._gtk.Dialog(title, buttons, label, consumables_confirm,self,widget)

#选择哪个功能
def consumables_confirm(dialog, response_id, klippy_gtk,self,*args):
    self._gtk.remove_dialog(dialog)
    if response_id==1:
        parameter_item = {
            "panel": 'edit_consumables',
            "icon": None,
        }
        self.menu_item_clicked(args[0], parameter_item)
    if response_id==2:
        parameter_item = {
            "panel": 'control_consumables',
            "icon": None,
        }
        self.menu_item_clicked(args[0], parameter_item)


#更改耗材每次载入抽回的距离,并更改对应选中按钮的颜色
def change_consumables_button(widget, self, type,value):
    value = int(value)
    self.labels[type] = value
    logging.info(f"Change {type} value : {value}")
    for distance_button in self.labels[f'{type}_button']:
        text=distance_button.get_label()
        if int(text) == value:
            distance_button.get_style_context().remove_class('distance_button')
            distance_button.get_style_context().add_class('select_distance_button')
        else:
            distance_button.get_style_context().remove_class('select_distance_button')
            distance_button.get_style_context().add_class('distance_button')
