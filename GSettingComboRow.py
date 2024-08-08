import os
from typing import List

import Utils
import constants
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, Gtk

from __init__ import GSetting # FIXME: Change this to absolute import


class GSettingComboRow(Adw.ComboRow):
    def __init__(self, gsetting: GSetting, values: List[str], display: List[str]):
        self.gsetting = gsetting

        super().__init__(title=self.gsetting.title, subtitle=self.gsetting.subtitle)
        if self.gsetting.icon_name:
            self.set_icon_name(self.gsetting.icon_name)

        self.values = values
        self.original_length = len(values)
        self.display_list_store = Gio.ListStore()

        for display_item in display:
            self.display_list_store.append(Gtk.StringObject.new(str(display_item)))
        self.set_model(self.display_list_store)

        self.on_setting_changed(self.gsetting.settings, self.gsetting.key)

        self.connect("notify::selected", self.on_row_changed)
        self.gsetting.settings.connect("changed", self.on_setting_changed)

    def on_setting_changed(self, settings: Gio.Settings, key: str):
        if key == self.gsetting.key:
            current_value = Utils.serialize_setting(settings, key)
            if current_value != self.values[self.get_selected()]:
                try:
                    index = self.values.index(current_value)
                except ValueError:
                    self.display_list_store.append(Gtk.StringObject.new(str(current_value)))
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

        current_value = Utils.serialize_setting(self.gsetting.settings, self.gsetting.key)
        if current_value != self.values[row.get_selected()]:
            Utils.set_unknown_type(self.gsetting.settings, self.gsetting.key, self.values[value_index])
