import logging
import os
import pathlib
from functools import lru_cache
import json
import logging

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GdkPixbuf, Gio, Gtk, Pango
from ks_includes.widgets.scroll import CustomScrolledWindow
from jinja2 import Template
from datetime import datetime
from ks_includes.screen_panel import ScreenPanel
from ks_includes.KlippyGtk import find_widget
from ks_includes.widgets.flowboxchild_extended import PrintListItem



def format_label(widget):
    label = find_widget(widget, Gtk.Label)
    if label is not None:
        label.set_line_wrap_mode(Pango.WrapMode.CHAR)
        label.set_line_wrap(True)
        label.set_ellipsize(Pango.EllipsizeMode.END)
        label.set_lines(3)

#对打印时间格式化
def print_time_format(time):
    if time < 3600:
        return f'{int(time / 60)}m'
    else:
        hours = int(time / 3600)
        minutes = int((time - hours * 3600) / 60)
        return f'{hours}h{minutes}m'

#刷新按钮，重新加载文件列表
def refresh_loading(widget,self,*args):
    set_loading(self,True)
    for child in self.labels['flowbox'].get_children():
        self.labels['flowbox'].remove(child)
    self._screen._ws.klippy.get_dir_info(self.load_files, self.cur_directory)

#创建打印文件显示格子，里面有图片模型，文件名 打印时间，打印重量
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
    print_file = Gtk.Button()
    fileinfo = self._screen.files.get_file_info(path)
    # 暂时不用选择打印的盘和选择和选择耗材 select_disc_print matching_consumables
    # parameter_item = {
    #     "panel": 'matching_consumables',
    #     "fileinfo":fileinfo,
    #     "icon": None
    # }
    # print_file.connect("clicked", self.menu_item_clicked, parameter_item)
    print_file.connect("clicked", confirm_print,self, path)
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
            estimated_time.set_markup(f'<b>T:</b>{print_time_format(fileinfo["estimated_time"])}')
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
    image_load(self,*image_args)
    return print_file

# 判断加载显示完所有文件信息后显示页面
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

#加载3D模型图片
def image_load(self, filepath, widget, size=-1, small=False, iconname=None):
    pixbuf = self.get_file_image(filepath, 170, 150, False)
    if pixbuf is not None:
        widget.set_image(Gtk.Image.new_from_pixbuf(pixbuf))
    elif iconname is not None:
        widget.set_image(self._gtk.Image(iconname, 170, 150))
    format_label(widget)

#确认打印文件的Dialog
def confirm_print(widget,self, filename):
    action = _("Print") if self._printer.extrudercount > 0 else _("Start")

    buttons = [
        {"name": _("Delete"), "response": Gtk.ResponseType.REJECT, "style": 'waring_button'},
        {"name": action, "response": Gtk.ResponseType.OK, "style": 'print_button'},
        {"name": _("Cancel"), "response": Gtk.ResponseType.CANCEL, "style": 'dialog_cancel'}
    ]

    main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, vexpand=True)

    orientation = Gtk.Orientation.VERTICAL if self._screen.vertical_mode else Gtk.Orientation.HORIZONTAL
    inside_box = Gtk.Box(orientation=orientation, vexpand=True)

    if self._screen.vertical_mode:
        width = self._screen.width * .9
        height = (self._screen.height - self._gtk.dialog_buttons_height - self._gtk.font_size * 5) * .45
    else:
        width = self._screen.width * .5
        height = (self._screen.height - self._gtk.dialog_buttons_height - self._gtk.font_size * 6)

    pixbuf = self.get_file_image(filename, 200, 200)
    if pixbuf is not None:
        image = Gtk.Image.new_from_pixbuf(pixbuf)
        inside_box.pack_start(image, True, True, 0)

    info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, vexpand=True)
    fileinfo = self._screen.files.get_file_info(filename)
    format_fileinfo = Gtk.Label(
        label=get_file_info_extended(self,fileinfo), use_markup=True, ellipsize=Pango.EllipsizeMode.END
    )
    info_box.pack_start(format_fileinfo, True, True, 0)
    info_box.get_style_context().add_class("dialog_info_box")
    inside_box.pack_start(info_box, True, True, 0)
    main_box.pack_start(inside_box, True, True, 0)
    self._gtk.Dialog(f'{filename}', buttons, main_box,confirm_print_response, self,fileinfo)

