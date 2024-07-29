import array
import os
import gi

import LayoutManager

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk, GObject, Gio, GLib, Gdk,GdkPixbuf

import constants

layout_dir = os.path.join(constants.MAIN_DIR, "layouts")
preview_dir = os.path.join(layout_dir, "previews")

buttons = []

def refresh_buttons(layout_id):
    for button in buttons:
        button.layout_setting_changed(layout_id)
        button.change_layout = True


@Gtk.Template(filename=os.path.join(constants.UI_DIR, "LayoutButton.ui"))
class LayoutButton(Adw.Bin):
    __gtype_name__ = "LayoutButton"
    change_layout = False
    preview: Gtk.Image = Gtk.Template.Child()
    label: Gtk.Label = Gtk.Template.Child()
    check: Gtk.CheckButton = Gtk.Template.Child()

    def __init__(self, layout_id, last_button: None):
        super().__init__()
        buttons.append(self)
        self.layout_name = LayoutManager.get_layout_name_from_id(layout_id)
        self.layout_id = layout_id
        self.svg_path = os.path.join(preview_dir, f"{layout_id}.svg")
        self.style_manager = Adw.StyleManager.get_default()

        self.style_manager.connect("notify::dark", lambda _style,_dark: self.set_image())

        if layout_id == "custom":
            self.set_sensitive(False)
            self.check.set_sensitive(False)

        self.set_image()
        self.label.set_label(self.layout_name)
        if last_button:
            self.check.set_group(last_button.check)

    def set_image(self):
        if os.path.exists(self.svg_path):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.svg_path)
            # Invert colors for dark mode, otherwise keep it for light
            if self.style_manager.get_dark():
                pixbuf = invert_pixbuf(pixbuf)
            self.preview.set_from_paintable(Gdk.Texture.new_for_pixbuf(pixbuf))
        else:
            print(self.svg_path)
            self.preview.set_from_icon_name("dialog-question-symbolic")
            self.preview.set_pixel_size(72)

        self.check.connect("toggled", self.toggled)

    def toggled(self, _check_button):
        if self.change_layout and self.check.get_active() and self.layout_id != "custom":
            LayoutManager.set_layout(self.layout_id)

    def layout_setting_changed(self, layout_id):
        self.change_layout = False
        if layout_id == self.layout_id:
            self.check.set_active(True)


def invert_pixbuf(pixbuf):
    # Get the dimensions and number of channels
    width = pixbuf.get_width()
    height = pixbuf.get_height()
    channels = pixbuf.get_n_channels()

    # Get the pixel data as a Python array
    pixels = pixbuf.get_pixels()
    arr = array.array('B', pixels)

    # Invert the colors
    for i in range(0, len(arr), channels):
        arr[i] = 255 - arr[i]     # Red
        arr[i+1] = 255 - arr[i+1] # Green
        arr[i+2] = 255 - arr[i+2] # Blue
        # If there's an alpha channel, leave it unchanged

    # Create a new pixbuf with the inverted data
    inverted_pixbuf = GdkPixbuf.Pixbuf.new_from_data(
        arr.tobytes(),
        GdkPixbuf.Colorspace.RGB,
        pixbuf.get_has_alpha(),
        8,
        width,
        height,
        pixbuf.get_rowstride()
    )

    return inverted_pixbuf
