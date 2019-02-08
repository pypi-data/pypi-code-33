
from . import breaks


__all__ = ('Handle',)


class Handle:

    __slots__ = ('_cache',)

    def __init__(self, cache):

        self._cache = cache

    def ready(self, data):

        parts = breaks.ready(data)

        version, user_data, channels_data, guilds_data, session_id = parts

        guild_ids = self._cache.ready(user_data, channels_data, guilds_data)

        return version, guild_ids, session_id

    def channel_create(self, data):

        guild_id, channel_data = breaks.channel_create(data)

        guild, channel = self._cache.channel_create(guild_id, channel_data)

        return guild, channel

    def channel_update(self, data):

        guild_id, channel_id, channel_data = breaks.channel_update(data)

        parts = (guild_id, channel_id, channel_data)

        guild, channel, old_channel = self._cache.channel_update(*parts)

        return guild, channel, old_channel

    def channel_delete(self, data):

        guild_id, channel_id = breaks.channel_delete(data)

        guild, channel = self._cache.channel_delete(guild_id, channel_id)

        return guild, channel

    def channel_pins_update(self, data):

        guild_id, channel_id, timestamp = breaks.channel_pins_update(data)

        guild, channel = self._cache.channel_pins_update(guild_id, channel_id)

        return guild, channel, timestamp

    def guild_create(self, data):

        guild_data = breaks.guild_create(data)

        guild = self._cache.guild_create(guild_data)

        return guild

    def guild_update(self, data):

        guild_id, guild_data = breaks.guild_update(data)

        guild, old_guild = self._cache.guild_update(guild_id, guild_data)

        return guild, old_guild

    def guild_delete(self, data):

        guild_id, unavailable = breaks.guild_delete(data)

        guild = self._cache.guild_delete(guild_id)

        return guild, unavailable

    def guild_ban_add(self, data):

        guild_id, user_data = breaks.guild_ban_add(data)

        guild, user = self._cache.guild_ban_add(guild_id, user_data)

        return guild, user

    def guild_ban_remove(self, data):

        guild_id, user_data = breaks.guild_ban_remove(data)

        guild, user = self._cache.guild_ban_remove(guild_id, user_data)

        return guild, user

    def guild_emojis_update(self, data):

        guild_id, emojis_data = breaks.guild_emojis_update(data)

        parts = (guild_id, emojis_data)

        guild, old_emojis = self._cache.guild_emojis_update(*parts)

        return guild, old_emojis

    def guild_integrations_update(self, data):

        guild_id = breaks.guild_integrations_update(data)

        guild = self._cache.guild_integrations_update(guild_id)

        return guild

    def guild_member_add(self, data):

        guild_id, member_data = breaks.guild_member_add(data)

        guild, member = self._cache.guild_member_add(guild_id, member_data)

        return guild, member

    def guild_member_remove(self, data):

        guild_id, user_data = breaks.guild_member_remove(data)

        parts = (guild_id, user_data)

        guild, member = self._cache.guild_member_remove(*parts)

        return guild, member

    def guild_member_update(self, data):

        guild_id, member_data = breaks.guild_member_update(data)

        parts = (guild_id, member_data)

        guild, member, old_member = self._cache.guild_member_update(*parts)

        return guild, member, old_member

    def guild_members_chunk(self, data):

        guild_id, members_data = breaks.guild_members_chunk(data)

        guild = self._cache.guild_members_chunk(guild_id, members_data)

        return guild

    def guild_role_create(self, data):

        guild_id, role_data = breaks.guild_role_create(data)

        guild, role = self._cache.guild_role_create(guild_id, role_data)

        return guild, role

    def guild_role_update(self, data):

        guild_id, role_id, role_data = breaks.guild_role_update(data)

        parts = (guild_id, role_id, role_data)

        guild, role, old_role = self._cache.guild_role_update(*parts)

        return guild, role, old_role

    def guild_role_delete(self, data):

        guild_id, role_id = breaks.guild_role_delete(data)

        guild, role = self._cache.guild_role_delete(guild_id, role_id)

        return guild, role

    def message_create(self, data):

        guild_id, channel_id, message_data = breaks.message_create(data)

        parts = (guild_id, channel_id, message_data)

        guild, channel, message = self._cache.message_create(*parts)

        return guild, channel, message

    def message_update(self, data):

        parts = breaks.message_update(data)

        guild_id, channel_id, message_id, message_data = parts

        parts = (guild_id, channel_id, message_id, message_data)

        values = self._cache.message_update(*parts)

        guild, channel, message, old_message = values

        return guild, channel, message, old_message

    def message_delete(self, data):

        guild_id, channel_id, message_id = breaks.message_delete(data)

        parts = (guild_id, channel_id, message_id)

        guild, channel, message = self._cache.message_delete(*parts)

        return guild, channel, message

    def message_delete_bulk(self, data):

        guild_id, channel_id, message_ids = breaks.message_delete_bulk(data)

        parts = (guild_id, channel_id, message_ids)

        guild, channel, messages = self._cache.message_delete_bulk(*parts)

        return guild, channel, messages

    def message_reaction_add(self, data):

        parts = breaks.message_reaction_add(data)

        guild_id, channel_id, message_id, user_id, emoji_data = parts

        parts = (guild_id, channel_id, message_id, user_id, emoji_data)

        values = self._cache.message_reaction_add(*parts)

        guild, channel, message, user, emoji = values

        return guild, channel, message, user, emoji

    def message_reaction_remove(self, data):

        parts = breaks.message_reaction_remove(data)

        guild_id, channel_id, message_id, user_id, emoji_data = parts

        parts = (guild_id, channel_id, message_id, user_id, emoji_data)

        values = self._cache.message_reaction_remove(*parts)

        guild, channel, message, user, emoji = values

        return guild, channel, message, user, emoji

    def message_reaction_remove_all(self, data):

        parts = breaks.message_reaction_remove_all(data)

        guild_id, channel_id, message_id = parts

        parts = (guild_id, channel_id, message_id)

        values = self._cache.message_reaction_remove_all(*parts)

        guild, channel, message, reactions = values

        return guild, channel, message, reactions

    def presence_update(self, data):

        guild_id, user_id, presence_data = breaks.presence_update(data)

        guild_ids = (guild_id,) if guild_id else self._cache.guilds.keys()

        for guild_id in guild_ids:

            parts = (guild_id, user_id, presence_data)

            values = self._cache.presence_update(*parts)

            yield values

    def typing_start(self, data):

        guild_id, channel_id, user_id, timestamp = breaks.typing_start(data)

        parts = (guild_id, channel_id, user_id)

        guild, channel, user = self._cache.typing_start(*parts)

        return guild, channel, user, timestamp

    def user_update(self, data):

        user_data = data

        user, old_user = self._cache.user_update(data)

        return user, old_user

    def voice_state_update(self, data):

        parts = breaks.voice_state_update(data)

        guild_id, channel_id, user_id, state_data = parts

        parts = (guild_id, channel_id, user_id, state_data)

        values = self._cache.voice_state_update(*parts)

        guild, channel, user, state, old_state = values

        return guild, channel, user, state, old_state

    def voice_server_update(self, data):

        guild_id, endpoint, token = breaks.voice_server_update(data)

        guild = self._cache.voice_server_update(guild_id)

        return guild, endpoint, token

    def webhooks_update(self, data):

        guild_id, channel_id = breaks.webhooks_update(data)

        guild, channel = self._cache.webhooks_update(guild_id, channel_id)

        return guild, channel
