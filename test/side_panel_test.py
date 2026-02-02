# !/usr/bin/env python3
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="GTK侧面板示例")
        self.set_default_size(800, 600)
        self.set_position(Gtk.WindowPosition.CENTER)

        # 创建主布局
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.add(main_box)

        # 左侧主内容区域
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        left_box.set_margin_left(20)
        left_box.set_margin_right(20)
        left_box.set_margin_top(20)
        left_box.set_margin_bottom(20)

        # 主界面标题
        title_label = Gtk.Label()
        title_label.set_markup("<span size='20000' weight='bold'>主界面内容</span>")
        left_box.pack_start(title_label, False, False, 0)

        # 说明文本
        desc_label = Gtk.Label()
        desc_label.set_text("这是主界面的内容区域\n点击右侧按钮可以打开侧面板")
        desc_label.set_justify(Gtk.Justification.CENTER)
        left_box.pack_start(desc_label, False, False, 10)

        # 主要功能按钮
        main_button = Gtk.Button(label="主要功能按钮")
        main_button.set_size_request(200, 40)
        main_button.connect("clicked", self.on_main_button_clicked)
        left_box.pack_start(main_button, False, False, 10)

        # 添加一些占位内容
        for i in range(5):
            label = Gtk.Label(label=f"主界面内容项目 {i + 1}")
            left_box.pack_start(label, False, False, 5)

        main_box.pack_start(left_box, True, True, 0)

        # 右侧按钮区域
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        right_box.set_margin_left(10)
        right_box.set_margin_right(10)
        right_box.set_margin_top(20)
        right_box.set_margin_bottom(20)

        # 触发侧面板的按钮
        self.toggle_button = Gtk.Button(label="▶ 打开侧面板")
        self.toggle_button.set_size_request(120, 40)
        self.toggle_button.connect("clicked", self.on_toggle_sidebar)
        right_box.pack_start(self.toggle_button, False, False, 0)

        main_box.pack_start(right_box, False, False, 0)

        # 创建侧面板
        self.create_sidebar()

        # 标记侧面板状态
        self.sidebar_visible = False

    def create_sidebar(self):
        # 创建侧面板窗口
        self.sidebar = Gtk.Window()
        self.sidebar.set_default_size(300, 600)
        self.sidebar.set_decorated(False)  # 去掉窗口装饰
        self.sidebar.set_keep_above(True)  # 置于顶层
        self.sidebar.set_skip_taskbar_hint(True)  # 不在任务栏显示
        self.sidebar.set_skip_pager_hint(True)  # 不在分页器显示

        # 设置样式
        screen = self.sidebar.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.sidebar.set_visual(visual)

        # 侧面板主布局
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        sidebar_box.set_margin_left(15)
        sidebar_box.set_margin_right(15)
        sidebar_box.set_margin_top(15)
        sidebar_box.set_margin_bottom(15)

        # 侧面板标题
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        title_label = Gtk.Label()
        title_label.set_markup("<span size='14000' weight='bold'>侧面板</span>")
        title_box.pack_start(title_label, True, True, 0)

        # 关闭按钮
        close_button = Gtk.Button(label="×")
        close_button.set_size_request(30, 30)
        close_button.connect("clicked", self.on_toggle_sidebar)
        title_box.pack_end(close_button, False, False, 0)

        sidebar_box.pack_start(title_box, False, False, 0)

        # 分隔线
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        sidebar_box.pack_start(separator, False, False, 0)

        # 侧面板内容
        content_label = Gtk.Label()
        content_label.set_text("这是侧面板的内容区域\n可以放置各种控件和信息")
        content_label.set_justify(Gtk.Justification.CENTER)
        content_label.set_line_wrap(True)
        sidebar_box.pack_start(content_label, False, False, 10)

        # 功能按钮区域
        button_grid = Gtk.Grid()
        button_grid.set_column_spacing(10)
        button_grid.set_row_spacing(10)

        # 添加多个功能按钮
        buttons = [
            ("设置", self.on_settings_clicked),
            ("帮助", self.on_help_clicked),
            ("保存", self.on_save_clicked),
            ("加载", self.on_load_clicked),
            ("导出", self.on_export_clicked),
            ("导入", self.on_import_clicked)
        ]

        for i, (label, callback) in enumerate(buttons):
            button = Gtk.Button(label=label)
            button.set_size_request(120, 35)
            button.connect("clicked", callback)
            row = i // 2
            col = i % 2
            button_grid.attach(button, col, row, 1, 1)

        sidebar_box.pack_start(button_grid, False, False, 10)

        # 信息显示区域
        info_frame = Gtk.Frame(label="信息")
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        info_box.set_margin_left(10)
        info_box.set_margin_right(10)
        info_box.set_margin_top(10)
        info_box.set_margin_bottom(10)

        info_labels = [
            "状态: 运行中",
            "版本: 1.0.0",
            "用户: 默认用户",
            "连接: 已连接"
        ]

        for text in info_labels:
            label = Gtk.Label(label=text)
            label.set_xalign(0)  # 左对齐
            info_box.pack_start(label, False, False, 2)

        info_frame.add(info_box)
        sidebar_box.pack_start(info_frame, False, False, 10)

        # 底部按钮
        bottom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        ok_button = Gtk.Button(label="确定")
        ok_button.set_size_request(100, 35)
        ok_button.connect("clicked", self.on_ok_clicked)
        bottom_box.pack_end(ok_button, False, False, 0)

        cancel_button = Gtk.Button(label="取消")
        cancel_button.set_size_request(100, 35)
        cancel_button.connect("clicked", self.on_cancel_clicked)
        bottom_box.pack_end(cancel_button, False, False, 0)

        sidebar_box.pack_end(bottom_box, False, False, 0)

        self.sidebar.add(sidebar_box)

        # 监听窗口焦点事件
        self.sidebar.connect("focus-out-event", self.on_sidebar_focus_out)

    def on_toggle_sidebar(self, widget):
        if self.sidebar_visible:
            self.sidebar.hide()
            self.toggle_button.set_label("▶ 打开侧面板")
            self.sidebar_visible = False
        else:
            # 计算侧面板位置
            window_x, window_y = self.get_position()
            window_width = self.get_allocated_width()
            sidebar_x = window_x + window_width  # 稍微重叠一点
            sidebar_y = window_y

            self.sidebar.move(sidebar_x, sidebar_y)
            self.sidebar.show_all()
            self.toggle_button.set_label("◀ 关闭侧面板")
            self.sidebar_visible = True

    def on_sidebar_focus_out(self, widget, event):
        # 当侧面板失去焦点时自动隐藏
        if self.sidebar_visible:
            self.sidebar.hide()
            self.toggle_button.set_label("▶ 打开侧面板")
            self.sidebar_visible = False
        return False

    def on_main_button_clicked(self, widget):
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="主界面按钮被点击!"
        )
        dialog.run()
        dialog.destroy()

    # 侧面板内按钮的回调函数
    def on_settings_clicked(self, widget):
        self.show_info_dialog("设置功能", "设置按钮被点击")

    def on_help_clicked(self, widget):
        self.show_info_dialog("帮助",
                              "帮助信息:\n1. 点击按钮打开侧面板\n2. 侧面板可以浮动显示\n3. 点击关闭按钮或失去焦点时自动隐藏")

    def on_save_clicked(self, widget):
        self.show_info_dialog("保存", "数据已保存")

    def on_load_clicked(self, widget):
        self.show_info_dialog("加载", "数据加载完成")

    def on_export_clicked(self, widget):
        self.show_info_dialog("导出", "数据导出成功")

    def on_import_clicked(self, widget):
        self.show_info_dialog("导入", "数据导入完成")

    def on_ok_clicked(self, widget):
        self.show_info_dialog("确认", "操作已确认")

    def on_cancel_clicked(self, widget):
        self.sidebar.hide()
        self.toggle_button.set_label("▶ 打开侧面板")
        self.sidebar_visible = False

    def show_info_dialog(self, title, message):
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.set_title(title)
        dialog.run()
        dialog.destroy()


def main():
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
