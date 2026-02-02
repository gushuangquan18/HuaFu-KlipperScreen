import json
import logging

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, GdkPixbuf
from jinja2 import Template
from ks_includes.screen_panel import ScreenPanel
from ks_includes.widgets.autogrid import AutoGrid


class Panel(ScreenPanel):

    def __init__(self, screen, title, items=None):
        super().__init__(screen, title)
        self.items = items
        self.j2_data = self._printer.get_printer_status_data()
        self.create_menu_items()
        self.scroll = self._gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        # self.autogrid = AutoGrid()

    def activate(self):
        self.j2_data = self._printer.get_printer_status_data()
        self.add_content()

    def add_content(self):
        for child in self.scroll.get_children():
            self.scroll.remove(child)
        # self.scroll.add(self.arrangeMenuItems(self.items))
        if not self.content.get_children():
            self.content.add(self.scroll)


    def arrangeMenuItems(self, items, columns=None, expand_last=False):
        print("arrangeMenuItems")

    def create_child_items(self,i):
        self.counter =i
        key = list(self.items[i])[0]
        item = self.items[i][key]
        item_control_name = None

        if(item['type']=="Image"):
            item_control_name = Gtk.Image()
            image = self._screen.env.from_string(item['src']).render(self.j2_data) if item['src'] else None
            height = int(self._screen.env.from_string(item['height']).render(self.j2_data) if item['height'] else None)
            width = int(self._screen.env.from_string(item['width']).render(self.j2_data) if item['width'] else None)
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(image)
            scaled_pixbuf = pixbuf.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)
            item_control_name.set_from_pixbuf(scaled_pixbuf)
            self.counter += 1

        elif(item['type']=="Button"):
            self.counter += 1
            if(item["icon"] != "None"):
                icon = self._screen.env.from_string(item['icon']).render(self.j2_data) if item['icon'] else None
                item_control_name = self._gtk.Button(icon)
            else:
                item_control_name = Gtk.Button()
            if (item["panel"] != "None"):
                parameter_item = {
                    "panel": item["panel"],
                    "icon": None,
                }
                item_control_name.connect("clicked", self.menu_item_clicked, parameter_item)
            if(self.counter<len(self.items)):
                key_child = list(self.items[self.counter])[0]
                item_child = self.items[self.counter]
                if (item_child[key_child]['type'] == "Grid"):
                    item_control_name.add(self.create_child_items(self.counter))

        elif(item['type'] == "Label"):
            value = self._screen.env.from_string(item['value']).render(self.j2_data) if item['value'] else None
            item_control_name = Gtk.Label(label=_(value))
            self.counter += 1
        elif(item['type'] == "Grid"):
            item_control_name = Gtk.Grid(orientation=Gtk.Orientation.HORIZONTAL)
            # item_control_name.set_column_homogeneous(True)
            # item_control_name.set_row_homogeneous(True)
            i+=1
            while i<len(self.items):
                key_child = list(self.items[i])[0]
                key_father = ' '.join(key_child.split()[:-1]) if key_child and key_child.strip() else ''
                item_child = self.items[i][key_child]
                if (key_father == key and len((list(self.items[i])[0]).split()) > 1):
                    item_control_name.attach(self.create_child_items(i),
                                       int(item_child['column']),
                                       int(item_child['row']),
                                       int(item_child['columnspan']),
                                       int(item_child['rowspan']))
                    i = self.counter
                else:
                    i = self.counter + 1
                    break
        elif (item['type'] == "Switch"):
            item_control_name= Gtk.Switch()
            value = self._screen.env.from_string(item['value']).render(self.j2_data) if item['value'] else None
            item_control_name.set_active(bool(value))
            # self.binary_switch.connect("notify::active", self.on_binary_switch_toggled)
            self.counter += 1
        return item_control_name




    def create_menu_items(self):
        """
            创建主界面 下半部分元素
        :return:
        """
        parent_grid = Gtk.Grid()
        self.counter = i = 0
        while i<len(self.items):
            key = list(self.items[i])[0]
            item = self.items[i][key]
            parent_grid.attach(self.create_child_items(i),
                    int(item['column']),
                    int(item['row']),
                    int(item['columnspan']),
                    int(item['rowspan']))
            i = self.counter
        parent_grid.set_column_homogeneous(True)
        parent_grid.set_row_homogeneous(True)
        self.labels['parent_grid'] = parent_grid
        # self.content.add(parent_grid)

    def evaluate_enable(self, enable):
        """
            是否启用按钮
        :param enable:
        :return:
        """
        if enable == "{{ moonraker_connected }}":
            logging.info(f"moonraker connected {self._screen._ws.connected}")
            return self._screen._ws.connected
        try:
            j2_temp = Template(enable, autoescape=True)
            return j2_temp.render(self.j2_data) == 'True'
        except Exception as e:
            logging.debug(f"Error evaluating enable statement: {enable}\n{e}")
            return False
