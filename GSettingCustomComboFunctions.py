import os

_HOME = os.getenv("HOME")


# Checks all subdirectories for a file and adds it to a list
# (used for things like checking GTK themes)
def check_dir_for_file_to_list(input_list, directory, file_check):
    if os.path.isdir(directory):
        for item in os.listdir(directory):
            if item not in input_list and os.path.isdir(directory + "/" + item) \
                    and os.path.exists(directory + item + file_check):
                input_list.append(item)
    return input_list


# Scans for icon themes because cursor themes can be
# considered icon themes, so they need to be filter out
def check_dir_for_icon_theme(input_list, directory, file_check):
    if os.path.isdir(directory):
        for item in os.listdir(directory):
            if item not in input_list and os.path.isdir(directory + "/" + item) \
                    and os.path.exists(directory + item + file_check):
                icon_theme_dirs = []
                for item1 in os.listdir(directory + item):
                    if os.path.isdir(directory + item + "/" + item1):
                        icon_theme_dirs = [item1]
                if icon_theme_dirs != [] and icon_theme_dirs != ["cursors"]:
                    input_list.append(item)
    return input_list


# Checks for Gtk theme
def get_legacy_themes():
    gtk_themes = ["Adwaita", "Adwaita-dark"]

    gtk_themes = check_dir_for_file_to_list(
        gtk_themes,
        "/usr/share/themes/",
        "/gtk-3.0/gtk.css"
    )

    gtk_themes = check_dir_for_file_to_list(
        gtk_themes,
        _HOME + "/.themes/",
        "/gtk-3.0/gtk.css"
    )

    gtk_themes = check_dir_for_file_to_list(
        gtk_themes,
        _HOME + "/.local/share/themes/",
        "/gtk-3.0/gtk.css"
    )

    return gtk_themes, gtk_themes, gtk_themes


# Checks for icon themes
def get_icon_themes():
    icon_themes = []

    icon_themes = check_dir_for_icon_theme(
        icon_themes,
        "/usr/share/icons/",
        "/index.theme"
    )

    icon_themes = check_dir_for_icon_theme(
        icon_themes,
        _HOME + "/.icons/",
        "/index.theme"
    )

    icon_themes = check_dir_for_icon_theme(
        icon_themes,
        _HOME + "/.local/share/icons/",
        "/index.theme"
    )

    return icon_themes, icon_themes, icon_themes


# Checks for cursor themes
def get_cursor_themes():
    cursor_themes = []

    cursor_themes = check_dir_for_file_to_list(
        cursor_themes,
        "/usr/share/icons/",
        "/cursors/"
    )
    cursor_themes = check_dir_for_file_to_list(
        cursor_themes,
        _HOME + "/.icons/",
        "/cursors/"
    )
    cursor_themes = check_dir_for_file_to_list(
        cursor_themes,
        _HOME + "/.local/share/icons/",
        "/cursors/"
    )

    return cursor_themes, cursor_themes, cursor_themes


function_ids = {
    "legacy_themes": get_legacy_themes,
    "icon_themes": get_icon_themes,
    "cursor_themes": get_cursor_themes
}
