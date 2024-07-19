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

@Gtk.Template(filename=os.path.join(constants.UI_DIR, "ExtensionRow.ui"))
class ExtensionRow(Adw.ExpanderRow):
    __gtype_name__ = "ExtensionRow"

    def __init__(self, extension, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extension_uuid = extension_uuid
        print(self.get_extension_uuid)


def add_extensions_to_group(group: str, system: bool):
    extensions = _proxy.get_extensions()
    for extension in extensions:
        print(extensions[extension])