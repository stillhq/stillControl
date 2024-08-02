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
    "show-windows-preview",
    "show-apps-at-top",
    "show-apps-always-in-the-edge",

]
arc_settings = Gio.Settings.new("org.gnome.shell.extensions.arcmenu")
arc_keys = arc_menu_settings = [
    "activate-on-hover",
    "all-apps-button-action",
    "alphabetize-all-programs",
    "apps-show-extra-details",
    "arcmenu-extra-categories-links",
    "arcmenu-extra-categories-links-location",
    "arcmenu-hotkey",
    "avatar-style",
    "az-layout-extra-shortcuts",
    "brisk-layout-extra-shortcuts",
    "button-item-icon-size",
    "button-padding",
    "category-icon-type",
    "custom-grid-icon-size",
    "custom-menu-button-icon-size",
    "custom-menu-button-text",
    "dash-to-panel-standalone",
    "default-menu-view",
    "default-menu-view-redmond",
    "default-menu-view-tognee",
    "disable-recently-installed-apps",
    "disable-scrollview-fade-effect",
    "disable-tooltips",
    "disable-user-avatar",
    "distro-icon",
    "eleven-disable-frequent-apps",
    "eleven-layout-extra-shortcuts",
    "enable-activities-shortcut",
    "enable-clock-widget-raven",
    "enable-clock-widget-unity",
    "enable-horizontal-flip",
    "enable-unity-homescreen",
    "enable-weather-widget-raven",
    "enable-weather-widget-unity",
    "extra-categories",
    "force-menu-location",
    "gnome-dash-show-applications",
    "hide-overview-on-startup",
    "highlight-search-result-terms",
    "hotkey-open-primary-monitor",
    "insider-layout-extra-shortcuts",
    "left-panel-width",
    "max-search-results",
    "menu-arrow-rise",
    "menu-button-appearance",
    "menu-button-icon",
    "menu-button-left-click-action",
    "menu-button-middle-click-action",
    "menu-button-position-offset",
    "menu-button-right-click-action",
    "menu-font-size",
    "menu-height",
    "menu-layout",
    "menu-position-alignment",
    "menu-width-adjustment",
    "mint-layout-extra-shortcuts",
    "misc-item-icon-size",
    "multi-lined-labels",
    "multi-monitor",
    "override-menu-theme",
    "plasma-enable-hover",
    "pop-default-view",
    "pop-folders-data",
    "position-in-panel",
    "power-display-style",
    "quicklinks-item-icon-size",
    "raven-position",
    "raven-search-display-style",
    "right-panel-width",
    "runner-font-size",
    "runner-hotkey",
    "runner-hotkey-open-primary-monitor",
    "runner-menu-height",
    "runner-menu-width",
    "runner-position",
    "runner-search-display-style",
    "runner-show-frequent-apps",
    "search-entry-border-radius",
    "search-provider-open-windows",
    "search-provider-recent-files",
    "searchbar-default-bottom-location",
    "searchbar-default-top-location",
    "settings-height",
    "settings-width",
    "shortcut-icon-type",
    "show-activities-button",
    "show-bookmarks",
    "show-category-sub-menus",
    "show-external-devices",
    "show-hidden-recent-files",
    "show-search-result-details",
    "sleek-layout-extra-shortcuts",
    "sleek-layout-panel-width",
    "unity-layout-extra-shortcuts",
    "vert-separator",
    "windows-disable-frequent-apps",
    "windows-disable-pinned-apps",
    "windows-layout-extra-shortcuts"
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
    for key in panel_monitor_keys:
        try:
            layout_dict["panel"][key] = get_panel_monitor_setting(key)
        except:
            print("Skipping panel key: " + key)
            layout_dict["panel"][key] = {}
            print("value:\n" + panel_settings.get_string(key) + "\n")
    for key in panel_keys:
        layout_dict["panel"][key] = serialize_setting(panel_settings, key)

if "dash-to-dock@micxgx.gmail.com" in enabled_extensions:
    layout_dict["dock"] = {}
    for key in dock_keys:
        layout_dict["dock"][key] = serialize_setting(dock_settings, key)

if "arcmenu@arcmenu.com" in enabled_extensions:
    current_layout = arc_settings.get_string("menu-layout")
    layout_dict["arc"] = {}
    for key in arc_keys:
        # Make sure layout specifc settings are not included
        commit_key = True
        for layout in panel_layouts:
            if key.startswith(layout.lower()) and layout != current_layout:
                commit_key = False
                break

        if commit_key:
            layout_dict["arc"][key] = serialize_setting(arc_settings, key)

filename = f"{layout_name.replace(" ", "_").lower()}.json"
with open(filename, "w") as f:
    json.dump(layout_dict, f, indent=4)
    print(f"Layout saved to {filename}")
