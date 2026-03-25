import logging
import os

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Pango, GdkPixbuf
from ks_includes.screen_panel import ScreenPanel
from ks_includes.sdbus_nm import SdbusNm
from datetime import datetime


def init_panel(self):
    logging.exception("Initializing Wifi panel")
    self.last_drop_time = datetime.now()
    self.show_add = False
    self.sdbus_nm = SdbusNm(popup_callback)
    self.connected_wifi = {}
    self.other_wifi = {}
    self.other_count_wifi =1
    self.network_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True)
    self.network_rows = {}
    self.networks = {}
    self.wifi_switch.set_active(self.sdbus_nm.is_wifi_enabled())
    self.grid['current_network_grid'] = Gtk.Grid(orientation=Gtk.Orientation.HORIZONTAL)
    self.grid['current_network_grid'].set_size_request(520, 50)
    self.grid['current_network_grid'].set_name('current_network_grid')
    self.grid['other_network_grid'] = Gtk.Grid(orientation=Gtk.Orientation.HORIZONTAL)
    self.grid['other_network_grid'].set_size_request(520, 400)
    self.grid['other_network_grid'].set_name('other_network_grid')
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
    # {'BSSID': 'CE:4D:6B:96:64:E9', 'SSID': 'HuangHai', 'channel': '1', 'frequency': '2.4', 'known': False,'security': 'AES WPA-PSK', 'signal_level': 94}
    # MAC                           Name                    群组          频段                  是否连接        加密方式                    信号强度
    wifi_list = self.sdbus_nm.get_networks()
    for net in wifi_list:
        add_network(self, net['BSSID'])
    # GLib.timeout_add_seconds(10, self._gtk.Button_busy, self.buttons['reload_wifi'], False)
    self.grid['wifi_message_grid'].set_column_homogeneous(True)
    self.grid['current_network_grid'].set_column_homogeneous(True)
    self.grid['other_network_grid'].set_column_homogeneous(True)
    if len(self.connected_wifi) <= 0:
        self.grid['wifi_message_grid'].attach(self.grid['other_network_grid'], 0, 0, 1, 1)
    if len(self.other_wifi) <= 0:
        self.grid['wifi_message_grid'].attach(self.grid['current_network_grid'], 0, 0, 1, 1)
    else:
        self.grid['wifi_message_grid'].attach(self.grid['current_network_grid'], 0, 0, 1, 1)
        self.grid['wifi_message_grid'].attach(self.grid['other_network_grid'], 0, 1, 1, 1)
    self.content.show_all()
    if widget:
        self._gtk.Button_busy(widget, False)
    return False

#刷新Wifi列表
def reload_wifi(widget, self):
    self.connected_wifi = {}
    self.other_wifi = {}
    self.other_count_wifi =1
    del self.network_rows
    self.network_rows = {}
    grid_list = ['current_network_grid', 'other_network_grid']
    for grid in grid_list:
        if grid in self.grid and self.grid[grid] is not None:
            for child in self.grid[grid].get_children():
                if child is not None:
                    self.grid[grid].remove(child)
        else:
            self.grid[grid] = Gtk.Grid(orientation=Gtk.Orientation.HORIZONTAL)
            self.grid[grid].set_size_request(520, 400)

    if self.sdbus_nm is not None and self.sdbus_nm.wifi:
        if widget:
            self._gtk.Button_busy(widget, True)
        # self.sdbus_nm.rescan()
        load_networks(self,widget)

