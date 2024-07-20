import constants
import gi
import os

from ExtensionSearchPage import ExtensionSearchPage

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

import ManageExtensionsPage

from __init__ import GSetting  # FIXME: Change this to absolute import


class StillControl(Adw.Application):
    def __init__(self):
        super().__init__(application_id="io.stillhq.Control")

        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(constants.UI_DIR, "stillControl.ui"))

        self.main_window = self.builder.get_object("main_window")
        self.setup_extension_page()
        # self.connect("activate", self.do_activate)

    def setup_extension_page(self):
        ManageExtensionsPage.set_builder(self.builder)
        ManageExtensionsPage.add_extensions_to_groups()
        self.builder.get_object("install_extensions_clamp").set_child(
            ExtensionSearchPage(self.builder, ManageExtensionsPage._proxy)
        )





    def do_activate(self):
        self.main_window.set_application(self)
        self.main_window.present()