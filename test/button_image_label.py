
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class ButtonWithImageAndText:
    def __init__(self):
        # 创建主窗口
        self.window = Gtk.Window(title="GTK按钮图片与文字示例")
        self.window.set_default_size(300, 200)
        self.window.connect("destroy", Gtk.main_quit)

        # 创建一个水平盒子容器
        box = Gtk.HBox(spacing=10)
        box.set_border_width(10)

        # 加载图片
        image = Gtk.Image()
        image.set_from_file("icon.png")  # 替换为你的图片路径

        # 创建标签
        label = Gtk.Label(label="按钮文字")

        # 创建按钮容器
        button_box = Gtk.HBox(spacing=5)
        button_box.pack_start(image, False, False, 0)
        button_box.pack_start(label, False, False, 0)

        # 创建按钮并添加容器
        button = Gtk.Button()
        button.add(button_box)

        # 将按钮添加到主窗口
        box.pack_start(button, False, False, 0)
        self.window.add(box)

    def run(self):
        self.window.show_all()
        Gtk.main()

if __name__ == "__main__":
    app = ButtonWithImageAndText()
    app.run()
