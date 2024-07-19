from gi.repository import Gio


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

    def install_remote_extension(self, uuid):
        return self.proxy.InstallRemoteExtension('(s)', uuid)

    def open_extension_prefs(self, uuid):
        print(self.window)
        return self.proxy.OpenExtensionPrefs("(ssa{sv})", uuid, str(self.window), {})

    def enable_extension(self, uuid):
        return self.proxy.EnableExtension('(s)', uuid)

    def disable_extension(self, uuid):
        return self.proxy.DisableExtension('(s)', uuid)