#添加WIFI项
def add_network(self, bssid):
    row = 0

    net = next(net for net in self.sdbus_nm.get_networks() if bssid == net['BSSID'])
    ssid = net['SSID']
    # net_list = next(net for net in self.sdbus_nm.get_networks() if ssid == net['SSID'])
    #筛选重复的
    if ssid in self.network_rows:
        return
    else:
        self.network_rows[ssid] = net

    width = 515
    height = 40
    wifi_button = self._gtk.Button(button_width = width, button_height = height, hexpand=True)
    self.other_wifi[ssid] = wifi_button

    single_wifi_grid = Gtk.Grid(orientation=Gtk.Orientation.HORIZONTAL)
    wifi_button.add(single_wifi_grid)
    # single_wifi_grid.set_size_request(width, height)

    if bssid == self.sdbus_nm.get_connected_bssid():
        self.connected_wifi[ssid] = self.other_wifi.pop(ssid)

        current_network_label = Gtk.Label(label=_('Current Network'))
        self.grid['current_network_grid'].attach(current_network_label, 0, 0, 1, 1)


        check_mark_icon = Gtk.Image()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file("images/check_mark.png")
        scaled_pixbuf = pixbuf.scale_simple(23, 23, GdkPixbuf.InterpType.BILINEAR)
        check_mark_icon.set_from_pixbuf(scaled_pixbuf)
        single_wifi_grid.attach(check_mark_icon, row, 0, 1, 1)
        row = row + 1

        wifi_button.connect("clicked", remove_confirm_dialog, self, ssid)
        wifi_button.get_style_context().add_class('single_wifi_current')
        self.grid['current_network_grid'].attach(wifi_button, 0, 1, 1, 1)
    else:
        other_network_label = Gtk.Label(label=_('Other Network'))
        self.grid['other_network_grid'].attach(other_network_label, 0, 0, 1, 1)
        wifi_button.connect("clicked", remove_confirm_dialog, self, ssid)
        wifi_button.get_style_context().add_class('single_wifi_other')


    wifi_name = Gtk.Label(label=ssid)
    single_wifi_grid.attach(wifi_name, row, 0, 1, 1)
    row = row+1

    space_label = Gtk.Label()
    space_label.set_hexpand(True)
    single_wifi_grid.attach(space_label, row, 0, 1, 1)
    row = row + 1
    if not bssid == self.sdbus_nm.get_connected_bssid():
        lock_icon = Gtk.Image()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file("images/lock.png")
        scaled_pixbuf = pixbuf.scale_simple(30, 30, GdkPixbuf.InterpType.BILINEAR)
        lock_icon.set_from_pixbuf(scaled_pixbuf)
        single_wifi_grid.attach(lock_icon, row, 0, 1, 1)
        row = row + 1

    wifi_icon = Gtk.Image()
    pixbuf = GdkPixbuf.Pixbuf.new_from_file("images/wifi_icon.png")
    scaled_pixbuf = pixbuf.scale_simple(38, 30, GdkPixbuf.InterpType.BILINEAR)
    wifi_icon.set_from_pixbuf(scaled_pixbuf)
    single_wifi_grid.attach(wifi_icon, row, 0, 1, 1)
    if not bssid == self.sdbus_nm.get_connected_bssid():
        self.grid['other_network_grid'].attach(wifi_button, 0, self.other_count_wifi, 1, 1)
        self.other_count_wifi =  self.other_count_wifi+1


#移除已经连接WiFi的Dialog
def remove_confirm_dialog(widget,self,ssid):
    title=_("Remove network")
    buttons = [
        {"name": _("Forget"), "response": Gtk.ResponseType.OK, "style": 'dialog_waring_button'},
        {"name": _("Cancel"), "response": Gtk.ResponseType.CANCEL, "style": 'dialog_cancel_button'}
    ]
    label = Gtk.Label(hexpand=True, vexpand=True, wrap=True)
    label.set_markup(_("Do you want to forget this network?"))
    self._gtk.Dialog(title, buttons, label, confirm_removal, self, ssid)

def confirm_removal(dialog, response_id, klippy_gtk, self, ssid):
    self._gtk.remove_dialog(dialog)
    if response_id == Gtk.ResponseType.CANCEL:
        return
    # bssid = self.sdbus_nm.get_bssid_from_ssid(ssid)
    if response_id == Gtk.ResponseType.OK:
        logging.info(f"Deleting {ssid}")
        self.sdbus_nm.delete_network(ssid)
    reload_wifi(None, self)






