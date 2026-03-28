import logging
import os

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Pango, GdkPixbuf
from ks_includes.screen_panel import ScreenPanel
from ks_includes.sdbus_nm import SdbusNm
from datetime import datetime

def format_label(widget, lines=2):
    label = find_widget(widget, Gtk.Label)
    if label is not None:
        label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        label.set_line_wrap(True)
        label.set_ellipsize(Pango.EllipsizeMode.END)
        label.set_lines(lines)

def init_panel(self):
    logging.exception("Initializing Wifi panel")
    self.last_drop_time = datetime.now()
    self.show_add = False
    self.sdbus_nm = SdbusNm(popup_callback)
    self.current_wifi = {}
    self.current_wifi_grid = {}
    self.other_wifi = {}
    self.other_wifi_grid = {}
    self.wifi_switch.set_active(self.sdbus_nm.is_wifi_enabled())
    self.box['current_network_box'] = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    self.box['current_network_box'].set_name('current_network_box')
    self.box['current_network_box'].set_homogeneous(False)
    self.box['other_network_box'] = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=25)
    self.box['other_network_box'].set_name('other_network_box')
    self.box['other_network_box'].set_homogeneous(False)
    self.network_interfaces = self.sdbus_nm.get_interfaces()
    logging.info(f"Network interfaces: {self.network_interfaces}")

    self.wireless_interfaces = [iface.interface for iface in self.sdbus_nm.get_wireless_interfaces()]
    logging.info(f"Wireless interfaces: {self.wireless_interfaces}")

    self.interface = self.sdbus_nm.get_primary_interface()
    logging.info(f"Primary interface: {self.interface}")

    if self.interface is not None:
        self.labels['wifi_ip'].set_hexpand(True)
        self.labels['wifi_ip'].set_text(f"IP: {self.sdbus_nm.get_ip_address()}")


    if self.sdbus_nm.wifi:
        load_networks(self)
        # self.sdbus_nm.enable_monitoring(True)
        # self.conn_status = GLib.timeout_add_seconds(1, self.sdbus_nm.monitor_connection_status)
    # else:
    #     self._screen.show_popup_message(_("No wireless interface has been found"), level=2)
    #     self.labels['networkinfo'] = Gtk.Label()
    #     scroll.add(self.labels['networkinfo'])
    #     self.update_single_network_info()

def popup_callback(self, msg, level=3):
    self._screen.show_popup_message(msg, level)

#加载wifi列表
def load_networks(self, widget = None):
    wifi_list = self.sdbus_nm.get_networks()
    for net in wifi_list:
        add_network(self, net['BSSID'])
    # GLib.timeout_add_seconds(10, self._gtk.Button_busy, self.buttons['reload_wifi'], False)
    current_network_label = Gtk.Label(label=_('Current Network'))
    other_network_label = Gtk.Label(label=_('Other Network'))
    row = 0
    if len(self.current_wifi) > 0:
        self.box['current_network_box'].add(current_network_label)
        for wifi_button in self.current_wifi_grid:
            self.box['current_network_box'].add(self.current_wifi_grid[wifi_button])
        self.grid['wifi_message_grid'].attach(self.box['current_network_box'], 0, row, 1, 1)
        row = row+1
    if len(self.other_wifi) > 0:
        self.box['other_network_box'].add(other_network_label)
        for wifi_button in self.other_wifi_grid:
            self.box['other_network_box'].add(self.other_wifi_grid[wifi_button])
        self.grid['wifi_message_grid'].attach(self.box['other_network_box'], 0, row, 1, 1)

    self.content.show_all()
    if widget:
        self._gtk.Button_busy(widget, False)
    return False

#刷新Wifi列表
def reload_wifi(widget, self):
    self.current_wifi = {}
    self.current_wifi_grid = {}
    self.other_wifi = {}
    self.other_wifi_grid = {}
    for child in self.grid['wifi_message_grid'].get_children():
        self.grid['wifi_message_grid'].remove(child)

    box_list = ['current_network_box', 'other_network_box']
    for box in box_list:
        self.box[box] = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True)
        self.box[box].set_name(box)
        self.box[box].set_homogeneous(False)

    if self.sdbus_nm is not None and self.sdbus_nm.wifi:
        if widget:
            self._gtk.Button_busy(widget, True)
        # self.sdbus_nm.rescan()
        load_networks(self,widget)

