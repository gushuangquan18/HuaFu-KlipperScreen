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

def format_label(widget):
    label = find_widget(widget, Gtk.Label)
    if label is not None:
        label.set_line_wrap_mode(Pango.WrapMode.CHAR)
        label.set_line_wrap(True)
        label.set_ellipsize(Pango.EllipsizeMode.END)
        label.set_lines(3)


class Panel(ScreenPanel):

    def __init__(self, screen, title, items=None, fileinfo=None):
        super().__init__(screen, title)
        self.items = items
        self.loading_msg = _('Loading...')
        self.j2_data = self._printer.get_printer_status_data()
        self.create_menu_items(title,fileinfo)
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



    def create_menu_items(self,panel_name,fileinfo=None):
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
        self.change_item = ['chassis_temperature', 'hotbed_temperature', 'left_nozzle_extruder', 'right_nozzle_extruder',
                            'percentage_progress', 'floor_height_progress', 'remaining_time','floor_height_progress',
                            'print_modeling_graphics', 'print_file_name', 'print_state','pause_button']
        while i< len(self.items):
            key = list(self.items[i])[0]
            item = self.items[i][key]
            parent_grid.attach(self.create_child_items(i,fileinfo),
                    int(item['column']),
                    int(item['row']),
                    int(item['columnspan']),
                    int(item['rowspan']))
            i = self.counter
        parent_grid.set_name(panel_name)
        if(panel_name == "printer_control_menu" or panel_name == "messages_menu"):
            parent_grid.set_row_homogeneous(True)
        if panel_name == "print_file_list":
            self._screen._ws.klippy.get_dir_info(self.load_files, self.cur_directory)
        self.labels['parent_grid'] = parent_grid
        # self.content.add(parent_grid)

    def create_child_items(self,i,fileinfo=None):
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
                "icon": None
            }
            if (item["panel"] != None and item["panel"] == 'print_menu'):
                item_control_name.connect("clicked", self.print_start, parameter_item)
            if (item["panel"] != None):
                item_control_name.connect("clicked", self.menu_item_clicked, parameter_item)
            elif(current_key == 'go_back'):
                item_control_name.connect("clicked", self._screen._menu_go_back)
            elif(item['method'] == 'show_dialog'):
                item_control_name.connect("clicked", self.show_dialog,current_key)
            elif(item['method'] == 'on_digit_clicked'):
                item_control_name.connect("clicked", self.on_digit_clicked ,value,key_array[len(key_array)-3])
            elif(item['method'] == 'set_nozzle_type'):
                item_control_name.connect("clicked", self.set_nozzle_type)
            elif (item['method'] == 'refresh_loading'):
                item_control_name.connect("clicked", self.refresh_loading)
            elif (item['method'] == 'cancel_confirm'):
                item_control_name.connect("clicked", self.cancel_confirm)
            elif (item['method'] == 'pause_confirm'):
                item_control_name.connect("clicked", self.pause_confirm)

            if(self.counter<len(self.items)):
                key_child = list(self.items[self.counter])[0]
                item_child = self.items[self.counter]
                if (item_child[key_child]['type'] == "Grid" and len(key_child.split(" "))>len(key.split(" "))):
                    item_control_name.add(self.create_child_items(self.counter,fileinfo))

            if current_key in self.change_item:
                self.labels[current_key]=item_control_name
                return self.labels[current_key]

        elif(item['type'] == "Label"):
            self.counter += 1
            if current_key in {'file_name', 'print_file_name','print_modeling_graphics'} and fileinfo is not None:
                item_control_name = Gtk.Label(hexpand=True, halign=Gtk.Align.START, ellipsize=Pango.EllipsizeMode.END)
                value=fileinfo['filename'].replace('.gcode', '')
                item_control_name.set_markup(f"<b>{value}</b>")
                return item_control_name
            else:
                value = self._screen.env.from_string(item['value']).render(self.j2_data) if item['value'] else None

            if (key_array[len(key_array) - 1] == "nozzle1_temperature"):
                value=self._printer.get_stat('extruder', "temperature")

            if(current_key == "percentage_progress"):
                self.percentage_progress=int(value)*0.01;
                value=f"{value}%"

            if (key_array[len(key_array) - 1] == "space_label"):
                item_control_name = Gtk.Label()
                item_control_name.set_hexpand(True)
            else:
                item_control_name = Gtk.Label(label=_(value))


            if current_key in self.change_item:
                self.labels[current_key]=item_control_name
                return self.labels[current_key]

            if key_array[len(key_array) - 1].endswith("extruder_temperature") :
                self.labels[key_array[len(key_array) - 1]] = item_control_name
                return self.labels[key_array[len(key_array) - 1]]

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
                    item_control_name.attach(self.create_child_items(i,fileinfo),
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
            self.entry[key_array[len(key_array)-2]] = item_control_name

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
        if panel_name == "home_menu":
            for dev in self.labels:
                if dev.endswith("extruder_temperature"):
                    self.update_temp(
                        'extruder',
                        self._printer.get_stat('extruder', "temperature"),
                        self._printer.get_stat('extruder', "target"),
                        self._printer.get_stat('extruder', "power"),
                        name=dev
                    )
        elif panel_name == "print_menu" and action == 'notify_status_update':
            self.update_time_left(data)

    def update_time_left(self,data):

        a=0

        if ('virtual_sdcard' in data) and ('file_path' in data['virtual_sdcard']):
            #'/home/orangepi/printer_data/gcodes/Rabbit.gcode'
            if data['virtual_sdcard']['file_path'] is not None:
                path=data['virtual_sdcard']['file_path']
                name = os.path.splitext(os.path.basename(path))[0]
                self.labels["print_file_name"].set_label(name)
                # 设置缩放后的图片到Image控件 'Box.gcode'

                # pixbuf = self.get_file_image(path, 320, 320, False)
                # ['http', '.thumbs/Box-300x300.png']
                path = f'.thumbs/{name}-300x300.png'
                pixbuf=self._gtk.PixbufFromHttp(path, 300, 300)
                self.labels["print_modeling_graphics"].set_from_pixbuf(pixbuf)

            if 'progress' in data['virtual_sdcard']:
                percentage_progress = data['virtual_sdcard']['progress']
                self.labels["percentage_progress"].set_label(f' {int(percentage_progress*100)}%')
                self.labels['progressBar'].set_fraction(percentage_progress)


        if ('heater_bed' in data) and ('temperature' in data['heater_bed']):
            self.labels["hotbed_temperature"].set_label(f'{int(data['heater_bed']['temperature'])}℃')

        if ('heater_bed' in data) and ('temperature' in data['heater_bed']):
            self.labels["chassis_temperature"].set_label(f'{int(data['heater_bed']['temperature'])}℃')

        if ('extruder' in data) and ('temperature' in data['extruder']):
            self.labels["left_nozzle_extruder"].set_label(f'{int(data['extruder']['temperature'])}℃')
            self.labels["right_nozzle_extruder"].set_label(f'{int(data['extruder']['temperature'])}℃')
        if ('toolhead' in data) and ('estimated_print_time' in data['toolhead']):
            estimated_print_time=int(data['toolhead']['estimated_print_time'])
            self.labels["remaining_time"].set_label(f' - {self.print_time_format(estimated_print_time)}')
        if ('print_stats' in data) and ('state' in data['print_stats']):
            if data['print_stats']['state'] == 'paused':
                self.change_pause_button_state(data['print_stats']['state'])
        if ('webhooks' in data) and ('state' in data['webhooks']):
            #  打印层数 数据未实时更新
            self.labels["floor_height_progress"].set_label(f' 2/30 |')

    # 'floor_height_progress'

    def pause_confirm(self, widget):
        logging.debug("Pauseing print")
        state = ''
        if self.labels['print_state'].get_label() == "打印中":
            state = 'paused'
        elif self.labels['print_state'].get_label() == " 暂 停":
            state = 'printing'
        self.change_pause_button_state(state)

    def change_pause_button_state(self,state):
        pixbuf = ''
        state_text = ''
        filename = ''
        # printing 打印中 paused暂停
        if state == "printing":
            self._screen._ws.klippy.print_resume()
            state_text = "打印中"
            filename="images/pause.png"

        elif state == "paused":
            self._screen._ws.klippy.print_pause()
            state_text = " 暂 停"
            filename = "images/start.png"

        self.labels['print_state'].set_label(state_text)
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=filename,
            width=50,
            height=50,
            preserve_aspect_ratio=True  # 设为False则强制50x50（可能拉伸）
        )
        # 设置缩放后的图片到Image控件
        image = Gtk.Image.new_from_pixbuf(pixbuf)
        self.labels['pause_button'].set_image(image)

    def cancel_confirm(self,widget):
        logging.debug("Canceling print")
        self._screen._ws.klippy.print_cancel()
        parameter_item = {
            "panel": "home_menu",
            "icon": "home_menu_icon",
        }
        self.menu_item_clicked(widget,parameter_item)





    def print_time_format(self,time):
        if time< 3600:
            return  f'{int(time / 60)}m'
        else:
            hours = int(time/ 3600)
            minutes = int((time - hours * 3600) / 60)
            return f'{hours}h{minutes}m'

    def load_files(self, result, method, params):
        self.set_loading(True)

        items = [self.create_print_file_list_item(item) for item in [*result["result"]["dirs"], *result["result"]["files"]]]
        i = column = row = 0
        for item in filter(None, items):
            self.labels['flowbox'].attach(item,column,row,1,1)
            i+=1
            if i%4==0:
                row += 1
                column = 0
            else:
                column += 1
        self.set_loading(False)

    def create_print_file_list_item(self, item):
        name = path = ''
        if 'dirname' in item:
            if item['dirname'].startswith("."):
                return
            name = item['dirname']
            path = f"{self.cur_directory}/{name}"
        elif 'filename' in item:
            if (item['filename'].startswith(".") or
                    os.path.splitext(item['filename'])[1] not in {'.gcode', '.gco', '.g'}):
                return
            name = item['filename']
            path = f"{self.cur_directory}/{name}"
            path = path.replace('gcodes/', '')
        else:
            logging.error(f"Unknown item {item}")
            return
        basename = os.path.splitext(name)[0]
        print_file=Gtk.Button()
        fileinfo = self._screen.files.get_file_info(path)
        # 暂时不用选择打印的盘 select_disc_print
        parameter_item = {
            "panel": 'matching_consumables',
            "fileinfo":fileinfo,
            "icon": None
        }
        print_file.connect("clicked", self.menu_item_clicked, parameter_item)
        button_grid = Gtk.Grid(hexpand=True, vexpand=False, valign=Gtk.Align.CENTER)
        print_file.add(button_grid)
        if self.list_mode:
            itemname = Gtk.Label(hexpand=True, halign=Gtk.Align.START, ellipsize=Pango.EllipsizeMode.END)
            itemname.set_markup(f"<b>{basename}</b>")
            estimated_time = Gtk.Label(
                hexpand=True, halign=Gtk.Align.START, xalign=0,
                wrap=True, wrap_mode=Pango.WrapMode.WORD_CHAR,
            )
            if "estimated_time" in fileinfo:
                estimated_time.set_markup(f'<b>T:</b>{self.print_time_format(fileinfo["estimated_time"])}')
            filament_weight_total = Gtk.Label(
                hexpand=True, halign=Gtk.Align.START, xalign=0,
                wrap=True, wrap_mode=Pango.WrapMode.WORD_CHAR,
            )
            if "filament_weight_total" in fileinfo:
                filament_weight_total.set_markup(f'<b>W</b>:{fileinfo["filament_weight_total"]}g')

            icon = Gtk.Button()
            button_grid.attach(icon, 0, 0, 4, 4)
            button_grid.attach(itemname, 0, 4, 4, 1)
            button_grid.attach(estimated_time, 1, 5, 1, 1)
            button_grid.attach(filament_weight_total, 3, 5, 1, 1)
            image_args = (path, icon, self.thumbsize / 2, True, "file")

        else:  # Thumbnail view
            icon = self._gtk.Button(label=basename)
            if 'filename' in item:
                image_args = (path, icon, self.thumbsize, False, "file")
            elif 'dirname' in item:
                image_args = (None, icon, self.thumbsize, False, "folder")
            else:
                return
        self.image_load(*image_args)
        return print_file

    def image_load(self, filepath, widget, size=-1, small=False, iconname=None):
        pixbuf = self.get_file_image(filepath, 170, 150, False)
        if pixbuf is not None:
            widget.set_image(Gtk.Image.new_from_pixbuf(pixbuf))
        elif iconname is not None:
            widget.set_image(self._gtk.Image(iconname, 170, 150))
        format_label(widget)

    #判断加载显示完所有文件信息后显示页面
    def set_loading(self, loading):
        self.loading = loading
        for child in self.labels['flowbox'].get_children():
            child.set_sensitive(not loading)
        if loading:
            self.labels['flowbox'].show()
            return
        if self.cur_directory == 'gcodes':
            self.labels['flowbox'].hide()
        else:
            self.labels['flowbox'].show()
        self.content.show_all()

    def refresh_loading(self,*args):
        self.set_loading(True)
        for child in self.labels['flowbox'].get_children():
            self.labels['flowbox'].remove(child)
        self._screen._ws.klippy.get_dir_info(self.load_files, self.cur_directory)


    def print_start(self,widget,parameter_item):
        print(1)
        fileinfo=parameter_item['fileinfo']
        self._screen._ws.klippy.print_start(fileinfo['filename'])
        self.menu_item_clicked(widget,parameter_item)