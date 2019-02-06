

__all__ = ()


async def propagate(execute, limit, state, critical, parse = None):

    while True:

        values = await execute(limit, state)

        if parse:

            values = parse(values)

        sent = 0

        for value in values:

            yield value

            sent += 1

            if not sent < limit:

                break

        if not sent:

            break

        limit -= sent

        if not limit > 0:

            break

        state = critical(value)


def position(bundles, keys = ('id', 'position')):

    generate = (zip(keys, bundle) for bundle in bundles)

    data = tuple(map(dict, generate))

    return data
