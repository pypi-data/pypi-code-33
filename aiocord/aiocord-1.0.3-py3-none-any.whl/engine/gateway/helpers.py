

__all__ = ()


def events_from_client(value):

    events = {
        'READY': value.ready,
        'RESUMED': value.resumed,
        'CHANNEL_CREATE': value.channel_create,
        'CHANNEL_UPDATE': value.channel_update,
        'CHANNEL_DELETE': value.channel_delete,
        'CHANNEL_PINS_UPDATE': value.channel_pins_update,
        'GUILD_CREATE': value.guild_create,
        'GUILD_UPDATE': value.guild_update,
        'GUILD_DELETE': value.guild_delete,
        'GUILD_BAN_ADD': value.guild_ban_add,
        'GUILD_BAN_REMOVE': value.guild_ban_remove,
        'GUILD_EMOJIS_UPDATE': value.guild_emojis_update,
        'GUILD_INTEGRATIONS_UPDATE': value.guild_integrations_update,
        'GUILD_MEMBER_ADD': value.guild_member_add,
        'GUILD_MEMBER_REMOVE': value.guild_member_remove,
        'GUILD_MEMBER_UPDATE': value.guild_member_update,
        'GUILD_MEMBERS_CHUNK': value.guild_members_chunk,
        'GUILD_ROLE_CREATE': value.guild_role_create,
        'GUILD_ROLE_UPDATE': value.guild_role_update,
        'GUILD_ROLE_DELETE': value.guild_role_delete,
        'MESSAGE_CREATE': value.message_create,
        'MESSAGE_UPDATE': value.message_update,
        'MESSAGE_DELETE': value.message_delete,
        'MESSAGE_DELETE_BULK': value.message_delete_bulk,
        'MESSAGE_REACTION_ADD': value.message_reaction_add,
        'MESSAGE_REACTION_REMOVE': value.message_reaction_remove,
        'MESSAGE_REACTION_REMOVE_ALL': value.message_reaction_remove_all,
        'PRESENCE_UPDATE': value.presence_update,
        'TYPING_START': value.typing_start,
        'USER_UPDATE': value.user_update,
        'VOICE_STATE_UPDATE': value.voice_state_update,
        'VOICE_SERVER_UPDATE': value.voice_server_update,
        'WEBHOOKS_UPDATE': value.webhooks_update
    }

    return events
