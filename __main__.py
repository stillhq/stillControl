import stillControl
import GSettingGroup

if __name__ == "__main__":
    app = stillControl.StillControl()

    app.builder.get_object("theming_group").add_boolean(
        GSettingGroup.GSetting(
            title="Show Battery Percentage",
            subtitle="This shows the battery percentage in the top bar. This is only useful if you have a laptop.",
            icon_name="weather-clear-night-symbolic",
            schema="org.gnome.desktop.interface",
            key="show-battery-percentage"
        )
    )
    app.run()
