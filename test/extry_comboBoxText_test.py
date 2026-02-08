import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class TemperatureEntryWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="温度输入（℃ 内嵌）")
        self.set_default_size(300, 200)
        self.set_resizable(False)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        vbox.set_margin_start(15)
        vbox.set_margin_end(15)
        vbox.set_margin_top(15)
        vbox.set_margin_bottom(15)
        self.add(vbox)

        # === 输入框 ===
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("输入温度值")
        self.entry.set_text("℃")  # 初始带单位
        self.entry.set_position(0)  # 光标在最前
        self.entry.set_alignment(0.5)

        # 监听内容变化
        self.entry.connect("changed", self.on_entry_changed)
        # 监听按键（防止删除 ℃）
        self.entry.connect("key-press-event", self.on_key_press)

        vbox.pack_start(self.entry, False, False, 0)

        # === 数字键盘 ===
        grid = Gtk.Grid()
        grid.set_row_spacing(5)
        grid.set_column_spacing(5)
        grid.set_halign(Gtk.Align.CENTER)

        buttons = [
            (1, 0, 0), (2, 0, 1), (3, 0, 2),
            (4, 1, 0), (5, 1, 1), (6, 1, 2),
            (7, 2, 0), (8, 2, 1), (9, 2, 2),
            (0, 3, 1),
        ]

        for num, row, col in buttons:
            btn = Gtk.Button(label=str(num))
            btn.set_size_request(60, 50)
            btn.connect("clicked", self.on_digit_clicked, num)
            grid.attach(btn, col, row, 1, 1)

        vbox.pack_start(grid, True, True, 0)

    def on_digit_clicked(self, button, digit):
        current = self.entry.get_text()
        if current.endswith("℃"):
            # 插入数字到 ℃ 前
            new_text = current[:-1] + str(digit) + "℃"
        else:
            new_text = current + str(digit) + "℃"
        self.entry.set_text(new_text)
        self.entry.set_position(len(new_text) - 1)  # 光标停在数字末尾（℃前）

    def on_entry_changed(self, entry):
        text = entry.get_text()
        if not text.endswith("℃"):
            # 自动补上 ℃
            if "℃" in text:
                # 如果中间有 ℃，清理掉（只保留末尾）
                text = text.replace("℃", "") + "℃"
            else:
                text = text + "℃"
            entry.set_text(text)
            entry.set_position(len(text) - 1)

    def on_key_press(self, entry, event):
        # 获取当前光标位置
        pos = entry.get_position()
        text = entry.get_text()
        length = len(text)

        # 如果光标在最后（即 ℃ 后面），禁止输入（因为 ℃ 是固定的）
        if pos == length:
            # 不允许在 ℃ 后输入
            return True  # 阻止事件

        # 如果选中了 ℃ 并按删除，阻止
        start, end = entry.get_selection_bounds() if entry.get_has_selection() else (pos, pos)
        if start < length and end >= length - 1:  # 选中了 ℃
            return True  # 阻止删除单位

        return False  # 允许其他操作


# === 运行 ===
def main():
    win = TemperatureEntryWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()