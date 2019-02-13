

__all__ = ()


async def propagate(execute, limit, state, critical, parse = None):

    while limit > 0:

        values = await execute(limit, state)

        if parse:

            values = parse(values)

        for index, value in enumerate(values):

            yield value

        if not index:

            break

        limit -= index + 1

        state = critical(value)


def position(bundles, keys = ('id', 'position')):

    generate = (zip(keys, bundle) for bundle in bundles)

    data = tuple(map(dict, generate))

    return data
