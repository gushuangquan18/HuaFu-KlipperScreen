import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class ButtonHeightExample:
    def __init__(self):
        # 创建主窗口
        self.window = Gtk.Window(title="按钮高度示例")
        self.window.set_default_size(300, 200)
        self.window.connect("destroy", Gtk.main_quit)

        # 创建一个垂直布局容器
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.window.add(vbox)

        # 创建按钮并设置其大小
        button = Gtk.Button(label="点击我")
        button.set_size_request(-1, 100)  # -1 表示宽度自适应，50 表示高度为 50 像素
        button.connect("clicked", self.on_button_clicked)
        vbox.pack_start(button, False, False, 0)

        # 显示窗口和按钮
        self.window.show_all()

    def on_button_clicked(self, button):
        print("按钮被点击了！")

if __name__ == "__main__":
    example = ButtonHeightExample()
    Gtk.main()
