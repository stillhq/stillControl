import constants
import gi
import os

from ExtensionSearchPage import ExtensionSearchPage

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

import ManageExtensionsPage
import LayoutManager
import LayoutButton

from __init__ import GSetting  # FIXME: Change this to absolute import


class StillControl(Adw.Application):
    def __init__(self):
        super().__init__(application_id="io.stillhq.Control")

        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(constants.UI_DIR, "stillControl.ui"))

        self.main_window = self.builder.get_object("main_window")
        self.main_stack = self.builder.get_object("main_stack")
        self.layout_stack = self.builder.get_object("layout_stack")
        self.setup_layout_page()
        self.setup_extension_page()

    def setup_extension_page(self):
        ManageExtensionsPage.set_builder(self.builder)
        ManageExtensionsPage.add_extensions_to_groups()
        self.builder.get_object("install_extensions_clamp").set_child(
            ExtensionSearchPage(self.builder, ManageExtensionsPage._proxy)
        )

    def layout_page_child_clicked(self, flowbox, child):
        if child.get_child().get_sensitive():
            child.get_child().check.set_active(True)

    def layout_page_visible(self, _stack, _prop):
        if self.main_stack.get_visible_child_name() == "layout" and self.layout_stack.get_visible_child_name() == "layout":
            LayoutButton.refresh_buttons(LayoutManager.get_current_layout())

    def setup_layout_page(self):
        available_layouts = LayoutManager.get_available_layouts()
        if len(available_layouts) >= 2:
            layout_box = self.builder.get_object("layout_box")
            last_button = LayoutButton.LayoutButton("custom", None)
            layout_box.append(last_button)
            current_layout = LayoutManager.get_current_layout()
            for layout in LayoutManager.get_available_layouts():
                layout_button = LayoutButton.LayoutButton(layout, last_button)
                if layout == current_layout:
                    layout_button.check.set_active(True)
                layout_box.append(layout_button)
                last_button = layout_button
            LayoutButton.refresh_buttons(current_layout)

            layout_box.connect("child-activated", self.layout_page_child_clicked)
            self.main_stack.connect("notify::visible-child-name", self.layout_page_visible)
            self.layout_stack.connect("notify::visible-child-name", self.layout_page_visible)
        else:
            self.layout_stack.remove(self.builder.get_object("layout_page").get_child())
            self.layout_stack.set_visible_child(self.layout_stack.get_first_child())

    def do_activate(self):
        self.main_window.set_application(self)
        self.main_window.present()

        # Builder for some reason breaks if I try to set the stacks
        self.main_stack.set_visible_child_name("layout_view")
        self.layout_stack.set_visible_child_name("layout_page")