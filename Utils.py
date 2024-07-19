import os

from gi.repository import Gio
import json


class ExtensionProxy:
    def __init__(self):
        self.window = ""
        self.proxy = Gio.DBusProxy.new_sync(
            Gio.bus_get_sync(Gio.BusType.SESSION, None),
            0, None,
            'org.gnome.Shell',
            '/org/gnome/Shell',
            'org.gnome.Shell.Extensions',
            None
        )

    # THIS CURRENTLY DOESN'T WORK
    def set_window(self, window):
        self.window = window.get_id()

    def get_extensions(self):
        return self.proxy.ListExtensions()

    def remove_extension(self, uuid):
        return self.proxy.UninstallExtension('(s)', uuid)

    def check_updates(self):
        return self.proxy.CheckForUpdates()

    def get_extension_info(self, uuid):
        return self.proxy.GetExtensionInfo('(s)', uuid)

    def get_supported_shell_versions(self, uuid):
        return self.get_supported_shell_versions_from_data(self.get_extension_info(uuid))

    def get_supported_shell_versions_from_data(self, extension):
        json_path = os.path.join(extension["path"], "metadata.json")
        if os.path.exists(json_path):
            with open(os.path.join(extension["path"], "metadata.json"), "r") as file:
                metadata = json.load(file)
                return metadata["shell-version"]
        return []


    def install_remote_extension(self, uuid):
        return self.proxy.InstallRemoteExtension('(s)', uuid)

    def open_extension_prefs(self, uuid):
        return self.proxy.OpenExtensionPrefs("(ssa{sv})", uuid, str(self.window), {})

    def enable_extension(self, uuid):
        return self.proxy.EnableExtension('(s)', uuid)

    def disable_extension(self, uuid):
        return self.proxy.DisableExtension('(s)', uuid)

    def is_system_extension(self, uuid):
        return self.is_system_extension_from_data(self.get_extension_info(uuid))

    # Faster way without requesting the extension info from dbus
    def is_system_extension_from_data(self, extension):
        return extension["path"].startswith("/usr/share/gnome-shell/extensions/")