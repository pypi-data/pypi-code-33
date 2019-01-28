#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ssl
from urllib3.poolmanager import PoolManager
from requests.adapters import HTTPAdapter


class TlsAdapter(HTTPAdapter):
    """"Transport adapter" that allows us to use SSLv3."""

    def init_poolmanager(self, connections, maxsize, block=False, **kwargs):
        self.poolmanager = PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_version=ssl.PROTOCOL_TLSv1_2)
