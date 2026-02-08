import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="主界面")
        self.set_default_size(300, 200)
        self.set_border_width(15)

        # 创建主界面按钮
        self.main_btn = Gtk.Button(label="点击弹出对话框")
        self.main_btn.connect("clicked", self.on_main_btn_clicked)

        # 添加按钮到主窗口
        self.add(self.main_btn)

    def on_main_btn_clicked(self, widget):
        # 创建对话框（模态窗口，关联主窗口）
        dialog = Gtk.Dialog(
            title="确认对话框",
            transient_for=self,  # 设置主窗口为父窗口
            flags=Gtk.DialogFlags.MODAL  # 模态对话框，阻止父窗口交互
        )
        dialog.set_default_size(250, 120)

        # 获取对话框内容区域，添加提示文本
        content_area = dialog.get_content_area()
        content_area.set_border_width(15)
        label = Gtk.Label(label="请确认操作")
        content_area.add(label)

        # 添加确认按钮并连接信号
        confirm_btn = dialog.add_button("确认", Gtk.ResponseType.OK)
        confirm_btn.connect("clicked", lambda btn: dialog.destroy())  # 点击后销毁对话框

        # 显示对话框所有组件并运行
        dialog.show_all()
        dialog.run()  # 阻塞等待用户操作


if __name__ == "__main__":
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
