import itertools

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

        try:

            (*values, value) = helpers.crawl(value, keys)

        except ValueError:

            pass

        return value

    def query(self, data):

        return (data[key] for key in self._primaries)

    def create(self, keys, data):

        (*start, final) = keys

        value = self

        for (index, key) in enumerate(start):

            try:

                value = value[key]

            except KeyError:

                pass

            else:

                continue

            value[key] = value = self.__class__(self._primaries)

        value[final] = entry = Entry(data)

        return entry

    def destroy(self, keys):

        path, keys = itertools.tee(keys)

        values = tuple(helpers.crawl(self, keys))

        origins, values = itertools.tee(values)

        stores = (self, *origins)

        bundles = zip(stores, path, values)

        orderly = reversed(tuple(bundles))

        for (index, bundle) in enumerate(orderly):

            (store, key, value) = bundle

            if index:

                if value:

                    break

            else:

                entry = value

            del store[key]

        return entry
