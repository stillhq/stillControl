import math
import os
from typing import List

import constants
import gi
import json

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, Gtk, GLib

from __init__ import GSetting # FIXME: Change this to absolute import
import GSettingComboRow


class DashToPanelMonitorComboRow(GSettingComboRow.GSettingComboRow):
    def __init__(self, gsetting: GSetting, values: List[str], display: List[str]):
        super().__init__(gsetting, values, display)

    def get_setting_value(self):
        settings = json.loads(self.gsetting.settings.get_string(self.gsetting.key))
        try:
            return list(settings.values())[0]
        except IndexError: 
            return ""

    def set_setting_value(self, value):
        settings = json.loads(self.gsetting.settings.get_string(self.gsetting.key))
        for monitor in settings:
            settings[monitor] = value
        self.gsetting.settings.set_string(self.gsetting.key, json.dumps(settings))

    def on_setting_changed(self, settings: Gio.Settings, key: str):
        if key == self.gsetting.key:
            current_value = self.get_setting_value()
            if current_value != self.values[self.get_selected()]:
                try:
                    index = self.values.index(current_value)
                except ValueError:
                    self.display_list_store.append(Gtk.StringObject.new(current_value))
                    self.values.append(current_value)
                    self.add_css_class("error")
                    index = len(self.values) - 1
                self.set_selected(index)

    def on_row_changed(self, row: Gtk.ComboBoxText, _selected):
        value_index = row.get_selected()
        if not value_index >= self.original_length:
            while len(self.values) > self.original_length:
                del self.values[-1]
                self.display_list_store.remove(self.display_list_store.get_n_items() - 1)
            self.remove_css_class("error")

        current_value = self.get_setting_value()
        if current_value != self.values[row.get_selected()]:
            self.set_setting_value(self.values[value_index])


def dtp_monitor_spin_setting_changed(settings, key, spin_row, gsetting):
    if key == gsetting.key:
        settings = json.loads(gsetting.settings.get_string(gsetting.key))

        try:
            new_value = list(settings.values())[0]

            if int(spin_row.get_value()) != int(new_value):
                spin_row.set_value(new_value)

        except IndexError: 
            new_value = 0

def dtp_monitor_spin_row_changed(spin_row, _value, gsetting):
    spin_row.set_sensitive(False)
    # Makes the row not sensitive for 0.5 seconds to prevent spamming the setting and causing lag

    value = spin_row.get_value()

    settings = json.loads(gsetting.settings.get_string(gsetting.key))
    for monitor in settings:
        settings[monitor] = math.floor(value)
    gsetting.settings.set_string(gsetting.key, json.dumps(settings))

    # Makes the row sensitive again after 0.5 seconds
    GLib.timeout_add(500, lambda: spin_row.set_sensitive(True))
