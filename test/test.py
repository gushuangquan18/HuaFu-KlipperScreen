import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

class ProgressBarWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="进度条颜色示例")
        self.set_default_size(400, 50)
        self.set_border_width(10)

        # 创建进度条
        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_fraction(0.5)  # 设置初始进度为 50%

        # 添加到窗口
        self.add(self.progressbar)

        # 应用自定义 CSS 样式
        css_provider = Gtk.CssProvider()

        # 定义 CSS 样式
        css = """
        progressbar trough {
            background-color: #EDEDED; /* 背景颜色 */
        }
        progressbar progress {
            background-color: red; /* 进度条颜色 */
        }
        """

        # 加载 CSS 样式
        css_provider.load_from_data(css.encode('utf-8'))

        # 获取当前屏幕并添加样式提供器
        screen = Gdk.Screen.get_default()
        style_context = self.get_style_context()
        style_context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

# 启动应用
win = ProgressBarWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()