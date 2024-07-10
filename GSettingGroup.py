import os

import constants

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, GObject, Gtk


class GSetting(GObject.GObject):
    __gtype_name__ = "GSetting"
    _title = ""
    _subtitle = ""
    _icon_name = None
    _schema = ""
    _key = ""
    settings = None

    @GObject.Property(type=str)
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @GObject.Property(type=str)
    def subtitle(self):
        return self._subtitle

    @subtitle.setter
    def subtitle(self, value):
        self._subtitle = value

    @GObject.Property(type=str)
    def icon_name(self):
        return self._icon_name

    @icon_name.setter
    def icon_name(self, value):
        self._icon_name = value

    @GObject.Property(type=str)
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, value):
        self._schema = value
        self.settings = Gio.Settings.new(self._schema)

    @GObject.Property(type=str)
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        self._key = value


@Gtk.Template(filename=os.path.join(constants.UI_DIR, "GSettingsGroup.ui"))
class GSettingsGroup(Adw.PreferencesGroup):
    __gtype_name__ = "GSettingsGroup"

    def add_boolean(self, gsetting: GSetting):
        switch_row = Adw.SwitchRow(title=gsetting.title, subtitle=gsetting.subtitle)
        if gsetting.icon_name:
            switch_row.set_icon_name(gsetting.icon_name)
        switch_row.set_active(gsetting.settings.get_boolean(gsetting.key))
        switch_row.connect("notify::active", boolean_row_changed, gsetting)
        gsetting.settings.connect("changed", boolean_setting_changed, switch_row, gsetting)
        self.add(switch_row)


def boolean_row_changed(switch_row, _active, gsetting):
    gsetting.settings.set_boolean(gsetting.key, switch_row.get_active())


def boolean_setting_changed(settings, key, switch_row, gsetting):
    if key == gsetting.key:
        if switch_row.get_active() != settings.get_boolean(key):
            switch_row.set_active(settings.get_boolean(key))