def add_new_network(self, widget, ssid):
    self._screen.remove_keyboard()
    psk = self.labels['network_psk'].get_text()
    identity = self.labels['network_identity'].get_text()
    eap_method = self.get_dropdown_value(self.labels['network_eap_method'])
    phase2 = self.get_dropdown_value(self.labels['network_phase2'])
    logging.debug(f"{phase2=}")
    logging.debug(f"{eap_method=}")
    result = self.sdbus_nm.add_network(ssid, psk, eap_method, identity, phase2)
    if "error" in result:
        self._screen.show_popup_message(result["message"])
        if result["error"] == "psk_invalid":
            return
    else:
        self.connect_network(widget, ssid, showadd=False)
    self.close_add_network()

def get_dropdown_value(self, dropdown, default=None):
    tree_iter = dropdown.get_active_iter()
    model = dropdown.get_model()
    result = model[tree_iter][0]
    return result if result != "disabled" else None

def back(self):
    if self.show_add:
        self.close_add_network()
        return True
    return False

def close_add_network(self):
    if not self.show_add:
        return

    for child in self.content.get_children():
        self.content.remove(child)
    self.content.add(self.labels['main_box'])
    self.content.show()
    for i in ['add_network', 'network_psk', 'network_identity']:
        if i in self.labels:
            del self.labels[i]
    self.show_add = False

def connect_network(self, widget, ssid, showadd=True):
    if showadd and not self.sdbus_nm.is_known(ssid):
        sec_type = self.sdbus_nm.get_security_type(ssid)
        if sec_type == "Open" or "OWE" in sec_type:
            logging.debug("Network is Open do not show psk")
            result = self.sdbus_nm.add_network(ssid, '')
            if "error" in result:
                self._screen.show_popup_message(result["message"])
        else:
            self.show_add_network(widget, ssid)
        self.activate()
        return
    bssid = self.sdbus_nm.get_bssid_from_ssid(ssid)
    if bssid and bssid in self.network_rows:
        self.remove_network_from_list(bssid)
    self.sdbus_nm.connect(ssid)
    reload_wifi(self)



def on_popup_shown(self, combo_box, params):
    if combo_box.get_property("popup-shown"):
        logging.debug("Dropdown popup show")
        self.last_drop_time = datetime.now()
    else:
        elapsed = (datetime.now() - self.last_drop_time).total_seconds()
        if elapsed < 0.2:
            logging.debug(f"Dropdown closed too fast ({elapsed}s)")
            GLib.timeout_add(50, combo_box.popup)
            return
        logging.debug("Dropdown popup close")

def show_add_network(self, widget, ssid):
    if self.show_add:
        return

    for child in self.content.get_children():
        self.content.remove(child)

    if "add_network" in self.labels:
        del self.labels['add_network']

    eap_method = Gtk.ComboBoxText(hexpand=True)
    eap_method.connect("notify::popup-shown", self.on_popup_shown)
    for method in ("peap", "ttls", "pwd", "leap", "md5"):
        eap_method.append(method, method.upper())
    self.labels['network_eap_method'] = eap_method
    eap_method.set_active(0)

    phase2 = Gtk.ComboBoxText(hexpand=True)
    phase2.connect("notify::popup-shown", self.on_popup_shown)
    for method in ("mschapv2", "gtc", "pap", "chap", "mschap", "disabled"):
        phase2.append(method, method.upper())
    self.labels['network_phase2'] = phase2
    phase2.set_active(0)

    auth_selection_box = Gtk.Box(no_show_all=True)
    auth_selection_box.add(self.labels['network_eap_method'])
    auth_selection_box.add(self.labels['network_phase2'])

    self.labels['network_identity'] = Gtk.Entry(hexpand=True, no_show_all=True)
    self.labels['network_identity'].connect("touch-event", self._screen.show_keyboard)
    self.labels['network_identity'].connect("button-press-event", self._screen.show_keyboard)

    self.labels['network_psk'] = Gtk.Entry(hexpand=True)
    self.labels['network_psk'].connect("activate", self.add_new_network, ssid)
    self.labels['network_psk'].connect("touch-event", self._screen.show_keyboard)
    self.labels['network_psk'].connect("button-press-event", self._screen.show_keyboard)

    save = self._gtk.Button("sd", _("Save"), "color3")
    save.set_hexpand(False)
    save.connect("clicked", self.add_new_network, ssid)

    user_label = Gtk.Label(label=_("User"), hexpand=False, no_show_all=True)
    auth_grid = Gtk.Grid()
    auth_grid.attach(user_label, 0, 0, 1, 1)
    auth_grid.attach(self.labels['network_identity'], 1, 0, 1, 1)
    auth_grid.attach(Gtk.Label(label=_("Password"), hexpand=False), 0, 1, 1, 1)
    auth_grid.attach(self.labels['network_psk'], 1, 1, 1, 1)
    auth_grid.attach(save, 2, 0, 1, 2)

    if "802.1x" in self.sdbus_nm.get_security_type(ssid):
        user_label.show()
        self.labels['network_eap_method'].show()
        self.labels['network_phase2'].show()
        self.labels['network_identity'].show()
        auth_selection_box.show()

    self.labels['add_network'] = Gtk.Box(
        orientation=Gtk.Orientation.VERTICAL, spacing=5, valign=Gtk.Align.CENTER,
        hexpand=True, vexpand=True
    )
    self.labels['add_network'].add(Gtk.Label(label=_("Connecting to %s") % ssid))
    self.labels['add_network'].add(auth_selection_box)
    self.labels['add_network'].add(auth_grid)
    scroll = self._gtk.ScrolledWindow()
    scroll.add(self.labels['add_network'])
    self.content.add(scroll)
    self.labels['network_psk'].grab_focus_without_selecting()
    self.content.show_all()
    self.show_add = True

