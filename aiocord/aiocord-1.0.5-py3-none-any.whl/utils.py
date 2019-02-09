import functools
import base64
import datetime
import re

from . import helpers


__all__ = ('Permissions', 'avatar_from_bytes', 'datetime_from_iso8601',
           'datetime_from_snowflake', 'datetime_from_unix', 'shard_id',
           'avatar_id')


class PermissionsMeta(type):

    __slots__ = ()

    indexes = {
        # general
        'create_instant_invite': 0x1,
        'kick_members': 0x2,
        'ban_members': 0x4,
        'administrator': 0x8,
        'manage_channels': 0x10,
        'manage_guild': 0x20,
        'add_reactions': 0x40,
        'view_audit_logs': 0x80,
        'change_nickname': 0x4000000,
        'manage_nicknames': 0x8000000,
        'manage_roles': 0x10000000,
        'manage_webhooks': 0x20000000,
        'manage_emojis': 0x40000000,
        # text
        'view_channel': 0x400,
        'send_messages': 0x800,
        'send_tts_Messages': 0x1000,
        'manage_messages': 0x2000,
        'embed_links': 0x4000,
        'attach_files': 0x8000,
        'read_message_history': 0x10000,
        'mention_everyone': 0x20000,
        'use_external_emojis': 0x40000,
        # voice
        'connect': 0x100000,
        'speak': 0x200000,
        'mute_members': 0x400000,
        'deafen_members': 0x800000,
        'move_members': 0x1000000,
        'use_vad': 0x2000000,
        'priority_speaker': 0x100,
    }

    def none(self):

        return self(0)

    def some(self, values):

        return functools.reduce(self.add, values, self.none())

    def full(self):

        return self.some(self.indexes.values())

    def in_guild(self, guild, member):

        if guild.owner_id == member.user.id:

            return self.full()

        roles = (guild.roles[role_id] for role_id in member.roles)

        values = (role.permissions for role in roles)

        default = guild.roles[guild.id]

        return self.some(values).add(default.permissions)

    @functools.lru_cache(maxsize = None)
    def __getattr__(self, key):

        try:

            index = self.indexes[key]

        except KeyError:

            raise AttributeError(key) from None

        return self(index)


class Permissions(helpers.BitGroup, metaclass = PermissionsMeta):

    __slots__ = ()

    indexes = PermissionsMeta.indexes

    bypass = indexes['administrator']

    def can(self, index):

        return index == bypass or super().can(index)

    def __add__(self, other):

        return self.__class__(self.add(other))

    def __sub__(self, other):

        return self.__class__(self.pop(other))

    def __getattr__(self, key):

        try:

            index = self.indexes[key]

        except KeyError:

            raise AttributeError(key) from None

        return super().can(index)


def avatar_from_bytes(value):

    mime = helpers.mime_from_bytes(value)

    data = base64.b64encode(value).decode('ascii')

    return f'data:{mime};base64,{data}'


timezone = datetime.timezone.utc


def datetime_from_iso8601(timestamp, cleaner = re.compile(r'[^\d]')):

    naive = timestamp.replace('+00:00', '')

    cleans = cleaner.split(naive)

    values = map(int, cleans)

    return datetime.datetime(*values, tzinfo = timezone)


def unix_from_snowflake(snowflake, epoch = 1420070400000):

    return (int(snowflake) >> 22) + epoch


def timestamp_from_unix(unix):

    return unix / 1000


def timestamp_from_snowflake(snowflake):

    return timestamp_from_unix(unix_from_snowflake(snowflake))


def datetime_from_timestamp(timestamp):

    return datetime.datetime.fromtimestamp(timestamp, timezone)


def datetime_from_snowflake(snowflake):

    return datetime_from_timestamp(timestamp_from_snowflake(snowflake))


def shard_id(guild_id, shard_count):

    return (int(guild_id) >> 22) % shard_count


def avatar_id(discriminator):

    return discriminator % 5