# 用于确定确定打印文件Dialog中格式化文件信息方法 获取传递过来的文件信息，并格式化，用于打印前显示详细的打印文件信息
def get_file_info_extended(self, fileinfo):

    info = ""
    if "modified" in fileinfo:
        info += _("Modified")
        if self.time_24:
            info += f':<b> {datetime.fromtimestamp(fileinfo["modified"]):%Y/%m/%d %H:%M}</b>\n'
        else:
            info += f':<b> {datetime.fromtimestamp(fileinfo["modified"]):%Y/%m/%d %I:%M %p}</b>\n'
    if "layer_height" in fileinfo:
        info += _("Layer Height") + f': <b>{fileinfo["layer_height"]}</b> ' + _("mm") + '\n'

    if "filament_type" in fileinfo:
        info += _("Filament Type") + f': <b>{fileinfo["filament_type"]}</b>\n'
    # if "filament_name" in fileinfo:
    #     info += f'    <b>{fileinfo["filament_name"]}</b>\n'
    if "filament_weight_total" in fileinfo:
        info += _("Weight") + f': <b>{fileinfo["filament_weight_total"]:.2f}</b> ' + _("g") + '\n'
    if "nozzle_diameter" in fileinfo:
        info += _("Nozzle diameter") + f': <b>{fileinfo["nozzle_diameter"]}</b> ' + _("mm") + '\n'
    if "slicer" in fileinfo:
        info += (
                _("Slicer") +
                f': <b>{fileinfo["slicer"]} '
                f'{fileinfo["slicer_version"] if "slicer_version" in fileinfo else ""}</b>\n'
        )
    if "size" in fileinfo:
        info += _("Size") + f': <b>{self.format_size(fileinfo["size"])}</b>\n'
    if "estimated_time" in fileinfo:
        info += _("Print Time") + f': <b>{self.format_time(fileinfo["estimated_time"])}</b>\n'
    if "job_id" in fileinfo:
        history = self._screen.apiclient.send_request(f"server/history/job?uid={fileinfo['job_id']}")
        if history and history['job']['status'] == "completed":
            info += _("Last Duration") + f": <b>{self.format_time(history['job']['print_duration'])}</b>"
    return info

# 确认打印文件Dialog回滚方法 打印文件 或者取消 或者删除文件
def confirm_print_response(dialog, response_id, klippy_gtk, self,fileinfo):
    self._gtk.remove_dialog(dialog)
    if response_id == Gtk.ResponseType.CANCEL:
        return
    elif response_id == Gtk.ResponseType.OK:
        print_start(dialog, self, fileinfo)
    elif response_id == Gtk.ResponseType.REJECT:
        confirm_delete_file(self,None, f"gcodes/{fileinfo["filename"]}")

#开始打印文件，跳转到Print_menu界面
def print_start(widget,self,fileinfo):
    logging.info(f"Starting print: {fileinfo['filename']}")
    self._screen._ws.klippy.print_start(fileinfo['filename'])
    parameter_item = {
        "panel": 'print_menu',
        "fileinfo":fileinfo,
        "icon": None
    }
    self.menu_item_clicked(widget,parameter_item)

# 删除对应文件
def confirm_delete_file(self, widget, filepath):
    logging.debug(f"Sending delete_file {filepath}")
    params = {"path": f"{filepath}"}
    self._screen._confirm_send_action(
        None,
        _("Delete File?") + "\n\n" + filepath,
        "server.files.delete_file",
        params
    )


#Print_menu界面使用的方法

#改变按钮控件状态 暂停 开始
def change_pause_button_state(self, state, *args):
    pixbuf = ''
    state_text = ''
    filename = ''
    button_text = ''
    # printing 打印中 paused暂停
    if state == "printing...":
        #args[0],widget 发出请求的按钮控件
        # if len(args) == 1:
        #     self._gtk.Button_busy(args[0], True)
        self._screen._ws.klippy.print_resume()
        # self._gtk.Button_busy(args[0], False)
        state_text = _("Printing...")
        filename = "images/pause.png"
        button_text = _("Pause")

    elif state == "paused":
        # if len(args) == 1:
        #     self._gtk.Button_busy(args[0], True)
        self._screen._ws.klippy.print_pause()
        # self._gtk.Button_busy(args[0], False)
        state_text = _("Paused")
        filename = "images/start.png"
        button_text = _("Start")

    self.labels['print_state'].set_label(state_text)
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
        filename=filename,
        width=50,
        height=50,
        preserve_aspect_ratio=True  # 设为False则强制50x50（可能拉伸）
    )
    self.buttons['pause_button'].set_label(button_text)
    # 设置缩放后的图片到Image控件
    image = Gtk.Image.new_from_pixbuf(pixbuf)
    self.buttons['pause_button'].set_image(image)

