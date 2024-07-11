import os
from typing import List

import constants
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, Gtk

from __init__ import GSetting # FIXME: Change this to absolute import


class GSettingDetailedComboRow(Adw.ExpanderRow):
    def __init__(self, gsetting: GSetting, values, display, display_subtitles):
        self.gsetting = gsetting
        assert len(values) == len(display)
        assert len(display) == len(display_subtitles)

        super().__init__(title=self.gsetting.title)
        self.values = values
        self.display = display
        self.display_subtitles = display_subtitles

        self.items = []
        self.radio_group = None

        self.original_length = len(values)
        for i in range(len(self.values)):
            self.add_item(self.values[i], self.display[i], self.display_subtitles[i])

    def add_item(self, value, display, display_subtitle):
        item = DetailedDropdownItem(
            value, display, display_subtitle, self,
            self.items[-1] if self.items else None
        )
        self.items.append(item)
        self.add_row(item)
        return item

    def item_clicked(self, item):
        self.gsetting.settings.set_string(self.gsetting.key, item.value)
        self.set_subtitle(item.display)

    def get_selected_item(self):
        for item in self.items:
            if item.radio.get_active():
                return item

    def on_setting_changed(self, settings: Gio.Settings, key: str):
        if key == self.gsetting.key:
            if settings.get_string(key) != self.get_selected_item().value:
                current_value = settings.get_string(key)
                item_not_found = True
                for item in self.items:
                    if item.value == current_value:
                        item_not_found = False
                        item.radio.set_active(True)
                        self.set_subtitle(item.title)
                        break
                if len(self.items) >= self.original_length:
                    for item in self.items[self.original_length:]:
                        if not item.radio.get_active():
                            self.remove(item)
                if item_not_found:
                    item = self.add_item(current_value, current_value, current_value)
                    item.add_css_class("error")
                    item.radio.set_active(True)


class DetailedDropdownItem(Adw.ActionRow):
    def __init__(self, value, display, display_subtitle, parent_row, last_widget):
        super().__init__(title=display)
        self.value = value
        self.display = display
        self.display_subtitle = display_subtitle
        self.parent_row = parent_row
        self.last_widget = last_widget

        self.set_subtitle(self.display_subtitle)

        self.radio = Gtk.CheckButton()
        self.radio.set_halign(Gtk.Align.END)
        if last_widget is not None:
            self.radio.set_group(last_widget.radio)
        if parent_row.gsetting.settings.get_string(parent_row.gsetting.key) == self.value:
            self.radio.set_active(True)
            parent_row.set_subtitle(display)
        self.add_suffix(self.radio)
        self.set_activatable(True)
        self.set_activatable_widget(self.radio)

        self.connect("activated", self.on_clicked)

    def on_clicked(self, widget):
        self.parent_row.item_clicked(self)
