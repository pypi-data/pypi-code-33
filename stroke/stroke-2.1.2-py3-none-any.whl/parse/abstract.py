import re
import itertools


__all__ = ()


def flag(escape, values, keys):

    assets = (re.finditer(key, values) for key in keys)

    matches = itertools.chain.from_iterable(assets)

    assets = ((match.re.pattern, match.span()) for match in matches)

    try:

        keys, spans = zip(*assets)

    except ValueError:

        assets = ()

    else:

        assets = sorted(zip(*zip(*spans), keys))

        revert = len(escape)

        kills = 0

    revert = len(escape)

    current = None

    for *spots, key in assets:

        start, stop = (spot - kills for spot in spots)

        back = start - revert

        if values[back:start] == escape:

            values = values[:back] + values[start:]

            kills += revert

            continue

        yield (current, values[:start])

        current = key

        values = values[stop:]

        kills += stop

    yield (current, values)
