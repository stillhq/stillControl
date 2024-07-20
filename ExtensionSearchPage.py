import json
import os
import subprocess
import threading

import requests

import gi

import Utils
from RemoteExtensionPage import RemoteExtensionPage

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GObject, Gio, GLib

import constants

_QUERY_URL = "https://extensions.gnome.org/extension-query/"


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


@Gtk.Template(filename=os.path.join(constants.UI_DIR, "ExtensionSearchPage.ui"))
class ExtensionSearchPage(Gtk.Box):
    __gtype_name__ = "ExtensionSearchPage"

    query = ""
    sort = "relevance"
    page = 1
    page_amount = 0

    search_entry = Gtk.Template.Child()
    sort_dropdown = Gtk.Template.Child()
    extension_view = Gtk.Template.Child()
    results_stack = Gtk.Template.Child()
    loading_spinner = Gtk.Template.Child()
    more_button = Gtk.Template.Child()

    def __init__(self, builder, proxy):
        super().__init__()
        self.proxy = proxy
        self.builder = builder

        self.store = Gio.ListStore.new(RemoteExtensionItem)
        self.extension_view.set_model(Gtk.NoSelection.new(self.store))
        self.extension_view.connect("activate", self.row_activated)
        self.sort_dropdown.connect("notify::selected-item", self.dropdown_changed)
        self.more_button.connect("clicked", self.more_clicked)
        self.search_entry.connect("search-changed", self.search_changed)
        self.query_search_thread()

    def row_activated(self, _list_view, position):
        page = RemoteExtensionPage(
            self.proxy,
            Utils.RemoteExtensionInfo.new_remote_from_uuid(self.proxy, self.store.get_item(position).uuid)
        )
        page.add_to_window(self.builder)


    def dropdown_changed(self, _combo, _item):
        self.sort = self.sort_dropdown.get_selected_item().get_string().lower()
        self.page = 1
        self.store.remove_all()
        self.query_search_thread()

    def search_changed(self, search_entry):
        self.page = 1
        self.store.remove_all()
        self.query = self.search_entry.get_text()
        self.query_search_thread()

    def query_search_thread(self):
        self.loading_spinner.start()
        self.results_stack.set_visible_child_name("loading")
        threading.Thread(target=self.query_gnome_extensions, args=(True,)).start()

    def query_load_more_thread(self):
        threading.Thread(target=self.query_gnome_extensions, args=(False,)).start()

    def query_gnome_extensions(self, spinner):
        params = {
            "n_per_page": 20,
            "sort": self.sort,
            "page": self.page,
            "search": self.query,
            "shell_version": "46"  # replace with your GNOME shell version
        }
        response = requests.get(_QUERY_URL, params=params)
        if response.status_code == 200:
            results = json.loads(response.text)

            for extension in results["extensions"]:
                self.store.append(RemoteExtensionItem.new_from_extension_info(extension))
            self.page_amount = results["numpages"]
            GLib.idle_add(self.update_page_btn)
            if spinner:
                GLib.idle_add(lambda: self.loading_spinner.stop())
                GLib.idle_add(lambda: self.results_stack.set_visible_child_name("results"))
            else:
                GLib.idle_add(lambda: self.search_entry.set_sensitive(True))
                GLib.idle_add(lambda: self.more_button.set_sensitive(True))
        else:
            print(f"Request failed with status code {response.status_code}")

    def update_page_btn(self):
        if self.page + 1 <= self.page_amount:
            self.more_button.set_visible(True)
        else:
            self.more_button.set_visible(False)

    def more_clicked(self, button):
        self.page += 1
        self.search_entry.set_sensitive(False)
        self.more_button.set_sensitive(False)
        self.query_load_more_thread()