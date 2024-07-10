import constants
import gi
import os

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw


class StillControl(Adw.Application):
    def __init__(self):
        super().__init__(application_id="io.stillhq.stillControl")

        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(constants.UI_DIR, "stillControl.ui"))

        self.main_window = self.builder.get_object("main_window")
        # self.connect("activate", self.do_activate)

    def do_activate(self):
        self.main_window.set_application(self)
        self.main_window.present()