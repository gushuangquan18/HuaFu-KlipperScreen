import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import sys
import os


class PanelApplication:
    def __init__(self):
        # 创建主窗口
        self.window = Gtk.Window(title="GTK面板应用")
        self.window.set_default_size(500, 400)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.connect("destroy", Gtk.main_quit)

        # 设置窗口样式
        self.window.set_border_width(20)

        # 创建主布局
        main_box = Gtk.VBox(spacing=20)

        # 创建标题
        title_label = Gtk.Label()
        title_label.set_markup("<span size='x-large' weight='bold'>GTK弹窗面板演示</span>")
        title_label.set_margin_bottom(10)

        # 创建主按钮
        self.main_button = Gtk.Button(label="点击弹出选择面板")
        self.main_button.set_size_request(200, 50)
        self.main_button.connect("clicked", self.on_main_button_clicked)

        # 页面显示区域
        self.page_display = Gtk.Frame(label="页面显示区域")
        self.page_display.set_shadow_type(Gtk.ShadowType.IN)

        page_content = Gtk.VBox(spacing=10)
        page_content.set_border_width(15)

        self.current_page_label = Gtk.Label()
        self.current_page_label.set_markup("<span size='large' weight='bold'>欢迎页面</span>")
        self.current_page_label.set_justify(Gtk.Justification.CENTER)

        page_description = Gtk.Label()
        page_description.set_text("请点击上面的按钮选择要跳转的页面")
        page_description.set_line_wrap(True)

        page_content.pack_start(self.current_page_label, False, False, 0)
        page_content.pack_start(page_description, False, False, 0)

        self.page_display.add(page_content)

        # 添加组件到主布局
        main_box.pack_start(title_label, False, False, 0)
        main_box.pack_start(self.main_button, False, False, 0)
        main_box.pack_start(self.page_display, True, True, 0)

        self.window.add(main_box)

    def on_main_button_clicked(self, button):
        """主按钮点击事件"""
        self.show_selection_dialog()

    def show_selection_dialog(self):
        """显示无标题选择对话框"""
        # 创建无装饰的对话框
        dialog = Gtk.Dialog(parent=self.window, flags=0)
        dialog.set_decorated(False)  # 移除窗口装饰（标题栏和关闭按钮）
        dialog.set_default_size(300, 150)
        dialog.set_modal(True)
        dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)

        # 设置对话框样式
        content_area = dialog.get_content_area()
        content_area.set_border_width(15)
        content_area.set_spacing(15)

        # 创建说明标签
        info_label = Gtk.Label()
        info_label.set_markup("<span size='medium' weight='bold'>请选择要跳转的页面:</span>")
        content_area.pack_start(info_label, False, False, 0)

        # 创建按钮区域
        button_box = Gtk.HBox(spacing=10)
        button_box.set_halign(Gtk.Align.CENTER)

        # A按钮
        button_a = Gtk.Button(label="A页面")
        button_a.set_size_request(80, 40)
        button_a.connect("clicked", self.on_page_selected, "A", dialog)

        # B按钮
        button_b = Gtk.Button(label="B页面")
        button_b.set_size_request(80, 40)
        button_b.connect("clicked", self.on_page_selected, "B", dialog)

        # C按钮
        button_c = Gtk.Button(label="C页面")
        button_c.set_size_request(80, 40)
        button_c.connect("clicked", self.on_page_selected, "C", dialog)

        # 添加按钮到布局
        button_box.pack_start(button_a, False, False, 0)
        button_box.pack_start(button_b, False, False, 0)
        button_box.pack_start(button_c, False, False, 0)

        content_area.pack_start(button_box, False, False, 0)

        # 显示对话框
        dialog.show_all()

    def on_page_selected(self, button, page_name, dialog):
        """页面选择事件"""
        dialog.destroy()
        self.navigate_to_page(page_name)

    def navigate_to_page(self, page_name):
        """跳转到指定页面"""
        self.current_page_label.set_markup(f"<span size='large' weight='bold'>{page_name}页面</span>")

        # 根据页面名称设置不同的描述
        descriptions = {
            "A": "这是A页面的内容区域。\n您可以在这里放置A页面特有的功能和信息。",
            "B": "这是B页面的内容区域。\n这里是B页面专属的功能模块和数据显示区。",
            "C": "这是C页面的内容区域。\nC页面为您提供了独特的操作界面和数据展示。"
        }

        # 更新页面显示区域
        frame_children = self.page_display.get_children()
        if frame_children:
            content_box = frame_children[0]
            if isinstance(content_box, Gtk.VBox):
                # 移除旧的描述标签
                children = content_box.get_children()
                if len(children) > 1:
                    old_description = children[1]
                    content_box.remove(old_description)

                # 添加新的描述标签
                description_label = Gtk.Label()
                description_label.set_text(descriptions.get(page_name, f"这是{page_name}页面"))
                description_label.set_line_wrap(True)
                content_box.pack_start(description_label, False, False, 0)
                description_label.show()

    def run(self):
        self.window.show_all()
        Gtk.main()


if __name__ == "__main__":
    app = PanelApplication()
    app.run()
