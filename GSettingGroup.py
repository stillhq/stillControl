import enum
import os
from typing import List

import constants

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk, Pango

from GSettingDetailedComboRow import GSettingDetailedComboRow
from GSettingComboRow import GSettingComboRow

from __init__ import GSetting  # FIXME: Change this to absolute import


class SpinType(enum.Enum):
    INT = 0
    UINT = 1
    DOUBLE = 2


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
        return row

    def add_switch_inverse(self, gsetting: GSetting):
        row = Adw.SwitchRow(title=gsetting.title, subtitle=gsetting.subtitle)
        if gsetting.icon_name:
            row.set_icon_name(gsetting.icon_name)
        row.set_active(not gsetting.settings.get_boolean(gsetting.key))
        row.connect("notify::active", switch_inverse_row_changed, gsetting)
        gsetting.settings.connect("changed", switch_inverse_setting_changed, row, gsetting)
        self.add(row)
        return row

    def add_extension_switch(self, gsetting: GSetting, uuid: str):
        row = Adw.SwitchRow(title=gsetting.title, subtitle=gsetting.subtitle)
        if gsetting.icon_name:
            row.set_icon_name(gsetting.icon_name)
        row.set_active()
        row.connect("notify::active", extension_switch_row_changed, gsetting)
        gsetting.settings.connect("changed", extension_changed, row, gsetting)
        self.add(row)
        return row

    def add_spin(self, gsetting: GSetting, spin_type, percent, adjustment):
        row = Adw.SpinRow(title=gsetting.title, subtitle=gsetting.subtitle)
        if gsetting.icon_name:
            row.set_icon_name(gsetting.icon_name)

        if type(spin_type) is str:
            spin_type = SpinType[spin_type.upper()]

        row.set_adjustment(adjustment)
        if not percent:
            row.set_digits(2)

        spin_setting_changed(
            gsetting.settings, gsetting.key, row, gsetting, spin_type, percent
        )

        row.connect("notify::value", spin_row_changed, gsetting, spin_type, percent)
        gsetting.settings.connect("changed", spin_setting_changed, row, gsetting, spin_type, percent)
        self.add(row)
        return row

    def add_font(self, gsetting: GSetting):
        row = Adw.ActionRow(title=gsetting.title, subtitle=gsetting.subtitle, activatable=True)
        if gsetting.icon_name:
            row.set_icon_name(gsetting.icon_name)

        font_dialog = Gtk.FontDialog()

        font_button = Gtk.FontDialogButton.new(font_dialog)
        font_button.set_use_font(True)
        font_button.set_use_size(True)
        # font_button.add_css_class("flat")
        font_button.set_valign(Gtk.Align.CENTER)
        set_font_button(font_button, gsetting.settings.get_string(gsetting.key))

        font_button.connect("notify::font-desc", font_row_changed, gsetting)
        gsetting.settings.connect("changed", font_setting_changed, font_button, gsetting)

        row.add_suffix(font_button)
        row.set_activatable_widget(font_button)
        self.add(row)
        return row

    def add_combo(self, gsetting: GSetting, values: List, display: List):
        row = GSettingComboRow(gsetting, values, display)
        self.add(row)
        return row

    def add_detailed_combo(self, gsetting: GSetting, values: List, display: List, display_subtitles: List):
        row = GSettingDetailedComboRow(gsetting, values, display, display_subtitles)
        self.add(row)
        return row


def switch_row_changed(switch_row, _active, gsetting):
    gsetting.settings.set_boolean(gsetting.key, switch_row.get_active())


def switch_setting_changed(settings, key, switch_row, gsetting):
    if key == gsetting.key:
        if switch_row.get_active() != settings.get_boolean(key):
            switch_row.set_active(settings.get_boolean(key))


def switch_inverse_row_changed(switch_row, _active, gsetting):
    gsetting.settings.set_boolean(gsetting.key, not switch_row.get_active())


def switch_inverse_setting_changed(settings, key, switch_row, gsetting):
    if key == gsetting.key:
        if switch_row.get_active() == settings.get_boolean(key):
            switch_row.set_active(not settings.get_boolean(key))


def extension_switch_row_changed(switch_row, _active, gsetting):
    if switch_row.get_active():
        if gsetting.key not in gsetting.settings.get_strv("enabled-extensions"):
            gsetting.settings.set_strv(
                "enabled-extensions", gsetting.settings.get_strv("enabled-extensions") + [gsetting.key]
            )
        if gsetting.key in gsetting.settings.get_strv("disabled_extensions"):
            gsetting.settings.set_strv(
                "disabled_extensions", [ext for ext in gsetting.settings.get_strv("disabled_extensions") if ext != gsetting.key]
            )
    else:
        if gsetting.key in gsetting.settings.get_strv("enabled-extensions"):
            gsetting.settings.set_strv(
                "enabled-extensions", [ext for ext in gsetting.settings.get_strv("enabled-extensions") if ext != gsetting.key]
            )


def extension_changed(settings, key, switch_row, extension_uuid):
    toggle = False
    if key == "enabled-extensions" or "disabled_extensions":
        enabled = extension_uuid in settings.get_strv("enabled-extensions")
        not_disabled = extension_uuid not in settings.get_strv("disabled-extensions")
        toggle = enabled and not_disabled
    if switch_row.get_active() != toggle:
        switch_row.set_active(toggle)


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
            case _:
                return

        if percent:
            new_value *= 100

        if spin_row.get_value() != float(new_value):
            spin_row.set_value(new_value)


def set_font_button(button, font):
    font_desc = Pango.FontDescription.from_string(font)
    button.set_font_desc(font_desc)


def font_row_changed(button, _font_desc, gsetting):
    font_desc = button.get_font_desc()
    if gsetting.settings.get_string(gsetting.key) != font_desc.to_string():
        gsetting.settings.set_string(gsetting.key, font_desc.to_string())


def font_setting_changed(settings, key, button, gsetting):
    if key == gsetting.key:
        font_desc = button.get_font_desc()
        if settings.get_string(key) != font_desc.to_string():
            set_font_button(button, settings.get_string(key))
