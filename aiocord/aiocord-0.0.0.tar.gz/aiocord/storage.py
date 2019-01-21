import functools
import collections

from . import helpers


__all__ = ()


missing = object()


class Structure:

    __slots__ = ('__dict__',)

    def __init__(self, *args, **extra):

        try:

            (data,) = args

        except ValueError:

            pass

        else:

            extra.update(data)

        update_structure(self, extra)

    def __getattr__(self, name, forbidden = '__'):

        if name.startswith(forbidden):

            raise AttributeError(name)

        blueprint = _blueprint(self.__class__)

        available = blueprint.keys()

        if name in available:

            return missing

        raise AttributeError(name)

    def __repr__(self):

        return f'<{self.__class__.__name__}>'


@functools.lru_cache(maxsize = None)
def _structure(name):

    bases = (Structure,)

    namespace = {}

    value = type(name, bases, namespace)

    return value


@functools.lru_cache(maxsize = None)
def _blueprint(structure):

    return _blueprints[structure.__name__]


@functools.lru_cache(maxsize = None)
def _structure_update():

    skip = (missing,)

    place = (Structure, list, dict)

    def wrapper(value, data):

        blueprint = _blueprint(value.__class__)

        return helpers.update_generic(blueprint, value, data, skip = skip)

    return wrapper


def update_structure(value, data):

    return _structure_update()(value, data)


@functools.lru_cache(maxsize = None)
def _list_update(build):

    update = _structure_update()

    return helpers.cached_partial(helpers.update_list, update, build)


def update_list(build, *args, **kwargs):

    return _list_update(build)(*args, **kwargs)


@functools.lru_cache(maxsize = None)
def _dict_update(build, keys):

    update = _structure_update()

    identify = helpers.cached_partial(helpers.crawl, keys)

    return helpers.cached_partial(helpers.update_dict, update, build, identify)


def update_dict(build, keys, *args, **kwargs):

    return _dict_update(build, keys)(*args, **kwargs)


@functools.lru_cache(maxsize = None)
def _field(create, update):

    return (create, update)


_string = str


_integer = int


_boolean = bool


_list = list


_dict = dict


