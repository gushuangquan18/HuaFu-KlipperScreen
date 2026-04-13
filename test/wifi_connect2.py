import gi

gi.require_version('Gtk', '3.0')
gi.require_version('NM', '1.0')
from gi.repository import Gtk, GLib, NM


class WiFiWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="WiFi 扫描器 (去重版)")
        self.set_border_width(10)
        self.set_default_size(900, 500)

        self.client = NM.Client.new(None)
        self.selected_ap = None
        self._setup_ui()

    def _setup_ui(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        self.scan_btn = Gtk.Button(label="开始扫描")
        self.scan_btn.connect("clicked", self.on_scan_clicked)
        vbox.pack_start(self.scan_btn, False, False, 0)

        # 数据列: 0:SSID, 1:信号%, 2:安全性, 3:BSSID, 4:频率, 5:信道, 6:模式, 7:速率, 8:AP对象
        self.liststore = Gtk.ListStore(str, int, str, str, str, int, str, int, object)
        self.liststore.set_sort_func(1, self._sort_by_signal)
        self.liststore.set_sort_column_id(1, Gtk.SortType.DESCENDING)

        treeview = Gtk.TreeView(model=self.liststore)
        treeview.set_search_column(0)
        treeview.get_selection().connect("changed", self.on_selection_changed)

        col_ssid = self._add_text_column(treeview, "SSID (网络名称)", 0, expand=True)
        col_ssid.set_sort_column_id(0)

        renderer = Gtk.CellRendererProgress()
        col_signal = Gtk.TreeViewColumn("信号强度", renderer, value=1)
        col_signal.set_min_width(100)
        col_signal.set_sort_column_id(1)
        treeview.append_column(col_signal)

        col_sec = self._add_text_column(treeview, "安全性", 2)
        col_sec.set_sort_column_id(2)

        self._add_text_column(treeview, "BSSID (MAC)", 3)
        self._add_text_column(treeview, "频率", 4)

        col_chan = self._add_text_column(treeview, "信道", 5)
        col_chan.set_sort_column_id(5)

        self._add_text_column(treeview, "模式", 6)

        col_rate = self._add_text_column(treeview, "速率 (Mb/s)", 7)
        col_rate.set_sort_column_id(7)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.add(treeview)
        vbox.pack_start(scrolled, True, True, 0)

        hbox = Gtk.Box(spacing=6)
        self.pwd_entry = Gtk.Entry()
        self.pwd_entry.set_placeholder_text("输入密码...")
        self.pwd_entry.set_visibility(False)
        self.pwd_entry.set_sensitive(False)
        hbox.pack_start(self.pwd_entry, True, True, 0)

        self.conn_btn = Gtk.Button(label="连接")
        self.conn_btn.connect("clicked", self.on_connect_clicked)
        self.conn_btn.set_sensitive(False)
        hbox.pack_start(self.conn_btn, False, False, 0)
        vbox.pack_start(hbox, False, False, 0)

        self.status_label = Gtk.Label(label="准备就绪")
        vbox.pack_start(self.status_label, False, False, 0)

    def _add_text_column(self, treeview, title, col_id, expand=False):
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(title, renderer, text=col_id)
        column.set_resizable(True)
        if expand:
            column.set_expand(True)
        else:
            column.set_min_width(100)
        treeview.append_column(column)
        return column

    def _sort_by_signal(self, model, iter1, iter2, user_data):
        val1 = model.get_value(iter1, 1)
        val2 = model.get_value(iter2, 1)
        if val1 < val2:
            return 1
        elif val1 > val2:
            return -1
        else:
            return 0

    def _get_wifi_device(self):
        devices = self.client.get_devices()
        for dev in devices:
            if dev.get_device_type() == NM.DeviceType.WIFI:
                return dev
        return None

    def _get_security_type(self, ap):
        flags = ap.get_flags()
        if not (flags & 0x1): return "开放"
        wpa_flags = ap.get_wpa_flags()
        rsn_flags = ap.get_rsn_flags()
        sec = []
        if wpa_flags: sec.append("WPA")
        if rsn_flags: sec.append("WPA2")
        return "/".join(sec) if sec else "WEP"

    def _freq_to_channel(self, freq):
        if freq == 2484:
            return 14
        elif freq < 2484:
            return (freq - 2412) // 5 + 1
        elif freq >= 5035 and freq <= 5865:
            return (freq - 5035) // 5 + 7
        return 0

    def on_scan_clicked(self, widget):
        self.status_label.set_text("正在扫描...")
        self.scan_btn.set_sensitive(False)
        dev = self._get_wifi_device()
        if not dev:
            self.status_label.set_text("未找到 WiFi 设备")
            self.scan_btn.set_sensitive(True)
            return
        try:
            dev.request_scan_async(None, self.on_scan_finished, dev)
        except Exception as e:
            self.status_label.set_text("正在刷新列表...")
            GLib.timeout_add(500, self.refresh_ap_list, dev)

    def on_scan_finished(self, dev, res, user_data):
        try:
            dev.request_scan_finish(res)
            GLib.timeout_add(800, self.refresh_ap_list, dev)
        except Exception as e:
            GLib.timeout_add(500, self.refresh_ap_list, dev)

    def refresh_ap_list(self, dev):
        """
        核心逻辑：
        1. 预处理：按 SSID 分组，只保留信号最强的
        2. 再更新 UI 列表
        """
        all_aps = dev.get_access_points()

        # --- 第一步：去重筛选 (核心修改) ---
        # 字典结构: { "SSID字符串": (信号强度, AP对象) }
        best_aps_dict = {}

        for ap in all_aps:
            ssid_bytes = ap.get_ssid()
            if ssid_bytes is None: continue

            try:
                ssid_str = ssid_bytes.get_data().decode('utf-8')
            except:
                ssid_str = ssid_bytes.get_data().decode('latin-1')

            if not ssid_str: continue

            current_strength = ap.get_strength()

            # 检查这个 SSID 是否已经记录过
            if ssid_str in best_aps_dict:
                # 如果已存在，比较信号强度
                stored_strength, _ = best_aps_dict[ssid_str]
                if current_strength > stored_strength:
                    # 当前信号更强，替换掉
                    best_aps_dict[ssid_str] = (current_strength, ap)
            else:
                # 如果不存在，添加进去
                best_aps_dict[ssid_str] = (current_strength, ap)

        # 现在 best_aps_dict 里的值就是我们需要的、去重后的 AP 列表
        filtered_aps = [ap for (strength, ap) in best_aps_dict.values()]

        # --- 第二步：用筛选后的列表更新 UI ---
        # 记录当前列表里的 SSID (注意：现在用 SSID 作为 key 来比对 UI 行，而不是 BSSID)
        existing_ssids = {}
        if self.liststore:
            iter = self.liststore.get_iter_first()
            while iter:
                ui_ssid = self.liststore.get_value(iter, 0)
                existing_ssids[ui_ssid] = iter
                iter = self.liststore.iter_next(iter)

        count_new = 0
        count_updated = 0

        for ap in filtered_aps:
            # 重新获取一遍属性 (虽然刚才获取过，但为了代码清晰)
            ssid_bytes = ap.get_ssid()
            ssid_str = ssid_bytes.get_data().decode('utf-8', errors='replace')

            bssid = ap.get_bssid() or "N/A"
            strength = ap.get_strength()
            security = self._get_security_type(ap)
            freq_mhz = ap.get_frequency()
            channel = self._freq_to_channel(freq_mhz)
            freq_ghz = f"{freq_mhz / 1000:.2f} GHz"
            mode = "2.4 GHz" if freq_mhz < 3000 else "5 GHz"
            bitrate = ap.get_max_bitrate() // 1000

            if ssid_str in existing_ssids:
                # 更新已存在的行
                it = existing_ssids.pop(ssid_str)
                self.liststore.set(it,
                                   0, ssid_str,
                                   1, strength, #信号强度
                                   2, security, #安全性
                                   3, bssid,  # 虽然 SSID 一样，BSSID 可能变了（切到了另一个更强的路由器）
                                   4, freq_ghz, #频率
                                   5, channel, #信道
                                   7, bitrate, #模式
                                   8, ap #速率
                                   )
                count_updated += 1
            else:
                # 添加新行
                self.liststore.append([
                    ssid_str, strength, security, bssid, freq_ghz,
                    channel, mode, bitrate, ap
                ])
                count_new += 1

        # 删除消失的 WiFi
        for ssid, it in existing_ssids.items():
            self.liststore.remove(it)

        count_removed = len(existing_ssids)
        self.status_label.set_text(
            f"完成: 显示 {len(filtered_aps)} 个 (已合并同名, 新增 {count_new}, 移除 {count_removed})"
        )
        self.scan_btn.set_sensitive(True)
        return False

    def on_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter:
            self.selected_ap = model[treeiter][8]
            self.pwd_entry.set_sensitive(True)
            self.conn_btn.set_sensitive(True)
        else:
            self.selected_ap = None

    def on_connect_clicked(self, widget):
        if not self.selected_ap: return
        pwd = self.pwd_entry.get_text()
        self.status_label.set_text("正在连接...")
        self.conn_btn.set_sensitive(False)
        conn = self._create_connection_profile(self.selected_ap, pwd)
        dev = self._get_wifi_device()

        self.client.add_and_activate_connection_async(
            conn, dev, self.selected_ap, None,
            self.on_connect_finished
        )

    def _create_connection_profile(self, ap, password):
        conn = NM.SimpleConnection.new()
        s_con = NM.SettingConnection.new()
        s_con.set_property(NM.SETTING_CONNECTION_ID, ap.get_ssid().get_data().decode('utf-8'))
        s_con.set_property(NM.SETTING_CONNECTION_TYPE, NM.SETTING_WIRELESS_SETTING_NAME)
        conn.add_setting(s_con)

        s_wifi = NM.SettingWireless.new()
        s_wifi.set_property(NM.SETTING_WIRELESS_SSID, ap.get_ssid())
        s_wifi.set_property(NM.SETTING_WIRELESS_MODE, "infrastructure")
        conn.add_setting(s_wifi)

        s_wsec = NM.SettingWirelessSecurity.new()
        s_wsec.set_property(NM.SETTING_WIRELESS_SECURITY_KEY_MGMT, "wpa-psk")
        s_wsec.set_property(NM.SETTING_WIRELESS_SECURITY_PSK, password)
        conn.add_setting(s_wsec)

        s_ip4 = NM.SettingIP4Config.new()
        s_ip4.set_property(NM.SETTING_IP_CONFIG_METHOD, "auto")
        conn.add_setting(s_ip4)

        s_ip6 = NM.SettingIP6Config.new()
        s_ip6.set_property(NM.SETTING_IP_CONFIG_METHOD, "auto")
        conn.add_setting(s_ip6)

        return conn

    def on_connect_finished(self, client, res, user_data):
        try:
            active_conn = client.add_and_activate_connection_finish(res)
            self.status_label.set_text("连接成功！" if active_conn else "连接失败")
        except Exception as e:
            self.status_label.set_text(f"连接失败: {str(e)}")
        self.conn_btn.set_sensitive(True)


if __name__ == "__main__":
    win = WiFiWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
