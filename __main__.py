import gi
gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

import stillControl
import GSettingGroup

if __name__ == "__main__":
    app = stillControl.StillControl()

    app.builder.get_object("theming_group").add_switch(
        GSettingGroup.GSetting(
            title="Show Battery Percentage",
            subtitle="This shows the battery percentage in the top bar. This is only useful if you have a laptop.",
            icon_name="weather-clear-night-symbolic",
            schema="org.gnome.desktop.interface",
            key="show-battery-percentage"
        )
    )
    app.builder.get_object("theming_group").add_spin(
        GSettingGroup.GSetting(
            title="Font Scaling Factor",
            subtitle="The scaling factor for font sizes.",
            icon_name="weather-clear-night-symbolic",
            schema="org.gnome.desktop.interface",
            key="text-scaling-factor"
        ),
        GSettingGroup.SpinType.DOUBLE, True,
        Gtk.Adjustment(lower=50, upper=300, step_increment=25)
    )
    app.run()
