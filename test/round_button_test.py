import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GObject
import math


class CircularDirectionPad(Gtk.DrawingArea):
    __gsignals__ = {
        'direction-pressed': (GObject.SIGNAL_RUN_LAST, None, (str,))
    }

    def __init__(self):
        super().__init__()
        self.set_size_request(250, 250)  # 控件大小
        self.set_events(
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.TOUCH_MASK
        )
        self.connect("draw", self.on_draw)
        self.connect("button-press-event", self.on_button_press)
        self.connect("touch-event", self.on_touch_event)

        # 扇区定义：顺时针从右开始（0° = +X）
        self.sectors = [
            {"label": "+X", "angle": 0},  # 右
            {"label": "+10", "angle": 45},  # 右上
            {"label": "+Y", "angle": 90},  # 上
            {"label": "-1", "angle": 135},  # 左上
            {"label": "-X", "angle": 180},  # 左
            {"label": "-10", "angle": 225},  # 左下
            {"label": "-Y", "angle": 270},  # 下
            {"label": "+1", "angle": 315},  # 右下
        ]

    def on_draw(self, widget, cr):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) * 0.45  # 外圆半径

        # 绘制外圆背景
        cr.arc(center_x, center_y, radius, 0, 2 * math.pi)
        cr.set_source_rgba(0.2, 0.2, 0.2, 0.9)
        cr.fill_preserve()
        cr.set_source_rgb(0.6, 0.6, 0.6)
        cr.set_line_width(2)
        cr.stroke()

        # 绘制分割线
        for sector in self.sectors:
            angle_rad = math.radians(sector["angle"])
            x1 = center_x + radius * 0.8 * math.cos(angle_rad)
            y1 = center_y + radius * 0.8 * math.sin(angle_rad)
            x2 = center_x + radius * 1.0 * math.cos(angle_rad)
            y2 = center_y + radius * 1.0 * math.sin(angle_rad)
            cr.move_to(x1, y1)
            cr.line_to(x2, y2)
            cr.set_source_rgb(0.4, 0.4, 0.4)
            cr.set_line_width(1)
            cr.stroke()

        # 绘制扇区文字
        for sector in self.sectors:
            angle_rad = math.radians(sector["angle"])
            text_x = center_x + radius * 0.65 * math.cos(angle_rad)
            text_y = center_y + radius * 0.65 * math.sin(angle_rad)

            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            cr.set_font_size(14)
            cr.set_source_rgb(1, 1, 1)
            xbearing, ybearing, width, height, _, _ = cr.text_extents(sector["label"])
            cr.move_to(text_x - width / 2, text_y + height / 2)
            cr.show_text(sector["label"])

        # 绘制中心按钮（房子图标）
        center_radius = 35
        cr.arc(center_x, center_y, center_radius, 0, 2 * math.pi)
        cr.set_source_rgba(0.3, 0.8, 0.3, 0.9)
        cr.fill_preserve()
        cr.set_source_rgb(0.9, 0.9, 0.9)
        cr.set_line_width(2)
        cr.stroke()

        # 简化房子图标
        house_size = 12
        cr.move_to(center_x, center_y - house_size)
        cr.line_to(center_x - house_size, center_y + house_size * 0.5)
        cr.line_to(center_x + house_size, center_y + house_size * 0.5)
        cr.close_path()
        cr.set_source_rgb(0.95, 0.95, 0.95)
        cr.fill()

    def get_direction_at_point(self, x, y):
        """根据坐标返回方向"""
        width = self.get_allocated_width()
        height = self.get_allocated_height()
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) * 0.45
        center_radius = 35

        dx = x - center_x
        dy = y - center_y
        dist_from_center = math.hypot(dx, dy)

        # 检查是否点击中心
        if dist_from_center <= center_radius:
            return "HOME"

        # 检查是否在有效圆内
        if dist_from_center > radius:
            return None

        # 计算角度（0° = +X 轴，逆时针为正）
        angle_deg = math.degrees(math.atan2(dy, dx))
        if angle_deg < 0:
            angle_deg += 360

        # 匹配扇区
        for sector in self.sectors:
            start_angle = sector["angle"] - 22.5  # 每个扇区 ±22.5°
            end_angle = sector["angle"] + 22.5
            if start_angle <= angle_deg < end_angle:
                return sector["label"]
        return None

    def on_button_press(self, widget, event):
        direction = self.get_direction_at_point(event.x, event.y)
        if direction:
            self.emit('direction-pressed', direction)
        return True

    def on_touch_event(self, widget, event):
        if event.type == Gdk.EventType.TOUCH_BEGIN:
            direction = self.get_direction_at_point(event.x, event.y)
            if direction:
                self.emit('direction-pressed', direction)
        return True


# === 主程序 ===
def on_direction_pressed(pad, direction):
    print(f"点击: {direction}")


window = Gtk.Window()
window.set_title("圆形扇形按钮")
window.set_default_size(300, 300)
window.connect("destroy", Gtk.main_quit)

pad = CircularDirectionPad()
pad.connect('direction-pressed', on_direction_pressed)

window.add(pad)
window.show_all()

Gtk.main()