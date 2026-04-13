import gi
import binascii
import logging

gi.require_version("Gtk", "3.0")
gi.require_version('NM', '1.0')
from gi.repository import Gtk, Gdk, GLib, Pango, GdkPixbuf, NM
from ks_includes.screen_panel import ScreenPanel
from datetime import datetime



# ====================== 配置日志系统 ======================
# 配置日志级别为 INFO，方便调试和查看运行状态
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def format_label(widget, lines=2):
    label = find_widget(widget, Gtk.Label)
    if label is not None:
        label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        label.set_line_wrap(True)
        label.set_ellipsize(Pango.EllipsizeMode.END)
        label.set_lines(lines)


#self.buttons['reload_wifi']  刷新按钮方法   self.refresh_btn
#self.labels['wifi_ip'] wifi_Ip_Label  self.ip_label
#self.switch['wifi_switch'] Switch 开关 self.wifi_switch
#self.grid['wifi_message_grid']  显示wifi的列表信息grid
#self.box['current_network_box'] 当前网络    self.current_wifi_box
#self.box['other_network_box']  其他网络    self.other_wifi_box
def init_panel(self):
    logging.exception("Initializing Wifi panel")
    # 初始化 NetworkManager 客户端，用于和系统网络管理通信
    self.client = NM.Client.new(None)

    # 全局变量初始化
    self.selected_ap = None  # 当前选中的未连接AP对象
    self.connected_ssid = None  # 当前已连接的WiFi SSID
    self.current_ap = None  # 当前已连接的AP对象
    self.current_ip = "未获取"  # 当前IP地址
    self._scan_pending = False  # 扫描状态标志，防止重复扫描
    self.current_wifi = {}
    self.current_wifi_grid = {}
    self.other_wifi = {}
    self.other_wifi_grid = {}
    self.net_list = {}

    # 自动刷新相关变量
    self._auto_refresh_timer_id = None  # 定时器ID，用于管理启停
    self._auto_refresh_interval = 5000  # 自动刷新间隔，单位毫秒（5000=5秒）

    # 初始化界面布局
    setup_ui(self)

    #初始化Wifi状态
    init_wifi_state(self)

# 初始化界面布局
def setup_ui(self):
    #当前网络区域
    self.box['current_network_box'] = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    self.box['current_network_box'].set_name('current_network_box')
    self.box['current_network_box'].set_homogeneous(False)
    #其他网络区域
    self.box['other_network_box'] = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=25)
    self.box['other_network_box'].set_name('other_network_box')
    self.box['other_network_box'].set_homogeneous(False)

#初始化Wifi状态
def init_wifi_state(self):
    """初始化WiFi状态：同步开关、刷新列表、启动自动刷新"""
    # 忽略弃用警告，获取WiFi当前状态
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        wifi_enabled = self.client.wireless_get_enabled()

    # 同步UI状态
    self.switch['wifi_switch'].set_active(wifi_enabled)
    self.buttons['reload_wifi'].set_sensitive(wifi_enabled)
    update_connected_info(self)

    # 如果WiFi已开启，启动自动刷新并立即扫描一次
    if wifi_enabled:
        start_auto_refresh(self)
        GLib.timeout_add(1000, wait_device_and_scan, self)

def update_connected_info(self):
    """更新当前已连接的WiFi信息和IP地址"""
    # 重置变量
    self.connected_ssid = None
    self.current_ap = None
    self.current_ip = "未连接"
    self.active_conn = None
    self.active_dev = None

    # 遍历所有激活的连接
    active_conns = self.client.get_active_connections()
    for conn in active_conns:
        # 只处理WiFi连接
        if conn.get_connection_type() != "802-11-wireless":
            continue

        # 获取IP地址
        ip4 = conn.get_ip4_config()
        if ip4:
            addrs = ip4.get_addresses()
            if addrs:
                self.current_ip = addrs[0].get_address().format()

        # 获取SSID和AP对象
        devs = conn.get_devices()
        for dev in devs:
            if dev.get_device_type() == NM.DeviceType.WIFI:
                ap = dev.get_active_access_point()
                if ap:
                    self.connected_ssid = ap.get_ssid().get_data().decode('utf-8', 'replace')
                    self.current_ap = ap
                    self.active_conn = conn
                    self.active_dev = dev

    # 更新UI显示
    self.labels['wifi_ip'].set_text(f"IP: {self.current_ip}")
    refresh_wifi_list_ui(self)

