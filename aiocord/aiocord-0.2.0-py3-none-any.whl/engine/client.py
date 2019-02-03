import asyncio
import aiocord
import itertools

from . import rest
from . import gateway
from . import helpers


__all__ = ('Client',)


_limit = float('inf')


class Client:

    __slots__ = ('_rest', '_gateway', '_shards', '_token', '_session', '_loop')

    def __init__(self, session, token, cache = 2048, loop = None):

        if not loop:

            loop = asyncio.get_event_loop()

        client = aiocord.rest.Client(session, loop = loop)

        client.authorize(token)

        self._rest = rest.Client(client)

        self._gateway = gateway.Client(maxsize = cache, loop = loop)

        self._shards = []

        self._token = token

        self._session = session

        self._loop = loop

    @property
    def shards(self):

        return self._shards

    @property
    def cache(self):

        return self._gateway.cache

    @property
    def track(self):

        return self._gateway.track

    @property
    def check(self):

        return self._gateway.check

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

    def delete_member(self, *path, **data):

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

    async def start(self, *shard_ids, shard_count = None, bot = True, **kwargs):

        gateway = await self.get_gateway(bot = bot)

        if not shard_count:

            shard_count = gateway.shards

        if not shard_ids:

            shard_ids = range(shard_count)

        length = len(shard_ids) - 1

        shards = []

        for shard_id in shard_ids:

            info = (shard_id, shard_count)

            shard = aiocord.gateway.Client(
                self._session,
                self._token,
                info,
                **kwargs,
                loop = self._loop
            )

            self._gateway.attach(shard)

            shard.update(gateway.url)

            shards.append(shard)

        self._shards.extend(shards)

        for index in itertools.count():

            shard = shards[index]

            await shard.start()

            if not index < length:

                break

            await asyncio.sleep(5.5)

    async def close(self):

        coroutines = (shard.close() for shard in self._shards)

        await asyncio.gather(*coroutines, loop = self._loop)
