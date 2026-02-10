import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="父窗口示例")
        # 设置主窗口初始大小
        self.set_default_size(600, 400)
        self.set_border_width(10)

        # 创建主布局
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        # 创建触发按钮
        self.button = Gtk.Button(label="打开对齐的对话框")
        self.button.connect("clicked", self.on_button_clicked)
        vbox.pack_start(self.button, True, True, 0)

    def on_button_clicked(self, widget):
        # 获取父窗口的GdkWindow对象（确保窗口已映射到屏幕）
        parent_gdk_window = self.get_window()
        if not parent_gdk_window:
            return

        # 关键：获取窗口的完整几何范围（包含标题栏、边框）
        # frame_extents 返回 (x, y, width, height) 是窗口在屏幕上的实际占用区域
        frame_extents = parent_gdk_window.get_frame_extents()
        parent_actual_x = frame_extents.x
        parent_actual_y = frame_extents.y
        parent_actual_width = frame_extents.width
        parent_actual_height = frame_extents.height

        # 计算对话框参数（精准对齐）
        dialog_width = parent_actual_width // 2  # 宽度为父窗口一半
        dialog_height = parent_actual_height  # 高度与父窗口一致
        # 核心修正：父窗口右边界 - 对话框宽度 = 对话框左边界（保证右侧对齐）
        dialog_x = parent_actual_x + parent_actual_width - dialog_width
        dialog_y = parent_actual_y  # 上侧对齐

        # 创建对话框
        dialog = Gtk.Dialog(
            title="对齐的对话框",
            parent=self,
            flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT
        )
        # 强制固定对话框尺寸（避免内容撑开）
        dialog.set_size_request(dialog_width, dialog_height)
        dialog.set_resizable(False)  # 禁止调整对话框大小
        # 移动到精准位置
        dialog.move(dialog_x, dialog_y)

        # 对话框内容
        content_area = dialog.get_content_area()
        label = Gtk.Label(label=f"父窗口实际宽度：{parent_actual_width}\n对话框宽度：{dialog_width}\n已精准右对齐")
        content_area.pack_start(label, True, True, 10)

        # 关闭按钮
        dialog.add_button("关闭", Gtk.ResponseType.CLOSE)
        dialog.connect("response", lambda d, r: d.destroy())

        # 显示对话框
        dialog.show_all()


if __name__ == "__main__":
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