def refresh_wifi_list_ui(self):
    """刷新WiFi列表UI：清空旧列表，添加新条目"""
    # 清空网络列表
    for child in self.grid['wifi_message_grid'].get_children():
        self.grid['wifi_message_grid'].remove(child)
    box_list = ['current_network_box', 'other_network_box']
    for box in box_list:
        self.box[box] = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True)
        self.box[box].set_name(box)
        self.box[box].set_homogeneous(False)
    self.current_wifi = {}
    self.current_wifi_grid = {}
    self.other_wifi = {}
    self.other_wifi_grid = {}
    self.net_list = {}
    # 扫描所有网络
    if hasattr(self, 'filtered_aps'):
        for ap in self.filtered_aps:
            ssid = ap.get_ssid().get_data().decode('utf-8', 'replace')
            self.net_list[ssid] = {}
            self.net_list[ssid]["SSID"] = ssid
            secure = is_security(self, ap)
            self.net_list[ssid]["security"] = get_security_type(self, ap)
            self.net_list[ssid]["BSSID"] = ap.get_bssid() or "N/A"
            freq_mhz = ap.get_frequency()
            self.net_list[ssid]["signal_level"] = ap.get_strength()
            self.net_list[ssid]["channel"] = freq_to_channel(self, freq_mhz)
            self.net_list[ssid]["mode"] = "2.4 GHz" if freq_mhz < 3000 else "5 GHz"
            self.net_list[ssid]["bitrate"] = ap.get_max_bitrate() // 1000
            create_wifi_item(self, ssid, False, secure, ap)

        current_network_label = Gtk.Label(label=_('Current Network'))
        other_network_label = Gtk.Label(label=_('Other Network'))
        row = 0
        if len(self.current_wifi) > 0:
            self.box['current_network_box'].add(current_network_label)
            for wifi_button in self.current_wifi_grid:
                self.box['current_network_box'].add(self.current_wifi_grid[wifi_button])
            self.grid['wifi_message_grid'].attach(self.box['current_network_box'], 0, row, 1, 1)
            row = row + 1
        if len(self.other_wifi) > 0:
            self.box['other_network_box'].add(other_network_label)
            for wifi_button in self.other_wifi_grid:
                self.box['other_network_box'].add(self.other_wifi_grid[wifi_button])
            self.grid['wifi_message_grid'].attach(self.box['other_network_box'], 0, row, 1, 1)

    # 刷新界面显示
    self.content.show_all()

