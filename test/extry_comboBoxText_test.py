# !/usr/bin/env python3
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class InputWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="GTK输入组件示例")
        self.set_border_width(10)
        self.set_default_size(400, 200)

        # 创建主垂直布局
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(main_vbox)

        # 创建文本输入框
        self.create_text_entry(main_vbox)

        # 创建下拉选择框（非隐藏式）
        self.create_combo_box(main_vbox)

        # 添加状态标签
        self.status_label = Gtk.Label()
        self.status_label.set_text("请选择选项或输入文本")
        main_vbox.pack_start(self.status_label, False, False, 0)

    def create_text_entry(self, container):
        """创建文本输入框"""
        # 文本框标签
        label = Gtk.Label()
        label.set_text("文本输入框:")
        label.set_halign(Gtk.Align.START)
        container.pack_start(label, False, False, 0)

        # 文本输入框
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("请输入文本...")
        self.entry.connect("changed", self.on_entry_changed)
        container.pack_start(self.entry, False, False, 0)

    def create_combo_box(self, container):
        """创建下拉选择框（非隐藏式）"""
        # 下拉框标签
        label = Gtk.Label()
        label.set_text("下拉选择框（常显）:")
        label.set_halign(Gtk.Align.START)
        container.pack_start(label, False, False, 0)

        # 创建下拉选项列表
        combo_list = ["选项 1", "选项 2", "选项 3", "选项 4", "选项 5"]

        # 创建ComboBoxText并添加选项
        self.combo = Gtk.ComboBoxText()
        for item in combo_list:
            self.combo.append_text(item)

        # 设置默认选中第一项
        self.combo.set_active(0)

        # 连接选择变化事件
        self.combo.connect("changed", self.on_combo_changed)

        # 设置下拉框样式使其选项常显
        container.pack_start(self.combo, False, False, 0)

    def on_entry_changed(self, entry):
        """文本输入框内容变化事件"""
        text = entry.get_text()
        self.status_label.set_text(f"输入文本: {text}")

    def on_combo_changed(self, combo):
        """下拉框选择变化事件"""
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            selected = combo.get_active_text()
            self.status_label.set_text(f"选择选项: {selected}")

    def run(self):
        """运行应用程序"""
        self.connect("destroy", Gtk.main_quit)
        self.show_all()
        Gtk.main()


if __name__ == "__main__":
    app = InputWindow()
    app.run()
