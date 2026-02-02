# !/usr/bin/env python3
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class ComponentWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="GTK UI组件示例")
        self.set_border_width(10)
        self.set_default_size(400, 300)

        # 创建主容器
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(main_box)

        # 文本输入框部分
        text_frame = Gtk.Frame(label="文本输入框")
        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        text_frame.add(text_box)

        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("请输入文本...")
        self.entry.connect("changed", self.on_entry_changed)
        text_box.pack_start(self.entry, False, False, 0)

        self.label_display = Gtk.Label()
        self.label_display.set_text("输入内容将在这里显示")
        text_box.pack_start(self.label_display, False, False, 0)

        main_box.pack_start(text_frame, False, False, 0)

        # 下拉选择框部分
        combo_frame = Gtk.Frame(label="下拉选择框")
        combo_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        combo_frame.add(combo_box)

        languages = ["Python", "Java", "C++", "JavaScript", "Go", "Rust"]
        self.combo = Gtk.ComboBoxText()
        self.combo.set_entry_text_column(0)
        for lang in languages:
            self.combo.append_text(lang)
        self.combo.set_active(0)
        self.combo.connect("changed", self.on_combo_changed)
        combo_box.pack_start(self.combo, False, False, 0)

        self.combo_label = Gtk.Label()
        self.combo_label.set_text(f"当前选择: {languages[0]}")
        combo_box.pack_start(self.combo_label, False, False, 0)

        main_box.pack_start(combo_frame, False, False, 0)

        # 复选框部分
        check_frame = Gtk.Frame(label="复选框")
        check_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        check_frame.add(check_box)

        self.check_options = {
            "选项1": Gtk.CheckButton(label="启用功能A"),
            "选项2": Gtk.CheckButton(label="启用功能B"),
            "选项3": Gtk.CheckButton(label="启用功能C")
        }

        for key, checkbox in self.check_options.items():
            checkbox.connect("toggled", self.on_checkbox_toggled, key)
            check_box.pack_start(checkbox, False, False, 0)

        self.check_result = Gtk.Label()
        self.check_result.set_text("选中状态: 无")
        check_box.pack_start(self.check_result, False, False, 0)

        main_box.pack_start(check_frame, False, False, 0)

        # 底部按钮
        button_box = Gtk.Box(spacing=6)
        main_box.pack_start(button_box, False, False, 0)

        clear_btn = Gtk.Button.new_with_label("清空")
        clear_btn.connect("clicked", self.on_clear_clicked)
        button_box.pack_start(clear_btn, True, True, 0)

        quit_btn = Gtk.Button.new_with_label("退出")
        quit_btn.connect("clicked", self.on_quit_clicked)
        button_box.pack_start(quit_btn, True, True, 0)

    def on_entry_changed(self, entry):
        """文本输入框内容改变事件"""
        text = entry.get_text()
        self.label_display.set_text(f"输入内容: {text}")

    def on_combo_changed(self, combo):
        """下拉框选择改变事件"""
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            selected = combo.get_active_text()
            self.combo_label.set_text(f"当前选择: {selected}")

    def on_checkbox_toggled(self, checkbox, name):
        """复选框切换事件"""
        active_checks = [key for key, cb in self.check_options.items() if cb.get_active()]
        if active_checks:
            self.check_result.set_text(f"选中状态: {', '.join(active_checks)}")
        else:
            self.check_result.set_text("选中状态: 无")

    def on_clear_clicked(self, widget):
        """清空按钮事件"""
        self.entry.set_text("")
        self.combo.set_active(0)
        for checkbox in self.check_options.values():
            checkbox.set_active(False)

    def on_quit_clicked(self, widget):
        """退出按钮事件"""
        Gtk.main_quit()


def main():
    window = ComponentWindow()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
