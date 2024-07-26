import os
import gi

import LayoutManager

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk, GObject, Gio, GLib

import constants

layout_dir = os.path.join(constants.MAIN_DIR, "layouts")
preview_dir = os.path.join(layout_dir, "previews")

@Gtk.Template(filename=os.path.join(constants.UI_DIR, "LayoutButton.ui"))
class LayoutButton(Adw.Bin):
    __gtype_name__ = "LayoutButton"
    preview: Gtk.Picture = Gtk.Template.Child()
    label: Gtk.Label = Gtk.Template.Child()
    check: Gtk.CheckButton = Gtk.Template.Child()

    def __init__(self, layout_name, layout_id, last_button: None):
        super().__init__()
        self.layout_name = layout_name
        self.layout_id = layout_id

        self.preview.set_content_fit(Gtk.ContentFit.SCALE_DOWN)
        if os.path.exists(os.path.join(preview_dir, f"{layout_id}.svg")):
            self.preview.set_filename(os.path.join(preview_dir, f"{layout_id}.svg"))
            #else:
            #self.preview.set_from_icon_name("dialog-question-symbolic")

        print(layout_name)
        self.label.set_label(layout_name)
        if last_button:
            self.check.set_group(last_button.check)
