import asyncio
import yarl
import json
import aiohttp

from . import errors
from . import helpers


__all__ = ('Client',)


class Client:

    __slots__ = ('_session', '_headers', '_loop')

    _base = yarl.URL('https://discordapp.com/api/v7')

    _errors = {
        400: errors.BadRequest,
        401: errors.Unauthorized,
        403: errors.Forbidden,
        404: errors.NotFound,
        405: errors.MethodNotAllowed,
        429: errors.TooManyRequests,
        502: errors.GatewayUnavailable
    }

    def __init__(self, session, loop = None):

        if not loop:

            loop = asyncio.get_event_loop()

        self._session = session

        self._headers = {}

        self._loop = loop

    def authorize(self, token, key = 'Authorization'):

        if token:

            self._headers[key] = token

        else:

            del self._headers[key]

    async def request(self, method, path, **kwargs):

        headers = helpers.get_soft(kwargs, 'headers', dict)

        headers.update(self._headers)

        try:

            params = kwargs['params']

        except KeyError:

            pass

        else:

            helpers.fix_params(params)

        url = self._base.with_path(self._base.path + path)

        response = await self._session.request(method, url, **kwargs)

        data = await response.text()

        payload = json.loads(data)

        if response.status < 400:

            return payload

        try:

            error = self._errors[response.status]

        except KeyError:

            error = errors.RequestError

        message = '{0} {1}'.format(payload['code'], payload['message'])

        errors = payload.get('errors')

        if errors:

            causes = json.dumps(errors, indent = 4)

            message = '{0}\n{1}'.format(message, causes)

        raise error(response, message)

    def _multi(self, files = None, json = None):

        form = aiohttp.FormData()

        if files:

            for file in files:

                form.add_field('file', file)

        if json:

            json = self._session._json_serialize(json)

            form.add_field('payload_json', json)

        return form

    def get_gateway(self):

        path = '/gateway'

        return self.request('GET', path)

    def get_gateway_bot(self):

        path = '/gateway/bot'

        return self.request('GET', path)

    def get_audit_log(self, parts, query):

        template = '/guilds/{0}/audit-logs'

        path = template.format(*parts)

        return self.request('GET', path, params = query)

    def get_channel(self, parts):

        template = '/channels/{0}'

        path = template.format(*parts)

        return self.request('GET', path)

    def modify_channel(self, parts, data):

        template = '/channels/{0}'

        path = template.format(*parts)

        return self.request('PATCH', path, json = data)

    def delete_channel(self, parts):

        template = '/channels/{0}'

        path = template.format(*parts)

        return self.request('DELETE', path)

    def get_channel_messages(self, parts, query):

        template = '/channels/{0}/messages'

        path = template.format(*parts)

        return self.request('GET', path, params = query)

    def get_channel_message(self, parts):

        template = '/channels/{0}/messages{1}'

        path = template.format(*parts)

        return self.request('GET', path)

    def create_message(self, parts, data):

        template = '/channels/{0}/messages'

        path = template.format(*parts)

        files = data.get('files')

        form = self._multi(files = files, json = data)

        return self.request('POST', path, data = form)

    def create_reaction(self, parts):

        template = '/channels/{0}/messages/{1}/reactions/{2}/@me'

        path = template.format(*parts)

        return self.request('PUT', path)

    def delete_own_reaction(self, parts):

        template = '/channels/{0}/messages/{1}/reactions/{2}/@me'

        path = template.format(*parts)

        return self.request('DELETE', path)

    def delete_user_reaction(self, parts):

        template = '/channels/{0}/messages/{1}/reactions/{2}/{3}'

        path = template.format(*parts)

        return self.request('DELETE', path)

    def get_reactions(self, parts, query):

        template = '/channels/{0}/messages/{1}/reactions/{2}'

        path = template.format(*parts)

        return self.request('GET', path, params = query)

    def delete_all_reactions(self, parts):

        template = '/channels/{0}/messages/{1}/reactions'

        path = template.format(*parts)

        return self.request('DELETE', path)

    def edit_message(self, parts, data):

        template = '/channels/{0}/messages/{1}'

        path = template.format(*parts)

        return self.request('PATCH', path, json = data)

    def delete_message(self, parts):

        template = '/channels/{0}/messages/{1}'

        path = template.format(*parts)

        return self.request('DELETE', path)

    def bulk_delete_messages(self, parts, data):

        template = '/channels/{0}/messages/bulk-delete'

        path = template.format(*parts)

        return self.request('DELETE', path, json = data)

    def edit_channel_permissions(self, parts, data):

        template = '/channels/{0}/permissions/{1}'

        path = template.format(*parts)

        return self.request('PATCH', path, json = data)

    def get_channel_invites(self, parts):

        template = '/channels/{0}/invites'

        path = template.format(*parts)

        return self.request('GET', path)

    def create_channel_invite(self, parts, data):

        template = '/channels/{0}/invites'

        path = template.format(*parts)

        return self.request('POST', path, json = data)

    def delete_channel_permission(self, parts):

        template = '/channels/{0}/permissions/{1}'

        path = template.format(*parts)

        return self.request('DELETE', path)

    def trigger_typing_indicator(self, parts):

        template = '/channels/{0}/typing'

        path = template.format(*parts)

        return self.request('POST', path)

    def get_pinned_messages(self, parts):

        template = '/channels/{0}/pins'

        path = template.format(*parts)

        return self.request('GET', path)

    def add_pinned_message(self, parts):

        template = '/channels/{0}/pins/{1}'

        path = template.format(*parts)

        return self.request('PUT', path)

    def delete_pinned_message(self, parts):

        template = '/channels/{0}/pins/{1}'

        path = template.format(*parts)

        return self.request('DELETE', path)

    def group_dm_add_recipient(self, parts, data):

        template = '/channels/{0}/recipients/{1}'

        path = template.format(*parts)

        return self.request('PUT', path, json = data)

    def group_dm_remove_recipient(self, parts):

        template = '/channels/{0}/recipients/{1}'

        path = template.format(*parts)

        return self.request('DELETE', path)

    def list_guild_emojis(self, parts):

        template = '/guilds/{0}/emojis'

        path = template.format(*parts)

        return self.request('GET', path)

    def get_guild_emoji(self, parts):

        template = '/guilds/{0}/emojis/{1}'

        path = template.format(*parts)

        return self.request('GET', path)

    def create_guild_emoji(self, parts, data):

        template = '/guilds/{0}/emojis'

        path = template.format(*parts)

        return self.request('POST', path, json = data)

    def modify_guild_emoji(self, parts, data):

        template = '/guilds/{0}/emojis/{1}'

        path = template.format(*parts)

        return self.request('PATCH', path, json = data)

    def delete_guild_emoji(self, parts):

        template = '/guilds/{0}/emojis'

        path = template.format(*parts)

        return self.request('DELETE', path)

    def create_guild(self, data):

        template = '/guilds'

        return self.request('POST', path, json = data)

    def get_guild(self, parts):

        template = '/guilds/{0}'

        path = template.format(*parts)

        return self.request('GET', path)

    def modify_guild(self, parts, data):

        template = '/guilds/{0}'

        path = template.format(*parts)

        return self.request('GET', path, json = data)

    def delete_guild(self, parts):

        template = '/guilds/{0}'

        path = template.format(*parts)

        return self.request('DELETE', path)

    def get_guild_channels(self, parts):

        template = '/guilds/{0}/channels'

        path = template.format(*parts)

        return self.request('GET', path)

    def create_guild_channel(self, parts, data):

        template = '/guilds/{0}/channels'

        path = template.format(*parts)

        return self.request('POST', path, json = data)

    def modify_guild_channel_positions(self, parts, data):

        template = '/guilds/{0}/channels'

        path = template.format(*parts)

        return self.request('PATCH', path, json = data)

    def get_guild_member(self, parts):

        template = '/guilds/{0}/members/{1}'

        path = template.format(*parts)

        return self.request('PATCH', path)

    def list_guild_members(self, parts, query):

        template = '/guilds/{0}/members'

        path = template.format(*parts)

        return self.request('GET', path, params = query)

    def add_guild_member(self, parts, data):

        template = '/guilds/{0}/members/{1}'

        path = template.format(*parts)

        return self.request('PUT', path, json = data)

    def modify_guild_member(self, parts, data):

        template = '/guilds/{0}/members/{1}'

        path = template.format(*parts)

        return self.request('PATCH', path, json = data)

    def modify_current_user_nick(self, parts, data):

        template = '/guilds/{0}/members/@me/nick'

        path = template.format(*parts)

        return self.request('PATCH', path, json = data)

    def add_guild_member_role(self, parts):

        template = '/guilds/{0}/members/{1}/roles/{2}'

        path = template.format(*parts)

        return self.request('PUT', path)

    def remove_guild_member_role(self, parts):

        template = '/guilds/{0}/members/{1}/roles/{2}'

        path = template.format(*parts)

        return self.request('DELETE', path)

    def remove_guild_member(self, parts):

        template = '/guilds/{0}/members/{1}'

        path = template.format(*parts)

        return self.request('DELETE', path)

    def get_guild_bans(self, parts):

        template = '/guilds/{0}/bans'

        path = template.format(*parts)

        return self.request('GET', path)

    def get_guild_ban(self, parts):

        template = '/guilds/{0}/bans/{1}'

        path = template.format(*parts)

        return self.request('GET', path)

    def create_guild_ban(self, parts, data):

        template = '/guilds/{0}/bans/{1}'

        path = template.format(*parts)

        return self.request('PUT', path, json = data)

    def remove_guild_ban(self, parts):

        template = '/guilds/{0}/bans/{1}'

        path = template.format(*parts)

        return self.request('DELETE', path)

    def get_guild_roles(self, parts):

        template = '/guilds/{0}/roles'

        path = template.format(*parts)

        return self.request('GET', path)

    def create_guild_role(self, parts, data):

        template = '/guilds/{0}/roles'

        path = template.format(*parts)

        return self.request('POST', path, json = data)

    def modify_guild_role_positions(self, parts, data):

        template = '/guilds/{0}/roles'

        path = template.format(*parts)

        return self.request('PATCH', path, json = data)

    def modify_guild_role(self, parts, data):

        template = '/guilds/{0}/roles/{1}'

        path = template.format(*parts)

        return self.request('PATCH', path, json = data)

    def delete_guild_role(self, parts):

        template = '/guilds/{0}/roles/{1}'

        path = template.format(*parts)

        return self.request('DELETE', path)

    def get_guild_prune_count(self, parts, query):

        template = '/guilds/{0}/prune'

        path = template.format(*parts)

        return self.request('GET', path, params = query)

    def begin_guild_prune_count(self, parts, query):

        template = '/guilds/{0}/prune'

        path = template.format(*parts)

        return self.request('POST', path, params = query)

    def get_guild_voice_regions(self, parts):

        template = '/guilds/{0}/regions'

        path = template.format(*parts)

        return self.request('POST', path)

    def get_guild_invites(self, parts):

        template = '/guilds/{0}/invites'

        path = template.format(*parts)

        return self.request('GET', path)

    def get_guild_integrations(self, parts):

        template = '/guilds/{0}/integrations'

        path = template.format(*parts)

        return self.request('GET', path)

    def create_guild_integration(self, parts, data):

        template = '/guilds/{0}/integrations'

        path = template.format(*parts)

        return self.request('POST', path, json = data)

    def modify_guild_integration(self, parts, data):

        template = '/guilds/{0}/integrations/{1}'

        path = template.format(*parts)

        return self.request('PATCH', path, json = data)

    def delete_guild_integration(self, parts):

        template = '/guilds/{0}/integrations/{1}'

        path = template.format(*parts)

        return self.request('DELETE', path)

    def sync_guild_integration(self, parts):

        template = '/guilds/{0}/integrations/{1}/sync'

        path = template.format(*parts)

        return self.request('POST', path)

    def get_guild_embed(self, parts):

        template = '/guilds/{0}/embed'

        path = template.format(*parts)

        return self.request('POST', path)

    def modify_guild_embed(self, parts, data):

        template = '/guilds/{0}/embed'

        path = template.format(*parts)

        return self.request('PATCH', path, json = data)

    def get_guild_vanity_url(self, parts):

        template = '/guilds/{0}/vanity-url'

        path = template.format(*parts)

        return self.request('GET', path)

    def get_guild_widget_image(self, parts, query):

        template = '/guilds/{0}/widget.png'

        path = template.format(*parts)

        return self.request('GET', path, params = query)

    def get_guild_embed_image(self, parts, query):

        template = '/guilds/{0}/embed.png'

        path = template.format(*parts)

        return self.request('GET', path, params = query)

    def get_invite(self, parts, query):

        template = '/invites/{0}'

        path = template.format(*parts)

        return self.request('GET', path, params = query)

    def delete_invite(self, parts):

        template = '/invites/{0}'

        path = template.format(*parts)

        return self.request('DELETE', path)

    def get_current_user(self):

        template = '/users/@me'

        return self.request('GET', path)

    def get_user(self, parts):

        template = '/users/{0}'

        path = template.format(*parts)

        return self.request('GET', path)

    def modify_current_user(self, data):

        template = '/users/@me'

        return self.request('PATCH', path, json = data)

    def get_current_user_guilds(self, query):

        template = '/users/@me/guilds'

        return self.request('GET', path, params = query)

    def leave_guild(self, parts):

        template = '/users/@me/guilds/{1}'

        path = template.format(*parts)

        return self.request('DELETE')

    def get_user_dms(self):

        template = '/users/@me/channels'

        return self.request('GET', path)

    def create_dm(self, data):

        template = '/users/@me/channels'

        return self.request('POST', path, json = data)

    def get_user_connections(self):

        template = '/users/@me/connections'

        return self.request('GET', path)

    def list_voice_regions(self):

        template = '/voice/regions'

        return self.request('GET', path)

    def create_webhook(self, parts, data):

        template = '/channels/{0}/webhooks'

        path = template.format(*parts)

        return self.request('POST', path, json = data)

    def get_channel_webhooks(self, parts):

        template = '/channels/{0}/webhooks'

        path = template.format(*parts)

        return self.request('GET', path)

    def get_guild_webhooks(self, parts):

        template = '/guilds/{0}/webhooks'

        path = template.format(*parts)

        return self.request('GET', path)

    def get_webhook(self, parts):

        template = '/webhooks/{0}'

        return self.request('GET', path)

    def modify_webhook(self, parts, data):

        template = '/webhooks/{0}'

        path = template.format(*parts)

        return self.request('PATCH', path, json = data)

    def modify_webhook_with_token(self, parts, data):

        template = '/webhooks/{0}/{1}'

        path = template.format(*parts)

        return self.request('PATCH', path, json = data)

    def delete_webhook(self, parts):

        template = '/webhooks/{0}'

        path = template.format(*parts)

        return self.request('DELETE', path)

    def delete_webhook_with_token(self, parts):

        template = '/webhooks/{0}/{1}'

        path = template.format(*parts)

        return self.request('DELETE', path)

    def execute_webhook(self, parts, data, query):

        template = '/webhooks/{0}/{1}'

        path = template.format(*parts)

        return self.request('POST', path, json = data, params = query)


class Client(Client):

    __slots__ = ('_rates',)

    _major = object()

    _majors = ('channels', 'guilds', 'webhooks')

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self._rates = {}

    async def request(self, method, path, **kwargs):

        parts = path.split('/')

        while not self._session.closed:

            try:

                payload = await super().request(method, path, **kwargs)

            except errors.GatewayUnavailable:

                await asyncio.sleep(1)

            except errors.TooManyRequests:

                if payload['global']:

                    major = self._major

                else:

                    for (index, part) in enumerate(parts):

                        if part in self._majors:

                            break

                    try:

                        major = parts[index + 1]

                    except IndexError:

                        major = path

                try:

                    rate = self._rates[major]

                except KeyError:

                    self._rates[major] = asyncio.Event(loop = self._loop)

                    delay = payload['retry_after'] / 1000

                    await asyncio.sleep(delay)

                    self._rates.pop(major).set()

                else:

                    await rate.wait()

            else:

                break

        else:

            raise errors.InterruptedRequestError()

        return payload
