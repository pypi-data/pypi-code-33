import asyncio
import aiocord


__all__ = ('Client',)


class Client:

    __slots__ = ('_client',)

    def __init__(self, client):

        self._client = client

    async def get_gateway(self):

        data = await self._client.get_gateway()

        value = aiocord.get_gateway(data)

        return value

    async def get_gateway_bot(self):

        data = await self._client.get_gateway_bot()

        value = aiocord.get_gateway_bot(data)

        return value

    async def get_audit_log(self, *path, **data):

        data = await self._client.get_audit_log(path, data)

        value = data

        return value

    async def get_channel(self, *path):

        data = await self._client.get_channel(path)

        value = aiocord.get_channel(data)

        return value

    async def update_channel(self, *path, **data):

        data = await self._client.modify_channel(path, data)

        value = aiocord.modify_channel(data)

        return value

    async def delete_channel(self, *path):

        data = await self._client.delete_channel(channel_id)

        value = data

        return value

    async def get_messages(self, *path, **data):

        data = await self._client.get_channel_messages(path, data)

        value = aiocord.get_channel_messages(data)

        return value

    async def get_message(self, *path):

        data = await self._client.get_channel_message(path)

        value = aiocord.get_channel_message(data)

        return aiocord.get_channel_message(data)

    async def create_message(self, *path, **data):

        data = await self._client.create_message(path, data)

        value = aiocord.create_message(data)

        return value

    async def create_reaction(self, *path):

        data = await self._client.create_reaction(path)

        value = data

        return value

    async def delete_own_reaction(self, *path):

        data = await self._client.delete_own_reaction(path)

        value = data

        return value

    async def delete_reaction(self, *path):

        data = await self._client.delete_user_reaction(path)

        value = data

        return value

    async def get_reactions(self, *path, **data):

        data = await self._client.get_reactions(path, data)

        value = aiocord.get_reactions(data)

        return value

    async def clear_reactions(self, *path):

        data = await self._client.delete_all_reactions(path)

        value = data

        return value

    async def update_message(self, *path, **data):

        data = await self._client.edit_message(path, data)

        value = aiocord.edit_message(data)

        return value

    async def delete_message(self, *path):

        data = await self._client.delete_message(path)

        value = data

        return value

    async def delete_messages(self, *path, **data):

        data = await self._client.bulk_delete_messages(path, data)

        value = data

        return value

    async def update_overwrite(self, *path, **data):

        data = await self._client.edit_channel_permissions(path)

        value = data

        return value

    async def get_channel_invites(self, *path):

        data = await self._client.get_channel_invites(path)

        value = aiocord.get_channel_invites(data)

        return value

    async def create_invite(self, *path, **data):

        data = await self._client.create_channel_invite(path, data)

        value = aiocord.create_channel_invite(data)

        return value

    async def delete_overwrite(self, *path):

        data = await self._client.delete_overwrite(path, overwrite_id)

        value = data

        return value

    async def start_typing(self, *path):

        data = await self._client.trigger_typing_indicator(path)

        value = data

        return value

    async def get_pins(self, *path):

        data = await self._client.get_pinned_messages(path)

        value = aiocord.get_pinned_messages(data)

        return value

    async def create_pin(self, *path):

        data = await self._client.add_pinned_message(path)

        value = data

        return value

    async def delete_pin(self, *path):

        data = await self._client.delete_pinned_message(path)

        value = data

        return value

    async def create_recipient(self, *path, **data):

        data = await self._client.group_dm_add_recipient(path, data)

        value = data

        return value

    async def delete_recipient(self, *path):

        data = await self._client.group_dm_remove_recipient(path)

        value = data

        return value

    async def get_emojis(self, *path):

        data = await self._client.get_guild_emojis(path)

        value = aiocord.list_guild_emojis(data)

        return value

    async def get_emoji(self, *path):

        data = await self._client.get_guild_emoji(path)

        value = aiocord.list_guild_emoji(data)

        return value

    async def create_emoji(self, *path, **data):

        data = await self._client.create_guild_emoji(path, data)

        value = aiocord.create_guild_emoji(data)

        return value

    async def update_emoji(self, *path, **data):

        data = await self._client.modify_guild_emoji(path, data)

        value = aiocord.modify_guild_emoji(data)

        return value

    async def delete_emoji(self, *path):

        data = await self._client.delete_guild_emoji(path)

        value = data

        return value

    async def create_guild(self, **data):

        data = await self._client.create_guild(data)

        value = aiocord.create_guild(data)

        return value

    async def get_guild(self, *path):

        data = await self._client.get_guild(path)

        value = aiocord.get_guild(data)

        return value

    async def update_guild(self, *path, **data):

        data = await self._client.modify_guild(path, data)

        value = aiocord.modify_guild(data)

        return value

    async def delete_guild(self, *path):

        data = await self._client.delete_guild(path)

        value = data

        return value

    async def get_channels(self, *path):

        data = await self._client.get_guild_channels(path)

        value = aiocord.get_guild_channels(data)

        return value

    async def create_channel(self, *path, **data):

        data = await self._client.create_guild_channel(path, data)

        value = aiocord.create_guild_channel(data)

        return data

    async def update_channel_positions(self, *args):

        *path, data = args

        data = await self._client.modify_guild_channel_positions(path, data)

        value = aiocord.modify_guild_channel_positions(data)

        return value

    async def get_member(self, *path):

        data = await self._client.get_guild_member(path)

        value = aiocord.get_guild_member(data)

        return value

    async def get_members(self, *path, **data):

        data = await self._client.list_guild_members(path, data)

        value = aiocord.list_guild_members(data)

        return value

    async def create_member(self, *path, **data):

        data = await self._client.add_guild_member(path, data)

        value = data

        return value

    async def update_member(self, *path, **data):

        data = await self._client.modify_guild_member(path, data)

        value = data

        return value

    async def update_own_nick(self, *path, **data):

        data = await self._client.modify_current_user_nick(path, data)

        vaue = aiocord.modify_current_user_nick(data)

        return value

    async def add_role(self, *path):

        data = await self._client.add_guild_member_role(path)

        value = data

        return data

    async def pop_role(self, *path):

        data = await self._client.remove_guild_member_role(path)

        value = data

        return data

    async def delete_member(self, *path):

        data = await self._client.remove_guild_member(path)

        value = data

        return data

    async def get_bans(self, *path):

        data = await self._client.get_guild_bans(path)

        value = aiocord.get_guild_bans(data)

        return value

    async def get_ban(self, *path):

        data = await self._client.get_guild_ban(path)

        value = aiocord.get_guild_ban(data)

        return value

    async def create_ban(self, *path, **data):

        data = await self._client.create_guild_ban(path, data)

        value = data

        return value

    async def delete_ban(self, *path):

        data = await self._client.remove_guild_ban(path)

        value = data

        return value

    async def get_roles(self, *path):

        data = await self._client.get_guild_roles(path)

        value = aiocord.get_guild_roles(data)

        return value

    async def create_role(self, *path, **data):

        data = await self._client.create_guild_role(path, data)

        value = aiocord.create_guild_role(data)

        return value

    async def update_role_positions(self, *args):

        *path, data = args

        data = await self._client.modify_guild_role_positions(path, data)

        value = aiocord.modify_guild_role_positions(data)

        return value

    async def update_role(self, *path, **data):

        data = await self._client.modify_guild_role(path, data)

        value = aiocord.modify_guild_role(data)

        return value

    async def delete_role(self, *path):

        data = await self._client.delete_guild_role(path)

        value = aiocord.delete_guild_role(data)

        return value

    async def get_prune(self, *path, **data):

        data = await self._client.get_guild_prune_count(path, data)

        value = aiocord.get_guild_prune_count(data)

        return value

    async def start_prune(self, *path, **data):

        data = await self._client.begin_guild_prune(path, data)

        value = aiocord.begin_guild_prune(data)

        return value

    async def get_guild_voice_regions(self, *path):

        data = await self._client.get_guild_voice_regions(path)

        value = aiocord.get_guild_voice_regions(data)

        return value

    async def get_guild_invites(self, *path):

        data = await self._client.get_guild_invites(path)

        value = aiocord.get_guild_invites(data)

        return value

    async def get_integrations(self, *path):

        data = await self._client.get_guild_integrations(path)

        value = aiocord.get_guild_integrations(data)

        return value

    async def create_integration(self, *parts, **data):

        data = await self._client.get_guild_integrations(path, data)

        value = data

        return value

    async def delete_integration(self, *path):

        data = await self._client.delete_guild_integrations(path)

        value = data

        return value

    async def sync_integration(self, *path):

        data = await self._client.sync_guild_integrations(path)

        value = aiocord.sync_guild_integrations(data)

        return value

    async def get_embed(self, *path):

        data = await self._client.get_guild_embed(path)

        value = aiocord.get_guild_embed(data)

        return value

    async def update_embed(self, *path):

        data = await self._client.modify_guild_embed(path)

        value = aiocord.modify_guild_embed(data)

        return value

    async def get_vanity_url(self, *path):

        data = await self._client.get_guild_vanity_url(path)

        value = aiocord.get_guild_vanity_url(data)

        return value

    async def get_widget_image(self, *path):

        data = await self._client.get_guild_widget_image(path)

        value = data

        return value

    async def get_embed_image(self, *path):

        data = await self._client.get_guild_embed_image(path)

        value = data

        return value

    async def get_invite(self, *path, **data):

        data = await self._client.get_invite(path, data)

        value = aiocord.get_invite(data)

        return value

    async def delete_invite(self, *path):

        data = await self._client.delete_invite(path)

        value = data

        return value

    async def get_own_user(self):

        data = await self._client.get_current_user()

        value = aiocord.get_current_user(data)

        return value

    async def get_user(self, *path):

        data = await self._client.get_user(path)

        value = aiocord.get_user(data)

        return value

    async def update_own_user(self, **data):

        data = await self._client.modify_current_user(data)

        value = aiocord.update_own_user(data)

        return value

    async def get_own_guilds(self, **data):

        data = await self._client.get_current_user_guilds(data)

        value = aiocord.get_current_user_guilds(data)

        return value

    async def leave_guild(self, *parts):

        data = await self._client.leave_guild(path)

        value = data

        return value

    async def get_dms(self):

        data = await self._client.get_user_dms()

        value = aiocord.get_user_dms(data)

        return value

    async def create_dm(self, **data):

        data = await self._client.create_dm(data)

        value = aiocord.create_dm(data)

        return value

    async def get_connections(self):

        data = await self._client.get_user_connections()

        value = aiocord.get_user_connections(data)

        return value

    async def get_voice_regions(self):

        data = await self._client.list_voice_regions()

        value = aiocord.list_voice_regions(data)

        return value

    async def create_webhook(self, *path, **data):

        data = await self._client.create_webhook(path, data)

        value = aiocord.create_webhook(data)

        return value

    async def get_channel_webhooks(self, *path):

        data = await self._client.get_channel_webhooks(path)

        value = aiocord.get_channel_webhooks(data)

        return value

    async def get_guild_webhooks(self, *path):

        data = await self._client.get_guild_webhooks(path)

        value = aiocord.get_guild_webhooks(data)

        return value

    async def get_webhook(self, *path):

        data = await self._client.get_webhook(path)

        value = aiocord.get_webhook(data)

        return value

    async def update_webhook(self, *path, **data):

        data = await self._client.modify_webhook(path, data)

        value = aiocord.modify_webhook(data)

        return value

    async def update_webhook_with_token(self, *path, **data):

        data = await self._client.modify_webhook_with_token(path, data)

        value = aiocord.modify_webhook_with_token(data)

        return value

    async def delete_webhook(self, *path):

        data = await self._client.delete_webhook(path)

        value = data

        return value

    async def delete_webhook_with_token(self, *path):

        data = await self._client.delete_webhook_with_token(path)

        value = data

        return value

    async def execute_webhook(self, *path, wait = True, **data):

        query = {'wait': wait}

        data = await self.client.execute_webhook(path, data, query)

        value = aiocord.execute_webhook(data) if wait else data

        return value
