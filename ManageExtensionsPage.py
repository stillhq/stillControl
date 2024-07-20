import os
import subprocess

import Utils
import constants
import requests
import threading

import gi

from RemoteExtensionPage import RemoteExtensionPage

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk, Gio, GdkX11, GLib

from __init__ import GSetting

_shell_settings = Gio.Settings.new("org.gnome.shell")
_control_settings = Gio.Settings.new("io.stillhq.control")
_proxy = Utils.ExtensionProxy()
_system_rows = []
_user_rows = []
_builder = None
_extensions_disabled = False


@Gtk.Template(filename=os.path.join(constants.UI_DIR, "ExtensionRow.ui"))
class ExtensionRow(Adw.ExpanderRow):
    __gtype_name__ = "ExtensionRow"

    def __init__(self, extension_info, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.remote_extension = None
        self.extension_info = extension_info

        self.switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        self.add_suffix(self.switch)
        self.switch.connect("state-set", self.switch_changed)

        self.prefs = Gtk.Button.new_from_icon_name("preferences-system-symbolic")
        self.prefs.set_valign(Gtk.Align.CENTER)
        self.prefs.add_css_class("circular")
        self.prefs.set_visible(False)
        self.prefs.connect("clicked", self.open_prefs)
        self.add_suffix(self.prefs)

        self.update = Gtk.Image.new_from_icon_name("software-update-available-symbolic")
        self.update.set_margin_end(5)
        self.update.set_valign(Gtk.Align.CENTER)
        self.update.add_css_class("circular")
        self.update.set_tooltip_text("This extension will be updated on next restart or login.")
        self.add_suffix(self.update)

        # Row to be revealed
        self.description_row = Adw.ActionRow()
        self.add_row(self.description_row)

        self.management_row = Adw.ActionRow()
        self.add_row(self.management_row)

        # Management Buttons
        self.path_button = Gtk.Button.new_from_icon_name("folder-open-symbolic")
        self.path_button.set_valign(Gtk.Align.CENTER)
        self.path_button.add_css_class("circular")
        self.path_button.add_css_class("flat")
        self.path_button.connect("clicked", self.open_path)
        self.management_row.add_suffix(self.path_button)

        self.info_button = Gtk.Button.new_from_icon_name("dialog-information-symbolic")
        self.info_button.set_valign(Gtk.Align.CENTER)
        self.info_button.add_css_class("circular")
        self.info_button.add_css_class("flat")
        self.info_button.set_margin_end(5)
        self.info_button.set_visible(False)
        self.info_button.connect("clicked", self.info_button_clicked)
        self.management_row.add_suffix(self.info_button)

        self.remove_button = Gtk.Button.new_with_label("Remove")
        self.remove_button.set_valign(Gtk.Align.CENTER)
        self.remove_button.add_css_class("destructive-action")
        self.remove_button.connect("clicked", self.remove_extension)
        self.management_row.add_suffix(self.remove_button)
        self.update_row(extension_info)

    def update_row(self, extension_info):
        self.extension_uuid = extension_info["uuid"]
        self.system = _proxy.is_system_extension_from_data(extension_info)
        self.set_title(extension_info["name"])
        self.set_subtitle(extension_info["uuid"])
        self.error = self.extension_info["error"] != ""

        self.switch.set_active(extension_info["enabled"])

        if self.error:
            self.add_css_class("error")
            self.set_icon_name("dialog-error-symbolic")
            self.set_subtitle(f"{extension_info["uuid"]}\n\n{extension_info["error"]}")
            self.switch.set_sensitive(False)
            self.prefs.set_sensitive(False)
            self.update.set_sensitive(False)

        if self.extension_info["hasPrefs"]:
            self.prefs.set_visible(True)
        else:
            self.prefs.set_visible(False)

        if not self.system and self.extension_info["hasUpdate"]:
            self.update.set_visible(True)
        else:
            self.update.set_visible(False)

        if extension_info["description"]:
            self.description_row.set_title(extension_info["description"].replace("&", "&amp;"))
        else:
            self.description_row.set_title("This extension provided no description.")

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

        if not self.system:
            self.path_button.set_visible(True)
            self.info_button.set_visible(True)
            self.remove_button.set_visible(True)
        else:
            self.path_button.set_visible(False)
            self.info_button.set_visible(False)
            self.remove_button.set_visible(False)

        self.check_for_remote()

    def open_path(self, button):
        subprocess.Popen(["/bin/xdg-open", self.extension_info["path"]])

    def check_for_remote(self):
        thread = threading.Thread(target=self.check_for_remote_thread)
        thread.start()

    def check_for_remote_thread(self):
        remote_extension = Utils.RemoteExtensionInfo.new_remote_from_uuid(_proxy, self.extension_uuid)
        if remote_extension:
            self.remote_extension = remote_extension
            if not self.system:
                GLib.idle_add(lambda: self.info_button.set_visible(True))

    def info_button_clicked(self, button):
        RemoteExtensionPage(_proxy, self.remote_extension).add_to_window(_builder)

    def remove_extension(self, button):
        _proxy.remove_extension(self.extension_uuid)

    def switch_changed(self, switch, state):
        if state:
            _proxy.enable_extension(self.extension_uuid)
        else:
            _proxy.disable_extension(self.extension_uuid)

    def open_prefs(self, button):
        _proxy.open_extension_prefs(self.extension_uuid)

    def destroy(self):
        self.super().destroy()


def set_builder(builder):
    global _builder
    _builder = builder
    system_visible_changed(_control_settings, "show-system-extensions")
    extensions_enabled_changed(_shell_settings, "disable-user-extensions")


# Bind system visible setting
def system_visible_changed(setting, key):
    if key == "show-system-extensions":
        if _builder:
            system_group = _builder.get_object("system_extensions_group")
            system_group.set_visible(setting.get_boolean(key))


_control_settings.connect("changed", system_visible_changed)


def extensions_enabled_changed(setting, key):
    global _extensions_disabled
    if key == "disable-user-extensions":
        _extensions_disabled = setting.get_boolean(key)
        if _builder:
            user_group = _builder.get_object("system_extensions_group")
            system_group = _builder.get_object("user_extensions_group")
            user_group.set_sensitive(not _extensions_disabled)
            system_group.set_sensitive(not _extensions_disabled)


_shell_settings.connect("changed", extensions_enabled_changed)


def add_extensions_to_groups():
    extensions = _proxy.get_extensions()
    user_group = _builder.get_object("user_extensions_group")
    system_group = _builder.get_object("system_extensions_group")

    for extension in extensions:
        row = ExtensionRow(extensions[extension])
        if _proxy.is_system_extension_from_data(extensions[extension]):
            system_group.add(row)
            _system_rows.append(row)
        else:
            user_group.add(row)
            _user_rows.append(row)


def update_rows():
    if not _extensions_disabled:
        extensions = _proxy.get_extensions()
        for extension in extensions:
            not_in_rows = True
            for row in _system_rows:
                if row.extension_uuid == extensions[extension]["uuid"]:
                    not_in_rows = False
                    row.update_row(extensions[extension])
            for row in _user_rows:
                if row.extension_uuid == extensions[extension]["uuid"]:
                    not_in_rows = False
                    row.update_row(extensions[extension])
            if not_in_rows:
                row = ExtensionRow(extensions[extension])
                if _proxy.is_system_extension_from_data(extensions[extension]):
                    _system_rows.append(row)
                    _builder.get_object("system_extensions_group").add(row)
                else:
                    _user_rows.append(row)
                    _builder.get_object("user_extensions_group").add(row)


def proxy_signal_handler(proxy, sender_name, signal_name, parameters):
    update_rows()


_proxy.proxy.connect("g-signal", proxy_signal_handler)