#添加WIFI项
def add_network(self, bssid):
    row = 0
    width = 800
    height = 100
    if self._screen.vertical_mode:
        width = 500
        height = 80
    net = next(net for net in self.sdbus_nm.get_networks() if bssid == net['BSSID'])
    ssid = net['SSID']

    check_mark_icon = Gtk.Image()
    pixbuf = GdkPixbuf.Pixbuf.new_from_file("images/check_mark.png")
    scaled_pixbuf = pixbuf.scale_simple(23, 23, GdkPixbuf.InterpType.BILINEAR)
    check_mark_icon.set_from_pixbuf(scaled_pixbuf)

    wifi_name = Gtk.Label(hexpand=True, halign=Gtk.Align.START, wrap=True, wrap_mode=Pango.WrapMode.WORD_CHAR)
    wifi_name.set_markup(f"<b>{ssid}</b>")

    lock_icon = Gtk.Image()
    pixbuf = GdkPixbuf.Pixbuf.new_from_file("images/lock.png")
    scaled_pixbuf = pixbuf.scale_simple(30, 30, GdkPixbuf.InterpType.BILINEAR)
    lock_icon.set_halign(Gtk.Align.END)
    lock_icon.set_from_pixbuf(scaled_pixbuf)

    wifi_icon = Gtk.Image()
    pixbuf = GdkPixbuf.Pixbuf.new_from_file("images/wifi_icon.png")
    scaled_pixbuf = pixbuf.scale_simple(38, 30, GdkPixbuf.InterpType.BILINEAR)
    wifi_icon.set_halign(Gtk.Align.END)
    wifi_icon.set_from_pixbuf(scaled_pixbuf)



    left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, vexpand=True,
                     halign=Gtk.Align.START, valign=Gtk.Align.CENTER, spacing=10)
    if bssid == self.sdbus_nm.get_connected_bssid():
        left_box.add(check_mark_icon)
    left_box.add(wifi_name)

    right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, vexpand=True,
                     halign=Gtk.Align.END, valign=Gtk.Align.CENTER, spacing=5)
    if not net["known"]:
        right_box.add(lock_icon)
    right_box.add(wifi_icon)


    wifi_button = self._gtk.Button(button_width=width, button_height=height, hexpand=True)
    single_wifi_box = Gtk.Box(spacing=3, hexpand=True, vexpand=False)
    single_wifi_box.add(left_box)
    single_wifi_box.add(right_box)
    wifi_button.add(single_wifi_box)
    # net_list = next(net for net in self.sdbus_nm.get_networks() if ssid == net['SSID'])
    # {'BSSID': 'CE:4D:6B:96:64:E9', 'SSID': 'HuangHai', 'channel': '1', 'frequency': '2.4', 'known': False,'max_bitrate'，130000'security': 'AES WPA-PSK', 'signal_level': 94}
    # MAC                           Name                    群组          频段                  是否连接        加密方式                    信号强度
    #筛选重复的
    if ssid in self.current_wifi:
        if self.current_wifi[ssid]['known'] or self.current_wifi[ssid]['signal_level'] > net['signal_level']:
            return
    elif ssid in self.other_wifi:
        if self.other_wifi[ssid]['known'] or self.other_wifi[ssid]['signal_level'] > net['signal_level']:
            return
    else:
        # if bssid == self.sdbus_nm.get_connected_bssid():
        if net["known"]:
            wifi_button.get_style_context().add_class("single_wifi_current")
            wifi_button.connect("clicked", remove_confirm_dialog, self, ssid)
            self.current_wifi[ssid] = net
            self.current_wifi_grid[ssid] = wifi_button
        else:
            wifi_button.get_style_context().add_class("single_wifi_other")
            wifi_button.connect("clicked", connect_network, self, ssid)
            self.other_wifi[ssid] = net
            self.other_wifi_grid[ssid] = wifi_button

#移除已经连接WiFi的Dialog
def remove_confirm_dialog(widget,self,ssid):
    title=_("Remove network")
    buttons = [
        {"name": _("Forget"), "response": Gtk.ResponseType.OK, "style": 'dialog_waring_button'},
        {"name": _("Cancel"), "response": Gtk.ResponseType.CANCEL, "style": 'dialog_cancel_button'}
    ]
    label = Gtk.Label(hexpand=True, vexpand=True, wrap=True)
    label.set_markup(_("Do you want to forget this network?"))
    net = next(net for net in self.sdbus_nm.get_networks() if ssid == net['SSID'])
    format_wifiinfo = Gtk.Label(
        label=get_wifi_info(self, net), use_markup=True, ellipsize=Pango.EllipsizeMode.END
    )
    self._gtk.Dialog(title, buttons, format_wifiinfo, confirm_removal, self, ssid)
#回调Dialog 按钮返回事件
def confirm_removal(dialog, response_id, klippy_gtk, self, ssid):
    self._gtk.remove_dialog(dialog)
    if response_id == Gtk.ResponseType.CANCEL:
        return
    # bssid = self.sdbus_nm.get_bssid_from_ssid(ssid)
    if response_id == Gtk.ResponseType.OK:
        logging.info(f"Deleting {ssid}")
        self.sdbus_nm.delete_network(ssid)
    reload_wifi(None, self)


#连接Wifi Diaolog
def connect_network(widget, self, ssid, showadd=True):
    if showadd and not self.sdbus_nm.is_known(ssid):
        sec_type = self.sdbus_nm.get_security_type(ssid)
        if sec_type == "Open" or "OWE" in sec_type:
            logging.debug("Network is Open do not show psk")
            result = self.sdbus_nm.add_network(ssid, '')
            if "error" in result:
                self._screen.show_popup_message(result["message"])
        else:
            show_connect_network_dialog(widget, self, ssid)
        return

    self.sdbus_nm.connect(ssid, self)
    reload_wifi(None, self)

