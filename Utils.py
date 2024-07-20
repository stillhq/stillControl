import math
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
        self._shell_version = self.proxy.get_cached_property("ShellVersion").get_string()

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

    def get_shell_version(self):
        return self._shell_version

    @staticmethod
    def get_supported_shell_versions_from_data(extension):
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
    @staticmethod
    def is_system_extension_from_data(extension):
        return extension["path"].startswith("/usr/share/gnome-shell/extensions/")


def shell_version_supported(shell_version, supported_versions):
    for version in supported_versions:
        if shell_version.startswith(version + "."):
            return True
        elif version == shell_version:
            return True
    return False


class RemoteExtensionInfo:
    uuid: str = ""
    name: str = ""
    creator: str = ""
    creator_url: str = ""
    description: str = ""
    link: str = ""
    icon: str = ""
    screenshot: str = ""
    version: str = ""
    shell_versions: list = []
    is_supported = False
    downloads: int = 0
    homepage: str = ""
    donate: str = None

    @classmethod
    def get_remote_from_uuid(cls, proxy, uuid):
        response = requests.get(f"https://extensions.gnome.org/extension-query/?uuid={uuid}")
        if response.status_code != 200:
            return None

        try:
            data = response.json()["extensions"][0]
        except IndexError:
            return None
        return cls.from_json(proxy, data)


    @classmethod
    def from_json(cls, proxy, json):
        remote_extension = cls()
        remote_extension.name = json["name"]
        remote_extension.uuid = json["uuid"]
        remote_extension.creator = json["creator"]
        remote_extension.creator_url = json["creator_url"]
        remote_extension.description = json["description"]
        remote_extension.link = json["link"]
        remote_extension.icon = json["icon"]
        remote_extension.screenshot = json["screenshot"]
        remote_extension.downloads = json["downloads"]

        remote_extension.is_supported = shell_version_supported(proxy.get_shell_version(), json["shell_version_map"].keys())
        try:
            remote_extension.supported_version = json["shell_version_map"][str(float(proxy.get_shell_version()))]["version"]
        except KeyError:
            try:
                remote_extension.supported_version = json["shell_version_map"][str(math.floor(float(proxy.get_shell_version())))]["version"]
            except KeyError:
                remote_extension.supported_version = None
        remote_extension.shell_versions = json["shell_version_map"].keys()
        remote_extension.homepage = json["url"]
        if "donate" in json:
            remote_extension.donate = json["donate"][0]

        return remote_extension
