import logging
import os
import pathlib
from functools import lru_cache
import json
import logging
import gi
import re

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GdkPixbuf, Gio, Gtk, Pango
from ks_includes.widgets.scroll import CustomScrolledWindow
from jinja2 import Template
from datetime import datetime
from ks_includes.screen_panel import ScreenPanel
from ks_includes.KlippyGtk import find_widget
from ks_includes.KlippyGcodes import KlippyGcodes

#热床自动校准
def bed_mesh_calibration(widget,self):
    widget.set_sensitive(False)
    self._screen.show_popup_message(_("Calibrating"), level=1)
    if self._printer.get_stat("toolhead", "homed_axes") != "xyz":
        self._screen._ws.klippy.gcode_script("G28")
    if (
            "Z_TILT_ADJUST" in self._printer.available_commands
            and not bool(self._printer.get_stat("z_tilt", "applied"))
    ):
        self._screen._ws.klippy.gcode_script("Z_TILT_ADJUST")
    if (
            "QUAD_GANTRY_LEVEL" in self._printer.available_commands
            and not bool(self._printer.get_stat("quad_gantry_level", "applied"))
    ):
        self._screen._ws.klippy.gcode_script("QUAD_GANTRY_LEVEL")
    self._screen._send_action(widget, "printer.gcode.script", {"script": "BED_MESH_CALIBRATE"})
    # self._screen._send_action(widget, "printer.gcode.script", {'script': 'SAVE_CONFIG'})




def start_z_calibration(widget, self):
    command = 'PROBE_CALIBRATE'
    self.buttons['start_z_calibration'].set_sensitive(False)
    self._screen._ws.klippy.gcode_script("SET_GCODE_OFFSET Z=0")
    if self._printer.config_section_exists("bed_mesh"):
        self._screen._ws.klippy.gcode_script("BED_MESH_CLEAR")
    if self._printer.get_stat("toolhead", "homed_axes") != "xyz":
        self._screen._ws.klippy.gcode_script("G28")
    x,y=get_calibration_location(widget, self)
    move_to_position(widget, self, x, y)
    self._screen._ws.klippy.gcode_script('PROBE_CALIBRATE')
    # self.labels['new_z_value'].set_text(f"New:{abs(position[2] - self.z_offset):.3f}")

def get_calibration_location(widget,self):
    #判断
    if self.ks_printer_cfg is not None:
        x = self.ks_printer_cfg.getfloat("calibrate_x_position", None)
        y = self.ks_printer_cfg.getfloat("calibrate_y_position", None)
        if x and y:
            logging.debug(f"Using KS configured position: {x}, {y}")
            return x, y

    #判断
    self.zero_ref = []
    if 'zero_reference_position' in self._printer.get_config_section("bed_mesh"):
        self.zero_ref = csv_to_array(mesh['zero_reference_position'])
    init_xyz_offset(self)
    if self.zero_ref:
        logging.debug(f"Using zero reference position: {self.zero_ref}")
        return self.zero_ref[0] - self.x_offset, self.zero_ref[1] - self.y_offset

    #判断
    if ("safe_z_home" in self._printer.get_config_section_list() and
            "Z_ENDSTOP_CALIBRATE" not in self._printer.available_commands):
        return get_safe_z(self)

    self.mesh_radius = None
    self.mesh_origin = [0, 0]
    mesh = self._printer.get_config_section("bed_mesh")
    if 'mesh_radius' in mesh:
        self.mesh_radius = float(mesh['mesh_radius'])
        if 'mesh_origin' in mesh:
            self.mesh_origin = csv_to_array(mesh['mesh_origin'])
    elif 'mesh_min' in mesh and 'mesh_max' in mesh:
        self.mesh_min = csv_to_array(mesh['mesh_min'])
        self.mesh_max = csv_to_array(mesh['mesh_max'])
    elif 'min_x' in mesh and 'min_y' in mesh and 'max_x' in mesh and 'max_y' in mesh:
        self.mesh_min = [float(mesh['min_x']), float(mesh['min_y'])]
        self.mesh_max = [float(mesh['max_x']), float(mesh['max_y'])]
    if 'zero_reference_position' in self._printer.get_config_section("bed_mesh"):
        self.zero_ref = csv_to_array(mesh['zero_reference_position'])
    if self.mesh_radius or "delta" in self._printer.get_config_section("printer")['kinematics']:
        logging.info(f"Round bed calibrating at {self.mesh_origin}")
        return self.mesh_origin[0] - self.x_offset, self.mesh_origin[1] - self.y_offset

    x, y = calculate_position(widget, self)
    return x, y

def csv_to_array(string):
    return [float(i.strip()) for i in string.split(',')]

def get_safe_z(self):
    safe_z = self._printer.get_config_section("safe_z_home")
    safe_z_xy = csv_to_array(safe_z['home_xy_position'])
    logging.debug(f"Using safe_z {safe_z_xy[0]}, {safe_z_xy[1]}")
    if 'z_hop' in safe_z:
        self.z_hop = float(safe_z['z_hop'])
    if 'z_hop_speed' in safe_z:
        self.z_hop_speed = float(safe_z['z_hop_speed'])
    return safe_z_xy[0], safe_z_xy[1]

