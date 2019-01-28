#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['EkylibreApi']

from mycroft.configuration import ConfigurationManager
from mycroft.util.log import LOG
from .tls_adapter import TlsAdapter
import requests


class EkylibreApi:
    """Ekylibre API class"""

    def __init__(self):
        self.config_api = ConfigurationManager.get().get("ekylibre_api")
        self.url = self.config_api.get('url')
        self.user = self.config_api.get('user')
        self.password = self.config_api.get('password')
        self.session = requests.Session()
        self.session.mount(self.url, TlsAdapter())
        self.simple_token = ""

    def get_token(self):
        LOG.info("GET TOKEN")
        try:
            url = self.url + "tokens"
            payload = {'email': self.user, 'password': self.password}
            r = self.session.post(url, data=payload)
            if r.status_code == requests.codes.ok:
                token = r.json()
                self.simple_token = "simple-token {user} {token}".format(user=self.user, token=token['token'])
                self.session.headers.update({'Authorization': self.simple_token})

        except Exception as err:
            LOG.error("Unable to get token: {0}".format(err))
            return "Unable to get token: {0}".format(err)

    def get(self, endpoint):
        if self.simple_token == "":
            self.get_token()
        LOG.error("SimpleToken = " + self.simple_token)
        try:
            url = self.url + endpoint
            r = self.session.get(url)
            return r.json()

        except Exception as err:
            return "API GET error: {0}".format(err)

    def post(self, endpoint, payload):
        if self.simple_token == "":
            self.get_token()
        LOG.error("SimpleToken = " + self.simple_token)

        try:
            url = self.url + endpoint
            r = self.session.post(url, json=payload)
            return r.json()

        except Exception as err:
            return "API POST error: {0}".format(err)
