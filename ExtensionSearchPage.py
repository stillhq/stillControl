import json
import os
import subprocess
import requests

import gi

import Utils
from RemoteExtensionPage import RemoteExtensionPage

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

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
    extensions_group = Gtk.Template.Child()
    page = 1

    def __init__(self, builder, proxy):
        super().__init__()
        self.proxy = proxy
        self.builder = builder

        self.search_entry.connect("search-changed", self.search_changed)

    def add_row(self, row):
        self.rows.append(row)
        self.extensions_group.add(row)

    def clear_rows(self):
        for child in self.rows:
            child.destroy()

    def search_changed(self, search_entry):
        self.clear_rows()

        self.page = 1
        query = self.search_entry.get_text()
        sort = self.sort_dropdown.get_selected_item().get_string().lower()

        result = query_gnome_extensions(query, sort, self.page)
        self.query_to_rows(result)


    def query_to_rows(self, result):
        print(result)
        if result is not None:
            for extension in result["extensions"]:
                self.add_row(SearchExtensionRow(self.builder, Utils.RemoteExtensionInfo.from_json(self.proxy, extension)))

