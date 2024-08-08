import json
import os

from gi.repository import Gio, GLib

import constants, Utils

_LAYOUTS_UI = os.path.join(os.path.dirname(__file__), "layouts")
_monitor_specific_panel_settings = [
    "panel-anchors", "panel-element-positions",
    "panel-lengths", "panel-positions", "panel-sizes"
]


def import_settings(schema):
    setting = Gio.Settings.new(schema)
    setting.delay()
    return setting


_shell_settings = import_settings("org.gnome.shell")
_panel_settings = import_settings("org.gnome.shell.extensions.dash-to-panel")

_extension_settings = {  # Panel settings not included, needs to be treated separate due to monitor specific settings
    "dash-to-dock@micxgx.gmail.com": import_settings("org.gnome.shell.extensions.dash-to-dock"),
    "arcmenu@arcmenu.com": import_settings("org.gnome.shell.extensions.arcmenu"),
    "just-perfection-desktop@just-perfection": import_settings("org.gnome.shell.extensions.just-perfection"),
    #"gtk4-ding@smedius.github.com": import_settings("org.gnome.shell.extensions.gtk4-ding")
}


def get_settings_list():
    settings = [_panel_settings]
    for ext in _extension_settings:
        if _extension_settings[ext]:
            settings.append(_extension_settings[ext])
    return settings


def apply_settings():
    settings = get_settings_list()
    settings.append(_shell_settings)
    for setting in settings:
        setting.apply()


def set_extensions(to_enable, to_disable):
    enabled_extensions = _shell_settings.get_strv("enabled-extensions")
    disabled_extensions = _shell_settings.get_strv("disabled-extensions")
    for extension in to_disable:
        while extension in enabled_extensions:
            enabled_extensions.remove(extension)
        if extension not in disabled_extensions:
            disabled_extensions.append(extension)
    for extension in to_enable:
        if extension not in enabled_extensions:
            enabled_extensions.append(extension)
        while extension in disabled_extensions:
            disabled_extensions.remove(extension)

    _shell_settings.set_strv("enabled-extensions", enabled_extensions)
    _shell_settings.set_strv("disabled-extensions", disabled_extensions)


def check_extensions(enabled, disabled):
    if not _shell_settings:
        return False
    enabled_extensions = _shell_settings.get_strv("enabled-extensions")
    disabled_extensions = _shell_settings.get_strv("disabled-extensions")
    for extension in enabled:
        if extension not in enabled_extensions or extension in disabled_extensions:
            return False
    for extension in disabled:
        if extension in enabled_extensions and extension not in disabled_extensions:
            return False
    return True


def reset_settings():
    for setting in get_settings_list():
        settings_schema = setting.props.settings_schema
        keys_to_reset = settings_schema.list_keys()

        # check if there's exclusion rules
        if settings_schema.get_id() in constants.SETTINGS_FOR_RESET_EXCLUDE.keys():
            for key in constants.SETTINGS_FOR_RESET_EXCLUDE[settings_schema.get_id()]:
                while key in keys_to_reset:
                    keys_to_reset.remove(key)
        for key in keys_to_reset:
            setting.reset(key)


def set_panel_settings(settings):
    for key in settings:
        if key in _monitor_specific_panel_settings:
            set_monitor_specific_panel_setting(key, settings[key])
        else:
            Utils.set_unknown_type(_panel_settings, key, settings[key])


def check_panel_settings(settings):
    for key in settings:
        if key in _monitor_specific_panel_settings:
            if not check_monitor_specific_panel_setting(key, settings[key]):
                return False
        else:
            if Utils.serialize_setting(_panel_settings, key) != settings[key]:
                return False
    return True


def set_extension_settings(extension_uuid, layout_settings):
    if _extension_settings[extension_uuid]:
        for key in layout_settings:
            Utils.set_unknown_type(_extension_settings[extension_uuid], key, layout_settings[key])


def check_extension_settings(extension_uuid, layout_settings):
    if not _extension_settings[extension_uuid]:
        return True
    settings = _extension_settings[extension_uuid]
    for key in layout_settings:
        if Utils.serialize_setting(settings, key) != layout_settings[key]:
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
    return Utils.serialize_setting(settings, key) == value


def check_gsettings(json):
    for key in json:
        if not check_setting(key, json[key]):
            return False
    return True


def check_monitor_specific_panel_setting(key, value):
    if not _panel_settings:
        return False
    settings = json.loads(_panel_settings.get_string(key))
    for monitor in settings:
        if settings[monitor] != value:
            return False
    return True


def set_monitor_specific_panel_setting(key, value):
    settings = json.loads(_panel_settings.get_string(key))
    if len(settings) != 0:
        for monitor in settings:
            settings[monitor] = value
    else:
        monitors = _panel_settings.get_value("available-monitors").unpack()
        for monitor in monitors:
            settings[str(monitor)] = value

    _panel_settings.set_string(key, json.dumps(settings))

def set_layout_from_dict(layout: dict):
    reset_settings()
    
    # Figure out extensions to enable and disable
    if "dash-to-panel@jderose9.github.com" in layout:
        set_panel_settings(layout["dash-to-panel@jderose9.github.com"])

    for ext in list(_extension_settings.keys()):
        if ext in layout:
            set_extension_settings(ext, layout[ext])

    set_extensions(layout["enabled_extensions"], layout["disabled_extensions"])

    if "gsettings" in layout:
        set_gsettings(layout["gsettings"])

    print(layout)
    apply_settings()


def set_layout(layout: str):
    json_file = f"{_LAYOUTS_UI}/{layout}.json"

    if os.path.exists(json_file):
        with open(json_file, "r") as file:
            set_layout_from_dict(layout_as_dict(file.read()))
    else:
        raise FileNotFoundError(f"Layout file {json_file} not found in {_LAYOUTS_UI} directory")


def layout_as_dict(json_str: str):
    layout = json.loads(json_str)

    for d in ["enabled_extensions", "disabled_extensions"]:
        if d not in layout:
            layout[d] = []

    extensions = ["dash-to-panel@jderose9.github.com"] + list(_extension_settings.keys())
    for extension in extensions:
        if extension in layout:
            layout["enabled_extensions"].append(extension)
        else:
            layout["disabled_extensions"].append(extension)

    return layout


def check_layout_dict(layout: dict):
    if not check_extensions(layout["enabled_extensions"], layout["disabled_extensions"]):
        return False

    if "dash-to-panel@jderose9.github.com" in layout:
        if not check_panel_settings(layout["dash-to-panel@jderose9.github.com"]):
            return False

    for ext in _extension_settings:
        if ext in layout:
            if _extension_settings[ext]:
                check_extension_settings(ext, layout[ext])

    if "gsettings" in layout:
        if not check_gsettings(layout["gsettings"]):
            return False

    return True


def get_layout_name_from_id(layout_id):
    if layout_id == "custom":
        return "Custom"

    with open(f"{_LAYOUTS_UI}/{layout_id}.json", "r") as file:
        layout_dict = layout_as_dict(file.read())
        return layout_dict.get("name")


def get_current_layout():
    for layout in get_available_layouts():
        with open(f"{_LAYOUTS_UI}/{layout}.json", "r") as file:
            if check_layout_dict(layout_as_dict(file.read())):
                return layout.replace(".json", "")
    return "custom"


def get_available_layouts():
    layouts = []
    for layout in os.listdir(_LAYOUTS_UI):
        if layout.endswith(".json"):
            layouts.append(layout.replace(".json", ""))
    return layouts
