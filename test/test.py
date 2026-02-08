import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


class FakeSwitch(Gtk.ToggleButton):
    def __init__(self, width=80, height=30):
        super().__init__()
        self.set_size_request(width, height)
        self.set_can_focus(False)  # 可选：禁用焦点框

        # 创建两个 Label 模拟开关状态（也可用图标）
        self.label_on = Gtk.Label(label="● ON")
        self.label_off = Gtk.Label(label="OFF ○")

        # 初始状态
        self.update_state()
        self.connect("toggled", self.on_toggled)

    def on_toggled(self, button):
        self.update_state()

    def update_state(self):
        if self.get_active():
            self.remove(self.get_child()) if self.get_child() else None
            self.add(self.label_on)
        else:
            self.remove(self.get_child()) if self.get_child() else None
            self.add(self.label_off)
        self.show_all()


# ===== 使用示例 =====
class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="自定义 Switch")
        self.set_border_width(20)
        self.set_default_size(250, 100)

        # 创建自定义 switch（宽 100px, 高 40px）
        fake_switch = FakeSwitch(width=100, height=40)
        fake_switch.set_active(True)

        # 可选：添加边框让它更像开关
        css_provider = Gtk.CssProvider()
        css = b"""
        togglebutton {
            border: 2px solid #999;
            border-radius: 20px;
            background: white;
        }
        togglebutton:checked {
            background: #4CAF50;
            color: white;
        }
        """
        css_provider.load_from_data(css)
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.add(fake_switch)


win = MainWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()