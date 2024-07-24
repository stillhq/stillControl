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
    disabled_extensions = _shell_settings.get_strv("disabled-extensions")
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


def check_extensions(enabled, disabled):
    enabled_extensions = _shell_settings.get_strv("enabled-extensions")
    disabled_extensions = _shell_settings.get_strv("disabled-extensions")
    for extension in enabled:
        if extension not in enabled_extensions:
            return False
    for extension in disabled:
        if extension in enabled_extensions and extension not in disabled_extensions:
            return False
    return True


def set_panel_settings(settings):
    for key in settings:
        if key in _monitor_specific_panel_settings:
            set_monitor_specific_panel_setting(key, settings[key])
        else:
            _panel_settings.set_value(key, settings[key])


def check_panel_settings(settings):
    for key in settings:
        if key in _monitor_specific_panel_settings:
            if not check_monitor_specific_panel_setting(key, settings[key]):
                return False
        else:
            if _panel_settings.get_value(key) != settings[key]:
                return False
    return True


def set_dock_settings(settings):
    for key in settings:
        _dock_settings.set_value(key, settings[key])


def check_dock_settings(settings):
    for key in settings:
        if _dock_settings.get_value(key) != settings[key]:
            return False
    return True


def set_arc_settings(settings):
    for key in settings:
        _arc_settings.set_value(key, settings[key])


def check_arc_settings(settings):
    for key in settings:
        if _arc_settings.get_value(key) != settings[key]:
            return False
    return True


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
    settings = json.loads(_panel_settings.get_string(key))
    for monitor in settings:
        if settings[monitor] != value:
            return False
    return True


def set_monitor_specific_panel_setting(key, value):
    settings = json.loads(_panel_settings.get_string(key))
    for monitor in settings:
        settings[monitor] = value
    _panel_settings.set_string(key, json.dumps(settings))


def set_layout_from_dict(layout: dict):
    # Figure out extensions to enable and disable
    if "panel" in layout:
        set_panel_settings(layout["panel"])

    if "dock" in layout:
        set_dock_settings(layout["dock"])

    if "arc" in layout:
        set_arc_settings(layout["arc"])

    set_extensions(layout["enabled_extension"], layout["disabled_extension"])

    if "gsettings" in layout:
        set_gsettings(layout["gsettings"])


def set_layout(layout: str):
    json_file = f"{_LAYOUTS_UI}/{layout}.json"

    if os.path.exists(json_file):
        with open(json_file, "r") as file:
            set_layout_from_dict(layout_as_dict(file.read()))
    else:
        raise FileNotFoundError(f"Layout file {json_file} not found in {_LAYOUTS_UI} directory")


def layout_as_dict(json_str: str):
    layout = json.loads(json_str)

    for d in ["enabled_extension", "disabled_extension"]:
        if d not in layout:
            layout[d] = []

    if "panel" in layout:
        layout["enabled_extension"].append("dash-to-panel@jderose9.github.com")
    else:
        layout["disabled_extension"].append("dash-to-panel@jderose9.github.com")

    if "dock" in layout:
        layout["enabled_extension"].append("dash-to-dock@micxgx.gmail.com")
    else:
        layout["disabled_extension"].append("dash-to-dock@micxgx.gmail.com")

    if "arc" in layout:
        layout["enabled_extension"].append("arcmenu@arcmenu.com")
    else:
        layout["disabled_extension"].append("arcmenu@arcmenu.com")
    return layout


def check_layout_dict(layout: dict):
    if not check_extensions(layout["enabled_extension"], layout["disabled_extension"]):
        return False

    if "panel" in layout:
        if not check_panel_settings(layout["panel"]):
            return False

    if "dock" in layout:
        if not check_dock_settings(layout["dock"]):
            return False

    if "arc" in layout:
        if not check_arc_settings(layout["arc"]):
            return False

    if "gsettings" in layout:
        if not check_gsettings(layout["gsettings"]):
            return False

    return True


def get_current_layout():
    for layout in os.listdir(_LAYOUTS_UI):
        if layout.endswith(".json"):
            with open(f"{_LAYOUTS_UI}/{layout}", "r") as file:
                if check_layout_dict(layout_as_dict(file.read())):
                    return layout.replace(".json", "")
    return "custom"


def get_available_layouts() -> list(str):
    layouts = []
    for layout in os.listdir(_LAYOUTS_UI):
        if layout.endswith(".json"):
            layouts.append(layout.replace(".json", ""))
    return layouts
