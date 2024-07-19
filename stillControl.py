import constants
import gi
import os

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

import ExtensionRow

from __init__ import GSetting  # FIXME: Change this to absolute import


class StillControl(Adw.Application):
    def __init__(self):
        super().__init__(application_id="io.stillhq.Control")

        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(constants.UI_DIR, "stillControl.ui"))

        self.main_window = self.builder.get_object("main_window")
        self.setup_manage_extension_page()
        # self.connect("activate", self.do_activate)

    def setup_manage_extension_page(self):
        ExtensionRow.add_extensions_to_groups(self.builder)



    def do_activate(self):
        self.main_window.set_application(self)
        self.main_window.present()