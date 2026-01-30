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
        self.autogrid = AutoGrid()

    def activate(self):
        self.j2_data = self._printer.get_printer_status_data()
        self.add_content()

    def add_content(self):
        for child in self.scroll.get_children():
            self.scroll.remove(child)
        self.scroll.add(self.arrangeMenuItems(self.items))
        if not self.content.get_children():
            self.content.add(self.scroll)


    def arrangeMenuItems(self, items, columns=None, expand_last=False):
        """
            添加主界面按钮信息
            自动布局
        :param items:
        :param columns:
        :param expand_last:
        :return:
        """
        self.autogrid.clear()
        enabled = []
        for item in items:
            key = list(item)[0]
            if not self.evaluate_enable(item[key]['enable']):
                logging.debug(f"X > {key}")
                continue
        self.autogrid.__init__(enabled, columns, expand_last, self._screen.vertical_mode)
        return self.autogrid

    def create_child_items(self,i):
        self.counter =i
        key = list(self.items[i])[0]
        item = self.items[i][key]
        control_name = None
        if(item['type']=="Image"):
            control_name = Gtk.Image()
            image = self._screen.env.from_string(item['src']).render(self.j2_data) if item['src'] else None
            height = int(self._screen.env.from_string(item['height']).render(self.j2_data) if item['height'] else None)
            width = int(self._screen.env.from_string(item['width']).render(self.j2_data) if item['width'] else None)
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(image)
            scaled_pixbuf = pixbuf.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)
            control_name.set_from_pixbuf(scaled_pixbuf)
            self.counter += 1
        elif(item['type']=="Button"):
            self.counter += 1
            if(item["panel"] is not None):
                print(item)
            if(item["icon"] is not None):
                icon = self._screen.env.from_string(item['icon']).render(self.j2_data) if item['icon'] else None
                control_name = self._gtk.Button(icon)
            else:
                control_name = Gtk.Button()
                j = self.counter
                while j <len(self.items):
                    key = list(self.items[j])[0]
                    item = self.items[j]
                    if (item[key]['type'] == "Grid"):
                        self.labels[key] = Gtk.Grid(orientation=Gtk.Orientation.HORIZONTAL)
                        control_name.add(self.labels[key] )
                        j=j+1
                        while True:
                            key_child = list(self.items[j])[0]
                            item_child = self.items[j][key_child]
                            key_father = ' '.join(key_child.split()[:-1]) if key_child and key_child.strip() else ''
                            if (key_father == key and len((list(self.items[j])[0]).split()) > 1):
                                self.labels[key].attach(
                                    self.create_child_items(j),
                                    int(item_child['column']),
                                    int(item_child['row']),
                                    int(item_child['columnspan']),
                                    int(item_child['rowspan']))
                                j = self.counter
                            else:
                                j = self.counter
                                break
                    break
        elif(item['type'] == "Label"):
            value = self._screen.env.from_string(item['value']).render(self.j2_data) if item['value'] else None
            control_name = Gtk.Label(label=_(value))
            self.counter += 1
        elif(item['type'] == "Grid"):
            self.labels[key] = Gtk.Grid(orientation=Gtk.Orientation.HORIZONTAL)
            i+=1
            while i<len(self.items):
                key_child = list(self.items[i])[0]
                item_child = self.items[i][key_child]
                key_father = ' '.join(key_child.split()[:-1]) if key_child and key_child.strip() else ''
                if (key_father == key and len((list(self.items[i])[0]).split()) > 1):
                    self.labels[key].attach(
                        self.create_child_items(i),
                        int(item_child['column']),
                        int(item_child['row']),
                        int(item_child['columnspan']),
                        int(item_child['rowspan']))
                    i = self.counter
                else:
                    i = self.counter + 1
                    break
            return self.labels[key]
        return control_name




    def create_menu_items(self):
        """
            创建主界面 下半部分元素
        :return:
        """
        parent_grid = Gtk.Grid()
        count = sum(bool(self.evaluate_enable(i[next(iter(i))]['enable'])) for i in self.items)
        scale = 1.1 if 12 < count <= 16 else None  # hack to fit a 4th row
        self.counter = i = 0

        # for i in range(len(self.items)):
        while i<len(self.items):
            key = list(self.items[i])[0]
            item = self.items[i][key]
            if(item['type']=="Grid"):
                self.labels[key] = Gtk.Grid()
                parent_grid.attach(
                    self.labels[key] ,
                    int(item['column']),
                    int(item['row']),
                    int(item['columnspan']),
                    int(item['rowspan']))
                i+=1
                while i<len(self.items):
                    key_child = list(self.items[i])[0]
                    item_child = self.items[i][key_child]
                    key_father = ' '.join(key_child.split()[:-1]) if key_child and key_child.strip() else ''
                    if (key_father == key and len((list(self.items[i])[0]).split()) > 1):
                        self.labels[key].attach(
                            self.create_child_items(i),
                            int(item_child['column']),
                            int(item_child['row']),
                            int(item_child['columnspan']),
                            int(item_child['rowspan']))
                        i = self.counter
                    else:
                        i = self.counter
                        break
        self.labels['parent_grid']=parent_grid
        return self.labels['parent_grid']


            # box = Gtk.HBox(spacing=10)
            # box.set_border_width(10)
            # image = Gtk.Image()
            # button_box = Gtk.VBox(spacing=5)
            # b = Gtk.Button()
            #
            # name = self._screen.env.from_string(item['name']).render(self.j2_data)
            # icon = self._screen.env.from_string(item['icon']).render(self.j2_data) if item['icon'] else None
            # image.set_from_file(icon)
            # style = self._screen.env.from_string(item['style']).render(self.j2_data) if item['style'] else None
            # image_pixbuf = GdkPixbuf.Pixbuf.new_from_file(f"styles/material-dark/images/{icon}.svg")  # 打印模型
            # label = Gtk.Label(label=name)
            #
            #
            # if icon == "notifications" and (
            #     bool(self._screen.server_info["warnings"])
            #     or bool(self._printer.warnings)
            #     or bool(self._screen.server_info["failed_components"])
            #     or bool(self._screen.server_info["missing_klippy_requirements"])
            # ):
            #     icon = "notification_important"
            #
            # # b = self._gtk.Button(icon, name, style or f"color{i % 4 + 1}", scale=scale)
            #
            # # if item['panel']:
            # #     b.connect("clicked", self.menu_item_clicked, item)
            # # elif item['method'] == "ks_confirm_save":
            # #     b.connect("clicked", self._screen.confirm_save)
            # # elif item['method']:
            # #     params = {}
            # #
            # #     if item['params'] is not False:
            # #         try:
            # #             p = self._screen.env.from_string(item['params']).render(self.j2_data)
            # #             params = json.loads(p)
            # #         except Exception as e:
            # #             logging.exception(f"Unable to parse parameters for [{name}]:\n{e}")
            # #             params = {}
            # #
            # #     if item['confirm'] is not None:
            # #         b.connect("clicked", self._screen._confirm_send_action, item['confirm'], item['method'], params)
            # #     else:
            # #         b.connect("clicked", self._screen._send_action, item['method'], params)
            # # else:
            # #     b.connect("clicked", self._screen._go_to_submenu, key)
            # if key == "print_file_list":
            #     button_box=Gtk.HBox(spacing=5)
            #     image_scaled_pixbuf = image_pixbuf.scale_simple(100, 100, GdkPixbuf.InterpType.BILINEAR)
            #     image.set_from_pixbuf(image_scaled_pixbuf)
            #     button_box.pack_start(image, False, False, 0)
            #     button_box.pack_start(label, False, False, 0)
            #     b.add(button_box)
            # elif key == "nozzle_extruder":
            #     image_scaled_pixbuf = image_pixbuf.scale_simple(100, 100, GdkPixbuf.InterpType.BILINEAR)
            #     image.set_from_pixbuf(image_scaled_pixbuf)
            #
            #     button_box.pack_start(image, False, False, 0)
            #     button_box.pack_start(label, False, False, 0)
            #     b.add(button_box)
            # elif key == "wifi":
            #     image_scaled_pixbuf = image_pixbuf.scale_simple(100, 100, GdkPixbuf.InterpType.BILINEAR)
            #     image.set_from_pixbuf(image_scaled_pixbuf)
            #     button_box.pack_start(image, False, False, 0)
            #     button_box.pack_start(label, False, False, 0)
            #     b.add(button_box)
            # elif key == "notifications":
            #     image_scaled_pixbuf = image_pixbuf.scale_simple(100, 100, GdkPixbuf.InterpType.BILINEAR)
            #     image.set_from_pixbuf(image_scaled_pixbuf)
            #     button_box.pack_start(image, False, False, 0)
            #     button_box.pack_start(label, False, False, 0)
            #     b.add(button_box)
            #
            # self.labels[key] = b

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
