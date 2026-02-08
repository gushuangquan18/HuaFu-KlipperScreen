import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="按钮左右对齐示例")
        self.set_default_size(400, 100)
        self.set_border_width(10)

        grid = Gtk.Grid()
        grid.set_column_spacing(10)  # 列间距（可选）

        # 左侧按钮
        left_button = Gtk.Button(label="左按钮")

        # 右侧按钮
        right_button = Gtk.Button(label="右按钮")

        # 将左按钮放在第 0 列
        grid.attach(left_button, 0, 0, 1, 1)

        # 将右按钮放在第 2 列（跳过第 1 列）
        grid.attach(right_button, 2, 0, 1, 1)

        # 关键：让中间的第 1 列自动拉伸填充空白
        grid.set_column_homogeneous(False)
        # 设置第 1 列为“可扩展”——通过给它分配权重
        grid.set_column_spacing(0)
        # 实际上 Grid 本身不直接支持“弹性列”，但可以通过添加一个占位 widget 并让它 hexpand=True 来实现

        # 更可靠的做法：显式添加一个空的、可扩展的占位标签
        spacer = Gtk.Label()  # 或 Gtk.Box(), 任意 widget
        spacer.set_hexpand(True)  # 水平方向自动拉伸
        grid.attach(spacer, 1, 0, 1, 1)

        self.add(grid)


win = MainWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()