def create_wifi_item(self, ssid, is_connected=False, is_secure=False, ap=None):
    """
    创建单个WiFi条目按钮
    参数:
        ssid: WiFi名称
        is_connected: 是否为已连接的WiFi（决定颜色）
        is_secure: 是否加密（决定是否显示锁图标）
        ap: WiFi AP对象（用于绑定点击事件）
    返回:
        Gtk.Button: 构建好的WiFi条目按钮
    """

    if ssid == self.connected_ssid:
        is_connected = True

    row = 0
    width = 800
    height = 100
    if self._screen.vertical_mode:
        width = 545
        height = 80

    check_mark_icon = Gtk.Image()
    pixbuf = GdkPixbuf.Pixbuf.new_from_file("images/check_mark.png")
    scaled_pixbuf = pixbuf.scale_simple(23, 23, GdkPixbuf.InterpType.BILINEAR)
    check_mark_icon.set_from_pixbuf(scaled_pixbuf)

    wifi_name = Gtk.Label(hexpand=True, halign=Gtk.Align.START, wrap=True, wrap_mode=Pango.WrapMode.WORD_CHAR)
    wifi_name.set_markup(f"<b>{ssid}</b>")



    wifi_icon = Gtk.Image()
    wifi_signal_icon = ""
    net = self.net_list[ssid]
    if net["signal_level"] >=80:
        wifi_signal_icon = "images/wifi_icon4.png"
    elif net["signal_level"] >=60:
        wifi_signal_icon = "images/wifi_icon3.png"
    elif net["signal_level"] >=30:
        wifi_signal_icon = "images/wifi_icon2.png"
    else:
        wifi_signal_icon = "images/wifi_icon1.png"
    pixbuf = GdkPixbuf.Pixbuf.new_from_file(wifi_signal_icon)
    scaled_pixbuf = pixbuf.scale_simple(38, 30, GdkPixbuf.InterpType.BILINEAR)
    wifi_icon.set_halign(Gtk.Align.END)
    wifi_icon.set_from_pixbuf(scaled_pixbuf)

    left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, vexpand=True,
                       halign=Gtk.Align.START, valign=Gtk.Align.CENTER, spacing=10)
    if is_secure and  is_connected:
        #连接成功图标
        left_box.add(check_mark_icon)
    left_box.add(wifi_name)

    right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, vexpand=True,
                        halign=Gtk.Align.END, valign=Gtk.Align.CENTER, spacing=5)
    # 锁图标（仅未连接的加密WiFi显示）
    if is_secure and not is_connected:
        # 未连接带锁的图标
        lock_icon = Gtk.Image()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file("images/lock.png")
        scaled_pixbuf = pixbuf.scale_simple(30, 30, GdkPixbuf.InterpType.BILINEAR)
        lock_icon.set_halign(Gtk.Align.END)
        lock_icon.set_from_pixbuf(scaled_pixbuf)
        right_box.add(lock_icon)
    right_box.add(wifi_icon)

    wifi_button = self._gtk.Button(button_width=width, button_height=height, hexpand=True)
    single_wifi_box = Gtk.Box(spacing=3, hexpand=True, vexpand=False)
    single_wifi_box.add(left_box)
    single_wifi_box.add(right_box)
    wifi_button.add(single_wifi_box)

    if is_connected:
        # 已连接WiFi：点击弹出忘记网络对话框
        wifi_button.get_style_context().add_class("single_wifi_current")
        wifi_button.connect("clicked", remove_confirm_dialog, self, ssid)
        self.current_wifi[ssid] = self.net_list[ssid]
        self.current_wifi_grid[ssid] = wifi_button
    else:

        # 未连接WiFi：点击弹出密码输入框
        wifi_button.get_style_context().add_class("single_wifi_other")
        wifi_button.connect("clicked", connect_dialog, self, ap, ssid)
        self.other_wifi[ssid] = self.net_list[ssid]
        self.other_wifi_grid[ssid] = wifi_button

def is_security(self, ap):
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


def get_security_type(self, ap):
    flags = ap.get_flags()
    if not (flags & 0x1): return "开放"
    wpa_flags = ap.get_wpa_flags()
    rsn_flags = ap.get_rsn_flags()
    sec = []
    if wpa_flags: sec.append("WPA")
    if rsn_flags: sec.append("WPA2")
    return "/".join(sec) if sec else "WEP"

def freq_to_channel(self, freq):
    if freq == 2484:
        return 14
    elif freq < 2484:
        return (freq - 2412) // 5 + 1
    elif freq >= 5035 and freq <= 5865:
        return (freq - 5035) // 5 + 7
    return 0




# ====================== 忘记网络功能（参考用户代码） ======================
#移除已经连接WiFi的Dialog
def remove_confirm_dialog(widget,self,ssid):
    title=_("Remove network")
    buttons = [
        {"name": _("Forget"), "response": Gtk.ResponseType.OK, "style": 'dialog_waring_button'},
        {"name": _("Cancel"), "response": Gtk.ResponseType.CANCEL, "style": 'dialog_cancel_button'}
    ]
    label = Gtk.Label(hexpand=True, vexpand=True, wrap=True)
    label.set_markup(_("Do you want to forget this network?"))
    format_wifiinfo = Gtk.Label(
        label=get_wifi_info(self, self.net_list[ssid]), use_markup=True, ellipsize=Pango.EllipsizeMode.END
    )
    self._gtk.Dialog(title, buttons, format_wifiinfo, confirm_removal, self, ssid)
