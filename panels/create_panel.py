import json
import logging
from xxlimited_35 import Null
import os

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, GdkPixbuf, Gdk, Pango
from jinja2 import Template
from datetime import datetime
from ks_includes.screen_panel import ScreenPanel
from ks_includes.KlippyGtk import find_widget
from ks_includes.widgets.flowboxchild_extended import PrintListItem
STATIC_CONSUMABLES = {
    'supplier_select': ('Bambu Lab', 'Generic', 'Polymaker', 'Overture', 'eSUN'),
    'consumables_select': ('PLA', 'PETH', 'TPU'),
    'dynamic_pressure_control_select': ('Default','Other')
}

from panels.print import (refresh_loading,
                                    cancel,
                                    set_loading,
                                    pause_confirm,
                                    update_time_left,
                                    create_print_file_list_item)
from panels.printer_control import (move,
                                  direction_home,
                                  on_digit_clicked,
                                  change_sprot_speed,
                                  change_target_temp)
from panels.edit_consumables import consumables_dialog,change_consumables_button,check_min_temp

class Panel(ScreenPanel):

    def __init__(self, screen, title, items=None, **panel_args):
        super().__init__(screen, title)
        self.items = items
        self.loading_msg = _('Loading...')
        self.j2_data = self._printer.get_printer_status_data()
        self.create_menu_items(title,**panel_args)
        self.scroll = self._gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        if "flowbox" in self.labels:
            self._screen._ws.klippy.get_dir_info(self.load_files, self.cur_directory)


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



    def create_menu_items(self,panel_name,fileinfo=None,father=None,select_extruder=None):
        """
            创建主界面 下半部分元素
        :return:
        """
        parent_grid = Gtk.Grid()
        self.counter = i = 0
        self.create_radionButton = False
        self.radioButton = {}
        self.entry = {}
        self.percentage_progress = 0.5;
        self.cur_directory = 'gcodes'
        self.list_mode = True
        self.time_24 = self._config.get_main_config().getboolean("24htime", True)
        self.list_button_size = self._gtk.img_scale * self.bts
        self.thumbsize = self._gtk.img_scale * self._gtk.button_image_scale * 2.5
        self.select_extruder="T0: "
        self.change_item = ['print_busy',
                            'chassis_temperature', 'heater_bed_temperature', 'extruder_temperature', 'extruder1_temperature',
                            'percentage_progress', 'floor_height_progress', 'remaining_time','floor_height_progress',
                            'print_modeling_graphics', 'print_file_name', 'print_state','pause_button',
                            't0_extruder_consumables_control',]
        if panel_name == "sport_control":
            self.labels["distance"]=10
            self.labels['distance_button']=[]
        if panel_name == "control_consumables":
            self.labels["length"]=10
            self.labels['length_button']=[]
            self.labels["speed"] = 10
            self.labels['speed_button'] = []

        while i< len(self.items):
            key = list(self.items[i])[0]
            item = self.items[i][key]
            parent_grid.attach(self.create_child_items(i,panel_name,fileinfo,father,select_extruder),
                    int(item['column']),
                    int(item['row']),
                    int(item['columnspan']),
                    int(item['rowspan']))
            i = self.counter
        parent_grid.set_name(panel_name)
        if(panel_name == "printer_control_menu" or panel_name == "messages_menu" ):
            parent_grid.set_row_homogeneous(True)
        if panel_name == "print_file_list":
            self._screen._ws.klippy.get_dir_info(self.load_files, self.cur_directory)
        self.labels['parent_grid'] = parent_grid
        # self.content.add(parent_grid)

    def create_child_items(self,i,panel_name,fileinfo=None,father=None,select_extruder=None):
        self.counter =i
        key = list(self.items[i])[0]
        key_array=key.split(' ')
        current_key=key_array[len(key_array)-1]
        item = self.items[i][key]
        item_control_name = None

        if(item['type']=="Image"):
            self.counter += 1
            item_control_name = Gtk.Image()
            item_control_name.set_name(current_key)
            image = self._screen.env.from_string(item['src']).render(self.j2_data) if item['src'] else None
            height = int(self._screen.env.from_string(item['height']).render(self.j2_data) if item['height'] else None)
            width = int(self._screen.env.from_string(item['width']).render(self.j2_data) if item['width'] else None)
            pixbuf = ''
            if fileinfo is not None and current_key in self.change_item:
                pixbuf = self.get_file_image(fileinfo["path"], height, width, False)
                item_control_name = Gtk.Image.new_from_pixbuf(pixbuf)
            else:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(image)
                scaled_pixbuf = pixbuf.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)
                item_control_name.set_from_pixbuf(scaled_pixbuf)

            if current_key == 'print_modeling_graphics':
                self.labels[current_key]=item_control_name
                return self.labels[current_key]

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
            hexpand = self._screen.env.from_string(item['hexpand']).render(self.j2_data) if item['hexpand'] else None
            vexpand = self._screen.env.from_string(item['vexpand']).render(self.j2_data) if item['vexpand'] else None
            item_control_name = self._gtk.Button(icon,value,style,width,height,hexpand,vexpand,button_width,button_height,position)
            parameter_item = {
                "panel": item["panel"],
                "fileinfo": fileinfo,
                "father":panel_name,
                "icon": None
            }
            if (item["panel"] != None and item["panel"] == 'print_menu') and father !='print_menu':
                item_control_name.connect("clicked", print_start, parameter_item)
            if item["panel"] != None:
                item_control_name.connect("clicked", self.menu_item_clicked, parameter_item)
            elif(current_key == 'go_back'):
                item_control_name.connect("clicked", self._screen._menu_go_back)
            elif(item['method'] == 'show_dialog'):
                item_control_name.connect("clicked", self.show_dialog,current_key)
            elif(item['method'] == 'consumables_dialog'):
                # current_key :t1_extruder_consumables_control
                item_control_name.connect("clicked", consumables_dialog,self,current_key)
            elif(item['method'] == 'on_digit_clicked'):
                #panel_name extruder_temperature chassis_temperature heater_bed_temperature
                item_control_name.connect("clicked", on_digit_clicked, self, value, panel_name)
            elif(item['method'] == 'set_nozzle_type'):
                item_control_name.connect("clicked", self.set_nozzle_type)
            elif (item['method'] == 'refresh_loading'):
                item_control_name.connect("clicked", refresh_loading,self)
            elif (item['method'] == 'cancel_confirm'):
                item_control_name.connect("clicked", cancel,self)
            elif (item['method'] == 'pause_confirm'):
                item_control_name.connect("clicked", pause_confirm,self)
            elif (item['method'] == 'change_target_temp'):
                #更改腔温 热床温度
                #panel_name extruder_temperature chassis_temperature heater_bed_temperature
                item_control_name.connect("clicked", change_target_temp,self,panel_name,value)
            elif (item['method'] == 'move'):
                item_control_name.connect("clicked", move,self,value)
            elif (item['method'] == 'direction_home'):
                item_control_name.connect("clicked", direction_home,self,value)
            elif (item['method'] == 'change_consumables_length'):
                item_control_name.connect("clicked", change_consumables_button,self,'length',value)
            elif (item['method'] == 'change_consumables_speed'):
                item_control_name.connect("clicked", change_consumables_button,self,'speed',value)
            elif (item['method'] == 'check_min_temp'):
                item_control_name.connect("clicked", check_min_temp,self,current_key)

            if current_key.startswith('distance'):
                self.labels['distance_button'].append(item_control_name)
            if current_key.startswith('length'):
                self.labels['length_button'].append(item_control_name)
            if current_key.startswith('speed_consumables') :
                self.labels['speed_button'].append(item_control_name)
            if current_key=='print_busy':
                if  father == 'print_menu':
                    item_control_name.set_no_show_all(False)
                else:
                    item_control_name.set_no_show_all(True)

            if(self.counter<len(self.items)):
                key_child = list(self.items[self.counter])[0]
                item_child = self.items[self.counter]
                if (item_child[key_child]['type'] == "Grid" and len(key_child.split(" "))>len(key.split(" "))):
                    item_control_name.add(self.create_child_items(self.counter,panel_name,fileinfo,father))

            if current_key in self.change_item:
                self.labels[current_key]=item_control_name
                return self.labels[current_key]

        elif(item['type'] == "Label"):
            self.counter += 1
            value = ''
            if current_key in {'file_name', 'print_file_name','print_modeling_graphics'} and fileinfo is not None:
                item_control_name = Gtk.Label(hexpand=True, halign=Gtk.Align.START, ellipsize=Pango.EllipsizeMode.END)
                value=fileinfo['filename'].replace('.gcode', '')
                item_control_name.set_markup(f"<b>{value}</b>")
                return item_control_name
            else:
                value = self._screen.env.from_string(item['value']).render(self.j2_data) if item['value'] else None

            # if (key_array[len(key_array) - 1] in self.change_item):
            #     value=self._printer.get_stat(key_array[len(key_array) - 1], "temperature")

            if(current_key == "percentage_progress"):
                self.percentage_progress=int(value)*0.01;
                value=f"{value}%"

            if select_extruder is not None:
                if select_extruder == 'extruder':
                    select_extruder = "T0: "
                else:
                    select_extruder = "T1: "
                if  current_key == "edit_consumables_label" or "control_consumables_label":
                    value = f"{select_extruder}{value}"

            if (key_array[len(key_array) - 1] == "space_label"):
                item_control_name = Gtk.Label()
                item_control_name.set_hexpand(True)
            else:
                item_control_name = Gtk.Label(label=_(value))


            if current_key in self.change_item:
                self.labels[current_key]=item_control_name
                return self.labels[current_key]

        elif(item['type'] == "Grid"):#移除默认边框
            item_control_name = Gtk.Grid(orientation=Gtk.Orientation.HORIZONTAL)
            item_control_name.set_name(current_key)
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
            if (key_array[len(key_array) - 1] == "file_list_body_grid"):
                self.labels['flowbox']= item_control_name
                self.counter=i
                return self.labels['flowbox']
            while i<len(self.items):
                key_child = list(self.items[i])[0]
                key_father = ' '.join(key_child.split()[:-1]) if key_child and key_child.strip() else ''
                item_child = self.items[i][key_child]
                if (key_father == key and len((list(self.items[i])[0]).split()) > 1):
                    item_control_name.attach(self.create_child_items(i,panel_name,fileinfo,father,select_extruder),
                                       int(item_child['column']),
                                       int(item_child['row']),
                                       int(item_child['columnspan']),
                                       int(item_child['rowspan']))
                    i = self.counter
                else:
                    i = self.counter + 1
                    break
        elif (item['type'] == "Switch"):
            self.counter += 1
            item_control_name= Gtk.Switch()
            value = self._screen.env.from_string(item['value']).render(self.j2_data) if item['value'] else None
            # width = int(self._screen.env.from_string(item['width']).render(self.j2_data) if item['width'] else None)
            # height = int(self._screen.env.from_string(item['height']).render(self.j2_data) if item['height'] else None)
            # item_control_name.set_size_request(width, height)
            item_control_name.set_active(bool(value))

        elif (item['type'] == "ProgressBar"):
            self.counter += 1
            item_control_name= Gtk.ProgressBar()
            #设置进度条百分比
            item_control_name.set_fraction(self.percentage_progress)
            item_control_name.set_show_text(False)
            width = int(self._screen.env.from_string(item['width']).render(self.j2_data) if item['width'] else None)
            height = int(self._screen.env.from_string(item['height']).render(self.j2_data) if item['height'] else None)
            item_control_name.set_size_request(width, height)
            self.labels['progressBar']=item_control_name

        elif (item['type'] == "RadioButton"):
            self.counter += 1
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

        elif (item['type'] == "Entry"):
            self.counter += 1
            value = self._screen.env.from_string(item['value']).render(self.j2_data) if item['value'] else None
            item_control_name = Gtk.Entry()
            item_control_name.set_text("℃")  # 初始带单位
            item_control_name.set_position(0)  # 光标在最前
            item_control_name.set_alignment(0.5) #文本居中
            item_control_name.set_size_request(400,100)
            item_control_name.get_style_context().add_class("entry_temperature")
            # panel_name extruder_temperature chassis_temperature heater_bed_temperature
            self.entry[panel_name] = item_control_name

        elif (item['type'] == "ComboBoxText"):
            self.counter += 1
            item_control_name = Gtk.ComboBoxText()
            combobox_key=current_key
            combobox_items=STATIC_CONSUMABLES[combobox_key]
            for combobox_item in combobox_items:
                item_control_name.append_text(combobox_item)
            item_control_name.set_active(0)
            width = int(self._screen.env.from_string(item['width']).render(self.j2_data) if item['width'] else None)
            height = int(self._screen.env.from_string(item['height']).render(self.j2_data) if item['height'] else None)
            item_control_name.set_size_request(width, height)
            style = self._screen.env.from_string(item['style']).render(self.j2_data) if item['style'] else None
            item_control_name.get_style_context().add_class(style)



        elif (item['type'] == "TextView"):
            self.counter += 1
            value = self._screen.env.from_string(item['value']).render(self.j2_data) if item['value'] else None
            item_control_name = Gtk.TextView()
            item_control_name.set_editable(False)# 设为只读
            item_control_name.set_cursor_visible(False)  # 隐藏光标（可选）
            buffer = item_control_name.get_buffer()
            buffer.set_text(value)

        elif (item['type'] == "CheckButton"):
            self.counter += 1
            value = self._screen.env.from_string(item['value']).render(self.j2_data) if item['value'] else None
            item_control_name = Gtk.CheckButton(label=_(value))
            item_control_name.set_active(True)  # 设为选中

        elif (item['type'] == "ColorButton"):
            self.counter += 1
            item_control_name = Gtk.ColorButton()
            value = self._screen.env.from_string(item['value']).render(self.j2_data) if item['value'] else None
            rgba = Gdk.RGBA()
            rgba.parse(value)  # 可以是 "blue", "#ff0000", "rgb(255,0,0)" 等
            item_control_name.set_rgba(rgba)
            item_control_name.connect("color-set", self.on_color_chosen)

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

    def process_update(self, panel_name,action,data):
        if panel_name == "home_menu" or panel_name == "printer_control_menu":
            for dev in self.labels:
                for type in ('extruder', 'extruder1','heater_bed','chassis'):
                    if dev.endswith(f'{type}_temperature'):
                        if type == "chassis":
                            type = "temperature_sensor filament_box_temp"
                        self.update_temp(
                            type,
                            self._printer.get_stat(type, "temperature"),
                            self._printer.get_stat(type, "target"),
                            self._printer.get_stat(type, "power"),
                            name=dev
                        )
                        break
        elif panel_name == "print_menu" and action == 'notify_status_update':
            update_time_left(self,data)
        #   删除文件后刷新页面
        elif "action" in data and data["action"] == "delete_file":
            refresh_loading(None,self)

    #打印文件列表页面，加载文件列表方法
    def load_files(self, result,method, params):
        set_loading(self,True)
        items = [create_print_file_list_item(self,item) for item in
                 [*result["result"]["dirs"], *result["result"]["files"]]]
        i = column = row = 0
        for item in filter(None, items):
            self.labels['flowbox'].attach(item, column, row, 1, 1)
            i += 1
            if i % 4 == 0:
                row += 1
                column = 0
            else:
                column += 1
        set_loading(self,False)



