import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

class ComboBoxWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="ComboBoxText 背景色修复版")
        self.set_border_width(15)
        self.set_default_size(300, 80)

        combo = Gtk.ComboBoxText()
        combo.append_text("苹果")
        combo.append_text("香蕉")
        combo.append_text("橙子")
        combo.set_active(0)

        # 👇 关键：添加自定义 CSS 类名
        combo.get_style_context().add_class("my-combo")

        # 设置尺寸（可选）
        combo.set_size_request(200, 35)

        # === 应用 CSS ===
        css_provider = Gtk.CssProvider()
        css = """
        /* 针对不可编辑的 ComboBoxText */
        .my-combo button {
            background-color: #FFCCBC;      /* 背景色 */
            border: 1px solid #FF8A65;      /* 可选：自定义边框 */
            color: #BF360C;                 /* 文字颜色 */
        }

        /* 下拉菜单中的选项样式（可选） */
        .my-combo popup > contents {
            background-color: white;
        }
        """
        css_provider.load_from_data(css.encode('utf-8'))

        # 应用到屏幕
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen,
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.add(combo)

# 启动
win = ComboBoxWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()