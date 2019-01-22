
from . import helpers


__all__ = ()


class Entry:

    __slots__ = ('__dict__',)

    __init__ = helpers.update_value

    def __getitem__(self, key):

        try:

            value = getattr(self, key)

        except AttributeError:

            raise KeyError(key) from None

        return value


class Entries(dict):

    __slots__ = ('_build', '_keys')

    def __init__(self, build, keys):

        self._build = build

        self._keys = keys

    @property
    def keys(self):

        return self._keys

    def get(self, *keys):

        value = self

        allowed = len(self._keys)

        for key in keys[:allowed]:

            value = value[key]

        return value

    def query(self, data):

        return (data[key] for key in self._keys)

    def create(self, data):

        query = tuple(self.query(data))

        (*start, final) = query

        value = self

        for (index, key) in enumerate(start):

            try:

                value = value[key]

            except KeyError:

                pass

            else:

                continue

            keys = query[index:]

            value[key] = value = self.__class__(self._build, keys)

        value[final] = entry = self._build(data)

        return entry

    def destroy(self, *keys):

        (*start, final) = keys

        values = self.get(*start)

        value = values.pop(final)

        return value
