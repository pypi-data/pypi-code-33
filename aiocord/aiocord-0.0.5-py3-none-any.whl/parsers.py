
from . import storage


__all__ = ('get_gateway', 'get_gateway_bot', 'get_channel', 'modify_channel',
           'delete_channel', 'get_channel_messages', 'get_channel_message',
           'create_message', 'get_reactions', 'edit_message',
           'get_channel_invites', 'create_channel_invite',
           'get_pinned_messages', 'list_guild_emojis', 'get_guild_emoji',
           'create_guild_emoji', 'modify_guild_emoji', 'create_guild',
           'get_guild', 'modify_guild', 'get_guild_channels',
           'create_guild_channel', 'get_guild_member', 'list_guild_members',
           'modify_current_user_nick', 'get_guild_bans', 'get_guild_ban',
           'get_guild_roles', 'create_guild_role',
           'modify_guild_role_positions', 'modify_guild_role',
           'get_guild_prune_count', 'begin_guild_prune',
           'get_guild_voice_regions', 'get_guild_invites',
           'get_guild_integrations', 'get_guild_embed', 'modify_guild_embed',
           'get_guild_vanity_url', 'get_invite', 'get_current_user', 'get_user',
           'modify_current_user', 'get_current_user_guilds', 'get_user_dms',
           'create_dm', 'get_user_connections', 'list_voice_regions',
           'create_webhook', 'get_channel_webhooks', 'get_guild_webhooks',
           'get_webhook', 'modify_webhook', 'modify_webhook_with_token',
           'execute_webhook')


def get_gateway(data):

    return storage.Gateway(data)


def get_gateway_bot(data):

    return storage.Gateway(data)


def get_channel(data):

    return storage.Channel(data)


def modify_channel(data):

    return storage.Channel(data)


def delete_channel(data):

    return storage.Channel(data)


def get_channel_messages(data):

    return map(storage.Message, data)


def get_channel_message(data):

    return storage.Message(data)


def create_message(data):

    return storage.Message(data)


def get_reactions(data):

    return map(storage.User, data)


def edit_message(data):

    return storage.Message(data)


def get_channel_invites(data):

    return map(storage.Invite, data)


def create_channel_invite(data):

    return storage.Invite(data)


def get_pinned_messages(data):

    return map(storage.Message, data)


def list_guild_emojis(data):

    return map(storage.Emoji, data)


def get_guild_emoji(data):

    return storage.Emoji(data)


def create_guild_emoji(data):

    return storage.Emoji(data)


def modify_guild_emoji(data):

    return storage.Emoji(data)


def create_guild(data):

    return storage.Guild(data)


def get_guild(data):

    return storage.Guild(data)


def modify_guild(data):

    return storage.Guild(data)


def get_guild_channels(data):

    return map(storage.Channel, data)


def create_guild_channel(data):

    return storage.Channel(data)


def get_guild_member(data):

    return storage.GuildMember(data)


def list_guild_members(data):

    return map(storage.GuildMember, data)


def modify_current_user_nick(data):

    return data


def get_guild_bans(data):

    return map(storage.Ban, data)


def get_guild_ban(data):

    return storage.Ban(data)


def get_guild_roles(data):

    return map(storage.Role, data)


def create_guild_role(data):

    return storage.Role(data)


def modify_guild_role_positions(data):

    return map(storage.Role, data)


def modify_guild_role(data):

    return storage.Role(data)


def get_guild_prune_count(data):

    return data['pruned']


def begin_guild_prune(data):

    return data['pruned']


def get_guild_voice_regions(data):

    return map(storage.VoiceRegion, data)


def get_guild_invites(data):

    return map(storage.Invite, data)


def get_guild_integrations(data):

    return map(storage.Integration, data)


def get_guild_embed(data):

    return storage.GuildEmbed(data)


def modify_guild_embed(data):

    return storage.GuildEmbed(data)


def get_guild_vanity_url(data):

    return storage.Invite(data)


def get_invite(data):

    return storage.Invite(data)


def get_current_user(data):

    return storage.User(data)


def get_user(data):

    return storage.User(data)


def modify_current_user(data):

    return storage.User(data)


def get_current_user_guilds(data):

    return map(storage.Guild, data)


def get_user_dms(data):

    return map(storage.Channel, data)


def create_dm(data):

    return storage.Channel(data)


def get_user_connections(data):

    return map(storage.Connection, data)


def list_voice_regions(data):

    return map(storage.VoiceRegion, data)


def create_webhook(data):

    return storage.Webhook(data)


def get_channel_webhooks(data):

    return map(storage.Webhook, data)


def get_guild_webhooks(data):

    return map(storage.Webhook, data)


def get_webhook(data):

    return storage.Webhook(data)


def modify_webhook(data):

    return storage.Webhook(data)


def modify_webhook_with_token(data):

    return modify_webhook(data)


def execute_webhook(data):

    return storage.Message(data) if data else data
