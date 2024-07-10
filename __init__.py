from gi.repository import GObject, Gio


class GSetting(GObject.GObject):
    __gtype_name__ = "GSetting"
    _title = ""
    _subtitle = ""
    _icon_name = None
    _schema = ""
    _key = ""
    settings = None

    @GObject.Property(type=str)
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @GObject.Property(type=str)
    def subtitle(self):
        return self._subtitle

    @subtitle.setter
    def subtitle(self, value):
        self._subtitle = value

    @GObject.Property(type=str)
    def icon_name(self):
        return self._icon_name

    @icon_name.setter
    def icon_name(self, value):
        self._icon_name = value

    @GObject.Property(type=str)
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, value):
        self._schema = value
        self.settings = Gio.Settings.new(self._schema)

    @GObject.Property(type=str)
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        self._key = value