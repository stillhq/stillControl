import os

import constants

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, GObject, Gtk


class GSetting(GObject.GObject):
    __gtype_name__ = "GSetting"
    _schema = ""
    _key = ""
    settings = None

    @GObject.Property(type=str)
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, value):
        self._schema = value
        settings = Gio.Settings.new(self._schema)
        settings.connect("changed", self.setting_changed)

    @GObject.Property(type=str)
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        self._key = value

    def setting_changed(self, settings, key):
        raise NotImplementedError("This should be implemented in a GSetting widget")


@Gtk.Template(filename=os.path.join(constants.UI_DIR, "GSettingsToggleRow.ui"))
class GSettingsToggleRow(Adw.SwitchRow, GSetting):
    def __init__(self):
        super().__init__(self)
        GSetting.__init__(self)