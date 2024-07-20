import os
import subprocess

import Utils

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Soup", "3.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Soup, Gdk, GLib, GObject

import constants


def url_row_clicked(widget, url):
    subprocess.run(["xdg-open", url])


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
    extension_homepage = Gtk.Template.Child()
    extension_link = Gtk.Template.Child()

    def __init__(self, proxy, remote_extension: Utils.RemoteExtensionInfo):
        super().__init__()

        self.proxy = proxy

        self.extension_uuid = remote_extension.uuid
        self.extension_name.set_label(remote_extension.name)
        self.extension_author.set_label(remote_extension.creator)
        self.extension_install.connect("clicked", self.install_clicked)

        if remote_extension.icon == "" or remote_extension.icon is None:
            self.extension_icon.set_visible(False)
        else:
            self.extension_icon.set_visible(True)
            self.set_url_image(remote_extension.icon, self.icon_on_receive_bytes, self.extension_icon)

        if remote_extension.screenshot == "" or remote_extension.screenshot is None:
            self.extension_screenshot.set_visible(False)
        else:
            self.extension_screenshot.set_visible(True)
            self.set_url_image(remote_extension.screenshot, self.screenshot_on_receive_bytes, self.extension_screenshot)

        self.extension_description.set_label(remote_extension.description)

        self.set_row(self.extension_downloads, str(remote_extension.downloads))
        self.set_row(self.extension_version, str(remote_extension.supported_version))
        self.set_row(self.extension_shell_versions, ", ".join(remote_extension.shell_versions))
        self.set_row(self.extension_homepage, remote_extension.homepage)
        self.set_row(self.extension_link, remote_extension.link)

        # Unsupported Version
        if not remote_extension.is_supported:
            self.extension_version.set_subtitle("This extension is not supported on your version of GNOME Shell")
            self.extension_shell_versions.set_icon_name("computer-fail-symbolic")  # EASTER EGG :D
            self.extension_version.set_visible(True)

        self.extension_homepage.set_activatable(True)
        self.extension_link.set_activatable(True)
        self.extension_homepage.connect("activate", url_row_clicked, remote_extension.homepage)
        self.extension_link.connect("activate", url_row_clicked, remote_extension.link)

        self.proxy.proxy.connect("g-signal", self.proxy_signal_handler)
        self.update_install_button()

    def install_clicked(self, button):
        self.proxy.install_remote_extension(self.extension_uuid)

    def proxy_signal_handler(self, proxy, sender_name, signal_name, parameters):
        if signal_name == "ExtensionStateChanged" and parameters[0] == self.extension_uuid:
            self.update_install_button()

    def update_install_button(self):
        if self.proxy.is_system_extension(self.extension_uuid):
            self.extension_install.set_sensitive(False)
        if self.proxy.get_installed(self.extension_uuid):
            self.extension_install.set_label("Installed")
            self.extension_install.set_sensitive(False)
        else:
            self.extension_install.set_label("Install")
            self.extension_install.set_sensitive(True)

    @staticmethod
    def set_row(row, value):
        if value is not None and value != "":
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
        self.extension_screenshot.set_size_request(
            -1, min(
                self.extension_screenshot.get_allocated_width() / texture.get_intrinsic_aspect_ratio(),
                400
            )
        )

    def set_url_image(self, url, bytes_received, image):
        try:
            session = Soup.Session()
            message = Soup.Message(
                method="GET",
                uri=GLib.Uri.parse(url, GLib.UriFlags.NONE),
            )
            session.send_and_read_async(
                message, GLib.PRIORITY_DEFAULT, None, bytes_received, message
            )
        except GLib.Error:
            image.set_visible(False)
