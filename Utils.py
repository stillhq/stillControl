import os

from gi.repository import Gio
import json

import requests


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


class RemoteExtensionInfo:
    uuid: str = ""
    name: str = ""
    creator: str = ""
    creator_url: str = ""
    description: str = ""
    link: str = ""
    icon: str = ""
    screenshot: str = ""
    shell_versions: list = []
    downloads: int = 0
    url: str = ""
    donate: str = None

    @classmethod
    def get_remote_from_uuid(cls, uuid):
        response = requests.get(f"https://extensions.gnome.org/extension-query/?uuid={uuid}")
        if response.status_code != 200:
            return None

        try:
            data = response.json()["extensions"][0]
        except IndexError:
            return None
        remote_extension = cls()

        remote_extension.name = data["name"]
        remote_extension.uuid = uuid
        remote_extension.creator = data["creator"]
        remote_extension.creator_url = data["creator_url"]
        remote_extension.description = data["description"]
        remote_extension.link = "https://extensions.gnome.org" + data["link"]
        if data["icon"]:
            remote_extension.icon = "https://extensions.gnome.org" + data["icon"]
        if data["screenshot"]:
            remote_extension.screenshot = "https://extensions.gnome.org" + data["screenshot"]
        remote_extension.downloads = data["downloads"]
        remote_extension.shell_versions = data["shell_version_map"].keys()
        remote_extension.url = data["url"]
        if "donate" in data:
            remote_extension.donate = data["donate"][0]

        return remote_extension