_blueprints = {
    'Channel': {
        'id': _field(
            _string,
            None
        ),
        'type': _field(
            _integer,
            None
        ),
        'guild_id': _field(
            _string,
            None
        ),
        'position': _field(
            _integer,
            None
        ),
        'permission_overwrites': _field(
            _dict,
            _dict_update(_structure('Overwrite'), ('id',))
        ),
        'name': _field(
            _string,
            None
        ),
        'topic': _field(
            _string,
            None
        ),
        'nsfw': _field(
            _boolean,
            None
        ),
        'last_message_id': _field(
            _string,
            None
        ),
        'bitrate': _field(
            _integer,
            None
        ),
        'user_limit': _field(
            _integer,
            None
        ),
        'rate_limit_per_user': _field(
            _integer,
            None
        ),
        'recipients': _field(
            _dict,
            _dict_update(_structure('User'), ('id',))
        ),
        'icon': _field(
            _string,
            None
        ),
        'owner_id': _field(
            _string,
            None
        ),
        'application_id': _field(
            _string,
            None
        ),
        'parent_id': _field(
            _string,
            None
        ),
        'last_pin_timestamp': _field(
            _string,
            None
        )
    },
    'Message': {
        'id': _field(
            _string,
            None
        ),
        'channel_id': _field(
            _string,
            None
        ),
        'guild_id': _field(
            _string,
            None
        ),
        'author': _field(
            _structure('User'),
            _structure_update(),
        ),
        'content': _field(
            _string,
            None
        ),
        'timestamp': _field(
            _string,
            None
        ),
        'edited_timestamp': _field(
            _string,
            None
        ),
        'tts': _field(
            _boolean,
            None
        ),
        'mention_everyone': _field(
            _boolean,
            None
        ),
        'mentions': _field(
            _list,
            _list_update(_structure('User'))
        ),
        'mention_roles': _field(
            _list,
            _list_update(_string)
        ),
        'attachments': _field(
            _list,
            _list_update(_structure('Attachment'))
        ),
        'embeds': _field(
            _list,
            _list_update(_structure('Embed'))
        ),
        'reactions': _field(
            _list,
            _list_update(_structure('Reaction'))
        ),
        'nonce': _field(
            _integer,
            None
        ),
        'pinned': _field(
            _boolean,
            None
        ),
        'webhook_id': _field(
            _string,
            None
        ),
        'type': _field(
            _integer,
            None
        ),
        'activity': _field(
            _structure('MessageActivity'),
            _structure_update()
        ),
        'application': _field(
            _structure('MessageApplication'),
            _structure_update()
        )
    },
    'MessageActivity': {
        'type': _field(
            _integer,
            None
        ),
        'party_id': _field(
            _string,
            None
        )
    },
    'MessageApplication': {
        'id': _field(
            _string,
            None
        ),
        'cover_image': _field(
            _string,
            None
        ),
        'description': _field(
            _string,
            None
        ),
        'icon': _field(
            _string,
            None
        ),
        'name': _field(
            _string,
            None
        )
    },
    'Reaction': {
        'count': _field(
            _integer,
            None
        ),
        'me': _field(
            _boolean,
            None
        ),
        'emoji': _field(
            _structure('Emoji'),
            _structure_update()
        )
    },
    'Overwrite': {
        'id': _field(
            _string,
            None
        ),
        'type': _field(
            _string,
            None
        ),
        'allow': _field(
            _string,
            None
        ),
        'deny': _field(
            _string,
            None
        )
    },
    'Embed': {
        'title': _field(
            _string,
            None
        ),
        'type': _field(
            _string,
            None
        ),
        'description': _field(
            _string,
            None
        ),
        'url': _field(
            _string,
            None
        ),
        'timestamp': _field(
            _string,
            None
        ),
        'color': _field(
            _integer,
            None
        ),
        'footer': _field(
            _structure('EmbedFooter'),
            _structure_update()
        ),
        'image': _field(
            _structure('EmbedImage'),
            _structure_update()
        ),
        'thumbnail': _field(
            _structure('EmbedThumbnail'),
            _structure_update()
        ),
        'video': _field(
            _structure('EmbedVideo'),
            _structure_update()
        ),
        'provider': _field(
            _structure('EmbedProvider'),
            _structure_update()
        ),
        'author': _field(
            _structure('EmbedAuthor'),
            _structure_update()
        ),
        'fields': _field(
            _list,
            _list_update(_structure('EmbedField'))
        )
    },
    'EmbedThumbnail': {
        'url': _field(
            _string,
            None
        ),
        'proxy_url': _field(
            _string,
            None
        ),
        'height': _field(
            _integer,
            None
        ),
        'width': _field(
            _integer,
            None
        )
    },
    'EmbedVideo': {
        'url': _field(
            _string,
            None
        ),
        'height': _field(
            _integer,
            None
        ),
        'width': _field(
            _integer,
            None
        )
    },
    'EmbedImage': {
        'url': _field(
            _string,
            None
        ),
        'proxy_url': _field(
            _string,
            None
        ),
        'height': _field(
            _integer,
            None
        ),
        'width': _field(
            _integer,
            None
        )
    },
    'EmbedProvider': {
        'name': _field(
            _string,
            None
        ),
        'url': _field(
            _string,
            None
        )
    },
    'EmbedAuthor': {
        'name': _field(
            _string,
            None
        ),
        'url': _field(
            _string,
            None
        ),
        'icon_url': _field(
            _string,
            None
        ),
        'proxy_icon_url': _field(
            _string,
            None
        )
    },
    'EmbedFooter': {
        'text': _field(
            _string,
            None
        ),
        'icon_url': _field(
            _string,
            None
        ),
        'proxy_icon_url': _field(
            _string,
            None
        )
    },
    'EmbedField': {
        'name': _field(
            _string,
            None
        ),
        'value': _field(
            _string,
            None
        ),
        'inline': _field(
            _boolean,
            None
        )
    },
    'Attachment': {
        'id': _field(
            _string,
            None
        ),
        'filename': _field(
            _string,
            None
        ),
        'size': _field(
            _integer,
            None
        ),
        'url': _field(
            _string,
            None
        ),
        'proxy_url': _field(
            _string,
            None
        ),
        'height': _field(
            _integer,
            None
        ),
        'width': _field(
            _integer,
            None
        )
    },
    'Emoji': {
        'id': _field(
            _string,
            None
        ),
        'name': _field(
            _string,
            None
        ),
        'roles': _field(
            _list,
            _list_update(_string)
        ),
        'require_colons': _field(
            _boolean,
            None
        ),
        'managed': _field(
            _boolean,
            None
        ),
        'animated': _field(
            _boolean,
            None
        )
    },
    'Guild': {
        'id': _field(
            _string,
            None
        ),
        'name': _field(
            _string,
            None
        ),
        'icon': _field(
            _string,
            None
        ),
        'splash': _field(
            _string,
            None
        ),
        'owner': _field(
            _boolean,
            None
        ),
        'owner_id': _field(
            _string,
            None
        ),
        'permissions': _field(
            _integer,
            None
        ),
        'region': _field(
            _string,
            None
        ),
        'afk_channel_id': _field(
            _string,
            None
        ),
        'afk_timeout': _field(
            _integer,
            None
        ),
        'embed_enabled': _field(
            _boolean,
            None
        ),
        'embed_channel_id': _field(
            _string,
            None
        ),
        'verification_level': _field(
            _integer,
            None
        ),
        'default_message_notifications': _field(
            _integer,
            None,
        ),
        'explicit_content_filter': _field(
            _integer,
            None
        ),
        'roles': _field(
            _dict,
            _dict_update(_structure('Role'), ('id',))
        ),
        'emojis': _field(
            _dict,
            _dict_update(_structure('Emoji'), ('id',))
        ),
        'features': _field(
            _list,
            _list_update(_string)
        ),
        'mfa_level': _field(
            _integer,
            None
        ),
        'application_id': _field(
            _string,
            None
        ),
        'widget_enabled': _field(
            _boolean,
            None
        ),
        'widget_channel_id': _field(
            _string,
            None
        ),
        'system_channel_id': _field(
            _string,
            None
        ),
        'joined_at': _field(
            _string,
            None
        ),
        'large': _field(
            _boolean,
            None
        ),
        'unavailable': _field(
            _boolean,
            None
        ),
        'member_count': _field(
            _integer,
            None
        ),
        'voice_states': _field(
            _dict,
            _dict_update(_structure('VoiceState'), ('user_id',))
        ),
        'members': _field(
            _dict,
            _dict_update(_structure('GuildMember'), ('user', 'id'))
        ),
        'channels': _field(
            _dict,
            _dict_update(_structure('Channel'), ('id',))
        ),
        'presences': _field(
            _dict,
            _dict_update(_structure('Presence'), ('user', 'id'))
        )
    },
    'GuildEmbed': {
        'enabled': _field(
            _boolean,
            None
        ),
        'channel_id': _field(
            _string,
            None
        )
    },
    'GuildMember': {
        'user': _field(
            _structure('User'),
            _structure_update()
        ),
        'nick': _field(
            _string,
            None
        ),
        'roles': _field(
            _list,
            _list_update(_string)
        ),
        'joined_at': _field(
            _string,
            None
        ),
        'deaf': _field(
            _boolean,
            None
        ),
        'mute': _field(
            _boolean,
            None
        )
    },
    'Integration': {
        'id': _field(
            _string,
            None
        ),
        'name': _field(
            _string,
            None
        ),
        'type': _field(
            _string,
            None
        ),
        'enabled': _field(
            _boolean,
            None
        ),
        'syncing': _field(
            _boolean,
            None
        ),
        'role_id': _field(
            _string,
            None
        ),
        'expire_behavior': _field(
            _integer,
            None
        ),
        'expire_grace_period': _field(
            _integer,
            None
        ),
        'user': _field(
            _structure('User'),
            _structure_update()
        ),
        'account': _field(
            _structure('IntegrationAccount'),
            _structure_update()
        ),
        'synced_at': _field(
            _string,
            None
        )
    },
    'IntegrationAccount': {
        'id': _field(
            _string,
            None
        ),
        'name': _field(
            _string,
            None
        )
    },
    'Ban': {
        'reason': _field(
            _string,
            None
        ),
        'user': _field(
            _structure('User'),
            _structure_update()
        )
    },
    'Invite': {
        'code': _field(
            _string,
            None
        ),
        'guild': _field(
            _structure('Guild'),
            _structure_update()
        ),
        'channel': _field(
            _structure('Channel'),
            _structure_update()
        ),
        'inviter': _field(
            _structure('User'),
            _structure_update()
        ),
        'uses': _field(
            _integer,
            None
        ),
        'max_uses': _field(
            _integer,
            None
        ),
        'max_age': _field(
            _integer,
            None
        ),
        'temporary': _field(
            _boolean,
            None
        ),
        'created_at': _field(
            _string,
            None
        ),
        'revoked': _field(
            _boolean,
            None
        )
    },
    'User': {
        'id': _field(
            _string,
            None
        ),
        'username': _field(
            _string,
            None
        ),
        'discriminator': _field(
            _string,
            None
        ),
        'avatar': _field(
            _string,
            None
        ),
        'bot': _field(
            _boolean,
            None
        ),
        'mfa_enabled': _field(
            _boolean,
            None
        ),
        'locale': _field(
            _string,
            None
        ),
        'verified': _field(
            _boolean,
            None
        ),
        'email': _field(
            _string,
            None
        ),
        'flags': _field(
            _integer,
            None
        ),
        'premium_type': _field(
            _integer,
            None
        )
    },
    'Connection': {
        'id': _field(
            _string,
            None
        ),
        'name': _field(
            _string,
            None
        ),
        'type': _field(
            _string,
            None
        ),
        'revoked': _field(
            _boolean,
            None
        ),
        'integrations': _field(
            _list,
            _list_update(_structure('Integration'))
        )
    },
    'VoiceState': {
        'guild_id': _field(
            _string,
            None
        ),
        'channel_id': _field(
            _string,
            None
        ),
        'user_id': _field(
            _string,
            None
        ),
        'member': _field(
            _structure('GuildMember'),
            _structure_update()
        ),
        'session_id': _field(
            _string,
            None
        ),
        'deaf': _field(
            _boolean,
            None
        ),
        'mute': _field(
            _boolean,
            None
        ),
        'self_deaf': _field(
            _boolean,
            None
        ),
        'self_mute': _field(
            _boolean,
            None
        ),
        'suppress': _field(
            _boolean,
            None
        )
    },
    'VoiceRegion': {
        'id': _field(
            _string,
            None
        ),
        'name': _field(
            _string,
            None
        ),
        'vip': _field(
            _boolean,
            None
        ),
        'optimal': _field(
            _boolean,
            None
        ),
        'deprecated': _field(
            _boolean,
            None
        ),
        'custom': _field(
            _boolean,
            None
        )
    },
    'Webhook': {
        'id': _field(
            _string,
            None
        ),
        'guild_id': _field(
            _string,
            None
        ),
        'channel_id': _field(
            _string,
            None
        ),
        'user': _field(
            _structure('User'),
            _structure_update()
        ),
        'name': _field(
            _string,
            None
        ),
        'avatar': _field(
            _string,
            None
        ),
        'token': _field(
            _string,
            None
        )
    },
    'Presence': {
        'user': _field(
            _structure('User'),
            _structure_update()
        ),
        'roles': _field(
            _list,
            _list_update(_string)
        ),
        'game': _field(
            _structure('Activity'),
            _structure_update()
        ),
        'guild_id': _field(
            _string,
            None
        ),
        'status': _field(
            _string,
            None
        ),
        'activities': _field(
            _dict,
            _dict_update(_structure('Activity'), ('name',))
        )
    },
    'Activity': {
        'name': _field(
            _string,
            None
        ),
        'type': _field(
            _integer,
            None
        ),
        'url': _field(
            _string,
            None
        ),
        'timestamps': _field(
            _structure('ActivityTimestamps'),
            _structure_update()
        ),
        'application_id': _field(
            _string,
            None
        ),
        'details': _field(
            _string,
            None
        ),
        'state': _field(
            _string,
            None
        ),
        'party': _field(
            _structure('ActivityParty'),
            _structure_update()
        ),
        'assets': _field(
            _structure('ActivityAssets'),
            _structure_update()
        ),
        'secrets': _field(
            _structure('ActivitySecrets'),
            _structure_update()
        ),
        'instance': _field(
            _boolean,
            None
        ),
        'flags': _field(
            _integer,
            None
        )
    },
    'ActivityTimestamps': {
        'start': _field(
            _integer,
            None
        ),
        'end': _field(
            _integer,
            None
        )
    },
    'ActivityParty': {
        'id': _field(
            _string,
            None
        ),
        'size': _field(
            _list,
            _list_update(_integer)
        )
    },
    'ActivityAssets': {
        'large_image': _field(
            _string,
            None
        ),
        'large_text': _field(
            _string,
            None
        ),
        'small_image': _field(
            _string,
            None
        ),
        'small_text': _field(
            _string,
            None
        )
    },
    'ActivitySecrets': {
        'join': _field(
            _string,
            None
        ),
        'spectate': _field(
            _string,
            None
        ),
        'match': _field(
            _string,
            None
        )
    },
    'Role': {
        'id': _field(
            _string,
            None
        ),
        'name': _field(
            _string,
            None
        ),
        'color': _field(
            _integer,
            None
        ),
        'hoist': _field(
            _boolean,
            None
        ),
        'position': _field(
            _integer,
            None
        ),
        'permissions': _field(
            _integer,
            None
        ),
        'managed': _field(
            _boolean,
            None
        ),
        'mentionable': _field(
            _boolean,
            None
        )
    },
    'Gateway': {
        'url': _field(
            _string,
            None
        ),
        'shards': _field(
            _integer,
            None
        ),
        'session_start_limit': _field(
            _structure('SessionStartLimit'),
            _structure_update()
        )
    },
    'SessionStartLimit': {
        'total': _field(
            _integer,
            None
        ),
        'remaining': _field(
            _integer,
            None
        ),
        'reset_after': _field(
            _integer,
            None
        )
    }
}


@functools.lru_cache(maxsize = None)
def __getattr__(name):

    available = _blueprints.keys()

    if not name in available:

        raise AttributeError(name)

    return _structure(name)


__all__ = ('missing', 'Structure', *_blueprints.keys())
