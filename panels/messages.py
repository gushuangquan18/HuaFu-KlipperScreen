import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from ks_includes.screen_panel import ScreenPanel
from panels.create_panel import Panel as CreatePanel


COLORS = {
    "time": "DarkGrey",
    "info": "Silver",
    "warning": "DarkOrange",
    "error": "FireBrick",
}


def remove_newlines(msg: str) -> str:
    return msg.replace('\n', ' ')


class Panel(CreatePanel):
    def __init__(self, screen, title, items=None):
        super().__init__(screen, title, items)
        grid = Gtk.Grid(row_homogeneous=True, column_homogeneous=True, hexpand=True, vexpand=True)
        scroll = self._gtk.ScrolledWindow()
        self.numpad_visible = False

        if self._screen.vertical_mode:
            print(self._screen.vertical_mode)
        else:
            scroll.add(self.labels["parent_grid"])
            grid.attach(scroll, 0, 0, 1, 1)
        self.content.add(grid)

    # def add_notification(self, log):
    #     if log["level"] == 0:
    #         if "error" in log["message"].lower() or "cannot" in log["message"].lower():
    #             color = COLORS["error"]
    #         else:
    #             color = COLORS["info"]
    #     elif log["level"] == 1:
    #         color = COLORS["info"]
    #     elif log["level"] == 2:
    #         color = COLORS["warning"]
    #     else:
    #         color = COLORS["error"]
    #     self.tb.insert_markup(
    #         self.tb.get_end_iter(),
    #         f'\n<span color="{COLORS["time"]}">{log["time"]}</span> '
    #         f'<span color="{color}"><b>{remove_newlines(log["message"])}</b></span>',
    #         -1
    #     )






