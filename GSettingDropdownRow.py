import os
from typing import List

import constants
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, Gtk

from . import GSetting

class ComboRow(Adw.ComboRow):
    def __init__(self, gsetting: GSetting, display: List[str], values: List[str])
        super().__init__(title=gsetting.title, subtitle=gsetting.subtitle)
        if gsetting.icon_name:
            self.set_icon_name(gsetting.icon_name)

        self.display = display
        self.values = values

        values_list_store = Gio.ListStore()
        for value in values:
            values_list_store.append(Gio.Variant.new_string(value))
        self.set_model()