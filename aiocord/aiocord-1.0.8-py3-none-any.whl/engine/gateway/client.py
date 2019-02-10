import asyncio
import aiocord
import collections
import functools

from . import helpers


__all__ = ('Client',)


class Client:

    __slots__ = ('_handle', '_cache', '_chunk', '_events', '_tracks',
                 '_initial', '_unavailable', '_loop')

    def __init__(self, chunk = True, maxsize = 2048, loop = None):

        if not loop:

            loop = asyncio.get_event_loop()

        cache = aiocord.Cache(maxsize = maxsize)

        self._handle = aiocord.Handle(cache)

        self._cache = cache

        self._chunk = chunk

        self._events = helpers.events_from_client(self)

        self._tracks = collections.defaultdict(list)

        self._initial = []

        self._unavailable = []

        self._loop = loop

    @property
    def cache(self):

        return self._cache

    def attach(self, shard):

        callback = functools.partial(self._callback, shard)

        shard.track(callback)

    def track(self, name):

        def decorator(function):

            def wrapper(*args):

                return function(*args)

            self._tracks[name].append(wrapper)

            return wrapper

        return decorator

    def check(self, name):

        value = asyncio.Event(loop = self._loop)

        def decorator(function):

            callbacks = self._tracks[name]

            async def callback(*args):

                if not await function(*args):

                    return

                value.set()

            callbacks.append(callback)

            async def observe():

                await value.wait()

                callbacks.remove(callback)

            coroutine = observe()

            self._loop.create_task(coroutine)

            return value

        return decorator

    async def _dispatch(self, name, values):

        callbacks = self._tracks[name]

        coroutines = (callback(*values) for callback in callbacks)

        await asyncio.gather(*coroutines, loop = self._loop)

    def _callback(self, shard, name, data):

        event = self._events[name]

        coroutine = event(shard, data)

        self._loop.create_task(coroutine)

    async def ready(self, shard, data):

        version, guild_ids, session_id = self._handle.ready(data)

        guild_ids = tuple(guild_ids)

        self._initial.extend(guild_ids)

        shard.patch(session_id)

        name = 'ready'

        values = (shard, version, guild_ids)

        await self._dispatch(name, values)

    async def resumed(self, shard, data):

        name = 'resumed'

        values = (shard,)

        await self._dispatch(name, values)

    async def channel_create(self, shard, data):

        guild, channel = self._handle.channel_create(data)

        name = 'channel create'

        values = (shard, guild, channel)

        await self._dispatch(name, values)

    async def channel_update(self, shard, data):

        guild, channel, old_channel = self._handle.channel_update(data)

        name = 'channel update'

        values = (shard, guild, channel, old_channel)

        await self._dispatch(name, values)

    async def channel_delete(self, shard, data):

        guild, channel = self._handle.channel_delete(data)

        name = 'channel delete'

        values = (shard, guild, channel)

        await self._dispatch(name, values)

    async def channel_pins_update(self, shard, data):

        guild, channel, timestamp = self._handle.channel_pins_update(data)

        name = 'pins update'

        values = (shard, guild, channel, timestamp)

        await self._dispatch(name, values)

    async def guild_create(self, shard, data):

        guild = self._handle.guild_create(data)

        try:

            self._unavailable.remove(guild.id)

        except ValueError:

            if guild.large and self._chunk:

                @self.check('members chunk')
                async def event_0(shard_, guild_):

                    guild_check = guild_.id == guild.id

                    members_check = len(guild_.members) >= guild_.member_count

                    final_check = guild_check == members_check

                    return final_check

                await shard.request_guild_members(guild.id)

                await event_0.wait()

            try:

                self._initial.remove(guild.id)

            except ValueError:

                name = 'guild create'

            else:

                name = 'guild cache'

        else:

            name = 'guild available'

        values = (shard, guild)

        await self._dispatch(name, values)

    async def guild_update(self, shard, data):

        guild, old_guild = self._handle.guild_update(data)

        name = 'guild update'

        values = (shard, guild, old_guild)

        await self._dispatch(name, values)

    async def guild_delete(self, shard, data):

        guild, unavailable = self._handle.guild_delete(data)

        if unavailable:

            self._unavailable.append(guild.id)

            name = 'guild unavailable'

        else:

            name = 'guild delete'

        values = (shard, guild)

        await self._dispatch(name, values)

    async def guild_ban_add(self, shard, data):

        guild, user = self._handle.guild_ban_add(data)

        name = 'ban create'

        values = (shard, guild, user)

        await self._dispatch(name, values)

    async def guild_ban_remove(self, shard, data):

        guild, user = self._handle.guild_ban_add(data)

        name = 'ban delete'

        values = (shard, guild, user)

        await self._dispatch(name, values)

    async def guild_emojis_update(self, shard, data):

        guild, old_emojis = self._handle.guild_emojis_update(data)

        name = 'emojis update'

        values = (shard, guild, old_emojis)

        await self._dispatch(name, values)

    async def guild_integrations_update(self, shard, data):

        guild = self._handle.guild_integrations_update(data)

        name = 'integrations update'

        values = (shard, guild)

        await self._dispatch(name, values)

    async def guild_member_add(self, shard, data):

        guild, member = self._handle.guild_member_add(data)

        name = 'member create'

        values = (shard, guild, member)

        await self._dispatch(name, values)

    async def guild_member_remove(self, shard, data):

        try:

            guild, member = self._handle.guild_member_remove(data)

        except KeyError:

            # this happens when the user is leaving an existing guild;
            # the event may occur afterward, when the guild is not longer
            # in cache, resulting in an error upon trying to fetch it

            return

        name = 'member delete'

        values = (shard, guild, member)

        await self._dispatch(name, values)

    async def guild_member_update(self, shard, data):

        guild, member, old_member = self._handle.guild_member_update(data)

        name = 'member update'

        values = (shard, guild, member, old_member)

        await self._dispatch(name, values)

    async def guild_members_chunk(self, shard, data):

        guild = self._handle.guild_members_chunk(data)

        name = 'members chunk'

        values = (shard, guild)

        await self._dispatch(name, values)

    async def guild_role_create(self, shard, data):

        guild, role = self._handle.guild_role_create(data)

        name = 'role create'

        values = (shard, guild, role)

        await self._dispatch(name, values)

    async def guild_role_update(self, shard, data):

        guild, role, old_role = self._handle.guild_role_update(data)

        name = 'role update'

        values = (shard, guild, role, old_role)

        await self._dispatch(name, values)

    async def guild_role_delete(self, shard, data):

        guild, role = self._handle.guild_role_delete(data)

        name = 'role delete'

        values = (shard, guild, role)

        await self._dispatch(name, values)

    async def message_create(self, shard, data):

        guild, channel, message = self._handle.message_create(data)

        name = 'message create'

        values = (shard, guild, channel, message)

        await self._dispatch(name, values)

    async def message_update(self, shard, data):

        guild, channel, message, old_message = self._handle.message_update(data)

        name = 'message update'

        values = (shard, guild, channel, message, old_message)

        await self._dispatch(name, values)

    async def message_delete(self, shard, data):

        guild, channel, message = self._handle.message_delete(data)

        name = 'message delete'

        values = (shard, guild, channel, message)

        await self._dispatch(name, values)

    async def message_delete_bulk(self, shard, data):

        guild, channel, messages = self._handle.message_delete_bulk(data)

        name = 'messages purge'

        values = (shard, guild, channel, messages)

        await self._dispatch(name, values)

    async def message_reaction_add(self, shard, data):

        parts = self._handle.message_reaction_add(data)

        guild, channel, message, user, emoji = parts

        name = 'reaction create'

        values = (shard, guild, channel, message, user, emoji)

        await self._dispatch(name, values)

    async def message_reaction_remove(self, shard, data):

        parts = self._handle.message_reaction_remove(data)

        guild, channel, message, user, emoji = parts

        name = 'reaction delete'

        values = (shard, guild, channel, message, user, emoji)

        await self._dispatch(name, values)

    async def message_reaction_remove_all(self, shard, data):

        parts = self._handle.message_reaction_remove_all(data)

        guild, channel, message, reactions = parts

        name = 'reactions clear'

        values = (shard, guild, channel, message, reactions)

        await self._dispatch(name, values)

    async def presence_update(self, shard, data):

        generate = self._handle.presence_update(data)

        coroutines = []

        for parts in generate:

            guild, member, fake_member, presence, old_presence = parts

            name = 'presence update'

            values = (shard, guild, member, fake_member, presence, old_presence)

            coroutine = self._dispatch(name, values)

            coroutines.append(coroutine)

        await asyncio.gather(*coroutines, loop = self._loop)

    async def typing_start(self, shard, data):

        guild, channel, user, timestamp = self._handle.typing_start(data)

        name = 'typing start'

        values = (shard, guild, channel, user, timestamp)

        await self._dispatch(name, values)

    async def user_update(self, shard, data):

        user, old_user = self._handle.user_update(data)

        name = 'user update'

        values = (shard, user, old_user)

        await self._dispatch(name, values)

    async def voice_state_update(self, shard, data):

        parts = self._handle.voice_state_update(data)

        guild, channel, user, state, old_state = parts

        name = 'voice state update'

        values = (shard, guild, channel, user, state, old_state)

        await self._dispatch(name, values)

    async def voice_server_update(self, shard, data):

        guild, endpoint, token = self._handle.voice_server_update(data)

        name = 'voice server update'

        values = (shard, guild, endpoint, token)

        await self._dispatch(name, values)

    async def webhooks_update(self, shard, data):

        guild, channel = self._handle.webhooks_update(data)

        name = 'webhooks update'

        values = (shard, guild, channel)

        await self._dispatch(name, values)
