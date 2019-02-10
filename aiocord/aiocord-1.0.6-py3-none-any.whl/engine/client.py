import asyncio
import aiocord
import itertools
import functools

from . import rest
from . import gateway
from . import voice
from . import helpers


__all__ = ('Client',)


_limit = float('inf')


class Client:

    def __init__(self, session, token, cache = 2048, loop = None):

        if not loop:

            loop = asyncio.get_event_loop()

        client = aiocord.rest.Client(session, loop = loop)

        client.authorize(token)

        rest_ = rest.Client(client)

        self._rest = rest_

        gateway_ = gateway.Client(maxsize = cache, loop = loop)

        self._gateway = gateway_

        def cache(guild_id, user_id):

            guild = gateway_.cache.guilds[guild_id]

            member = guild.members[user_id]

            return guild, member

        voice_ = voice.Client(cache, loop = loop)

        self._voice = voice_

        self._token = token

        self._shards = []

        self._voices = {}

        self._voices_state = set()

        self._audios = {}

        self._session = session

        self._loop = loop

    @property
    def shards(self):

        return self._shards

    @property
    def cache(self):

        return self._gateway.cache

    @property
    def voices(self):

        return self._voices

    @property
    def audios(self):

        return self._audios

    def _pick(self, name):

        if name in helpers.gateway_events:

            client = self._gateway

        elif name in helpers.voice_events:

            client = self._voice

        else:

            raise ValueError(f'unknown event: {name}')

        return client

    def track(self, name):

        client = self._pick(name)

        return client.track(name)

    def check(self, name):

        client = self._pick(name)

        return client.check(name)

    def get_gateway(self, bot = False):

        if bot:

            return self._rest.get_gateway_bot()

        return self._rest.get_gateway()

    def get_audit_log(self, *path):

        return self._rest.get_audit_log(*path)

    def get_channel(self, *path):

        return self._rest.get_channel(*path)

    def get_channels(self, *path):

        return self._rest.get_channels(*path)

    def create_channel(self, *path, **data):

        return self._rest.create_channel(*path)

    def update_channel(self, *path, **data):

        return self._rest.update_channel(*path, **data)

    def update_channel_positions(self, *args):

        *path, bundles = args

        data = helpers.position(bundles)

        return self._rest.update_channel_positions(*path, data)

    def delete_channel(self, *path, **data):

        return self._rest.delete_channel(*path, **data)

    def get_message(self, *path):

        return self._rest.get_message(*path)

    def get_messages(self, *path, limit = _limit, before = None, **data):

        def execute(limit, before):

            limit = min(limit, 100)

            extra = {'limit': limit, 'before': before}

            data.update(extra)

            return self._rest.get_messages(*path, **data)

        def critical(message):

            return message.id

        return helpers.propagate(execute, limit, before, critical)

    def create_message(self, *path, **data):

        return self._rest.create_message(*path, **data)

    def update_message(self, *path, **data):

        return self._rest.update_message(*path, **data)

    def delete_message(self, *path):

        return self._rest.delete_message(*path)

    def delete_messages(self, *path, **data):

        data['messages'] = data.pop('ids')

        return self._rest.delete_messages(*path, **data)

    def get_reactions(self, *path, limit = _limit, after = None, **data):

        def execute(limit, after):

            limit = min(limit, 100)

            extra = {'limit': limit, 'after': after}

            data.update(extra)

            return self._rest.get_reactions(*path, **data)

        def critical(user):

            return user.id

        return helpers.propagate(execute, limit, after, critical)

    def create_reaction(self, *path):

        return self._rest.create_reaction(*path)

    def delete_reaction(self, *path):

        if len(path) > 3:

            return self._rest.delete_reaction(*path)

        return self._rest.delete_own_reaction(*path)

    def clear_reactions(self, *path, **data):

        return self._rest.clear_reactions(*path, **data)

    def prune_messages(self, *path, values):

        data = {'messages': values}

        return self._rest.clear_reactions(*path, **data)

    def update_overwrite(self, *path, **data):

        return self._rest.update_overwrite(*path, **data)

    def delete_overwrite(self, *path):

        return self._rest.delete_overwrite(*path)

    def get_invite(self, *path, **data):

        return self._rest.get_invite(*path, **data)

    def get_invites(self, *path, full = False):

        if full:

            return self._rest.get_guild_invites(*path)

        return self._rest.get_channel_invites(*path)

    def create_invite(self, *path, **data):

        return self._rest.create_invite(*path, **data)

    def delete_invite(self, *path):

        return self._rest.delete_invite(*path)

    def start_typing(self, *path):

        return self._rest.start_typing(*path)

    def get_pins(self, *path):

        return self._rest.get_pins(*path)

    def create_pin(self, *path):

        return self._rest.create_pin(*path)

    def delete_pin(self, *path):

        return self._rest.delete_pin(*path)

    def create_recipient(self, *path, **data):

        return self._rest.create_recipient(*path, **data)

    def delete_recipient(self, *path, **data):

        return self._rest.delete_recipient(*path, **data)

    def get_emoji(self, *path):

        return self._rest.get_emoji(*path)

    def get_emojis(self, *path):

        return self._rest.get_emojis(*path)

    def create_emoji(self, *path, **data):

        return self._rest.create_emoji(*path, **data)

    def update_emoji(self, *path):

        return self._rest.update_emoji(*path, **data)

    def delete_emoji(self, *path):

        return self._rest.delete_emoji(*path)

    def get_guild(self, *path):

        return self._rest.get_guild(*path)

    def get_guilds(self, limit = _limit, after = None, **data):

        def execute(limit, after):

            limit = min(limit, 100)

            extra = {'limit': limit, 'after': after}

            data.update(extra)

            return self._rest.get_members(*path, **data)

        def critical(guild):

            return guild.id

        return helpers.propagate(execute, limit, after, critical)

    def create_guild(self, **data):

        return self._rest.create_guild(**data)

    def update_guild(self, *path, **data):

        return self._rest.update_guildd(*path, **data)

    def delete_guild(self, *path):

        return self._rest.delete_guild(*path)

    def pop_guild(self, *path):

        return self._rest.leave_guild(*path)

    def get_member(self, *path):

        return self._rest.get_member(*path)

    def get_members(self, *path, limit = _limit, after = None, **data):

        def execute(limit, after):

            limit = min(limit, 100)

            extra = {'limit': limit, 'after': after}

            data.update(extra)

            return self._rest.get_members(*path, **data)

        def critical(member):

            return member.user.id

        return helpers.propagate(execute, limit, after, critical)

    def create_member(self, *path, **data):

        return self._rest.create_member(*path, **data)

    def update_member(self, *path, **data):

        return self._rest.update_member(*path, **data)

    def delete_member(self, *path):

        return self._rest.delete_member(*path)

    def update_nick(self, *path, value):

        data = {'nick': value}

        return self._rest.update_nick(*path, **data)

    def get_ban(self, *path):

        return self._rest.get_ban(*path)

    def get_bans(self, *path):

        return self._rest.get_bans(*path)

    def create_ban(self, *path, **data):

        return self._rest.create_ban(*path, **data)

    def delete_ban(self, *path):

        return self._rest.delete_ban(*path)

    def get_roles(self, *path):

        return self._rest.get_roles(*path)

    def create_role(self, *path, **data):

        return self._rest.create_role(*path, **data)

    def update_role(self, *path, **data):

        return self._rest.update_role(*path, **data)

    def update_role_positions(self, *args):

        *path, bundles = args

        data = helpers.position(bundles)

        return self._rest.update_role_positions(*path, data)

    def delete_role(self, *path):

        return self._rest.delete_role(*path)

    def add_role(self, *path):

        return self._rest.add_role(*path)

    def pop_role(self, *path):

        return self._rest.pop_role(*path)

    def get_prune(self, *path, **data):

        return self._rest.get_prune(*path, **data)

    def start_prune(self, *path, **data):

        return self._rest.start_prune(*path, **data)

    def get_voice_regions(self, *path, full = False):

        if full:

            return self._rest.get_voice_regions()

        return self._rest.get_guild_voice_regions(*path)

    def get_integrations(self, *path):

        return self._rest.get_integrations(*path)

    def create_integration(self, *path, **data):

        return self._rest.create_integration(*path, **data)

    def delete_integration(self, *path):

        return self._rest.delete_integration(*path)

    def sync_integration(self, *path):

        return self._rest.sync_integration(*path)

    def get_embed(self, *path):

        return self._rest.get_embed(*path)

    def update_embed(self, *path):

        return self._rest.update_embed(*path)

    def get_vanity_url(self, *path):

        return self._rest.get_vanity_url(*path)

    def get_widget_image(self, *path):

        return self._rest.get_widget_image(*path)

    def get_embed_image(self, *path):

        return self._rest.get_embed_image(*path)

    def get_user(self, *path):

        if len(path) > 0:

            return self._rest.get_user(*path)

        return self._rest.get_own_user()

    def update_user(self, **data):

        return self._rest.update_user(**data)

    def get_dms(self):

        return self._rest.get_dms()

    def create_dm(self, user_id):

        data = {'recipient_id': user_id}

        return self._rest.create_dm(**data)

    def get_webhook(self, *path):

        return self._rest.get_webhook(*path)

    def get_webhooks(self, *path, full = False):

        if full:

            return self._rest.get_guild_webhooks(*path)

        return self._rest.get_channel_webhooks(*path)

    def update_webhook(self, *path, **data):

        if len(path) > 1:

            return self._rest.update_webhook_with_token(*path, **data)

        return self._rest.update_webhook(*path, **data)

    def delete_webhook(self, *path):

        if len(path) > 1:

            return self._rest.delete_webhook_with_token(*path)

        return self._rest.delete_webhook(*path)

    def execute_webhook(self, *path, **data):

        return self._rest.execute_webhook(*path, **data)

    async def start_gateway(self, info, url, **kwargs):

        args = (self._session, self._token, info)

        client = aiocord.gateway.Client(*args, **kwargs, loop = self._loop)

        self._gateway.attach(client)

        client.update(url)

        await client.start()

        self._shards.append(client)

        return client

    async def start(self, *shard_ids, shard_count = None, bot = True, **kwargs):

        gateway = await self.get_gateway(bot = bot)

        if not shard_count:

            shard_count = gateway.shards

        if not shard_ids:

            shard_ids = range(shard_count)

        length = len(shard_ids) - 1

        for (index, shard_id) in enumerate(shard_ids):

            info = (shard_id, shard_count)

            args = (info, gateway.url)

            await self.start_gateway(*args, **kwargs)

            if not index < length:

                break

            await asyncio.sleep(5.5)

    async def start_voice(self, shard, guild_id, channel_id):

        if guild_id in self._voices_state:

            raise ValueError(f'Already connecting in {guild_id}')

        self._voices_state.add(guild_id)

        user_id = self._gateway.cache.user.id

        url = token = session_id =  None

        @self._gateway.check('voice server update')
        async def event_0(shard_, guild_, endpoint_, token_):

            nonlocal url, token

            url = 'wss://' + endpoint_

            token = token_

            return guild_.id == guild_id

        @self._gateway.check('voice state update')
        async def event_1(shard_, guild_, channel_, user_, state_, old_state_):

            nonlocal session_id

            session_id = state_.session_id

            return guild_.id == guild_id and user_.id == user_id

        await shard.update_voice_state(guild_id, channel_id)

        await asyncio.gather(event_0.wait(), event_1.wait(), loop = self._loop)

        args = (self._session, url, token, user_id, guild_id, session_id)

        client = aiocord.voice.Client(*args, loop = self._loop)

        self._voice.attach(client)

        await client.start()

        self._voices[guild_id] = client

        audio = client.audio()

        await audio.create()

        self._audios[client] = audio

        self._voices_state.remove(guild_id)

        return (client, audio)

    async def stop_voice(self, shard, client):

        audio = self._audios.pop(client)

        await audio.destroy()

        del self._voices[client.guild_id]

        await client.close()

        await shard.update_voice_state(client.guild_id, None)

        return audio

    async def voice(self, shard, guild_id, channel_id):

        try:

            client = self._voices[guild_id]

        except KeyError:

            if not channel_id:

                raise ValueError('missing channel id')

            assets = await self.start_voice(shard, guild_id, channel_id)

        else:

            if channel_id:

                audio = self._audios[client]

                await shard.update_voice_state(guild_id, channel_id)

            else:

                audio = await self.stop_voice(shard, client)

            assets = (client, audio)

        return assets

    async def stop_gateway(self, client):

        self._shards.remove(client)

        (own_id, shard_count) = client.info

        parent = lambda guild_id: aiocord.utils.shard_id(guild_id, shard_count)

        family = lambda voice: parent(voice.guild_id) == own_id

        voices = (voice for voice in self._voices.values() if family(voice))

        coroutines = (self.stop_voice(client, voice) for voice in voices)

        await asyncio.gather(*coroutines, loop = self._loop)

        await client.close()

    async def close(self):

        coroutines = (self.stop_gateway(shard) for shard in self._shards)

        await asyncio.gather(*coroutines, loop = self._loop)
