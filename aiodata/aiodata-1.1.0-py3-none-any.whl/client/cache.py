
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

    __slots__ = ('_primaries',)

    def __init__(self, primaries):

        self._primaries = primaries

    @property
    def primaries(self):

        return self._primaries

    def get(self, *keys):

        value = self

        allowed = len(self._primaries)

        for key in keys[:allowed]:

            value = value[key]

        return value

    def query(self, data):

        return (data[key] for key in self._primaries)

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

            value[key] = value = self.__class__(keys)

        value[final] = entry = Entry(data)

        return entry

    def destroy(self, *keys):

        (*start, final) = keys

        values = self.get(*start)

        value = values.pop(final)

        return value
