import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class ScrolledWindowExample(Gtk.Window):
    def __init__(self):
        super().__init__(title="ScrolledWindow 示例")
        self.set_default_size(1000, 600)  # 窗口稍大一点，方便查看
        self.set_border_width(10)

        # 创建 ScrolledWindow
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_size_request(970, 520)  # 设置 ScrolledWindow 自身宽高
        scrolled_window.set_policy(
            Gtk.PolicyType.NEVER,      # 水平滚动条：从不显示
            Gtk.PolicyType.AUTOMATIC   # 垂直滚动条：内容超出时自动显示
        )

        # 创建一个高内容区域（例如一个垂直 Box，里面放很多标签）
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        # 添加大量行以触发垂直滚动
        for i in range(100):
            label = Gtk.Label(label=f"这是第 {i+1} 行内容 —— 用于测试滚动功能")
            label.set_xalign(0)  # 左对齐
            content_box.pack_start(label, False, False, 0)

        # 将内容添加到 ScrolledWindow
        scrolled_window.add(content_box)

        # 将 ScrolledWindow 添加到主窗口
        self.add(scrolled_window)

# 启动应用
win = ScrolledWindowExample()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()