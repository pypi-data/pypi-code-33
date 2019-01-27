import logging

from .errors import ApiError


logger = logging.getLogger(__name__)


class Api:

    def __init__(self, access_token, version, session, throttler, retry):
        self._access_token = access_token
        self._version = version
        self._session = session
        self._throttler = throttler
        self._retry = retry

    async def __call__(self, method_name, **params):
        async def api_call():
            async with self._throttler():
                response = await self._session.get(
                    path=f'/{method_name}',
                    params={**self._default_params, **params}
                )
                return response.json()

        json = await self._retry(api_call)()
        logger.info('%s(%s) -> %s', method_name, params, json)

        try:
            return json['response']
        except KeyError:
            raise ApiError(json['error']) from None

    def __getattr__(self, item):
        return MethodGroup(name=item, api=self)

    @property
    def _default_params(self):
        return {
            'access_token': self._access_token,
            'v': self._version,
        }


class MethodGroup:

    def __init__(self, name, api):
        self.name = name
        self.api = api

    def __getattr__(self, item):
        return Method(name=item, group=self)


class Method:

    def __init__(self, name, group):
        self.name = name
        self.group = group

    @property
    def full_name(self):
        return f'{self.group.name}.{self.name}'

    async def __call__(self, **params):
        return await self.group.api(self.full_name, **params)
