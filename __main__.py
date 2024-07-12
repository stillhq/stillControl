import gi
gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

import stillControl
import GSettingGroup
import JsonParser

if __name__ == "__main__":
    app = stillControl.StillControl()
    JsonParser.parse_json(app.builder)
    # app.builder.get_object("theming_group").add_switch(
    #     GSettingGroup.GSetting(
    #         title="Show Battery Percentage",
    #         subtitle="This shows the battery percentage in the top bar. This is only useful if you have a laptop.",
    #         icon_name="weather-clear-night-symbolic",
    #         schema="org.gnome.desktop.interface",
    #         key="show-battery-percentage"
    #     )
    # )
    # app.builder.get_object("theming_group").add_spin(
    #     GSettingGroup.GSetting(
    #         title="Font Scaling Factor",
    #         subtitle="The scaling factor for font sizes.",
    #         icon_name="weather-clear-night-symbolic",
    #         schema="org.gnome.desktop.interface",
    #         key="text-scaling-factor"
    #     ),
    #     GSettingGroup.SpinType.DOUBLE, True,
    #     Gtk.Adjustment(lower=50, upper=300, step_increment=25)
    # )
    # app.builder.get_object("theming_group").add_font(
    #     GSettingGroup.GSetting(
    #         title="Interface Font",
    #         subtitle="This is the primary font used by your system.",
    #         schema="org.gnome.desktop.interface", key="font-name"
    #     )
    # )
    # app.builder.get_object("theming_group").add_combo(
    #     GSettingGroup.GSetting(
    #         title="Theme Styling",
    #         subtitle="This is the same as the light and dark theme options in GNOME Control Center.",
    #         schema="org.gnome.desktop.interface", key="color-scheme"
    #     ), ["default", "prefer-dark"], ["Default", "Dark"]
    # )
    # app.builder.get_object("theming_group").add_detailed_combo(
    #     GSettingGroup.GSetting(
    #         title="Mouse Click Emulation",
    #         schema="org.gnome.desktop.interface", key="color-scheme"
    #     ), ["default", "prefer-dark"], ["Default", "Dark"],
    #     [
    #         "Click the touchpad with two fingers for right-click, and three fingers for middle click.",
    #         "Click the bottom right of the touchpad for right click and the bottom middle for middle click."
    #     ]
    # )
    app.run()
