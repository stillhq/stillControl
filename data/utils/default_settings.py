# Tool to create a layout from the current GNOME setup.
import json
from gi.repository import Gio, GLib

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
arc_keys = [
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
    "context-menu-items",
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
    "menu-foreground-color",
    "menu-height",
    "menu-layout",
    "menu-position-alignment",
    "menu-separator-color",
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


for key in panel_keys:
    panel_settings.reset(key)

for key in dock_keys:
    dock_settings.reset(key)

for key in arc_keys:
    arc_settings.reset(key)
