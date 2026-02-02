import gi
import threading
import time

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib


class GifDisplayApp:
    def __init__(self):
        # 创建主窗口
        self.window = Gtk.Window(title="GTK GIF动图自动播放")
        self.window.set_default_size(400, 300)
        self.window.connect("destroy", Gtk.main_quit)

        # 设置窗口居中
        self.window.set_position(Gtk.WindowPosition.CENTER)

        # 创建主布局
        main_box = Gtk.VBox(spacing=10)
        main_box.set_border_width(20)


        # 创建图像显示区域
        self.image = Gtk.Image()
        self.image.set_size_request(200, 200)

        main_box.pack_start(self.image, True, True, 0)

        self.window.add(main_box)

        # GIF动画相关变量
        self.animation_running = False
        self.current_frame = 0
        self.frames = []
        self.frame_delay = 100  # 毫秒

        # 加载GIF文件
        self.load_gif("../images/test.gif")

    def load_gif(self, filename):
        """加载GIF文件并提取帧"""
        try:
            # 加载GIF文件
            self.pixbuf_animation = GdkPixbuf.PixbufAnimation.new_from_file(filename)
            self.iter = self.pixbuf_animation.get_iter()

            # 获取第一帧显示
            pixbuf = self.iter.get_pixbuf()
            if pixbuf:
                # 缩放图片以适应显示区域
                scaled_pixbuf = pixbuf.scale_simple(200, 200, GdkPixbuf.InterpType.BILINEAR)
                self.image.set_from_pixbuf(scaled_pixbuf)

                # 启动自动播放
                self.start_animation_auto()
        except Exception as e:
            print(f"加载GIF失败: {e}")
            # 显示错误信息
            error_label = Gtk.Label(label="无法加载GIF文件")
            self.image.set_from_pixbuf(None)

    def start_animation_auto(self):
        """自动开始播放动画"""
        if not self.animation_running:
            self.animation_running = True
            self.animate()

    def stop_animation(self):
        """停止播放动画"""
        self.animation_running = False

    def animate(self):
        """动画播放函数"""
        if not self.animation_running:
            return

        # 获取当前帧
        pixbuf = self.iter.get_pixbuf()
        if pixbuf:
            # 缩放图片以适应显示区域
            scaled_pixbuf = pixbuf.scale_simple(200, 200, GdkPixbuf.InterpType.BILINEAR)
            self.image.set_from_pixbuf(scaled_pixbuf)

        # 计算下一帧的时间间隔
        delay_time = self.iter.get_delay_time()
        if delay_time == -1:
            delay_time = 100  # 默认100毫秒

        # 更新到下一帧
        self.iter.advance()

        # 继续播放下一帧
        if self.animation_running:
            GLib.timeout_add(delay_time, self.animate)

    def run(self):
        self.window.show_all()
        Gtk.main()


if __name__ == "__main__":
    app = GifDisplayApp()
    app.run()
