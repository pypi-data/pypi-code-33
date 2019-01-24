

__all__ = ()


def seek(escape, start, stop, values, find = 1):

    level = 0

    escaping = None

    for index in range(len(values)):

        if escaping:

            escaping = False

            continue

        value = values[index]

        if value == escape:

            escaping = True

        elif value == start:

            level += 1

        elif value == stop:

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

        if escaping:

            escaping = False

        else:

            value = values[index]

            if value == escape:

                escaping = True

            else:

                if value == start:

                    yield values[drag:index]

                    after = index

                    step = seek(values[after:])

                    index = after + step

                    yield values[after + 1:index]

                    drag = index + 1

                    continue

        index += 1

    if not drag == index:

        yield values[drag:]


def flag(escape, values, keys):

    index = drag = 0

    point = len(values)

    escaping = False

    current = None

    while index < point:

        if escaping:

            escaping = False

        else:

            value = values[index]

            if value == escape:

                escaping = True

            else:

                for key in keys:

                    step = len(key)

                    stop = index + step

                    against = values[index:stop]

                    if key == against:

                        break

                else:

                    key = None

                if not key is None:

                    yield (current, values[drag:index])

                    current = key

                    index = drag = stop

                    continue

        index += 1

    yield (current, values[drag:])
