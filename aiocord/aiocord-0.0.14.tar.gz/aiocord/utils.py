import functools
import base64
import datetime
import re

from . import helpers


__all__ = ('Permissions', 'avatar_from_bytes', 'datetime_from_iso8601',
           'datetime_from_snowflake', 'datetime_from_unix', 'shard_id',
           'avatar_id')


class Permissions(helpers.BitGroup):

    indexes = {
        # general
        'create_instant_invite': 0,
        'kick_members': 1,
        'ban_members': 2,
        'administrator': 3,
        'manage_channels': 4,
        'manage_guild': 5,
        'add_reactions': 6,
        'view_audit_logs': 7,
        'change_nickname': 26,
        'manage_nicknames': 27,
        'manage_roles': 28,
        'manage_webhooks': 29,
        'manage_emojis': 30,
        # text
        'view_channel': 10,
        'send_messages': 11,
        'send_tts_Messages': 12,
        'manage_messages': 13,
        'embed_links': 14,
        'attach_files': 15,
        'read_message_history': 16,
        'mention_everyone': 17,
        'use_external_emojis': 18,
        # voice
        'voice_connect': 20,
        'voice_speak': 21,
        'voice_mute_members': 22,
        'voice_deafen_members': 23,
        'voice_move_members': 24,
        'voice_use_vad': 25
    }


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


def shard_id(guild_id, count):

    return (int(guild_id) >> 22) % count


def avatar_id(discriminator):

    return discriminator % 5
