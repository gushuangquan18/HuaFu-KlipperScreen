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

#t弹窗提示
def dialog_message(widget,self):
    buttons = [
        {"name": _("Off"), "response": Gtk.ResponseType.CANCEL, "style": 'dialog_cancel_button'}
    ]
    label = Gtk.Label(hexpand=True, vexpand=True, wrap=True)
    label.set_markup(_("Stay tuned!"))
    self._gtk.Dialog(_("Messages"), buttons, label, close_dialog, self)

def close_dialog(dialog, response_id, klippy_gtk, self):
    self._gtk.remove_dialog(dialog)


