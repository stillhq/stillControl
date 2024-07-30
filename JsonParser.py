from constants import UI_DIR
import json
import os

from __init__ import GSetting  # FIXME: Change this to absolute import

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio

_SETTING_JSON_DIR = os.path.join(UI_DIR, "settings")
_shell_settings = Gio.Settings.new("org.gnome.shell")


def legacy_themes_placeholder():
    return (
        ["Adwaita", "Adwaita-dark", "adw-gtk3", "adw-gtk3-dark"],
        ["Adwaita", "Adwaita-dark", "adw-gtk3", "adw-gtk3-dark"],
        ["Adwaita", "Adwaita-dark", "adw-gtk3", "adw-gtk3-dark"]
    )


function_ids = {
    "legacy_themes": legacy_themes_placeholder,
    "icon_themes": legacy_themes_placeholder,
    "cursor_themes": legacy_themes_placeholder
}


def add_function_id(function_id, function):
    function_ids[function_id] = function


def parse_options(data):
    values, displays, display_subtitles = [], [], []
    subtitles = len(data[0]) > 2
    for item in data:
        displays.append(item[0])
        values.append(item[1])
        if subtitles:
            display_subtitles.append(item[2])
    return displays, values, display_subtitles


def extension_specific_setting(setting, key, row, extension_uuid):
    if key == "enabled-extensions":
        row.set_visible(extension_uuid in _shell_settings.get_strv("enabled-extensions"))


def parse_adjustment(data):
    adjustment = Gtk.Adjustment()
    if data.get("lower"):
        adjustment.set_lower(data["lower"])
    if data.get("upper"):
        adjustment.set_upper(data["upper"])
    if data.get("step_increment"):
        adjustment.set_step_increment(data["step_increment"])

    return adjustment


def parse_json(builder):
    for filename in os.listdir(_SETTING_JSON_DIR):
        if filename.endswith('.json'):
            file_path = os.path.join(_SETTING_JSON_DIR, filename)
            with open(file_path, "r") as file:
                data = json.load(file)
            for group_name in data:
                group = builder.get_object(group_name)
                if group is None:
                    raise ValueError(f"Group {group_name} not found in the builder")
                if data[group_name].get("requires_extension"):
                    Gio.Settings.new("org.gnome.shell").connect(
                        "changed", extension_specific_setting, group, data[group_name]["requires_extension"]
                    )
                for setting in data[group_name]["items"]:
                    setting_type = setting["type"]
                    setting_widget = None
                    match setting_type.replace("_", "-"):
                        case "switch":
                            gsetting = GSetting.from_dict(setting["gsetting"])
                            setting_widget = group.add_switch(gsetting)
                        case "switch-inverse":
                            gsetting = GSetting.from_dict(setting["gsetting"])
                            setting_widget = group.add_switch_inverse(gsetting)
                        case "switch-extension":
                            subtitle = setting.get("subtitle")
                            icon = setting.get("icon_name")
                            setting_widget = group.add_extension_switch(setting["title"], subtitle, icon, setting["extension"])
                        case "spin":
                            gsetting = GSetting.from_dict(setting["gsetting"])
                            setting_widget = group.add_spin(
                                gsetting, setting["spin_type"], setting["percent"],
                                parse_adjustment(setting["adjustment"])
                            )
                        case "font":
                            gsetting = GSetting.from_dict(setting["gsetting"])
                            setting_widget = group.add_font(gsetting)
                        case "combo":
                            gsetting = GSetting.from_dict(setting["gsetting"])
                            if setting.get("python_options"):
                                displays, values, *display_subtitles = function_ids[setting["python_options"]]()
                            else:
                                displays, values, *display_subtitles = parse_options(setting["options"])
                            setting_widget = group.add_combo(gsetting, values, displays)
                        case "detailed-combo":
                            gsetting = GSetting.from_dict(setting["gsetting"])
                            if setting.get("python_options"):
                                displays, values, display_subtitles = function_ids[setting["python_options"]]()
                            else:
                                displays, values, display_subtitles = parse_options(setting["options"])
                            setting_widget = group.add_detailed_combo(gsetting, values, displays, display_subtitles)
                        case "extension-setting-button":
                            subtitle = setting.get("subtitle")
                            icon = setting.get("icon_name")
                            setting_widget = group.add_extension_setting_button(
                                setting["title"], subtitle, icon, setting["extension"]
                            )
                            Gio.Settings.new("org.gnome.shell").connect(
                                "changed", extension_specific_setting,
                                setting_widget, setting["extension"]
                            )
                    if setting.get("extension_required"):
                        Gio.Settings.new("org.gnome.shell").connect(
                            "changed", extension_specific_setting,
                            setting_widget, setting["extension"]
                        )
