import json
import os

from gi.repository import Gio

import constants

_shell_settings = Gio.Settings.new("org.gnome.shell")
_panel_settings = Gio.Settings.new("org.gnome.shell.extensions.dash-to-panel")
_dock_settings = Gio.Settings.new("org.gnome.shell.extensions.dash-to-dock")
_arc_settings = Gio.Settings.new("org.gnome.shell.extensions.arcmenu")

_LAYOUTS_UI = os.path.join(os.path.dirname(__file__), "layouts")

_monitor_specific_panel_settings = [
    "panel-anchors", "panel-element-positions",
    "panel-lengths", "panel-positions", "panel-sizes"
]


def set_extensions(to_enable, to_disable):
    enabled_extensions = _shell_settings.get_strv("enabled-extensions")
    disabled_extensions = _shell_settings.get_strv("enabled-extensions")
    for extension in to_disable:
        if extension in enabled_extensions:
            enabled_extensions.remove(extension)
        if extension not in disabled_extensions:
            disabled_extensions.append(extension)
    for extension in to_enable:
        if extension not in enabled_extensions:
            enabled_extensions.append(extension)
        if extension in disabled_extensions:
            disabled_extensions.remove(extension)

    _shell_settings.set_strv("enabled-extensions", enabled_extensions)


def set_panel_settings(settings):
    for key in settings:
        if key in _monitor_specific_panel_settings:
            set_monitor_specific_panel_setting(key, settings[key])
        else:
            _panel_settings.set_value(key, settings[key])


def set_dock_settings(settings):
    for key in settings:
        _dock_settings.set_value(key, settings[key])


def set_arc_settings(settings):
    for key in settings:
        _arc_settings.set_value(key, settings[key])


def split_setting(setting):
    split = setting.split(".")
    key = split.pop()
    schema = ".".join(split)

    return schema, key


def set_gsetting(setting, value):
    schema, key = split_setting(setting)
    settings = Gio.Settings.new(schema)
    settings.set_value(key, value)


def set_gsettings(json):
    for key in json:
        set_gsetting(key, json[key])


def check_setting(setting, value):
    schema, key = split_setting(setting)
    settings = Gio.Settings.new(schema)
    return settings.get_value(key) == value


def check_gsettings(json):
    for key in json:
        if not check_setting(key, json[key]):
            return False
    return True


def check_monitor_specific_panel_setting(key, value):
    setting_value = _panel_settings.get_value(key)
    for monitor in setting_value:
        if setting_value[monitor] != value:
            return False
    return True


def set_monitor_specific_panel_setting(key, value):
    settings = _panel_settings.get_value(key)
    for monitor in settings:
        settings[monitor] = value
    _panel_settings.set_value(key, settings)


def set_layout_from_dict(layout: dict):
    enabled_exts = []
    disabled_exts = []

    # Figure out extensions to enable and disable
    if "panel" in layout:
        set_panel_settings(layout["panel"])
        enabled_exts.append("dash-to-panel@jderose9.github.com")
    else:
        disabled_exts.append("dash-to-panel@jderose9.github.com")

    if "dock" in layout:
        set_dock_settings(layout["dock"])
        enabled_exts.append("dash-to-dock@micxgx.gmail.com")
    else:
        disabled_exts.append("dash-to-dock@micxgx.gmail.com")

    if "arc" in layout:
        set_arc_settings(layout["arc"])
        enabled_exts.append("arcmenu@arcmenu.com")
    else:
        disabled_exts.append("arcmenu@arcmenu.com")

    set_extensions(enabled_exts, disabled_exts)

    if "gsettings" in layout:
        set_gsettings(layout["gsettings"])


def set_layout(layout: str):
    json_file = f"{_LAYOUTS_UI}/{layout}.json"

    if os.path.exists(json_file):
        with open(json_file, "r") as file:
            layout = json.load(file)
            set_layout_from_dict(layout)
    else:
        raise FileNotFoundError(f"Layout file {json_file} not found in {_LAYOUTS_UI} directory")