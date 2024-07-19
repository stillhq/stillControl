from constants import UI_DIR
import json
import os

from __init__ import GSetting  # FIXME: Change this to absolute import

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

_SETTINGS_JSON = os.path.join(UI_DIR, "settings.json")


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
    with open(_SETTINGS_JSON, "r") as file:
        data = json.load(file)

    for group_name in data:
        group = builder.get_object(group_name)
        for setting in data[group_name]:
            setting_type = setting["type"]
            gsetting = GSetting.from_dict(setting["gsetting"])
            match setting_type:
                case "switch":
                    group.add_switch(gsetting)
                case "switch-inverse":
                    group.add_switch_inverse(gsetting)
                case "spin":
                    group.add_spin(
                        gsetting, setting["spin_type"], setting["percent"],
                        parse_adjustment(setting["adjustment"])
                    )
                case "font":
                    group.add_font(gsetting)
                case "combo":
                    if setting.get("python_options"):
                        displays, values, _display_subtitles = function_ids[setting["python_options"]]()
                    else:
                        displays, values, _display_subtitles = parse_options(setting["options"])
                    group.add_combo(gsetting, values, displays)
                case "detailed_combo":
                    if setting.get("python_options"):
                        displays, values, display_subtitles = function_ids[setting["python_options"]]()
                    else:
                        displays, values, display_subtitles = parse_options(setting["options"])
                    group.add_detailed_combo(gsetting, values, displays, display_subtitles)
