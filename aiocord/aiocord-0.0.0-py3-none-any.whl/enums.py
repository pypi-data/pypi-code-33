import enum


__all__ = ('ChannelType', 'MessageType', 'MessageActivityType',
           'DefaultMessageNotificationLevel', 'ExplicitContentFilterLevel',
           'MfaLevel', 'VerificationLevel', 'ActivityTypes', 'ActivityFlags')


class ChannelType(enum.Enum):

    guild_text = 0
    dm = 1
    guild_voice = 2
    group_dm = 3
    guild_category = 4


class MessageType(enum.Enum):

    default = 0
    recipient_add = 1
    recipient_remove = 2
    call = 3
    channel_name_change = 4
    channel_icon_change = 5
    channel_pinned_message = 6
    guild_member_join = 7


class MessageActivityType(enum.Enum):

    join = 1
    spectate = 2
    listen = 3
    join_request = 5


class DefaultMessageNotificationLevel(enum.Enum):

    all_messages = 0
    only_mentions = 1


class ExplicitContentFilterLevel(enum.Enum):

    disabled = 0
    members_without_roles = 1
    all_members = 2


class MfaLevel(enum.Enum):

    none = 0
    elevated = 1


class VerificationLevel(enum.Enum):

    none = 0
    low = 1
    medium = 2
    high = 3
    very_high = 4


class ActivityTypes(enum.Enum):

    game = 0
    streaming = 1
    listening = 2


class ActivityFlags(enum.Enum):

    instance = 1 << 0
    join = 1 << 1
    spectate = 1 << 2
    join_request = 1 << 3
    sync = 1 << 4
    play = 1 << 5
