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

#更新固件信息
def update_system_info(self):
    print('a')
    system_info = self._printer.system_info
    if 'distribution' in system_info and 'id' in system_info['distribution']:
        system_version = f'{system_info['distribution']['id'].capitalize()} {system_info['distribution']['version']}'
        self.labels['system_version'].set_label(system_version)
    network_address = None
    if 'network' in system_info :
        network_address =  list(system_info['network'].keys())[0]
        self.labels['network_address'].set_label(network_address)
        self.labels['ip_address'].set_label(system_info['network'][network_address]['ip_addresses'][0]['address'])
        self.labels['mac_address'].set_label(system_info['network'][network_address]['mac_address'])
