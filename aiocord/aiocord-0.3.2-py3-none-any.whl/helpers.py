import functools


__all__ = ()


def update_generic(blueprint, value, datas, skip = ()):

    for (key, data) in datas.items():

        try:

            (create, update) = blueprint[key]

        except KeyError:

            handle = False

        else:

            handle = not data is None

        if handle:

            if update is None:

                new = create(data)

            else:

                try:

                    new = getattr(value, key)

                except AttributeError:

                    missing = True

                else:

                    missing = new in skip

                if missing or new is None:

                    new = create()

                update(new, data)

                if not missing:

                    continue
        else:

            new = data

        setattr(value, key, new)


def update_list(update, create, value, datas):

    keep = []

    for data in datas:

        contest = create(data)

        for inner in value:

            if not inner == contest:

                continue

            if not update is None:

                update(inner, data)

            break

        else:

            inner = contest

            value.append(inner)

        keep.append(inner)

    index = 0

    while index < len(value):

        inner = value[index]

        if inner in keep:

            index += 1

        else:

            value.remove(inner)


def update_dict(update, create, identify, value, datas, clean = True):

    fresh = []

    for data in datas:

        identity = identify(data)

        try:

            inner = value[identity]

        except KeyError:

            inner = value[identity] = create()

        update(inner, data)

        fresh.append(inner)

    if not clean:

        return

    for key, inner in tuple(value.items()):

        if inner in fresh:

            continue

        del value[key]


@functools.lru_cache(maxsize = None)
def cached_partial(*args, **kwargs):

    return functools.partial(*args, **kwargs)


def crawl(keys, data):

    for key in keys:

        data = data[key]

    return data


class LimitDict(dict):

    __slots__ = ('_maxsize',)

    def __init__(self, maxsize = float('inf')):

        self._maxsize = maxsize

    def __setitem__(self, key, value):

        if len(self) > self._maxsize:

            keys = self.keys()

            try:

                key = next(iter(keys))

            except StopIteration:

                pass

            else:

                del self[key]

        super().__setitem__(key, value)


class BitGroup(int):

    __slots__ = ()

    def can(self, value):

        return (self & value) == value

    def add(self, value):

        return self.__class__(self | value)

    def pop(self, value):

        return self.__class__(self & ~ value)


def mime_from_bytes(bytes):

    if (bytes.startswith(b'\xFF\xD8')
        and bytes.rstrip(b'\0').endswith(b'\xFF\xD9')):

        return 'image/jpeg'

    elif bytes.startswith(b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'):

        return 'image/png'

    elif (bytes.startswith(b'\x47\x49\x46\x38\x37\x61')
        or bytes.startswith(b'\x47\x49\x46\x38\x39\x61')):

        return 'image/gif'

    raise ValueError('could not resolve mime type')
