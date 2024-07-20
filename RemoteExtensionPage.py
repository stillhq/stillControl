import os

import Utils

from gi.repository import Gtk, Adw, Soup, Gdk, GLib

import constants


@Gtk.Template(filename=os.path.join(constants.UI_DIR, "RemoteExtensionPage.ui"))
class RemoteExtensionPage(Gtk.Box):
    __gtype_name__ = "RemoteExtensionPage"
    extension_name = Gtk.Template.Child()
    extension_author = Gtk.Template.Child()
    extension_icon = Gtk.Template.Child()
    extension_install = Gtk.Template.Child()
    extension_screenshot = Gtk.Template.Child()
    extension_description = Gtk.Template.Child()
    extension_downloads = Gtk.Template.Child()
    extension_version = Gtk.Template.Child()
    extension_shell_versions = Gtk.Template.Child()

    def __init__(self, remote_extension: Utils.RemoteExtensionInfo):
        super().__init__()

        self.extension_name.set_label(remote_extension.name)
        self.extension_author.set_label(remote_extension.creator)

        if remote_extension.icon == "":
            self.extension_icon.set_visible(False)
        else:
            self.extension_icon.set_visible(True)
            self.set_url_image(remote_extension.icon, self.icon_on_receive_bytes)

        if remote_extension.screenshot == "":
            self.extension_screenshot.set_visible(False)
        else:
            self.extension_screenshot.set_visible(True)
            self.set_url_image(remote_extension.screenshot, self.screenshot_on_receive_bytes)

        self.extension_description.set_label(remote_extension.description.replace("&", "&amp;"))

        self.set_row(self.extension_downloads, str(remote_extension.downloads))
        self.set_row(self.extension_version, str(remote_extension.version))
        self.set_row(self.extension_shell_versions, ", ".join(remote_extension.shell_versions))

    @staticmethod
    def set_row(row, value):
        if value is not None and value is not "":
            row.set_subtitle(value)
            row.set_visible(True)
        else:
            row.set_visible(False)

    def add_to_window(self, builder):
        page = Adw.NavigationPage(title=self.extension_name.get_label())
        page.set_child(self)
        builder.get_object("main_navigation").push(page)

    def icon_on_receive_bytes(self, session, result, message):
        bytes = session.send_and_read_finish(result)
        if message.get_status() != Soup.Status.OK:
            raise Exception(f"Got {message.get_status()}, {message.get_reason_phrase()}")
        texture = Gdk.Texture.new_from_bytes(bytes)
        self.extension_icon.set_from_paintable(texture)

    def screenshot_on_receive_bytes(self, session, result, message):
        bytes = session.send_and_read_finish(result)
        if message.get_status() != Soup.Status.OK:
            raise Exception(f"Got {message.get_status()}, {message.get_reason_phrase()}")
        texture = Gdk.Texture.new_from_bytes(bytes)
        self.extension_screenshot.set_paintable(texture)

    def set_url_image(self, url, bytes_recieved):
        session = Soup.Session()
        message = Soup.Message(
            method="GET",
            uri=GLib.Uri.parse(url, GLib.UriFlags.NONE),
        )
        session.send_and_read_async(
            message, GLib.PRIORITY_DEFAULT, None, bytes_recieved, message
        )
