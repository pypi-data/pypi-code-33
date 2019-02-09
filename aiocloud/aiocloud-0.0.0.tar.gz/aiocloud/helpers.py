import functools


__all__ = ()


def get_soft(root, key, factory):

    try:

        value = root[key]

    except KeyError:

        value = root[key] = factory()

    return value


def fix_params(root, booleans = ('false', 'true')):

    for (key, value) in tuple(root.items()):

        if value is None:

            del root[key]

            continue

        if isinstance(value, bool):

            value = _booleans[value]

        elif isinstance(value, (float, int)):

            value = str(value)

        else:

            continue

        root[key] = value


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
