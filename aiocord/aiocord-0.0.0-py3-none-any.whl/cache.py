import copy

from . import helpers
from . import storage


__all__ = ('Cache',)


class Cache:

    __slots__ = ('_user', '_guilds', '_channels', '_messages')

    def __init__(self, maxsize = 1024):

        self._user = None

        self._guilds = {}

        self._channels = {}

        self._messages = helpers.LimitDict(maxsize = maxsize)

    @property
    def user(self):

        return self._user

    @property
    def channels(self):

        return self._channels

    @property
    def guilds(self):

        return self._guilds

    @property
    def messages(self):

        return self._messages

    def ready(self, user_data, channels_data, guilds_data):

        self._user = storage.User(user_data)

        storage.update_dict(
            storage.Channel,
            ('id',),
            self._channels,
            channels_data
        )

        guilds = [storage.Guild(guild_data) for guild_data in guilds_data]

        return guilds

    def channel_create(self, guild_id, channel_data):

        if guild_id:

            guild = self._guilds[guild_id]

            channels_store = guild.channels

        else:

            guild = None

            channels_store = self._channels

        channel_id = channel_data['id']

        channel = storage.Channel(channel_data)

        channels_store[channel_id] = channel

        return guild, channel

    def channel_update(self, guild_id, channel_id, channel_data):

        if guild_id:

            guild = self._guilds[guild_id]

            channels_store = guild.channels

        else:

            guild = None

            channels_store = self._channels

        channel = channels_store[channel_id]

        fake_channel = copy.deepcopy(channel)

        storage.update_structure(channel, channel_data)

        return guild, channel, fake_channel

    def channel_delete(self, guild_id, channel_id):

        if guild_id:

            guild = self._guilds[guild_id]

            channels_store = guild.channels

        else:

            guild = None

            channels_store = self._channels

        channel = channels_store.pop(channel_id)

        return guild, channel

    def channel_pins_update(self, guild_id, channel_id):

        if guild_id:

            guild = self._guilds[guild_id]

            channels_store = guild.channels

        else:

            guild = None

            channels_store = self._channels

        channel = channels_store[channel_id]

        return guild, channel

    def guild_create(self, guild_data):

        guild_id = guild_data['id']

        try:

            guild = self._guilds[guild_id]

        except KeyError:

            guild = storage.Guild(guild_data)

            self._guilds[guild_id] = guild

        else:

            storage.update_structure(guild, guild_data)

        return guild

    def guild_update(self, guild_id, guild_data):

        guild = self._guilds[guild_id]

        fake_guild = copy.deepcopy(guild)

        storage.update_structure(guild, guild_data)

        return guild, fake_guild

    def guild_delete(self, guild_id):

        guild = self._guilds.pop(guild_id)

        return guild

    def guild_ban_add(self, guild_id, user_data):

        guild = self._guilds[guild_id]

        user = storage.User(user_data)

        return guild, user

    def guild_ban_remove(self, guild_id, user_data):

        guild = self._guilds[guild_id]

        user = storage.User(user_data)

        return guild, user

    def guild_emojis_update(self, guild_id, emojis_data):

        guild = self._guilds[guild_id]

        fake_emojis = copy.deepcopy(guild.emojis)

        storage.update_dict(
            storage.Emoji,
            ('id',),
            guild.emojis,
            emojis_data
        )

        return guild, fake_emojis

    def guild_integrations_update(self, guild_id):

        guild = self._guilds[guild_id]

        return guild

    def guild_member_add(self, guild_id, member_data):

        guild = self._guilds[guild_id]

        user_id = member_data['user']['id']

        member = storage.GuildMember(member_data)

        guild.members[user_id] = member

        return guild, member

    def guild_member_remove(self, guild_id, member_data):

        guild = self._guilds[guild_id]

        user_id = member_data['user']['id']

        try:

            member = guild.members.pop(user_id)

        except KeyError:

            member = storage.GuildMember(member_data)

        return guild, member

    def guild_members_chunk(self, guild_id, members_data):

        guild = self._guilds[guild_id]

        storage.update_dict(
            storage.GuildMember,
            ('user', 'id'),
            guild.members,
            members_data
        )

        return guild

    def guild_role_create(self, guild_id, role_data):

        guild = self._guilds[guild_id]

        role_id = role_data['id']

        role = storage.Role(role_data)

        guild.roles[role_id] = role

        return guild, role

    def guild_role_update(self, guild_id, role_id, role_data):

        guild = self._guilds[guild_id]

        role = guild.roles[role_id]

        fake_role = copy.deepcopy(role)

        storage.update_structure(role, role_data)

        return guild, role, fake_role

    def guild_role_delete(self, guild_id, role_id):

        guild = self._guilds[guild_id]

        role = guild.roles.pop(role_id)

        return guild, role

    def message_create(self, guild_id, channel_id, message_data):

        if guild_id:

            guild = self._guilds[guild_id]

            channels_store = guild.channels

        else:

            guild = None

            channels_store = self._channels

        channel = channels_store[channel_id]

        message_id = message_data['id']

        message = storage.Message(message_data)

        self._messages[message_id] = message

        return guild, channel, message

    def message_update(self, guild_id, channel_id, message_id, message_data):

        if guild_id:

            guild = self._guilds[guild_id]

            channels_store = guild.channels

        else:

            guild = None

            channels_store = self._channels

        channel = channels_store[channel_id]

        try:

            message = self._messages[message_id]

        except KeyError:

            fake_message = None

            message = storage.Message(message_data)

        else:

            fake_message = copy.deepcopy(message)

            storage.update_structure(message, message_data)

        return guild, channel, message, fake_message

    def message_delete(self, guild_id, channel_id, message_id):

        if guild_id:

            guild = self._guilds[guild_id]

            channels_store = guild.channels

        else:

            guild = None

            channels_store = self._channels

        channel = channels_store[channel_id]

        try:

            message = self._messages.pop(message_id)

        except KeyError:

            message_data = {'id': message_id, 'channel_id': channel_id}

            message = storage.Message(message_data)

        return guild, channel, message

    def message_delete_bulk(self, guild_id, channel_id, message_ids):

        if guild_id:

            guild = self._guilds[guild_id]

            channels_store = guild.channels

        else:

            guild = None

            channels_store = self._channels

        channel = channels_store[channel_id]

        messages = []

        for message_id in message_ids:

            try:

                message = self._messages.pop(message_id)

            except KeyError:

                message_data = {'id': message_id, 'channel_id': channel_id}

                message = storage.Message(message_data)

            messages.append(message)

        return guild, channel, messages

    def message_reaction_add(self,
                             guild_id,
                             channel_id,
                             message_id,
                             user_id,
                             emoji_data):

        if guild_id:

            guild = self._guilds[guild_id]

            channels_store = guild.channels

        else:

            guild = None

            channels_store = self._channels

        channel = channels_store[channel_id]

        try:

            message = self._messages[message_id]

        except KeyError:

            message_data = {'id': message_id, 'channel_id': channel_id}

            message = storage.Message(message_data)

            emoji = storage.Emoji(emoji_data)

        else:

            if message.reactions is storage.missing:

                message.reactions = []

            for reaction in message.reactions:

                emoji = reaction.emoji

                if not emoji.name == emoji_data['name']:

                    continue

                if not emoji.id == emoji_data['id']:

                    continue

                break

            else:

                reaction_data = {'count': 0, 'emoji': emoji_data}

                reaction = storage.Reaction(reaction_data)

                message.reactions.append(reaction)

                emoji = reaction.emoji

            reaction.count += 1

            if user_id == self._user.id:

                reaction.me = True

        if guild:

            try:

                member = guild.members[user_id]

            except KeyError:

                user_data = {'id': user_id}

                user = storage.User(user_data)

            else:

                user = member.user

        else:

            user = channel.recipients[user_id]

        return guild, channel, message, user, emoji

    def message_reaction_remove(self,
                                guild_id,
                                channel_id,
                                message_id,
                                user_id,
                                emoji_data):

        if guild_id:

            guild = self._guilds[guild_id]

            channels_store = guild.channels

        else:

            guild = None

            channels_store = self._channels

        channel = channels_store[channel_id]

        try:

            message = self._messages[message_id]

        except KeyError:

            message_data = {'id': message_id, 'channel_id': channel_id}

            message = storage.Message(message_data)

            emoji = storage.Emoji(emoji_data)

        else:

            if message.reactions is storage.missing:

                message.reactions = []

            for reaction in message.reactions:

                if not reaction.emoji.name == emoji_data['name']:

                    continue

                if not reaction.emoji.id == emoji_data['id']:

                    continue

                break

            reaction.count -= 1

            if user_id == self._user.id:

                reaction.me = False

            if reaction.count == 0:

                message.reactions.remove(reaction)

            emoji = reaction.emoji

        if guild:

            try:

                member = guild.members[user_id]

            except KeyError:

                user_data = {'id': user_id}

                user = storage.User(user_data)

            else:

                user = member.user

        else:

            user = channel.recipients[user_id]

        if user_id == self._user.id:

            reaction.me = True

        return guild, channel, message, user, emoji

    def message_reaction_remove_all(self, guild_id, channel_id, message_id):

        if guild_id:

            guild = self._guilds[guild_id]

            channels_store = guild.channels

        else:

            guild = None

            channels_store = self._channels

        channel = channels_store[channel_id]

        try:

            message = self._messages[message_id]

        except KeyError:

            fake_reactions = None

            message_data = {'id': message_id, 'channel_id': channel_id}

            message = storage.Message(message_data)

        else:

            fake_reactions = copy.deepcopy(message.reactions)

            message.reactions.clear()

        return guild, channel, message, fake_reactions

    def presence_update(self, guild_id, user_id, presence_data):

        guild = self._guilds[guild_id]

        try:

            member = guild.members[user_id]

        except KeyError:

            fake_member = None

            member = storage.GuildMember(presence_data)

        else:

            fake_member = copy.deepcopy(member)

            storage.update_structure(member, presence_data)

        try:

            presence = guild.presences[user_id]

        except KeyError:

            fake_presence = None

            presence = storage.Presence(presence_data)

            guild.presences[user_id] = presence

        else:

            fake_presence = copy.deepcopy(presence)

            storage.update_structure(presence, presence_data)

        return guild, member, fake_member, presence, fake_presence

    def typing_start(self, guild_id, channel_id, user_id):

        if guild_id:

            guild = self._guilds[guild_id]

            channels_store = guild.channels

        else:

            guild = None

            channels_store = self._channels

        channel = channels_store[channel_id]

        if guild:

            try:

                member = guild.members[user_id]

            except KeyError:

                user_data = {'id': user_id}

                user = storage.User(user_data)

            else:

                user = member.user

        else:

            user = channel.recipients[user_id]

        return guild, channel, user

    def user_update(self, user_data):

        user = self._user

        fake_user = copy.deepcopy(user)

        storage.update_structure(user, user_data)

        return user, fake_user

    def voice_state_update(self,
                           guild_id,
                           channel_id,
                           user_id,
                           voice_state_data):

        guild = self._guilds[guild_id]

        if channel_id:

            channel = guild.channels[channel_id]

        else:

            channel = None

        try:

            member = guild.members[user_id]

        except KeyError:

            user_data = {'id': user_id}

            user = storage.User(user_data)

        else:

            user = member.user

        try:

            voice_state = guild.voice_states[user_id]

        except KeyError:

            fake_voice_state = None

            voice_state = storage.VoiceState(voice_state_data)

            guild.voice_states[user_id] = voice_state

        else:

            fake_voice_state = copy.deepcopy(voice_state)

            storage.update_structure(voice_state, voice_state_data)

        return guild, channel, user, voice_state

    def voice_server_update(self, guild_id):

        guild = self._guilds[guild_id]

        return guild

    def webhooks_update(self, guild_id, channel_id):

        guild = self._guilds[guild_id]

        channel = guild.channels[channel_id]

        return guild, channel
