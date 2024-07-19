import os

import Utils
import constants

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk, Gio

from __init__ import GSetting

_shell_settings = Gio.Settings.new("org.gnome.shell")
_proxy = Utils.ExtensionProxy()
_extension_rows = []


@Gtk.Template(filename=os.path.join(constants.UI_DIR, "ExtensionRow.ui"))
class ExtensionRow(Adw.ExpanderRow):
    __gtype_name__ = "ExtensionRow"

    def __init__(self, extension_info, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _extension_rows.append(self)
        self.extension_info = extension_info
        self.extension_uuid = extension_info["uuid"]
        self.set_title(extension_info["name"])
        self.set_subtitle(extension_info["uuid"])

        self.switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        self.switch.set_active(extension_info["enabled"])
        self.switch.connect("state-set", self.switch_changed)

        if self.extension_info["error"] != "":
            self.add_css_class("error")
            self.set_icon_name("dialog-error-symbolic")
            self.set_subtitle(f"{extension_info["uuid"]}\n\n{extension_info["error"]}")
            self.switch.set_sensitive(False)

        if self.extension_info["hasPrefs"] is True:
            self.button = Gtk.Button.new_from_icon_name("preferences-system-symbolic")
            self.button.set_valign(Gtk.Align.CENTER)
            self.button.add_css_class("circular")
            # self.button.add_css_class("suggested-action")
            self.button.connect("clicked", self.open_prefs)
            self.add_suffix(self.button)

        self.add_suffix(self.switch)

    def switch_changed(self, switch, state):
        if state:
            _proxy.enable_extension(self.extension_uuid)
        else:
            _proxy.disable_extension(self.extension_uuid)

    def open_prefs(self, button):
        _proxy.open_extension_prefs(self.extension_uuid)


def add_extensions_to_groups(builder: Gtk.Builder):
    extensions = _proxy.get_extensions()
    user_group = builder.get_object("user_extensions_group")
    system_group = builder.get_object("system_extensions_group")
    _proxy.set_window(builder.get_object("main_window"))

    # Clear groups
    for row in _extension_rows:
        row.destroy()

    for extension in extensions:
        print(extensions[extension])
        if extensions[extension]["path"].startswith("/usr/share/gnome-shell/extensions/uuid"):
            system_group.add(ExtensionRow(extensions[extension]))
        else:
            user_group.add(ExtensionRow(extensions[extension]))