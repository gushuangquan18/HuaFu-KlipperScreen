import gi
import binascii
import logging

gi.require_version('Gtk', '3.0')
gi.require_version('NM', '1.0')
from gi.repository import Gtk, GLib, NM, Gdk

# ====================== 配置日志系统 ======================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ====================== CSS 样式定义 ======================
CSS_STYLE = """
window {
    background-color: #121212;
    color: #ffffff;
}
label {
    color: #ffffff;
    font-size: 16px;
}
.header-box {
    background-color: #121212;
    padding: 10px 15px;
}
.header-title {
    font-size: 22px;
    font-weight: bold;
}
.header-btn {
    background: transparent;
    border: none;
    outline: none;
}
.header-btn:hover {
    background-color: #333333;
    border-radius: 6px;
}

.switch-row {
    background-color: #444444;
    border-radius: 8px;
    margin: 10px 15px;
    padding: 15px 20px;
}
.switch-row label {
    font-size: 20px;
}
switch slider {
    background-color: #ffffff;
}
switch:checked {
    background-color: #1e88e5;
}

.section-title {
    font-size: 24px;
    font-weight: bold;
    margin: 15px 0;
}

.wifi-item-connected {
    background-color: #2e7d32;
    border-radius: 8px;
    margin: 5px 15px;
    padding: 18px 20px;
    border: none;
    outline: none;
}
.wifi-item-connected:hover {
    background-color: #388e3c;
}

.wifi-item-other {
    background-color: #d32f2f;
    border-radius: 8px;
    margin: 5px 15px;
    padding: 18px 20px;
    border: none;
    outline: none;
}
.wifi-item-other:hover {
    background-color: #e53935;
}

.wifi-icon {
    color: #ffffff;
    font-size: 24px;
}
.lock-icon {
    color: #ffffff;
    font-size: 20px;
    margin-right: 10px;
}

scrolledwindow {
    border: none;
    background-color: #121212;
}
viewport {
    background-color: #121212;
}

dialog {
    background-color: #222222;
}
dialog entry {
    background-color: #333333;
    color: #ffffff;
    font-size: 16px;
    padding: 8px;
    border-radius: 4px;
}
dialog button {
    background-color: #333333;
    color: #ffffff;
    padding: 8px 16px;
    border-radius: 4px;
}
dialog button:hover {
    background-color: #444444;
}
"""


class WiFiWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="WiFi")
        self.set_border_width(0)
        self.set_default_size(480, 800)

        self.client = NM.Client.new(None)
        self.selected_ap = None
        self.connected_ssid = None
        self.current_ap = None
        self.current_ip = "未获取"
        self._scan_pending = False

        # 连接过程中暂停自动刷新的标志
        self._is_connecting = False

        self._auto_refresh_timer_id = None
        self._auto_refresh_interval = 5000

        self._load_css()
        self._setup_ui()
        self._init_wifi_state()

        self.connect("destroy", self._on_window_destroy)

    def _load_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(CSS_STYLE.encode('utf-8'))
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _setup_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_box)

        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        header_box.get_style_context().add_class("header-box")
        main_box.pack_start(header_box, False, False, 0)

        back_btn = Gtk.Button()
        back_btn.get_style_context().add_class("header-btn")
        back_btn.set_image(Gtk.Image.new_from_icon_name("go-previous", Gtk.IconSize.LARGE_TOOLBAR))
        header_box.pack_start(back_btn, False, False, 0)

        title_label = Gtk.Label(label="WiFi")
        title_label.get_style_context().add_class("header-title")
        header_box.pack_start(title_label, True, False, 0)

        self.refresh_btn = Gtk.Button()
        self.refresh_btn.get_style_context().add_class("header-btn")
        self.refresh_btn.set_image(Gtk.Image.new_from_icon_name("view-refresh", Gtk.IconSize.LARGE_TOOLBAR))
        self.refresh_btn.connect("clicked", self.on_refresh_clicked)
        header_box.pack_end(self.refresh_btn, False, False, 0)

        switch_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        switch_row.get_style_context().add_class("switch-row")
        main_box.pack_start(switch_row, False, False, 0)

        wifi_label = Gtk.Label(label="WiFi")
        switch_row.pack_start(wifi_label, False, False, 0)

        self.ip_label = Gtk.Label(label=f"IP: {self.current_ip}")
        switch_row.pack_start(self.ip_label, True, False, 0)

        self.wifi_switch = Gtk.Switch()
        self.wifi_switch.connect("notify::active", self.on_wifi_switch_toggled)
        switch_row.pack_end(self.wifi_switch, False, False, 0)

        self.current_title = Gtk.Label(label="当前网络")
        self.current_title.get_style_context().add_class("section-title")
        main_box.pack_start(self.current_title, False, False, 0)

        self.current_wifi_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        main_box.pack_start(self.current_wifi_box, False, False, 0)

        self.other_title = Gtk.Label(label="其他网络")
        self.other_title.get_style_context().add_class("section-title")
        main_box.pack_start(self.other_title, False, False, 0)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        main_box.pack_start(scrolled, True, True, 0)
        self.other_wifi_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        scrolled.add(self.other_wifi_box)

    def _create_wifi_item(self, ssid, is_connected=False, is_secure=False, ap=None):
        item_btn = Gtk.Button()

        if is_connected:
            item_btn.get_style_context().add_class("wifi-item-connected")
        else:
            item_btn.get_style_context().add_class("wifi-item-other")

        item_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        item_btn.add(item_box)

        ssid_label = Gtk.Label(label=ssid)
        ssid_label.set_halign(Gtk.Align.START)
        item_box.pack_start(ssid_label, True, True, 0)

        icon_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        item_box.pack_end(icon_box, False, False, 0)

        # 加密WiFi显示锁图标，开放WiFi不显示
        if is_secure and not is_connected:
            lock_label = Gtk.Label(label="🔒")
            lock_label.get_style_context().add_class("lock-icon")
            icon_box.pack_start(lock_label, False, False, 0)

        signal_label = Gtk.Label(label="📶")
        signal_label.get_style_context().add_class("wifi-icon")
        icon_box.pack_start(signal_label, False, False, 0)

        if is_connected:
            item_btn.connect("clicked", self.on_current_wifi_clicked)
        else:
            item_btn.connect("clicked", self.on_wifi_item_clicked, ap)

        return item_btn

    def _get_wifi_device(self):
        devices = self.client.get_devices()
        for dev in devices:
            if dev.get_device_type() == NM.DeviceType.WIFI:
                return dev
        return None

    # ====================== 修复：简化加密判断，避免枚举兼容性问题 ======================
    def _get_security_type(self, ap):
        """
        简化版：判断AP是否加密（兼容性最好）
        返回: True=加密（需要密码），False=开放（无密码）
        """
        try:
            # 方法1：尝试获取 flags，如果有 PRIVACY 标志就是加密
            flags = ap.get_flags()
            # 直接用位运算判断，不依赖枚举名称
            if (flags & 0x1) != 0:  # 0x1 对应 PRIVACY 位
                return True

            # 方法2：检查 WPA 和 RSN 标志
            try:
                wpa_flags = ap.get_wpa_flags()
                rsn_flags = ap.get_rsn_flags()
                if wpa_flags != 0 or rsn_flags != 0:
                    return True
            except:
                pass

        except Exception as e:
            logger.debug(f"加密判断异常，默认按加密处理: {e}")
            return True

        # 都没有加密标志，认为是开放网络
        return False

    def _init_wifi_state(self):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            wifi_enabled = self.client.wireless_get_enabled()

        self.wifi_switch.set_active(wifi_enabled)
        self.refresh_btn.set_sensitive(wifi_enabled)
        self._update_connected_info()
        self._set_wifi_list_visible(wifi_enabled)

        if wifi_enabled:
            self._start_auto_refresh()
            GLib.timeout_add(1000, self._wait_device_and_scan)

    def _update_connected_info(self):
        # 正在连接时，不更新连接信息，防止UI乱跳
        if self._is_connecting:
            return

        self.connected_ssid = None
        self.current_ap = None
        self.current_ip = "未连接"
        self.active_conn = None
        self.active_dev = None
        active_conns = self.client.get_active_connections()

        for conn in active_conns:
            if conn.get_connection_type() != "802-11-wireless":
                continue
            ip4 = conn.get_ip4_config()
            if ip4:
                addrs = ip4.get_addresses()
                if addrs:
                    self.current_ip = addrs[0].get_address().format()
            devs = conn.get_devices()
            for dev in devs:
                if dev.get_device_type() == NM.DeviceType.WIFI:
                    ap = dev.get_active_access_point()
                    if ap:
                        self.connected_ssid = ap.get_ssid().get_data().decode('utf-8', 'replace')
                        self.current_ap = ap
                        self.active_conn = conn
                        self.active_dev = dev
        self.ip_label.set_text(f"IP: {self.current_ip}")
        self._refresh_wifi_list_ui()

    def _refresh_wifi_list_ui(self):
        for c in self.current_wifi_box.get_children():
            self.current_wifi_box.remove(c)
        for c in self.other_wifi_box.get_children():
            self.other_wifi_box.remove(c)

        if self.connected_ssid:
            item = self._create_wifi_item(self.connected_ssid, is_connected=True)
            self.current_wifi_box.pack_start(item, False, False, 0)

        if hasattr(self, 'filtered_aps'):
            for ap in self.filtered_aps:
                ssid = ap.get_ssid().get_data().decode('utf-8', 'replace')
                if ssid == self.connected_ssid:
                    continue
                secure = self._get_security_type(ap)
                item = self._create_wifi_item(ssid, False, secure, ap)
                self.other_wifi_box.pack_start(item, False, False, 0)
        self.show_all()

    def _set_wifi_list_visible(self, visible):
        self.current_title.set_visible(visible)
        self.current_wifi_box.set_visible(visible)
        self.other_title.set_visible(visible)
        self.other_wifi_box.set_visible(visible)

    def _start_auto_refresh(self):
        self._stop_auto_refresh()
        self._auto_refresh_timer_id = GLib.timeout_add(
            self._auto_refresh_interval,
            self._auto_refresh_callback
        )

    def _stop_auto_refresh(self):
        if self._auto_refresh_timer_id is not None:
            GLib.source_remove(self._auto_refresh_timer_id)
            self._auto_refresh_timer_id = None

    def _auto_refresh_callback(self):
        # 正在连接时，跳过自动刷新
        if self._is_connecting:
            return True

        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            wifi_enabled = self.client.wireless_get_enabled()

        if not wifi_enabled or self._scan_pending:
            return True

        self.start_scan()
        return True

    def _on_window_destroy(self, widget):
        self._stop_auto_refresh()
        Gtk.main_quit()

    def on_wifi_switch_toggled(self, switch, gparam):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            active = switch.get_active()
            self.client.wireless_set_enabled(active)

        self.refresh_btn.set_sensitive(active)
        self._set_wifi_list_visible(active)

        if active:
            self.ip_label.set_text("IP: 正在启用...")
            self._scan_pending = False
            self._start_auto_refresh()
            GLib.timeout_add(800, self._wait_device_and_scan)
        else:
            self._stop_auto_refresh()
            self.filtered_aps = []
            self.connected_ssid = None
            self.current_ap = None
            self.current_ip = "未连接"
            self.ip_label.set_text("IP: 未连接")
            self._refresh_wifi_list_ui()

    def _wait_device_and_scan(self):
        if self._scan_pending:
            return False
        dev = self._get_wifi_device()
        if not dev:
            self.ip_label.set_text("IP: 等待设备...")
            return True

        self._scan_pending = True
        self.ip_label.set_text("IP: 扫描中...")
        self.start_scan()
        return False

    def on_refresh_clicked(self, widget):
        if not self._scan_pending and not self._is_connecting:
            self.start_scan()

    def start_scan(self):
        dev = self._get_wifi_device()
        if not dev:
            return
        try:
            dev.request_scan_async(None, self.on_scan_finished, dev)
        except Exception as e:
            GLib.timeout_add(500, self.process_scan_result, dev)

    def on_scan_finished(self, dev, res, user_data):
        try:
            dev.request_scan_finish(res)
        except:
            pass
        GLib.timeout_add(600, self.process_scan_result, dev)

    def process_scan_result(self, dev):
        all_aps = dev.get_access_points()
        best = {}
        for ap in all_aps:
            ssid_b = ap.get_ssid()
            if not ssid_b:
                continue
            try:
                ssid = ssid_b.get_data().decode('utf-8')
            except:
                ssid = ssid_b.get_data().decode('latin-1', 'replace')
            if not ssid:
                continue
            strength = ap.get_strength()
            if ssid not in best or strength > best[ssid][0]:
                best[ssid] = (strength, ap)
        self.filtered_aps = [ap for (s, ap) in sorted(best.values(), key=lambda x: -x[0])]
        self._scan_pending = False
        self._update_connected_info()
        return False

    def on_current_wifi_clicked(self, widget):
        if not self.connected_ssid or not self.active_conn:
            return

        dialog = Gtk.Dialog(
            title=f"{self.connected_ssid}",
            parent=self,
            modal=True,
            destroy_with_parent=True
        )
        dialog.add_button("取消", Gtk.ResponseType.CANCEL)
        dialog.add_button("忘记网络", Gtk.ResponseType.APPLY)
        dialog.set_default_size(350, 180)

        area = dialog.get_content_area()
        area.set_spacing(15)
        area.set_margin_top(25)
        area.set_margin_bottom(20)
        area.set_margin_left(20)
        area.set_margin_right(20)

        area.pack_start(Gtk.Label(label=f"当前已连接：{self.connected_ssid}"), False, False, 0)
        area.pack_start(Gtk.Label(label="忘记后将断开连接，且不会自动重连"), False, False, 0)
        dialog.show_all()

        res = dialog.run()
        if res == Gtk.ResponseType.APPLY:
            self.delete_network(self.connected_ssid)
        dialog.destroy()

    def delete_network(self, ssid):
        if path := self.get_connection_path_by_ssid(ssid):
            self.delete_connection_path(path)
            if self.active_conn:
                self.client.deactivate_connection(self.active_conn)
            GLib.timeout_add(500, self._update_connected_info)
            self._msg("成功", f"已忘记网络：{ssid}")
        else:
            logger.debug(f"SSID '{ssid}' not found among saved connections")
            self._msg("错误", f"未找到已保存的网络：{ssid}")

    def get_connection_path_by_ssid(self, ssid):
        connections = self.client.get_connections()
        for conn in connections:
            s_con = conn.get_setting_connection()
            s_wifi = conn.get_setting_wireless()
            if s_wifi:
                ssid_bytes = s_wifi.get_ssid()
                if ssid_bytes:
                    conn_ssid = ssid_bytes.get_data().decode('utf-8', errors='replace')
                    if conn_ssid == ssid:
                        return conn.get_path()
        return None

    def delete_connection_path(self, path):
        try:
            connections = self.client.get_connections()
            for conn in connections:
                if conn.get_path() == path:
                    conn.delete_async(None, self._on_connection_deleted)
                    logger.info(f"Deleted connection path: {path}")
                    return
            logger.warning(f"Connection path not found: {path}")
        except Exception as e:
            logger.exception(f"Failed to delete connection path: {path} - {e}")
            self._msg("删除失败", f"无法删除连接：{e}")

    def _on_connection_deleted(self, connection, res):
        try:
            success = connection.delete_finish(res)
            if success:
                logger.info("Connection deleted successfully")
            else:
                logger.warning("Failed to delete connection")
        except Exception as e:
            logger.exception(f"Error in deletion callback: {e}")

    # ====================== 核心：区分开放/加密WiFi ======================
    def on_wifi_item_clicked(self, widget, ap):
        """点击未连接WiFi的回调：开放网络直接连，加密网络弹密码框"""
        self.selected_ap = ap
        ssid = ap.get_ssid().get_data().decode('utf-8', 'replace')
        is_secure = self._get_security_type(ap)

        # 1. 开放网络：直接连接，不弹密码框
        if not is_secure:
            logger.info(f"检测到开放网络：{ssid}，直接发起连接")
            self.connect_wifi(ap, pwd=None)
            return

        # 2. 加密网络：弹出密码输入框
        dialog = Gtk.Dialog(
            title=f"连接 {ssid}",
            parent=self,
            modal=True,
            destroy_with_parent=True
        )
        dialog.add_button("取消", Gtk.ResponseType.CANCEL)
        dialog.add_button("连接", Gtk.ResponseType.OK)
        dialog.set_default_size(350, 150)

        area = dialog.get_content_area()
        area.set_spacing(15)
        area.set_margin_top(20)
        area.set_margin_bottom(20)
        area.set_margin_left(20)
        area.set_margin_right(20)

        area.pack_start(Gtk.Label(f"请输入 {ssid} 密码"), False, False, 0)
        pwd_entry = Gtk.Entry()
        pwd_entry.set_visibility(False)
        pwd_entry.set_placeholder_text("WiFi密码")
        area.pack_start(pwd_entry, False, False, 0)
        dialog.show_all()

        if dialog.run() == Gtk.ResponseType.OK:
            input_pwd = pwd_entry.get_text().strip()
            self.connect_wifi(ap, pwd=input_pwd)
        dialog.destroy()

    # ====================== 适配开放网络的连接逻辑 ======================
    def connect_wifi(self, ap, pwd=None):
        """发起WiFi连接：自动适配开放/加密网络"""
        dev = self._get_wifi_device()
        if not dev:
            return

        # 设置正在连接标志，冻结UI更新
        self._is_connecting = True
        ssid = ap.get_ssid().get_data().decode('utf-8', 'replace')
        is_secure = self._get_security_type(ap)
        self.ip_label.set_text(f"IP: 正在连接 {ssid}...")

        # 构建基础连接配置
        conn = NM.SimpleConnection.new()

        # 1. 通用连接设置
        s_con = NM.SettingConnection.new()
        s_con.set_property(NM.SETTING_CONNECTION_ID, ssid)
        s_con.set_property(NM.SETTING_CONNECTION_TYPE, "802-11-wireless")
        conn.add_setting(s_con)

        # 2. WiFi基础设置
        s_wifi = NM.SettingWireless.new()
        s_wifi.set_property(NM.SETTING_WIRELESS_SSID, ap.get_ssid())
        s_wifi.set_property(NM.SETTING_WIRELESS_MODE, "infrastructure")
        # 锁定BSSID，防止连错同名WiFi
        bssid = ap.get_bssid()
        if bssid:
            try:
                mac = binascii.unhexlify(bssid.replace(':', ''))
                s_wifi.set_property(NM.SETTING_WIRELESS_BSSID, GLib.Bytes.new(mac))
            except:
                pass
        conn.add_setting(s_wifi)

        # 3. 加密网络才添加安全设置，开放网络不添加
        if is_secure and pwd:
            s_wsec = NM.SettingWirelessSecurity.new()
            s_wsec.set_property(NM.SETTING_WIRELESS_SECURITY_KEY_MGMT, "wpa-psk")
            s_wsec.set_property(NM.SETTING_WIRELESS_SECURITY_PSK, pwd)
            conn.add_setting(s_wsec)

        # 4. IP设置（自动DHCP）
        s_ip4 = NM.SettingIP4Config.new()
        s_ip4.set_property(NM.SETTING_IP_CONFIG_METHOD, "auto")
        conn.add_setting(s_ip4)
        s_ip6 = NM.SettingIP6Config.new()
        s_ip6.set_property(NM.SETTING_IP_CONFIG_METHOD, "auto")
        conn.add_setting(s_ip6)

        # 发起异步连接
        try:
            path = ap.get_object_path() if hasattr(ap, 'get_object_path') else ap.path
            self.client.add_and_activate_connection_async(
                conn, dev, path, None, self.on_connect_finished
            )
        except:
            self.client.add_and_activate_connection_async(
                conn, dev, None, None, self.on_connect_finished
            )

    def on_connect_finished(self, client, res, user_data=None):
        """连接完成回调：统一处理成功/失败逻辑"""
        # 先清除连接标志，恢复UI更新
        self._is_connecting = False

        try:
            ac = client.add_and_activate_connection_finish(res)
            if ac:
                # 连接成功
                logger.info("WiFi连接成功")
                self.ip_label.set_text("IP: 获取中...")
                # 延迟刷新，确保IP获取完成
                GLib.timeout_add(1500, self._update_connected_info)
            else:
                # 连接失败
                logger.warning("WiFi连接失败：未激活")
                self.ip_label.set_text(f"IP: {self.current_ip}")
                self._msg("连接失败", "无法连接到该网络，请重试")
        except Exception as e:
            # 连接异常（密码错误、网络不可用等）
            logger.exception(f"WiFi连接异常: {e}")
            self.ip_label.set_text(f"IP: {self.current_ip}")
            self._msg("连接失败", "密码错误或网络不可用，请检查后重试")

    def _msg(self, title, text):
        """通用消息弹窗"""
        d = Gtk.MessageDialog(
            parent=self,
            modal=True,
            destroy_with_parent=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        d.format_secondary_text(text)
        d.run()
        d.destroy()


if __name__ == "__main__":
    win = WiFiWindow()
    Gtk.main()
