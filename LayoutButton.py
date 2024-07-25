import os
import gi

import LayoutManager

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject, Gio, GLib

import constants

json_dir = os.path.join(constants.MAIN_DIR, "layouts")
preview_dir = os.path.join(constants.MAIN_DIR, "data", "layout_previews")

@Gtk.Template(filename=os.path.join(constants.UI_DIR, "LayoutButton.ui"))
class LayoutButton(Gtk.Box):
    __gtype_name__ = "LayoutButton"
    preview = Gtk.Template.Child()
    label = Gtk.Template.Child()
    check = Gtk.Template.Child()

    def __init__(self, layout_name, layout_id, last_button: None):
        super().__init__()
        self.layout_name = layout_name
        self.layout_id = layout_id

        if os.path.exists(os.path.join(preview_dir, f"{layout_id}.svg")):
            self.preview.set_from_file(os.path.join(preview_dir, f"{layout_id}.svg"))
        else:
            self.preview.set_from_icon_name("dialog-question-symbolic")

        self.label.set_label(layout_name)
        if last_button:
            self.check.set_group(last_button.check)