#回调Dialog 按钮返回事件
def confirm_removal(dialog, response_id, klippy_gtk, self, ssid):
    self._gtk.remove_dialog(dialog)
    if response_id == Gtk.ResponseType.CANCEL:
        return
    if response_id == Gtk.ResponseType.OK:
        logging.info(f"Deleting {ssid}")
        delete_network(self, self.connected_ssid)
    refresh_wifi_list_ui(self)

def delete_network(self, ssid):
    """
    参考用户代码：通过 SSID 删除网络
    参数:
        ssid: 要删除的WiFi名称
    """
    if path := get_connection_path_by_ssid(self, ssid):
        # 找到连接路径，执行删除
        delete_connection_path(self, path)
        # 删除成功后，断开当前连接
        if self.active_conn:
            self.client.deactivate_connection(self.active_conn)
        # 延迟刷新状态
        GLib.timeout_add(500, update_connected_info, self)
    else:
        # 未找到连接
        logger.debug(f"SSID '{ssid}' not found among saved connections")
        self._msg("错误", f"未找到已保存的网络：{ssid}")

def get_connection_path_by_ssid(self, ssid):
    """
        ssid: 要查找的WiFi名称
        str: 连接路径，未找到返回None
    """
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
    """
        path: 要删除的连接路径
    """
    try:
        # 查找对应的连接对象
        connections = self.client.get_connections()
        for conn in connections:
            if conn.get_path() == path:
                # 异步删除连接
                # conn.delete_async(None, on_connection_deleted, self)
                conn.delete_async(None)
                logger.info(f"Deleted connection path: {path}")
                return
        logger.warning(f"Connection path not found: {path}")
    except Exception as e:
        logger.exception(f"Failed to delete connection path: {path} - {e}")
        self._msg("删除失败", f"无法删除连接：{e}")

def on_connection_deleted(self, connection, res):
    """删除连接完成的回调"""
    try:
        success = connection.delete_finish(res)
        if success:
            logger.info("Connection deleted successfully")
        else:
            logger.warning("Failed to delete connection")
    except Exception as e:
        logger.exception(f"Error in deletion callback: {e}")

