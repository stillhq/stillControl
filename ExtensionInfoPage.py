import Utils

from gi.repository import Gtk, GLib, Adw

def add_extension_info_page(builder, remote_extension: Utils.RemoteExtensionInfo):
    builder.get_object("main_navigation")
    extension_name = builder.get_object("extension_name")
    extension_author = builder.get_object("extension_author")
    extension_icon = builder.get_object("extension_icon")
    extension_install = builder.get_object("extension_install")
    extension_screenshot = builder.get_object("extension_description")

    extension_name.set_text(remote_extension.name)
    extension_author.set_text(remote_extension.author)

    .set_text(remote_extension.description)