def calculate_position(widget, self):
    if self.mesh_max and self.mesh_min:
        mesh_mid_x = (self.mesh_min[0] + self.mesh_max[0]) / 2
        mesh_mid_y = (self.mesh_min[1] + self.mesh_max[1]) / 2
        logging.debug(f"Probe in the mesh center X:{mesh_mid_x} Y:{mesh_mid_y}")
        return mesh_mid_x - self.x_offset, mesh_mid_y - self.y_offset
    try:
        mid_x = float(self._printer.get_config_section("stepper_x")['position_max']) / 2
        mid_y = float(self._printer.get_config_section("stepper_y")['position_max']) / 2
    except KeyError:
        logging.error("Couldn't get max position from stepper_x and stepper_y")
        return None, None
    logging.debug(f"Probe in the center X:{mid_x} Y:{mid_y}")
    return mid_x - self.x_offset, mid_y - self.y_offset

#初始化xyz offset
def init_xyz_offset(self):
    self.z_hop_speed = 15.0
    self.z_hop = 5.0
    self.probe = self._printer.get_probe()
    if self.probe:
        self.x_offset = float(self.probe.get('x_offset', 0.0))
        self.y_offset = float(self.probe.get('y_offset', 0.0))
        self.z_offset = float(self.probe['z_offset'])
        if "sample_retract_dist" in self.probe:
            self.z_hop = float(self.probe['sample_retract_dist'])
        if "speed" in self.probe:
            self.z_hop_speed = float(self.probe['speed'])
    else:
        self.x_offset = 0.0
        self.y_offset = 0.0
        self.z_offset = 0.0
    self.labels['old_z_value'].set_text(f"Old:{self.z_offset:.3f}")

def move_to_position(widget,self, x, y):
    if not x or not y:
        self._screen.show_popup_message(_("Error: Couldn't get a position to probe"))
        return
    logging.info(f"Lifting Z: {self.z_hop}mm {self.z_hop_speed}mm/s")
    self._screen._ws.klippy.gcode_script(f"G91\nG0 Z{self.z_hop} F{self.z_hop_speed * 60}")
    logging.info(f"Moving to X:{x} Y:{y}")
    self._screen._ws.klippy.gcode_script(f'G90\nG0 X{x} Y{y} F3000')

#计算位置
def calculate_position(widget, self):
    if self.mesh_max and self.mesh_min:
        mesh_mid_x = (self.mesh_min[0] + self.mesh_max[0]) / 2
        mesh_mid_y = (self.mesh_min[1] + self.mesh_max[1]) / 2
        logging.debug(f"Probe in the mesh center X:{mesh_mid_x} Y:{mesh_mid_y}")
        return mesh_mid_x - self.x_offset, mesh_mid_y - self.y_offset
    try:
        mid_x = float(self._printer.get_config_section("stepper_x")['position_max']) / 2
        mid_y = float(self._printer.get_config_section("stepper_y")['position_max']) / 2
    except KeyError:
        logging.error("Couldn't get max position from stepper_x and stepper_y")
        return None, None
    logging.debug(f"Probe in the center X:{mid_x} Y:{mid_y}")
    return mid_x - self.x_offset, mid_y - self.y_offset

#更新Z的位置
def update_position(self, position):
    self.labels['z_value'].set_text(f"Z: {position[2]:.3f}")
    if hasattr(self, 'z_offset'):
        self.labels['new_z_value'].set_text(f"New:{abs(position[2] - self.z_offset):.3f}")

#确认更改新的值
def confrim_calibration(widget,self):
    logging.info("Accepting Z position")
    # self._screen.show_popup_message(self,"Accepting Z position")
    self._screen._ws.klippy.gcode_script("ACCEPT")
#中止Z偏移校准
def cancle_calibration(widget,self):
    text = _("Are you sure you want to stop the calibration?")
    methods =  "printer.gcode.script"
    script = {"script": "ABORT"}
    self._screen._confirm_send_action(widget,text,methods,script)

#更改按钮是否启用
def buttons_calibrating(self):
    self.buttons['start_z_calibration'].set_sensitive(False)
    self.buttons['raise_heater_bed'].set_sensitive(True)
    self.buttons['reduce_heater_bed'].set_sensitive(True)
    self.buttons['confirm'].set_sensitive(True)
    self.buttons['cancel'].set_sensitive(True)

def buttons_not_calibrating(self):
    self.buttons['start_z_calibration'].set_sensitive(True)
    self.buttons['raise_heater_bed'].set_sensitive(False)
    self.buttons['reduce_heater_bed'].set_sensitive(False)
    self.buttons['confirm'].set_sensitive(False)
    self.buttons['cancel'].set_sensitive(False)

