

__all__ = ()


gateway_events = (
    'ready',
    'resumed',
    'channel create',
    'channel update',
    'channel delete',
    'pins update',
    'members chunk',
    'guild create',
    'guild cache',
    'guild available',
    'guild update',
    'guild unavailable',
    'guild delete',
    'ban create',
    'ban delete',
    'emojis update',
    'integrations update',
    'member create',
    'member update',
    'member delete',
    'role create',
    'role update',
    'role delete',
    'message create',
    'message update',
    'message delete',
    'messages purge',
    'reaction create',
    'reaction delete',
    'reactions clear',
    'presence update',
    'typing start',
    'user update',
    'voice state update',
    'voice server update',
    'webhooks update'
)


voice_events = (
    'speaking',
)


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
