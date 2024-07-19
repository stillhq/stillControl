import os

import Utils
import constants

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk, Gio, GdkX11

from __init__ import GSetting

_shell_settings = Gio.Settings.new("org.gnome.shell")
_control_settings = Gio.Settings.new("io.stillhq.control")
_proxy = Utils.ExtensionProxy()
_extension_rows = []
_builder = None

@Gtk.Template(filename=os.path.join(constants.UI_DIR, "ExtensionRow.ui"))
class ExtensionRow(Adw.ExpanderRow):
    __gtype_name__ = "ExtensionRow"

    def __init__(self, extension_info, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _extension_rows.append(self)
        self.extension_info = extension_info
        self.extension_uuid = extension_info["uuid"]
        self.system = _proxy.is_system_extension_from_data(extension_info)
        self.set_title(extension_info["name"])
        self.set_subtitle(extension_info["uuid"])
        self.error = self.extension_info["error"] != ""

        self.switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        self.switch.set_active(extension_info["enabled"])
        self.switch.connect("state-set", self.switch_changed)
        self.add_suffix(self.switch)

        if self.error:
            self.add_css_class("error")
            self.set_icon_name("dialog-error-symbolic")
            self.set_subtitle(f"{extension_info["uuid"]}\n\n{extension_info["error"]}")
            self.switch.set_sensitive(False)

        if self.extension_info["hasPrefs"]:
            self.prefs = Gtk.Button.new_from_icon_name("preferences-system-symbolic")
            self.prefs.set_valign(Gtk.Align.CENTER)
            self.prefs.add_css_class("circular")
            # self.button.add_css_class("suggested-action")
            self.prefs.connect("clicked", self.open_prefs)
            if self.error:
                self.prefs.set_sensitive(False)
            self.add_suffix(self.prefs)

        if not self.system and self.extension_info["hasUpdate"]:
            self.update = Gtk.Image.new_from_icon_name("software-update-available-symbolic")
            self.update.set_margin_end(5)
            self.update.set_valign(Gtk.Align.CENTER)
            self.update.add_css_class("circular")
            if self.error:
                self.update.set_sensitive(False)
            self.update.set_tooltip_text("This extension will be updated on next restart or login.")
            self.add_suffix(self.update)

        # Row to be revealed
        self.description_row = Adw.ActionRow()
        if extension_info["description"]:
            self.description_row.set_title(extension_info["description"].replace("&", "&amp;"))
        else:
            self.description_row.set_title("This extension provided no description.")
        self.add_row(self.description_row)

        self.management_row = Adw.ActionRow()
        try:
            version = extension_info["version"]
        except KeyError:
            version = "Unknown"

        supported_versions = _proxy.get_supported_shell_versions(self.extension_uuid)
        if not supported_versions or supported_versions == []:
            supported = ", ".join(_proxy.get_supported_shell_versions(self.extension_uuid))
        else:
            supported = "Unknown"
        self.management_row.set_subtitle(f"Extension Version: {version}\nGNOME Versions Supported: {supported}")
        self.add_row(self.management_row)

        # Management Buttons
        if not self.system:
            self.info_button = Gtk.Button.new_from_icon_name("dialog-information-symbolic")
            self.info_button.set_valign(Gtk.Align.CENTER)
            self.info_button.add_css_class("circular")
            self.info_button.add_css_class("flat")
            self.info_button.set_margin_end(5)
            #self.info_button.connect("clicked", self.show_info)
            self.management_row.add_suffix(self.info_button)

            self.remove_button = Gtk.Button.new_with_label("Remove")
            self.remove_button.set_valign(Gtk.Align.CENTER)
            self.remove_button.add_css_class("destructive-action")
            self.remove_button.connect("clicked", self.remove_extension)
            self.management_row.add_suffix(self.remove_button)


    def get_info(self, button):


    def remove_extension(self, button):
        _proxy.remove_extension(self.extension_uuid)

    def switch_changed(self, switch, state):
        if state:
            _proxy.enable_extension(self.extension_uuid)
        else:
            _proxy.disable_extension(self.extension_uuid)

    def open_prefs(self, button):
        _proxy.open_extension_prefs(self.extension_uuid)


def set_builder(builder):
    global _builder
    _builder = builder
    system_visible_changed(_control_settings, "show-system-extensions")


# Bind system visible setting
def system_visible_changed(setting, key):
    if key == "show-system-extensions":
        if _builder:
            system_group = _builder.get_object("system_extensions_group")
            system_group.set_visible(setting.get_boolean(key))


_control_settings.connect("changed", system_visible_changed)


def add_extensions_to_groups():
    extensions = _proxy.get_extensions()
    user_group = _builder.get_object("user_extensions_group")
    system_group = _builder.get_object("system_extensions_group")

    # Clear groups
    for row in _extension_rows:
        row.destroy()

    for extension in extensions:
        print(extensions[extension])
        if _proxy.is_system_extension_from_data(extensions[extension]):
            system_group.add(ExtensionRow(extensions[extension]))
        else:
            user_group.add(ExtensionRow(extensions[extension]))