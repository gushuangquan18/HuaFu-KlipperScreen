import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class RadioButtonApp:
    def __init__(self):
        # 创建主窗口
        self.window = Gtk.Window(title="GTK单选按钮示例")
        self.window.set_default_size(300, 200)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.connect("destroy", Gtk.main_quit)

        # 创建主布局
        vbox = Gtk.VBox(spacing=10)
        vbox.set_border_width(20)

        # 创建标题标签
        title_label = Gtk.Label()
        title_label.set_markup("<span size='large' weight='bold'>请选择一个选项：</span>")

        # 创建单选按钮组（普通样式，无圆形图标）
        radio_group = None

        # 自动选项
        self.radio_auto = Gtk.RadioButton.new_with_label_from_widget(radio_group, "自动")
        self.radio_auto.connect("toggled", self.on_radio_toggled, "自动")
        # 设置为普通按钮样式
        # self.radio_auto.set_mode(False)

        # 开始选项
        self.radio_start = Gtk.RadioButton.new_with_label_from_widget(self.radio_auto, "开始")
        self.radio_start.connect("toggled", self.on_radio_toggled, "开始")
        # 设置为普通按钮样式
        # self.radio_start.set_mode(False)

        # 关闭选项
        self.radio_stop = Gtk.RadioButton.new_with_label_from_widget(self.radio_auto, "关闭")
        self.radio_stop.connect("toggled", self.on_radio_toggled, "关闭")
        # 设置为普通按钮样式
        # self.radio_stop.set_mode(False)

        # 状态显示标签
        self.status_label = Gtk.Label()
        self.status_label.set_text("当前选择: 无")
        self.status_label.set_line_wrap(True)

        # 添加组件到布局
        vbox.pack_start(title_label, False, False, 0)
        vbox.pack_start(self.radio_auto, False, False, 0)
        vbox.pack_start(self.radio_start, False, False, 0)
        vbox.pack_start(self.radio_stop, False, False, 0)
        vbox.pack_start(Gtk.Separator(), False, False, 0)
        vbox.pack_start(self.status_label, False, False, 0)

        self.window.add(vbox)

    def on_radio_toggled(self, button, name):
        """单选按钮切换事件处理"""
        if button.get_active():
            self.status_label.set_text(f"当前选择: {name}")
            print(f"选择了: {name}")

    def run(self):
        self.window.show_all()
        Gtk.main()


if __name__ == "__main__":
    app = RadioButtonApp()
    app.run()