# ====================== 连接未连接WiFi ======================
def connect_dialog(widget, self, ap, ssid):
    """点击未连接WiFi的回调：弹出密码输入框"""
    self.selected_ap = ap

    is_secure = is_security(self, ap)
    if not is_secure:
        logger.info(f"检测到开放网络：{ssid}，直接发起连接")
        add_new_network(None,None,None,self,ssid,ap)
        return

    if not is_secure:
        logger.info(f"检测到开放网络：{ssid}，直接发起连接")
        self.connect_wifi(ap, pwd=None)
        return
    title = _("Connect network")
    buttons = [
        {"name": _("Save"), "response": Gtk.ResponseType.OK, "style": 'dialog_print_button'},
        {"name": _("Cancel"), "response": Gtk.ResponseType.CANCEL, "style": 'dialog_cancel_button'}
    ]

    main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, vexpand=True)

    orientation = Gtk.Orientation.VERTICAL if self._screen.vertical_mode else Gtk.Orientation.HORIZONTAL
    inside_box = Gtk.Box(orientation=orientation, vexpand=True)

    info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, vexpand=True)
    format_wifiinfo = Gtk.Label(
        label=get_wifi_info(self, self.net_list[ssid]), use_markup=True, ellipsize=Pango.EllipsizeMode.END
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
    self.entry['wifi_psd'].connect("touch-event", self._screen.show_keyboard, key_board_box, None)
    self.entry['wifi_psd'].connect("button-press-event", self._screen.show_keyboard, key_board_box, None)
    self.entry['wifi_psd'].connect("changed", on_entry_text_changed, self)
    inside_box.pack_start(key_board_box, True, True, 0)
    main_box.pack_start(inside_box, True, True, 0)
    self._gtk.Dialog(title, buttons, main_box, add_new_network, self, ssid, ap)
    # connect_wifi(self, ap, pwd.get_text())

#获取输入框中wifi密码
def on_entry_text_changed(entry_widget,self):
    self.wifi_pwd = entry_widget.get_text()
    print("当前WiFi密码输入框内容：", self.wifi_pwd)

def add_new_network(dialog, response_id, klippy_gtk, self, ssid, ap):
    """
    连接指定WiFi
    参数:
        ap: 要连接的WiFi AP对象
        pwd: WiFi密码
    """
    self._gtk.remove_dialog(dialog)
    if response_id == Gtk.ResponseType.CANCEL:
        return
    dev = get_wifi_device(self)
    if not dev:
        return
    is_secure = is_security(self, ap)
    self.labels['wifi_ip'].set_text(f"IP: 正在连接...")


    # 构建NetworkManager连接配置
    conn = NM.SimpleConnection.new()

    # 1. 通用连接设置
    s_con = NM.SettingConnection.new()
    ssid = ap.get_ssid().get_data().decode('utf-8')
    s_con.set_property(NM.SETTING_CONNECTION_ID, ssid)
    s_con.set_property(NM.SETTING_CONNECTION_TYPE, "802-11-wireless")
    conn.add_setting(s_con)

    # 2. WiFi特定设置
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

    # 3. 安全设置（WPA-PSK）
    if is_secure :
        s_wsec = NM.SettingWirelessSecurity.new()
        s_wsec.set_property(NM.SETTING_WIRELESS_SECURITY_KEY_MGMT, "wpa-psk")
        s_wsec.set_property(NM.SETTING_WIRELESS_SECURITY_PSK, self.wifi_pwd)
        conn.add_setting(s_wsec)

    # 4. IP设置（自动DHCP）
    s_ip4 = NM.SettingIP4Config.new()
    s_ip4.set_property(NM.SETTING_IP_CONFIG_METHOD, "auto")
    conn.add_setting(s_ip4)
    s_ip6 = NM.SettingIP6Config.new()
    s_ip6.set_property(NM.SETTING_IP_CONFIG_METHOD, "auto")
    conn.add_setting(s_ip6)

    # 发起连接
    try:
        # 优先用D-Bus路径连接（确保连到指定AP）
        path = ap.get_object_path() if hasattr(ap, 'get_object_path') else ap.path
        self.client.add_and_activate_connection_async(
            conn, dev, path, None
        )
    except:
        # 备选方案：不传特定AP，让系统自己连
        self.client.add_and_activate_connection_async(
            conn, dev, None, None
        )


def start_auto_refresh(self):
    """启动5秒自动刷新定时器"""
    # 先停止已有的定时器，防止重复
    stop_auto_refresh(self)
    # 创建新的定时器，每5秒执行一次回调
    self._auto_refresh_timer_id = GLib.timeout_add(
        self._auto_refresh_interval,
        auto_refresh_callback, self
    )

def auto_refresh_callback(self):
    """
    自动刷新的回调函数
    返回:
        True: 继续执行定时器
        False: 停止定时器
    """
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        wifi_enabled = self.client.wireless_get_enabled()

    # WiFi关闭 或 正在扫描中，跳过本次刷新，继续等待下一次
    if not wifi_enabled or self._scan_pending:
        return True

    # 执行扫描
    start_scan(self)
    return True  # 返回True，定时器持续循环

def stop_auto_refresh(self):
    """停止自动刷新定时器"""
    if self._auto_refresh_timer_id is not None:
        GLib.source_remove(self._auto_refresh_timer_id)
        self._auto_refresh_timer_id = None

def wait_device_and_scan(self):
    """等待WiFi设备就绪后再扫描"""
    if self._scan_pending:
        return False
    dev = get_wifi_device(self)
    if not dev:
        self.labels['wifi_ip'].set_text("IP: 等待设备...")
        return True  # 继续等待

    # 设备已就绪，开始扫描
    self._scan_pending = True
    # self.labels['wifi_ip'].set_text("IP: 扫描中...")
    start_scan(self)
    return False

def get_wifi_device(self):
    """获取系统中第一个WiFi硬件设备"""
    devices = self.client.get_devices()
    for dev in devices:
        if dev.get_device_type() == NM.DeviceType.WIFI:
            return dev
    return None

def start_scan(self):
    """发起WiFi扫描请求"""
    dev = get_wifi_device(self)
    if not dev:
        return
    try:
        # 异步扫描，不阻塞UI
        dev.request_scan_async(None, on_scan_finished, self, dev)
    except Exception as e:
        # 扫描频繁被拒，直接读取现有列表
        GLib.timeout_add(500, process_scan_result, self, dev)

def on_scan_finished(dev, res, self, user_data):
    """扫描完成的回调"""
    try:
        dev.request_scan_finish(res)
    except:
        pass
    # 延迟一小会儿再读取列表，确保硬件更新完毕
    GLib.timeout_add(600, process_scan_result, self, dev)

def process_scan_result(self, dev):
    """
    处理扫描结果：去重（同名只保留信号最强的）+ 排序
    返回:
        False: 让timeout只执行一次
    """
    all_aps = dev.get_access_points()
    best = {}  # 字典结构: { "SSID字符串": (信号强度, AP对象) }

    # 第一步：去重筛选
    for ap in all_aps:
        ssid_b = ap.get_ssid()
        if not ssid_b:
            continue
        # 解码SSID
        try:
            ssid = ssid_b.get_data().decode('utf-8')
        except:
            ssid = ssid_b.get_data().decode('latin-1', 'replace')
        if not ssid:
            continue

        # 比较信号强度，只保留同SSID下信号最强的
        strength = ap.get_strength()
        if ssid not in best or strength > best[ssid][0]:
            best[ssid] = (strength, ap)

    # 第二步：按信号强度降序排序
    self.filtered_aps = [ap for (s, ap) in sorted(best.values(), key=lambda x: -x[0])]

    # 重置扫描标志，更新UI
    self._scan_pending = False
    update_connected_info(self)
    return False

# ====================== 刷新按钮 ======================
def on_refresh_clicked(self, widget):
    """手动点击刷新按钮的回调"""
    if not self._scan_pending:
        self.start_scan()

# ====================== WiFi开关控制 ======================
def on_wifi_switch_toggled(switch, gparam, self):
    """WiFi开关拨动时的回调函数"""
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        active = switch.get_active()
        # 设置系统WiFi开关
        self.client.wireless_set_enabled(active)

    # 同步UI状态
    self.buttons['reload_wifi'].set_sensitive(active)
    if active:
        # WiFi打开：启动自动刷新，延迟扫描
        self.labels['wifi_ip'].set_text("\nIP: 正在启用...\n")
        self._scan_pending = False
        start_auto_refresh(self)
        GLib.timeout_add(800, wait_device_and_scan, self)
    else:
        # WiFi关闭：停止自动刷新，清空列表
        stop_auto_refresh(self)
        self.filtered_aps = []
        self.current_wifi = {}
        self.current_wifi_grid = {}
        self.other_wifi = {}
        self.other_wifi_grid = {}
        self.net_list = {}
        self.connected_ssid = None
        self.current_ap = None
        self.current_ip = "未连接"
        self.labels['wifi_ip'].set_text("IP: 未连接")
        for child in self.grid['wifi_message_grid'].get_children():
            self.grid['wifi_message_grid'].remove(child)
        box_list = ['current_network_box', 'other_network_box']
        for box in box_list:
            self.box[box] = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True)
            self.box[box].set_name(box)
            self.box[box].set_homogeneous(False)

#获取wifi详细信息
def get_wifi_info(self, net):
    info = ""
    # {'BSSID': 'CE:4D:6B:96:64:E9', 'SSID': 'HuangHai', 'channel': '1', 'frequency': '2.4', 'known': False, ‘max_bitrate’：130000'security': 'AES WPA-PSK', 'signal_level': 94}
    # MAC                           Name                    群组          频段                  是否连接        加密方式                    信号强度
    if "SSID" in net:
        info += _("SSID") + f': <b>{net["SSID"]}</b> ' + '\n'

    if "channel" in net:
        info += _("Channel") + f': <b>{net["channel"]}</b> ' + '\n'

    if "mode" in net:
        info += _("Frequency") + f': <b>{net["mode"]}</b>' + '\n'

    if "signal_level" in net:
        info += _("Signal Level") + f': <b>{net["signal_level"]}%</b> ' + '\n'

    if "security" in net:
        info += _("Security") + f': <b>{net["security"]}</b> ' + '\n'

    if "BSSID" in net:
        info += _("MAC Address") + f': <b>{net["BSSID"]}</b> '
    return info