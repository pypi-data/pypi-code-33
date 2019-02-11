import logging

from .errors import ApiError


logger = logging.getLogger(__name__)


class Api:

    def __init__(self, access_token, version, session, throttler,
                 request_wrapper=None, object_hook=None):
        self._access_token = access_token
        self._version = version
        self._session = session
        self._throttler = throttler
        self._request_wrapper = request_wrapper
        self._object_hook = object_hook

    async def __call__(self, method_name, **params):
        async def make_request():
            async with self._throttler():
                return await self._session.get(
                    path=f'/{method_name}',
                    params={**self._meta_params, **params}
                )

        if self._request_wrapper is not None:
            make_request = self._request_wrapper(make_request)

        response = await make_request()

        payload = response.json(object_hook=self._object_hook)

        logger.info('%s(%s) -> %s', method_name, params, payload)

        try:
            return payload['response']
        except KeyError:
            raise ApiError(payload['error']) from None

    def __getattr__(self, key):
        return MethodGroup(name=key, api=self)

    @property
    def _meta_params(self):
        return {
            'access_token': self._access_token,
            'v': self._version,
        }


class MethodGroup:

    def __init__(self, name, api):
        self.name = name
        self.api = api

    def __getattr__(self, key):
        return Method(name=key, group=self)


class Method:

    def __init__(self, name, group):
        self.name = name
        self.group = group

    @property
    def full_name(self):
        return f'{self.group.name}.{self.name}'

    async def __call__(self, **params):
        return await self.group.api(self.full_name, **params)
