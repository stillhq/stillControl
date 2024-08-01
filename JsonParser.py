import timeit

from constants import UI_DIR
import json
import os
import threading

import Utils
from __init__ import GSetting  # FIXME: Change this to absolute import
import GSettingCustomComboFunctions

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib

_SETTING_JSON_DIR = os.path.join(UI_DIR, "settings")
_shell_settings = Gio.Settings.new("org.gnome.shell")
_extension_proxy = Utils.ExtensionProxy()
requires_extension = {}


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


def set_extension_widget_visibility_all():
    extensions_to_check = list(requires_extension.keys())
    extensions = _extension_proxy.get_extensions()
    for extension_uuid in extensions.keys():
        if extension_uuid in extensions_to_check:
            visible = extensions[extension_uuid]["enabled"]
            for widget in requires_extension[extension_uuid]:
                widget.set_visible(visible)
            extensions_to_check.remove(extension_uuid)
    for extension_uuid in extensions_to_check:
        for widget in requires_extension[extension_uuid]:
            widget.set_visible(False)


def extensions_changed(dbus_proxy, sender, signal, params):
    uuid = params[0]
    state = params[1]["enabled"]
    if uuid in requires_extension:
        for widget in requires_extension[uuid]:
            widget.set_visible(state)

_extension_proxy.proxy.connect("g-signal::ExtensionStateChanged", extensions_changed)


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
                    extension_uuid = data[group_name]["requires_extension"]
                    if extension_uuid not in requires_extension:
                        requires_extension[extension_uuid] = []
                    requires_extension[extension_uuid].append(group)
                for setting in data[group_name]["items"]:
                    setting_type = setting["type"]
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
                                item_function = GSettingCustomComboFunctions.function_ids[setting["python_options"]]
                                displays, values, display_subtitles = item_function()
                            else:
                                displays, values, *display_subtitles = parse_options(setting["options"])
                            setting_widget = group.add_combo(gsetting, values, displays)
                        case "detailed-combo":
                            gsetting = GSetting.from_dict(setting["gsetting"])
                            if setting.get("python_options"):
                                item_function = GSettingCustomComboFunctions.function_ids[setting["python_options"]]
                                displays, values, display_subtitles = item_function()
                            else:
                                displays, values, display_subtitles = parse_options(setting["options"])
                            setting_widget = group.add_detailed_combo(gsetting, values, displays, display_subtitles)
                        case "extension-setting-button":
                            subtitle = setting.get("subtitle")
                            icon = setting.get("icon_name")
                            setting_widget = group.add_extension_setting_button(
                                setting["title"], subtitle, icon, setting["extension"]
                            )
                            if setting["extension"] not in requires_extension:
                                requires_extension[setting["extension"]] = []
                            requires_extension[setting["extension"]].append(setting_widget)
                        case "dash-to-panel-monitor-dropdown":
                            gsetting = GSetting.from_dict(setting["gsetting"])
                            if setting.get("python_options"):
                                displays, values, *display_subtitles = function_ids[setting["python_options"]]()
                            else:
                                displays, values, *display_subtitles = parse_options(setting["options"])
                            setting_widget = group.add_dash_to_panel_monitor_dropdown(gsetting, values, displays)
                        case "dash-to-panel-monitor-spin":
                            gsetting = GSetting.from_dict(setting["gsetting"])
                            setting_widget = group.add_dash_to_panel_monitor_spin(
                                gsetting, parse_adjustment(setting["adjustment"])
                            )
                        case _:
                            raise ValueError(f"Unknown setting type {setting_type}")

                    if setting.get("extension_required"):
                        if setting["extension_required"] not in requires_extension:
                            requires_extension[setting["extension_required"]] = []
                        requires_extension[setting["extension_required"]].append(setting_widget)
    set_extension_widget_visibility_all()
