# Tool to create a layout from the current GNOME setup.
import json
from gi.repository import Gio, GLib


_type_strings = ["b", "y", "n", "q", "i", "u", "x", "t", "d", "s", "as", "ay"]
def serialize_setting(setting, key):
    value = setting.get_value(key)
    if value.get_type_string() in _type_strings:
        return value.unpack()
    else: # Serialize as bytes
        return value.print_(True)


shell_settings = Gio.Settings.new("org.gnome.shell")

panel_settings = Gio.Settings.new("org.gnome.shell.extensions.dash-to-panel")
panel_exclude = [
    "available-monitors"
]
panel_monitor_keys = [
    "panel-anchors", "panel-element-positions",
    "panel-lengths", "panel-positions", "panel-sizes"
]

dock_settings = Gio.Settings.new("org.gnome.shell.extensions.dash-to-dock")
dock_exclude = [
    "preferred-monitor",
    "preferred-monitor-by-connector"
]
arc_settings = Gio.Settings.new("org.gnome.shell.extensions.arcmenu")
arc_exclude = [
    "application-shortcuts",
    "pinned-apps",
]
panel_layouts = [
    'Default',
    'Brisk',
    'Whisker',
    'GnomeMenu',
    'Mint',
    'Elementary',
    'GnomeOverview',
    'Redmond',
    'Unity',
    'Budgie',
    'Insider',
    'Runner',
    'Chromebook',
    'Raven',
    'Tognee',
    'Plasma',
    'Windows',
    'Eleven',
    'AZ',
    'Enterprise',
    'Pop',
    'Sleek'
]


def get_panel_monitor_setting(key):
    settings = json.loads(panel_settings.get_string(key))
    return settings[list(settings)[0]]


layout_dict = {}

layout_name = input("Set name: ")
layout_dict["name"] = layout_name

enabled_extensions = shell_settings.get_strv("enabled-extensions")

if "dash-to-panel@jderose9.github.com" in enabled_extensions:
    layout_dict["panel"] = {}
    for key in panel_settings.props.settings_schema.list_keys():
        if key not in panel_exclude and not panel_settings.get_value(key).equal(panel_settings.get_default_value(key)):
            if key in panel_monitor_keys:
                try:
                    layout_dict["panel"][key] = get_panel_monitor_setting(key)
                except:
                    print("Skipping panel key: " + key)
                    layout_dict["panel"][key] = {}
                    print("value:\n" + panel_settings.get_string(key) + "\n")
            else:
                layout_dict["panel"][key] = serialize_setting(panel_settings, key)

if "dash-to-dock@micxgx.gmail.com" in enabled_extensions:
    layout_dict["dock"] = {}
    for key in dock_settings.props.settings_schema.list_keys():
        if key not in dock_exclude and not dock_settings.get_value(key).equal(dock_settings.get_default_value(key)):
            layout_dict["dock"][key] = serialize_setting(dock_settings, key)

if "arcmenu@arcmenu.com" in enabled_extensions:
    layout_dict["arc"] = {}
    for key in arc_settings.props.settings_schema.list_keys():
        if key not in arc_exclude and not arc_settings.get_value(key).equal(arc_settings.get_default_value(key)):
            layout_dict["arc"][key] = serialize_setting(arc_settings, key)


filename = f"{layout_name.replace(" ", "_").lower()}.json"
with open(filename, "w") as f:
    json.dump(layout_dict, f, indent=4)
    print(f"Layout saved to {filename}")
