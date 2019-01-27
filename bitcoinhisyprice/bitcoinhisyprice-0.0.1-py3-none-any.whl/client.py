#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tempfile
import json
import os
import requests
import requests_cache


class ApiClient(object):
    """
    coinmarketcap.com api wrapper with request cache feature
    """
    _session = None

    def __init__(self, request_timeout, enable_cache,
                 cache_filename, cache_expire_after):
        self.request_timeout = request_timeout
        self.enable_cache = enable_cache
        self.cache_filename = cache_filename
        self.cache_expire_after = cache_expire_after
        self.cache_file = os.path.join(tempfile.gettempdir(), self.cache_filename) if enable_cache else None

    @property
    def session(self):
        """
        wrapper for _session
        :return:
        """
        if self._session is None:
            if self.enable_cache:
                requests_cache.install_cache(self.cache_file, backend='sqlite', expire_after=self.cache_expire_after)
            self._session = requests.Session()
            self._session.headers.update({'Content-Type': 'application/json'})
            self._session.headers.update(
                {'User-agent': 'coinmarketcap-api(https://github.com/shyuntech/coinmarketcap-api)'})
        return self._session



    def request(self, base_url, params, disable_cache=False):
        if disable_cache:
            disable_cache_session = self.session
            with requests_cache.disabled():
                resp = disable_cache_session.get(base_url , params=params, timeout=self.request_timeout)
        else:
            resp = self.session.get(base_url, params=params, timeout=self.request_timeout)

        return resp.text