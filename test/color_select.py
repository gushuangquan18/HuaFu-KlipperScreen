import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


class ColorWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="GTK3 颜色选择器示例")
        self.set_border_width(10)
        self.set_default_size(250, 100)

        # 创建颜色选择按钮
        self.color_button = Gtk.ColorButton()

        # 设置默认颜色（可选）
        rgba = Gdk.RGBA()
        rgba.parse("red")  # 可以是 "blue", "#ff0000", "rgb(255,0,0)" 等
        self.color_button.set_rgba(rgba)

        # 连接信号：当用户选择新颜色时触发
        self.color_button.connect("color-set", self.on_color_chosen)

        # 将按钮加入窗口
        self.add(self.color_button)

    def on_color_chosen(self, color_button):
        rgba = color_button.get_rgba()
        print(f"选中的颜色 RGBA: {rgba.to_string()}")
        # 你也可以用 rgba.red, rgba.green, rgba.blue, rgba.alpha 获取分量（0.0~1.0）


# 启动应用
win = ColorWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()