#实时更新print_menu界面相关数据信息
def update_time_left(self, action,data):

    #热床温度
    if ('heater_bed' in data) and ('temperature' in data['heater_bed']):
        self.buttons["heater_bed_temperature"].set_label(f'{int(data['heater_bed']['temperature'])}℃')
    #腔温
    if ('temperature_sensor filament_box_temp' in data) and ('temperature' in data['temperature_sensor filament_box_temp']):
        self.buttons["chassis_temperature"].set_label(f'{int(data['temperature_sensor filament_box_temp']['temperature'])}℃')

    #T0喷嘴温度
    if ('extruder' in data) and ('temperature' in data['extruder']):
        self.buttons["extruder_temperature"].set_label(f'{int(data['extruder']['temperature'])}℃')
    #T1喷嘴温度
    if ('extruder1' in data) and ('temperature' in data['extruder1']):
        self.buttons["extruder1_temperature"].set_label(f'{int(data['extruder1']['temperature'])}℃')
    #更改打印状态
    if 'print_stats' in data :
        if 'state' in data['print_stats']:
            #更改打印状态
            if data['print_stats']['state'] == 'paused':
                change_pause_button_state(self,data['print_stats']['state'])

    name = ''
    # 放模型图
    if self.filename is not None:
        name = self.filename.replace('.gcode', '')
    elif ('virtual_sdcard' in data) and ('file_path' in data['virtual_sdcard']):
        # '/home/orangepi/printer_data/gcodes/Rabbit.gcode'
        if data['virtual_sdcard']['file_path'] is not None:
            path = data['virtual_sdcard']['file_path']
            name = os.path.splitext(os.path.basename(path))[0]
            # 'a.gcode'
            self.filename = f'{name}.gcode'
            self.labels["print_file_name"].set_label(name)
        else:
            self.labels["print_file_name"].set_label(name)
    # 设置缩放后的图片到Image控件 'Box.gcode'
    pixbuf = None
    if self.file_metadata is not None:
        path = self.file_metadata['thumbnails'][1]['relative_path']
        pixbuf = self._gtk.PixbufFromHttp(path, 320, 320)
    if pixbuf is None:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file("images/no_model_image.png")
        scaled_pixbuf = pixbuf.scale_simple(280, 280, GdkPixbuf.InterpType.BILINEAR)
        self.labels["print_modeling_graphics"].set_from_pixbuf(scaled_pixbuf)
    else:
        self.labels["print_modeling_graphics"].set_from_pixbuf(pixbuf)
    print_duration = float(self._printer.get_stat('print_stats', 'print_duration'))
    if  self.file_metadata is None:
        return self.init_file_data(True)


    #更新进度条
    progress = (
            max(self._printer.get_stat('virtual_sdcard', 'file_position') - self.file_metadata['gcode_start_byte'], 0)
            / (self.file_metadata['gcode_end_byte'] - self.file_metadata['gcode_start_byte'])
    ) if "gcode_start_byte" in self.file_metadata else self._printer.get_stat('virtual_sdcard', 'progress')
    estimated = self.file_metadata['estimated_time'] if 'estimated_time' in self.file_metadata else 0
    if progress*100 <1:
        self.labels['print_state'].set_label(_("Preprocessing in progress..."))
    else:
        self.labels['print_state'].set_label(_("Printing..."))
    if estimated > 1:
        # 更新剩余打印时间
        self.labels["remaining_time"].set_label(f" -{self.format_eta(estimated, print_duration)}")
        progress = min(max(print_duration / estimated, 0), 1)
        self.labels["percentage_progress"].set_label(f' {int(progress * 100)}%')
        self.labels['progressBar'].set_fraction(progress)
    #更新打印层数 total_layer 总层数  current_layer 打印层数
    # if 'info' in data["print_stats"]:
    #     if ('total_layer' in data['print_stats']['info']
    #             and data["print_stats"]['info']['total_layer'] is not None):
    #         self.labels['total_layers'].set_label(f"0 / {data['print_stats']['info']['total_layer']}")
    #     if ('current_layer' in data['print_stats']['info']
    #             and data['print_stats']['info']['current_layer'] is not None):
    #         self.labels['layer'].set_label(
    #             f"{data['print_stats']['info']['current_layer']} / "
    #             f"{self.labels['total_layers'].get_text()}"
    #         )


#暂停或开始打印
def pause_confirm(widget,self):
    logging.debug("Pauseing print")
    state = ''
    if self.labels['print_state'].get_label() == _("Printing..."):
        state = 'paused'
    elif self.labels['print_state'].get_label() == _("Paused"):
        state = 'printing...'
    change_pause_button_state(self,state,widget)


#停止打印窗口
def cancel(widget,self):
    buttons = [
        {"name": _("Confirm"), "response": Gtk.ResponseType.OK, "style": 'waring_button'},
        {"name": _("Back"), "response": Gtk.ResponseType.CANCEL, "style": 'dialog_cancel'}
    ]
    if len(self._printer.get_stat("exclude_object", "objects")) > 1:
        buttons.insert(0, {"name": _("Exclude Object"), "response": Gtk.ResponseType.APPLY})
    label = Gtk.Label(hexpand=True, vexpand=True, wrap=True)
    label.set_markup(_("Are you sure you wish to cancel this print?"))
    self._gtk.Dialog(_("Cancel"), buttons, label, cancel_confirm,self,widget)

#确认停止,关闭打印
def cancel_confirm(dialog, response_id, klippy_gtk,self,*args):
    self._gtk.remove_dialog(dialog)
    if response_id == Gtk.ResponseType.OK:
        logging.debug("Canceling print")
        #args[0],widget 发出请求的按钮控件
        # if len(args) == 1:
        #     self._gtk.Button_busy(args[0], True)
        if self._screen._ws.klippy.print_cancel():
            parameter_item = {
                "panel": "home_menu",
                "icon": "home_menu_icon",
            }
            self.menu_item_clicked(dialog, parameter_item)
        return
    # Cancel_dialog
    if response_id == Gtk.ResponseType.CANCEL:
        return


