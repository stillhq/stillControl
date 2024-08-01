# Tool to create a layout from the current GNOME setup.
import json
from gi.repository import Gio

shell_settings = Gio.Settings.new("org.gnome.shell")

panel_settings = Gio.Settings.new("org.gnome.shell.extensions.dash-to-panel")
panel_keys = [
    "intellihide",
    "appicon-margin",
    "appicon-padding",
    "focus-highlight",
    "dot-position",
    "dot-style-unfocused",
    "dot-style-focused",
    "show-favorites",
    "show-running-apps",
    "group-apps"
]
panel_monitor_keys = [
    "panel-anchors", "panel-element-positions",
    "panel-lengths", "panel-positions", "panel-sizes"
]

dock_settings = Gio.Settings.new("org.gnome.shell.extensions.dash-to-dock")
dock_keys = [
    "intellihide",
    "dock-position",
    "dash-max-icon-size",
    "height-fraction",
    "custom-theme-shrink",
    "show-favorites",
    "show-running",
    "isolate-monitors",
    "show-show-apps-button",
    "show-trash",
    "show-mounts",
    "show-window-previews",
    "show-apps-at-top",
    "show-apps-always-at-edge",

]
arc_settings = Gio.Settings.new("org.gnome.shell.extensions.arc-menu")
arc_keys = [

]

layout_dict = {}

layout_name = input("Set name: ")
layout_dict["name"] = layout_name

enabled_extensions = shell_settings.get_strv("enabled-extensions")

if "dash-to-panel@jderose9.github.com" in enabled_extensions:
    layout_dict["panel"] = panel_settings.get_string("settings")

