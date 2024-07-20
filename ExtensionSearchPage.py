import json
import os
import subprocess
import requests

import gi

import Utils
from RemoteExtensionPage import RemoteExtensionPage

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GObject, Gio

import constants

_QUERY_URL = "https://extensions.gnome.org/extension-query/"


def query_gnome_extensions(query, sort, page=1):
    params = {
        "n_per_page": 10,
        "sort": sort,
        "page": page,
        "search": query,
        "shell_version": "46"  # replace with your GNOME shell version
    }
    print(query)
    response = requests.get(_QUERY_URL, params=params)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print(f"Request failed with status code {response.status_code}")
        return None


class RemoteExtensionItem(GObject.GObject):
    __gtype_name__ = "RemoteExtensionItem"

    _name: str = ""
    _author: str = ""
    _uuid: str = ""

    @GObject.Property(type=str)
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @GObject.Property(type=str)
    def author(self):
        return self._author

    @author.setter
    def author(self, value):
        self._author = value

    @GObject.Property(type=str)
    def uuid(self):
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        self._uuid = value

    @classmethod
    def new_from_extension_info(cls, extension_info):
        item = cls()
        item.name = extension_info["name"]
        item.author = extension_info["creator"]
        item.uuid = extension_info["uuid"]
        return item

class SearchExtensionRow(Adw.ActionRow):
    __gtype_name__ = "SearchExtensionRow"

    def __init__(self, builder, extension_info):
        super().__init__()
        self.builder = builder
        self.extension_info = extension_info
        self.set_title(extension_info.name)
        self.set_subtitle(extension_info.creator)
        self.set_activatable(True)

        # Arrow image
        arrow = Gtk.Image.new_from_icon_name("go-next-symbolic")
        self.add_suffix(arrow)

        self.connect("activated", self.on_row_clicked)

    def on_row_clicked(self, _):
        RemoteExtensionPage(self.extension_info).add_to_window(self.builder)


@Gtk.Template(filename=os.path.join(constants.UI_DIR, "ExtensionSearchPage.ui"))
class ExtensionSearchPage(Gtk.Box):
    __gtype_name__ = "ExtensionSearchPage"
    rows = []
    search_entry = Gtk.Template.Child()
    sort_dropdown = Gtk.Template.Child()
    extension_view = Gtk.Template.Child()
    page = 1
    page_amount = 0

    def __init__(self, builder, proxy):
        super().__init__()
        self.proxy = proxy
        self.builder = builder

        self.store = Gio.ListStore.new(RemoteExtensionItem)
        self.extension_view.set_model(Gtk.NoSelection.new(self.store))
        self.search_entry.connect("search-changed", self.search_changed)

    def search_changed(self, search_entry):
        self.page = 1
        self.store.remove_all()
        query = self.search_entry.get_text()
        sort = self.sort_dropdown.get_selected_item().get_string().lower()
        results = query_gnome_extensions(query, sort, self.page)

        for extension in results["extensions"]:
            self.store.append(RemoteExtensionItem.new_from_extension_info(extension))
        self.page_amount = results["numpages"]