def update_all_networks(self):
    self.interface = self.sdbus_nm.get_primary_interface()
    self.labels['interface'].set_text(_("Interface") + f': {self.interface}')
    self.labels['ip'].set_text(f"IP: {self.sdbus_nm.get_ip_address()}")
    nets = self.sdbus_nm.get_networks()
    remove = [bssid for bssid in self.network_rows.keys() if bssid not in [net['BSSID'] for net in nets]]
    for bssid in remove:
        self.remove_network_from_list(bssid)
    for net in nets:
        if net['BSSID'] not in self.network_rows.keys():
            self.add_network(net['BSSID'])
        self.update_network_info(net)
    for i, net in enumerate(nets):
        for child in self.network_list.get_children():
            if child == self.network_rows[net['BSSID']]:
                self.network_list.reorder_child(child, i)
    self.network_list.show_all()
    return True

def update_network_info(self, net):
    if net['BSSID'] not in self.network_rows.keys() or net['BSSID'] not in self.networks:
        logging.info(f"Unknown SSID {net['SSID']}")
        return
    info = _("Password saved") + '\n' if net['known'] else ""
    chan = _("Channel") + f' {net["channel"]}'
    max_bitrate = _("Max:") + f"{self.format_speed(net['max_bitrate'])}"
    self.networks[net['BSSID']]['icon'].set_from_pixbuf(self.get_signal_strength_icon(net["signal_level"]))
    self.networks[net['BSSID']]['info'].set_markup(
        "<small>"
        f"{info}"
        f"{net['security']}\n"
        f"{max_bitrate}\n"
        f"{net['frequency']} Ghz  {chan}  {net['signal_level']} %\n"
        f"{net['BSSID']}"
        "</small>"
    )

def get_signal_strength_icon(self, signal_level):
    # networkmanager uses percentage not dbm
    if signal_level > 75:
        return self.wifi_signal_icons['excellent']
    elif signal_level > 60:
        return self.wifi_signal_icons['good']
    elif signal_level > 30:
        return self.wifi_signal_icons['fair']
    else:
        return self.wifi_signal_icons['weak']

def update_single_network_info(self):
    self.labels['networkinfo'].set_markup(
        f'<b>{self.interface}</b>\n\n'
        + '<b>' + _("Hostname") + f':</b> {os.uname().nodename}\n'
        f'<b>IPv4:</b> {self.sdbus_nm.get_ip_address()}\n'
    )
    self.labels['networkinfo'].show_all()
    return True

def toggle_wifi(switch, gparams, self):
    enable = switch.get_active()
    logging.info(f"WiFi {enable}")
    self.sdbus_nm.toggle_wifi(enable)
    if enable:
        self.network_rows = {}
        reload_wifi(None, self)
    else:
        self.grid['wifi_message_grid'].hide()
