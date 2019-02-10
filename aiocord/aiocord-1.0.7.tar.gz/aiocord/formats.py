import functools
import itertools


__all__ = ('user', 'channel', 'role', 'emoji')


def _format(prefix, value):

    return f'<{prefix}{value}>'


def user(user_id, nick = False):

    prefix = '@!' if nick else '@'

    value = user_id

    return _format(prefix, value)


def channel(channel_id):

    prefix = '#'

    value = channel_id

    return _format(prefix, value)


def role(role_id):

    prefix = '@&'

    value = role_id

    return _format(prefix, role_id)


def emoji(emoji_name, emoji_id, animated = False):

    prefix = 'a' if animated else ''

    value = f':{emoji_name}:{emoji_id}'

    return _format(prefix, value)


def _images_format(path,
                   host = 'https://cdn.discordapp.com/',
                   extension = 'png',
                   size = 2 ** 11):

    return f'{host}/{path}.{extension}?size={size}'


_images_bases = {
    'custom_emoji': 'emojis/',
    'guild_icon': 'icons/',
    'guild_splash': 'splashes/',
    'default_user_avatar': 'embed/avatars/',
    'user_avatar': 'avatars/',
    'application_icon': 'app-icons/',
    'application_asset': 'app-assets/'
}


def _images_handle(base, *parts, **kwargs):

    path = base + '/'.join(map(str, parts))

    return _images_format(path, **kwargs)


_handles = (
    (_images_bases, _images_handle),
)


@functools.lru_cache(maxsize = None)
def __getattr__(key):

    for (values, handle) in _handles:

        try:

            value = values[key]

        except KeyError:

            continue

        break

    else:

        raise AttributeError(key) from None

    return functools.partial(handle, value)


__all__ = (*__all__, *_images_bases.keys())