#显示连接Wifi Dialog
def show_connect_network_dialog(widget, self, ssid):
    title = _("Connect network")
    buttons = [
        {"name": _("Save"), "response": Gtk.ResponseType.OK, "style": 'dialog_print_button'},
        {"name": _("Cancel"), "response": Gtk.ResponseType.CANCEL, "style": 'dialog_cancel_button'}
    ]

    main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, vexpand=True)

    orientation = Gtk.Orientation.VERTICAL if self._screen.vertical_mode else Gtk.Orientation.HORIZONTAL
    inside_box = Gtk.Box(orientation=orientation, vexpand=True)

    info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, vexpand=True)
    net = next(net for net in self.sdbus_nm.get_networks() if ssid == net['SSID'])
    format_wifiinfo = Gtk.Label(
        label=get_wifi_info(self, net), use_markup=True, ellipsize=Pango.EllipsizeMode.END
    )
    info_box.pack_start(format_wifiinfo, True, True, 0)
    info_box.get_style_context().add_class("dialog_info_box")
    inside_box.pack_start(info_box, True, True, 0)

    self.entry['wifi_psd'] = Gtk.Entry(hexpand=True)
    self.entry['wifi_psd'].set_size_request(-1, 50)
    self.entry['wifi_psd'].set_name("wifi_password")
    # self.entry['wifi_psd'].set_visibility(False)  # 密码隐藏
    inside_box.pack_start(self.entry['wifi_psd'], True, True, 0)

    key_board_box = Gtk.Box(orientation=orientation, vexpand=True)
    self.entry['wifi_psd'].connect("touch-event", self._screen.show_keyboard,key_board_box,None)
    self.entry['wifi_psd'].connect("button-press-event", self._screen.show_keyboard,key_board_box,None)
    self.entry['wifi_psd'].connect("changed", on_entry_text_changed,self)
    inside_box.pack_start(key_board_box, True, True, 0)
    main_box.pack_start(inside_box, True, True, 0)
    self._gtk.Dialog(title, buttons, main_box, add_new_network, self, ssid)


#获取输入框中wifi密码
def on_entry_text_changed(entry_widget,self):
    self.wifi_pwd = entry_widget.get_text()
    print("当前WiFi密码输入框内容：", self.wifi_pwd)


#获取wifi详细信息
def get_wifi_info(self, net):
    info = ""
    # {'BSSID': 'CE:4D:6B:96:64:E9', 'SSID': 'HuangHai', 'channel': '1', 'frequency': '2.4', 'known': False, ‘max_bitrate’：130000'security': 'AES WPA-PSK', 'signal_level': 94}
    # MAC                           Name                    群组          频段                  是否连接        加密方式                    信号强度
    if "SSID" in net:
        info += _("SSID") + f': <b>{net["SSID"]}</b> ' + '\n'

    if "channel" in net:
        info += _("Channel") + f': <b>{net["channel"]}</b> ' + '\n'

    if "frequency" in net:
        info += _("Frequency") + f': <b>{net["frequency"]}</b>G' + '\n'

    if "signal_level" in net:
        info += _("Signal Level") + f': <b>{net["signal_level"]}%</b> ' + '\n'

    if "max_bitrate" in net:
        info += _("Max Bitrate") + f': <b>{net["max_bitrate"]}</b> ' + '\n'

    if "security" in net:
        info += _("Security") + f': <b>{net["security"]}</b> ' + '\n'

    if "BSSID" in net:
        info += _("MAC Address") + f': <b>{net["BSSID"]}</b> '
    return info

#连接Wifi Dialog callback回调方法
def add_new_network(dialog, response_id, klippy_gtk, self, ssid):
    self._gtk.remove_dialog(dialog)
    if response_id == Gtk.ResponseType.CANCEL:
        return
    # identity = self.labels['network_identity'].get_text()
    # eap_method = self.get_dropdown_value(self.labels['network_eap_method'])
    eap_list = ["peap", "ttls", "pwd", "leap", "md5"]
    eap_method = eap_list[0].upper()
    # phase2 = self.get_dropdown_value(self.labels['network_phase2'])
    phase2_list = ["mschapv2", "gtc", "pap", "chap", "mschap", "disabled"]
    phase2 = phase2_list[0].upper()
    logging.debug(f"{phase2=}")
    logging.debug(f"{eap_method=}")
    result = self.sdbus_nm.add_network(ssid, self.wifi_pwd, eap_method, '', phase2)
    if "error" in result:
        self._screen.show_popup_message(result["message"])
        if result["error"] == "psk_invalid":
            return
    else:
        connect_network(None, self, ssid, showadd=False)

#switch 开关控制方法
def toggle_wifi(switch, gparams, self):
    enable = switch.get_active()
    logging.info(f"WiFi {enable}")
    self.sdbus_nm.toggle_wifi(enable)
    if enable:
        self.current_wifi = {}
        self.current_wifi_grid = {}
        self.other_wifi = {}
        self.other_wifi_grid = {}
        reload_wifi(None, self)
    else:
        self.grid['wifi_message_grid'].hide()

