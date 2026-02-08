import json
import logging
from xxlimited_35 import Null

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, GdkPixbuf, Gdk
from jinja2 import Template
from ks_includes.screen_panel import ScreenPanel
from ks_includes.widgets.autogrid import AutoGrid

STATIC_CONSUMABLES = {
    'supplier_select': ('Bambu Lab', 'Generic', 'Polymaker', 'Overture', 'eSUN'),  # 元组不可修改
    'consumables_select': ('PLA', 'PETH', 'TPU'),
    'dynamic_pressure_control_select': ('Default','Other')
}

class Panel(ScreenPanel):

    def __init__(self, screen, title, items=None):
        super().__init__(screen, title)
        self.items = items
        self.j2_data = self._printer.get_printer_status_data()
        self.create_menu_items(title)
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



    def create_menu_items(self,panel_name):
        """
            创建主界面 下半部分元素
        :return:
        """
        parent_grid = Gtk.Grid()
        self.counter = i = 0
        self.create_radionButton = False
        self.radioButton = {}
        self.entry = {}
        while i<len(self.items):
            key = list(self.items[i])[0]
            item = self.items[i][key]
            parent_grid.attach(self.create_child_items(i),
                    int(item['column']),
                    int(item['row']),
                    int(item['columnspan']),
                    int(item['rowspan']))
            i = self.counter
        parent_grid.set_name(panel_name)
        if(panel_name == "printer_control_menu" or panel_name == "messages_menu"):
            parent_grid.set_row_homogeneous(True)

        self.labels['parent_grid'] = parent_grid
        # self.content.add(parent_grid)

    def create_child_items(self,i):
        self.counter =i
        key = list(self.items[i])[0]
        key_array=key.split(' ')
        item = self.items[i][key]
        item_control_name = None

        if(item['type']=="Image"):
            item_control_name = Gtk.Image()
            item_control_name.set_name(key_array[len(key_array)-1])
            image = self._screen.env.from_string(item['src']).render(self.j2_data) if item['src'] else None
            height = int(self._screen.env.from_string(item['height']).render(self.j2_data) if item['height'] else None)
            width = int(self._screen.env.from_string(item['width']).render(self.j2_data) if item['width'] else None)
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(image)
            scaled_pixbuf = pixbuf.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)
            item_control_name.set_from_pixbuf(scaled_pixbuf)
            self.counter += 1

        elif(item['type']=="Button"):
            self.counter += 1
            value = self._screen.env.from_string(item['value']).render(self.j2_data) if item['value'] else None
            style = self._screen.env.from_string(item['style']).render(self.j2_data) if item['style'] else None
            icon = self._screen.env.from_string(item['icon']).render(self.j2_data) if item['icon'] else None
            width = self._screen.env.from_string(item['width']).render(self.j2_data) if item['width'] else None
            height = self._screen.env.from_string(item['height']).render(self.j2_data) if item['height'] else None
            position = self._screen.env.from_string(item['position']).render(self.j2_data) if item['position'] else None
            button_width = self._screen.env.from_string(item['button_width']).render(self.j2_data) if item['button_width'] else None
            button_height = self._screen.env.from_string(item['button_height']).render(self.j2_data) if item['button_height'] else None
            hexpand = self._screen.env.from_string(item['button_hexpand']).render(self.j2_data) if item['button_hexpand'] else None
            vexpand = self._screen.env.from_string(item['button_vexpand']).render(self.j2_data) if item['button_vexpand'] else None
            item_control_name = self._gtk.Button(icon,value,style,width,height,hexpand,vexpand,position)
            if (item["panel"] != None):
                parameter_item = {
                    "panel": item["panel"],
                    "icon": None,
                }
                item_control_name.connect("clicked", self.menu_item_clicked, parameter_item)
            elif(key_array[len(key_array)-1] == 'go_back'):
                item_control_name.connect("clicked", self._screen._menu_go_back)
            elif(item['method'] == 'show_dialog'):
                item_control_name.connect("clicked", self.show_dialog)
            elif(item['method'] == 'on_digit_clicked'):
                item_control_name.connect("clicked", self.on_digit_clicked ,value,key_array[len(key_array)-3])
            elif(item['method'] == 'set_nozzle_type'):
                item_control_name.connect("clicked", self.set_nozzle_type)

            if(self.counter<len(self.items)):
                key_child = list(self.items[self.counter])[0]
                item_child = self.items[self.counter]
                if (item_child[key_child]['type'] == "Grid" and len(key_child.split(" "))>len(key.split(" "))):
                    item_control_name.add(self.create_child_items(self.counter))

        elif(item['type'] == "Label"):
            value = self._screen.env.from_string(item['value']).render(self.j2_data) if item['value'] else None
            if(key_array[len(key_array)-1] == "percentage_progress"):
                self.percentage_progress=int(value)*0.01;
                value=f"{value}%"
            item_control_name = Gtk.Label(label=_(value))
            self.counter += 1
        elif(item['type'] == "Grid"):#移除默认边框
            item_control_name = Gtk.Grid(orientation=Gtk.Orientation.HORIZONTAL)
            item_control_name.set_name(key_array[len(key_array)-1])
            height = int(self._screen.env.from_string(item['height']).render(self.j2_data) if item['height'] else None)
            width = int(self._screen.env.from_string(item['width']).render(self.j2_data) if item['width'] else None)
            item_control_name.set_size_request(width, height)
            if(item['column_spacing'] != None):
                column_spacing = int(self._screen.env.from_string(item['column_spacing']).render(self.j2_data) if item['column_spacing'] else None)
                item_control_name.set_column_spacing(50)
            if(item['row_spacing'] != None):
                row_spacing =int(self._screen.env.from_string(item['row_spacing']).render(self.j2_data) if item['row_spacing'] else None)
                item_control_name.set_row_spacing(50)
            if (item['column_homogeneous'] == 'True'):
                item_control_name.set_column_homogeneous(True)
            if (item['row_homogeneous'] == 'True'):
                item_control_name.set_row_homogeneous(True)
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
            self.counter += 1

        elif (item['type'] == "ProgressBar"):
            item_control_name= Gtk.ProgressBar()
            #设置进度条百分比
            item_control_name.set_fraction(self.percentage_progress)
            item_control_name.set_show_text(False)
            width = int(self._screen.env.from_string(item['width']).render(self.j2_data) if item['width'] else None)
            height = int(self._screen.env.from_string(item['height']).render(self.j2_data) if item['height'] else None)
            item_control_name.set_size_request(width, height)
            self.counter += 1

        elif (item['type'] == "RadioButton"):
            value = self._screen.env.from_string(item['value']).render(self.j2_data) if item['value'] else None
            if(not self.create_radionButton):
                self.radioButton['radio_button_group'] =  Gtk.RadioButton.new_with_label_from_widget(None, value)
                item_control_name = self.radioButton['radio_button_group']
                self.create_radionButton = True
            else:
                item_control_name = Gtk.RadioButton.new_with_label_from_widget(self.radioButton['radio_button_group'], value)
                # self.radioButton[key].connect("toggled", self.on_radio_toggled, value)
                # 创建单选按钮组（普通样式，无圆形图标）
                # self.radioButton[key].set_mode(False)
            self.counter += 1

        elif (item['type'] == "Entry"):
            value = self._screen.env.from_string(item['value']).render(self.j2_data) if item['value'] else None
            item_control_name = Gtk.Entry()
            item_control_name.set_text("℃")  # 初始带单位
            item_control_name.set_position(0)  # 光标在最前
            item_control_name.set_alignment(0.5) #文本居中
            self.entry[key_array[len(key_array)-2]] = item_control_name
            self.counter += 1

        elif (item['type'] == "ComboBoxText"):
            item_control_name = Gtk.ComboBoxText()
            combobox_key=key_array[len(key_array)-1]
            combobox_items=STATIC_CONSUMABLES[combobox_key]
            for item in combobox_items:
                item_control_name.append_text(item)
            item_control_name.set_active(0)
            self.counter += 1

        elif (item['type'] == "ColorButton"):
            item_control_name = Gtk.ColorButton()
            value = self._screen.env.from_string(item['value']).render(self.j2_data) if item['value'] else None
            rgba = Gdk.RGBA()
            rgba.parse(value)  # 可以是 "blue", "#ff0000", "rgb(255,0,0)" 等
            item_control_name.set_rgba(rgba)
            item_control_name.connect("color-set", self.on_color_chosen)
            self.counter += 1

        return item_control_name


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
