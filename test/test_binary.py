import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio
import subprocess
import os


class GTKControlsDemo:
    def __init__(self):
        # 创建主窗口
        self.window = Gtk.Window(title="GTK控件演示")
        self.window.set_default_size(500, 400)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.connect("destroy", Gtk.main_quit)

        # 设置窗口样式
        self.window.set_border_width(20)

        # 创建主布局
        main_box = Gtk.VBox(spacing=20)

        # 创建标题
        title_label = Gtk.Label()
        title_label.set_markup("<span size='x-large' weight='bold'>GTK控件演示</span>")
        title_label.set_margin_bottom(10)

        # 创建分隔线
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)

        # 创建控件区域
        controls_frame = Gtk.Frame(label="控件演示区域")
        controls_frame.set_shadow_type(Gtk.ShadowType.IN)

        controls_box = Gtk.VBox(spacing=15)
        controls_box.set_border_width(15)

        # 1. Binary开关控件
        binary_label = Gtk.Label()
        binary_label.set_markup("<b>Binary开关控件</b>")
        binary_label.set_xalign(0)

        self.binary_switch = Gtk.Switch()
        self.binary_switch.set_active(False)
        self.binary_switch.connect("notify::active", self.on_binary_switch_toggled)

        binary_box = Gtk.HBox(spacing=10)
        binary_box.pack_start(binary_label, False, False, 0)
        binary_box.pack_end(self.binary_switch, False, False, 0)

        # 2. Dropdown下拉控件
        dropdown_label = Gtk.Label()
        dropdown_label.set_markup("<b>Dropdown下拉控件</b>")
        dropdown_label.set_xalign(0)

        self.dropdown_combo = Gtk.ComboBoxText()
        self.dropdown_combo.append_text("选项 1")
        self.dropdown_combo.append_text("选项 2")
        self.dropdown_combo.append_text("选项 3")
        self.dropdown_combo.append_text("选项 4")
        self.dropdown_combo.set_active(0)
        self.dropdown_combo.connect("changed", self.on_dropdown_changed)

        dropdown_box = Gtk.HBox(spacing=10)
        dropdown_box.pack_start(dropdown_label, False, False, 0)
        dropdown_box.pack_end(self.dropdown_combo, False, False, 0)

        # 3. Printer按钮控件
        printer_label = Gtk.Label()
        printer_label.set_markup("<b>Printer打印按钮</b>")
        printer_label.set_xalign(0)

        self.printer_button = Gtk.Button(label="打印文档")
        self.printer_button.connect("clicked", self.on_printer_button_clicked)

        printer_box = Gtk.HBox(spacing=10)
        printer_box.pack_start(printer_label, False, False, 0)
        printer_box.pack_end(self.printer_button, False, False, 0)

        # 状态显示区域
        status_frame = Gtk.Frame(label="状态信息")
        status_frame.set_shadow_type(Gtk.ShadowType.OUT)

        self.status_text = Gtk.TextView()
        self.status_text.set_editable(False)
        self.status_text.set_wrap_mode(Gtk.WrapMode.WORD)
        self.status_text.set_size_request(-1, 100)

        status_scroll = Gtk.ScrolledWindow()
        status_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        status_scroll.add(self.status_text)

        # 添加所有控件到布局
        controls_box.pack_start(binary_box, False, False, 0)
        controls_box.pack_start(dropdown_box, False, False, 0)
        controls_box.pack_start(printer_box, False, False, 0)

        controls_frame.add(controls_box)

        main_box.pack_start(title_label, False, False, 0)
        main_box.pack_start(separator, False, False, 0)
        main_box.pack_start(controls_frame, False, False, 0)
        main_box.pack_start(status_frame, True, True, 0)

        self.window.add(main_box)

        # 初始化状态文本
        self.update_status("应用程序已启动\n")

    def on_binary_switch_toggled(self, switch, gparam):
        """Binary开关切换事件"""
        if switch.get_active():
            self.update_status("Binary开关已打开\n")
        else:
            self.update_status("Binary开关已关闭\n")

    def on_dropdown_changed(self, combo):
        """Dropdown下拉选择事件"""
        active_text = combo.get_active_text()
        if active_text:
            self.update_status(f"Dropdown选择: {active_text}\n")

    def on_printer_button_clicked(self, button):
        """Printer按钮点击事件"""
        self.update_status("Printer按钮被点击\n")
        self.update_status("正在准备打印...\n")
        # 模拟打印操作
        self.print_document()

    def print_document(self):
        """模拟打印文档"""
        self.update_status("打印操作完成\n")

    def update_status(self, message):
        """更新状态信息"""
        buffer = self.status_text.get_buffer()
        end_iter = buffer.get_end_iter()
        buffer.insert(end_iter, message)
        # 滚动到底部
        adj = self.status_text.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())

    def run(self):
        self.window.show_all()
        Gtk.main()


if __name__ == "__main__":
    app = GTKControlsDemo()
    app.run()
