import enum
import os

import constants

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, GObject, Gtk


class SpinType(enum.Enum):
    INT = 0
    UINT = 1
    DOUBLE = 2




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

    def add_switch(self, gsetting: GSetting):
        row = Adw.SwitchRow(title=gsetting.title, subtitle=gsetting.subtitle)
        if gsetting.icon_name:
            row.set_icon_name(gsetting.icon_name)
        row.set_active(gsetting.settings.get_boolean(gsetting.key))
        row.connect("notify::active", switch_row_changed, gsetting)
        gsetting.settings.connect("changed", switch_setting_changed, row, gsetting)
        self.add(row)

    def add_spin(self, gsetting: GSetting, spin_type, percent, adjustment):
        row = Adw.SpinRow(title=gsetting.title, subtitle=gsetting.subtitle)
        if gsetting.icon_name:
            row.set_icon_name(gsetting.icon_name)

        row.set_adjustment(adjustment)
        if not percent:
            row.set_digits(3)

        spin_setting_changed(
            gsetting.settings, gsetting.key, row, gsetting, spin_type, percent
        )

        row.connect("notify::value", spin_row_changed, gsetting, spin_type, percent)
        gsetting.settings.connect("changed", spin_setting_changed, row, gsetting, spin_type, percent)
        self.add(row)


def switch_row_changed(switch_row, _active, gsetting):
    gsetting.settings.set_boolean(gsetting.key, switch_row.get_active())


def switch_setting_changed(settings, key, switch_row, gsetting):
    if key == gsetting.key:
        if switch_row.get_active() != settings.get_boolean(key):
            switch_row.set_active(settings.get_boolean(key))


def spin_row_changed(spin_row, _value, gsetting, spin_type, percent):
    value = spin_row.get_value()
    if percent:
        value /= 100

    match spin_type:
        case SpinType.INT:
            gsetting.settings.set_int(gsetting.key, value)
        case SpinType.UINT:
            gsetting.settings.set_uint(gsetting.key, value)
        case SpinType.DOUBLE:
            gsetting.settings.set_double(gsetting.key, value)


def spin_setting_changed(settings, key, spin_row, gsetting, spin_type, percent):
    if key == gsetting.key:
        match spin_type:
            case SpinType.INT:
                new_value = settings.get_int(key)
            case SpinType.UINT:
                new_value = settings.get_uint(key)
            case SpinType.DOUBLE:
                new_value = settings.get_double(key)

        if spin_row.get_value() != float(new_value):
            if percent:
                new_value *= 100
            spin_row.set_value(new_value)

