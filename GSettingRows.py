import os

import constants

import gi
gi.require_version("Gtk", "4.0")
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
        self.settings = Gio.Settings.new(self._schema)
        self.settings.connect("changed", self.setting_changed)

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
    update_settings = True

    def __init__(self):
        super().__init__(self)
        GSetting.__init__(self)
        self.set_active(self.settings.get_boolean(self._key))
        self.connect("notify::active", self.switch_changed)

    def switch_changed(self, _switch_row, active):
        if self.update_settings:
            self.settings.set_boolean(self._key, active)

    def setting_changed(self, settings, key):
        self.update_settings = False
        self.set_active(self.settings.get_boolean(self._key))
        self.update_settings = True


@Gtk.Template(filename=os.path.join(constants.UI_DIR, "GSettingsToggleRow.ui"))
class GSettingsToggleRow(Adw.SwitchRow, GSetting):
    __gtype_name__ = "GSettingsToggleRow"
    update_settings = True

    def __init__(self):
        super().__init__(self)
        GSetting.__init__(self)
        self.set_active(self.settings.get_boolean(self._key))
        self.connect("notify::active", self.switch_changed)

    def switch_changed(self, _switch_row, active):
        if self.update_settings:
            self.settings.set_boolean(self._key, active)

    def setting_changed(self, settings, key):
        self.update_settings = False
        self.set_active(self.settings.get_boolean(self._key))
        self.update_settings = True
