

__all__ = ()


def seek(escape, start, stop, values, find = 1):

    level = 0

    escaping = None

    for (index, value) in enumerate(values):

        if escaping:

            escaping = False

            continue

        if value == escape:

            escaping = True

        if value == start:

            level += 1

        if value == stop:

            if not level:

                continue

            level -= 1

        if not level:

            find -= 1

        if not find:

            break

    return index


def clause(escape, start, seek, values):

    index = drag = 0

    point = len(values)

    escaping = False

    while index < point:

        value = values[index]

        if escaping:

            escaping = False

            continue

        if value == escape:

            escaping = True

        if value == start:

            yield values[drag:index]

            after = index

            step = seek(values[after:])

            index = after + step

            yield values[after + 1:index]

            drag = index + 1

        else:

            index += 1

    if not drag == index:

        yield values[drag:]


def _pair(key):

    return (key, [])


def flag(skip, values, keys):

    current, working = _pair(None)

    for value in values:

        check, value = skip(value)

        if value in keys and not check:

            yield (current, working)

            current, working = _pair(value)

            continue

        working.append(value)

    yield (current, working)
