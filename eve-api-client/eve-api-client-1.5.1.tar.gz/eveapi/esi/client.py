import datetime
import logging
import re
from urllib.parse import quote

import redis
import requests
from django.conf import settings
from django.utils import timezone

from eveapi import huey
from eveapi.esi.errors import ESIPermissionRevoked
from eveapi.sso import refresh
from huey.exceptions import TaskException

logger = logging.getLogger(__name__)
redis = redis.Redis(connection_pool=settings.REDIS_POOL)

base_url = 'https://esi.evetech.net'
oauth_url = 'https://login.eveonline.com/oauth'
token_url = 'https://login.eveonline.com/oauth/token'
authorize_url = 'https://login.eveonline.com/oauth/authorize'


class ESI:
    # for now, take refresh and access tokens as model objects
    def __init__(self, base=None, endpoint=None, headers=None, method=None, user_agent=None, version=None,
                 character=None, auth_callback=None):

        if headers is None:
            headers = {}  # apparently mutable datatype literals in function parameters are bad mkay

        if base:
            self._endpoint = endpoint or base._endpoint
            self._version = version or base._version
            self._datasource = base._datasource
            self._method = method or base._method
            self._headers = {**base._headers, **headers}
            self._character = character or base._character
            self._auth_callback = auth_callback or base._auth_callback

        else:
            self._endpoint = endpoint
            self._version = version or 'latest'
            self._datasource = 'tranquility'
            self._method = method or 'GET'
            self._character = character
            self._auth_callback = auth_callback
            self._headers = {
                'User-Agent': user_agent,
                'Accept': 'application/json',
                **headers,
            }

            if not user_agent:
                raise Exception('User agent required')

    def __str__(self):
        return '{} {}'.format(self._method, '/'.join([
            base_url,
            self._version,
            self._endpoint or '',  # endpoint may be None
        ]))

    def __getattr__(self, attr):
        """
        Adds to the esi path.

        If attr is an http method name, it will set the method attribute instead.
        Similarly, this sets the version.
        This allows you to reuse esi clients as a base for multiple routes that may need different methods or esi versions.

        Example:
            ```
            client = ESI(authtokens, etc.).v1.fleets[id]
            a = client.v2.members
            b = client.wings
            c = b.post()
            ```
        """
        if attr.startswith('_'):  # this gets called if you misspell an attribute
            logger.error('ESI attr {} starts with _, this should not happen'.format(attr))

        if attr == 'self' and self._character:  # replace self with auth character id
            attr = self._character

        elif attr in ['get', 'options', 'head', 'post', 'put', 'patch', 'delete']:  # set http method
            return ESI(self, method=attr.upper())

        elif re.match(r'(v\d+|latest|dev|legacy)', attr):  # set esi version instead of adding to the path
            return ESI(self, version=attr)

        url = self._endpoint + '/' + str(attr) if self._endpoint else str(attr)  # endpoint may be None
        return ESI(self, url)

    def __getitem__(self, key):
        return self.__getattr__(str(key))

    def __call__(self, value='', data=None, fetch_pages=False, cache=True, use_huey=True, blocking=True,
                 raise_error=False, **kwargs):
        url = '/'.join([
            base_url,
            self._version,
            self._endpoint or '',  # endpoint may be None
            quote(str(value))
        ])
        params = {key: quote(str(value_)) for key, value_ in kwargs.items()}

        args = [
            self._method,
            url,

            self._headers,
            params,
            data,
            fetch_pages,

            self._auth_callback,
            cache,
            raise_error,
        ]

        # run the esi call without huey, will default to huey on errors or multiple pages
        if not use_huey:
            return huey.esi(*args)

        task = huey.esi_task(*args)

        if blocking:
            logger.debug('waiting for ESI task response')
            # set a long timeout in case it hits max retries on long esi calls (max I've seen is 60 seconds)
            response = task.get(timeout=600, blocking=True)

            if raise_error and isinstance(response, requests.Response):
                response.raise_for_status()
            else:
                return response

        else:
            # if we're not blocking, return the task so we can make a bunch of calls,
            # then iterate through them to get(blocking) the results
            return task

    def _fork(self, **kwargs):
        return ESI(base=self, **kwargs)
