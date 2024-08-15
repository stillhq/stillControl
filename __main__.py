import os

import gi
gi.require_version("Gtk", "4.0")

from gi.repository import Gtk  # Required for GSettingGroup, removing unused import will break code
from gi.repository import Gio

import stillControl
import GSettingGroup   # Required to load custom widget in Gtk.Builder
import JsonParser
import constants

if __name__ == "__main__":
    resource = Gio.resource_load(os.path.join(constants.MAIN_DIR, "data", "io.stillhq.control.gresource"))
    Gio.Resource._register(resource)

    app = stillControl.StillControl()
    JsonParser.parse_json(app.builder)
    app.run()
