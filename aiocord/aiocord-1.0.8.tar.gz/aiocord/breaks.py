

__all__ = ('ready', 'resumed', 'channel_create', 'channel_update',
           'channel_delete', 'channel_pins_update', 'guild_create',
           'guild_update', 'guild_delete', 'guild_ban_add', 'guild_ban_remove',
           'guild_emojis_update', 'guild_integrations_update',
           'guild_member_add', 'guild_member_remove', 'guild_member_update',
           'guild_members_chunk', 'guild_role_create', 'guild_role_update',
           'guild_role_delete', 'message_create', 'message_update',
           'message_delete', 'message_delete_bulk', 'message_reaction_add',
           'message_reaction_remove', 'message_reaction_remove_all',
           'presence_update', 'typing_start', 'voice_state_update',
           'voice_server_update', 'webhooks_update')


def ready(data):

    version = data['v']

    user = data['user']

    channels = data['private_channels']

    guilds = data['guilds']

    session_id = data['session_id']

    return version, user, channels, guilds, session_id


def resumed(data):

    trace = data['_trace']

    return trace


def channel_create(data):

    guild_id = data.get('guild_id')

    channel = data

    return guild_id, channel


def channel_update(data):

    guild_id = data.get('guild_id')

    channel = data

    channel_id = channel['id']

    return guild_id, channel_id, channel


def channel_delete(data):

    guild_id = data.get('guild_id')

    channel_id = data['id']

    return guild_id, channel_id


def channel_pins_update(data):

    guild_id = data.get('guild_id')

    channel_id = data['channel_id']

    timestamp = data['last_pin_timestamp']

    return guild_id, channel_id, timestamp


def guild_create(data):

    guild = data

    return guild


def guild_update(data):

    guild = data

    guild_id = guild['id']

    return guild_id, guild


def guild_delete(data):

    guild = data

    guild_id = guild['id']

    unavailable = data.get('unavailable')

    return guild_id, unavailable


def guild_ban_add(data):

    guild_id = data['guild_id']

    user = data['user']

    return guild_id, user


def guild_ban_remove(data):

    guild_id = data['guild_id']

    user = data['user']

    return guild_id, user


def guild_emojis_update(data):

    guild_id = data['guild_id']

    emojis = data['emojis']

    return guild_id, emojis


def guild_integrations_update(data):

    guild_id = data['guild_id']

    return guild_id


def guild_member_add(data):

    guild_id = data['guild_id']

    member = data

    return guild_id, member


def guild_member_remove(data):

    guild_id = data['guild_id']

    user = data

    return guild_id, user


def guild_member_update(data):

    guild_id = data['guild_id']

    user = data

    return guild_id, user


def guild_members_chunk(data):

    guild_id = data['guild_id']

    members = data['members']

    return guild_id, members


def guild_role_create(data):

    guild_id = data['guild_id']

    role = data['role']

    return guild_id, role


def guild_role_update(data):

    guild_id = data['guild_id']

    role = data['role']

    role_id = role['id']

    return guild_id, role_id, role


def guild_role_delete(data):

    guild_id = data['guild_id']

    role_id = data['role_id']

    return guild_id, role_id


def message_create(data):

    guild_id = data.get('guild_id')

    channel_id = data['channel_id']

    message = data

    return guild_id, channel_id, message


def message_update(data):

    guild_id = data.get('guild_id')

    channel_id = data['channel_id']

    message = data

    message_id = message['id']

    return guild_id, channel_id, message_id, message


def message_delete(data):

    guild_id = data.get('guild_id')

    channel_id = data['channel_id']

    message = data

    message_id = message['id']

    return guild_id, channel_id, message_id


def message_delete_bulk(data):

    guild_id = data.get('guild_id')

    channel_id = data['channel_id']

    message_ids = data['ids']

    return guild_id, channel_id, message_ids


def message_reaction_add(data):

    guild_id = data.get('guild_id')

    channel_id = data['channel_id']

    message_id = data['message_id']

    user_id = data['user_id']

    emoji = data['emoji']

    return guild_id, channel_id, message_id, user_id, emoji


def message_reaction_remove(data):

    guild_id = data.get('guild_id')

    channel_id = data['channel_id']

    message_id = data['message_id']

    user_id = data['user_id']

    emoji = data['emoji']

    return guild_id, channel_id, message_id, user_id, emoji


def message_reaction_remove_all(data):

    guild_id = data.get('guild_id')

    channel_id = data['channel_id']

    message_id = data['message_id']

    return guild_id, channel_id, message_id


def presence_update(data):

    guild_id = data.get('guild_id')

    user_id = data['user']['id']

    presence = data

    return guild_id, user_id, data


def typing_start(data):

    guild_id = data.get('guild_id')

    channel_id = data['channel_id']

    user_id = data['user_id']

    timestamp = data['timestamp']

    return guild_id, channel_id, user_id, timestamp


def voice_state_update(data):

    guild_id = data.get('guild_id')

    channel_id = data['channel_id']

    user_id = data['user_id']

    voice_state = data

    return guild_id, channel_id, user_id, voice_state


def voice_server_update(data):

    guild_id = data['guild_id']

    endpoint = data['endpoint']

    token = data['token']

    return guild_id, endpoint, token


def webhooks_update(data):

    guild_id = data['guild_id']

    channel_id = data['channel_id']

    return guild_id, channel_id
