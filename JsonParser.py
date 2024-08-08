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
extension_conflicts = {}
setting_conflicts = {}
conflicting_settings = []


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


def check_extension_conflicts():
    for ext in extension_conflicts:
        state = ext in _shell_settings.get_strv("enabled-extensions")
        for conflict in extension_conflicts[ext]:
            widget, message, default_subtitle, fix, gsetting = conflict
            if state:
                if not message:
                    widget.set_visible(False)
                widget.set_sensitive(False)
                widget.set_subtitle(message)
                if fix is not None and gsetting is not None:
                    if Utils.serialize_setting(gsetting.settings, gsetting.key) != fix:
                        Utils.set_unknown_type(gsetting.settings, gsetting.key, fix)
                break

            widget.set_visible(True)
            widget.set_sensitive(True)
            widget.set_subtitle(default_subtitle)


def check_setting_conflicts(settings, _key, *args):
    print("checking setting conflict")
    for conflict in setting_conflicts[settings.props.schema_id]:
        key, value, widget, message, default_subtitle, fix, gsetting = conflict
        is_broken = Utils.serialize_setting(settings, key) == value
        if is_broken:
            if not message:
                widget.set_visible(False)
            widget.set_sensitive(False)
            widget.set_subtitle(message)
            if fix is not None and gsetting is not None:
                if Utils.serialize_setting(gsetting.settings, gsetting.key) != fix:
                    Utils.set_unknown_type(gsetting.settings, gsetting.key, fix)
            break

        widget.set_visible(True)
        widget.set_sensitive(True)
        widget.set_subtitle(default_subtitle)


def extensions_changed(dbus_proxy, sender, signal, params):
    uuid = params[0]
    state = params[1]["enabled"]
    if uuid in requires_extension:
        for widget in requires_extension[uuid]:
            widget.set_visible(state)
    check_extension_conflicts()


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

                # Extra Flags for GSetting Group
                if data[group_name].get("requires_extension"):
                    extension_uuid = data[group_name]["requires_extension"]
                    if extension_uuid not in requires_extension:
                        requires_extension[extension_uuid] = []
                    requires_extension[extension_uuid].append(group)

                # Adding items to GSetting Groups
                # Case statement links to type.
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


                    # Extra flags for settings:
                    if setting.get("extension_conflicts"):
                        for item in setting["extension_conflicts"]:
                            uuid = item.get("uuid")
                            message = item.get("message")
                            fix = item.get("fix")

                            if uuid not in extension_conflicts:
                                extension_conflicts[uuid] = []

                            if not gsetting:
                                gsetting = None

                            extension_conflicts[uuid].append(
                                (setting_widget, message, setting_widget.get_subtitle(), fix, gsetting)
                            )

                    if setting.get("setting_conflicts"):
                        for item in setting["setting_conflicts"]:
                            schema = item["schema"]
                            settings = Gio.Settings.new(schema)
                            key = item["key"]
                            value = item["value"]
                            message = item.get("message")
                            fix = item.get("fix")

                            if schema not in setting_conflicts:
                                setting_conflicts[schema] = []

                            setting_conflicts[schema].append(
                                (key, value, setting_widget, message, setting_widget.get_subtitle(), fix, gsetting)
                            )
                            if schema not in conflicting_settings:
                                conflicting_settings.append(schema)
                                settings.connect(f"changed", check_setting_conflicts)

                    if setting.get("extension_required"):
                        if setting["extension_required"] not in requires_extension:
                            requires_extension[setting["extension_required"]] = []
                        requires_extension[setting["extension_required"]].append(setting_widget)

    set_extension_widget_visibility_all()
    check_extension_conflicts()

    for setting in setting_conflicts.keys():
        check_setting_conflicts(Gio.Settings.new(setting), None, schema)

