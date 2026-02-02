import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class ProgressBarApp:
    def __init__(self):
        # 创建主窗口
        self.window = Gtk.Window(title="GTK进度条控制")
        self.window.set_default_size(400, 300)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.connect("destroy", Gtk.main_quit)

        # 设置窗口边距
        self.window.set_border_width(20)

        # 创建主布局
        main_vbox = Gtk.VBox(spacing=20)

        # 创建标题
        title_label = Gtk.Label()
        title_label.set_markup("<span size='x-large' weight='bold'>进度条控制面板</span>")

        # 创建进度条
        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_fraction(0.0)
        self.progressbar.set_text("0%")
        self.progressbar.set_show_text(True)

        # 创建按钮区域
        buttons_frame = Gtk.Frame(label="控制按钮")
        buttons_frame.set_shadow_type(Gtk.ShadowType.IN)

        buttons_grid = Gtk.Grid()
        buttons_grid.set_column_spacing(10)
        buttons_grid.set_row_spacing(10)
        buttons_grid.set_border_width(15)

        # 创建控制按钮
        # 0% 按钮
        button_0 = Gtk.Button(label="设置 0%")
        button_0.connect("clicked", self.on_set_progress, 0.0)

        # 25% 按钮
        button_25 = Gtk.Button(label="设置 25%")
        button_25.connect("clicked", self.on_set_progress, 0.25)

        # 100% 按钮
        button_100 = Gtk.Button(label="设置 100%")
        button_100.connect("clicked", self.on_set_progress, 1.0)

        # 加法按钮
        button_plus = Gtk.Button(label="增加 1%")
        button_plus.connect("clicked", self.on_increase_progress)

        # 减法按钮
        button_minus = Gtk.Button(label="减少 1%")
        button_minus.connect("clicked", self.on_decrease_progress)

        # 添加按钮到网格布局
        buttons_grid.attach(button_0, 0, 0, 1, 1)
        buttons_grid.attach(button_25, 1, 0, 1, 1)
        buttons_grid.attach(button_100, 2, 0, 1, 1)
        buttons_grid.attach(button_plus, 0, 1, 1, 1)
        buttons_grid.attach(button_minus, 1, 1, 1, 1)

        buttons_frame.add(buttons_grid)

        # 状态标签
        self.status_label = Gtk.Label()
        self.status_label.set_text("当前进度: 0%")

        # 添加所有组件到主布局
        main_vbox.pack_start(title_label, False, False, 0)
        main_vbox.pack_start(self.progressbar, False, False, 0)
        main_vbox.pack_start(buttons_frame, False, False, 0)
        main_vbox.pack_start(self.status_label, False, False, 0)

        self.window.add(main_vbox)

    def on_set_progress(self, button, fraction):
        """设置进度到指定百分比"""
        self.progressbar.set_fraction(fraction)
        percent = int(fraction * 100)
        self.progressbar.set_text(f"{percent}%")
        self.status_label.set_text(f"当前进度: {percent}%")

    def on_increase_progress(self, button):
        """增加1%进度"""
        current_fraction = self.progressbar.get_fraction()
        new_fraction = min(current_fraction + 0.01, 1.0)
        self.progressbar.set_fraction(new_fraction)
        percent = int(new_fraction * 100)
        self.progressbar.set_text(f"{percent}%")
        self.status_label.set_text(f"当前进度: {percent}%")

    def on_decrease_progress(self, button):
        """减少1%进度"""
        current_fraction = self.progressbar.get_fraction()
        new_fraction = max(current_fraction - 0.01, 0.0)
        self.progressbar.set_fraction(new_fraction)
        percent = int(new_fraction * 100)
        self.progressbar.set_text(f"{percent}%")
        self.status_label.set_text(f"当前进度: {percent}%")

    def run(self):
        self.window.show_all()
        Gtk.main()


if __name__ == "__main__":
    app = ProgressBarApp()
    app.run()
