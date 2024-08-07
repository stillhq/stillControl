import gi
gi.require_version("Gtk", "4.0")

from gi.repository import Gtk # Required for GSettingGroup

import stillControl
import GSettingGroup   # Required to load custom widget in Gtk.Biulder
import JsonParser

if __name__ == "__main__":
    app = stillControl.StillControl()
    JsonParser.parse_json(app.builder)
    app.run()
