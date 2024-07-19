import constants
import gi
import os

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

from __init__ import GSetting  # FIXME: Change this to absolute import


class StillControl(Adw.Application):
    def __init__(self):
        super().__init__(application_id="io.stillhq.stillControl")

        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(constants.UI_DIR, "stillControl.ui"))

        self.main_window = self.builder.get_object("main_window")
        self.setup_manage_extension_page()
        # self.connect("activate", self.do_activate)

    def setup_manage_extension_page(self):
        self.extension_group = self.builder.get_object("extension_group")
        third_party_extensions = self.extension_group.add_switch_inverse(
            GSetting(
                title="Enable Third Party Extensions",
                subtitle="Third party extensions are not supported by stillOS and may cause unforeseen issues. stillOS modifies GNOME Shell, so not every extension will work properly.",
                schema="org.gnome.shell", key="disable-user-extensions"
            )
        )
        system_extensions = self.extension_group.add_switch(
            GSetting(
                title="Show System Extensions",
                subtitle="These extensions are used by stillOS's UI. Disabling them may cause problems.",
                schema="io.stillhq.control", key="show-system-extensions"
            )
        )
        third_party_warning_image = Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
        third_party_warning_image.add_css_class("warning")
        system_extensions_warning_image = Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
        system_extensions_warning_image.add_css_class("warning")
        system_extensions.add_prefix(system_extensions_warning_image)
        third_party_extensions.add_prefix(third_party_warning_image)



    def do_activate(self):
        self.main_window.set_application(self)
        self.main_window.present()