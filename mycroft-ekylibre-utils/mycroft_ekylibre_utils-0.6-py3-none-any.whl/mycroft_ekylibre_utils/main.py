#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['EkylibreApi']

from mycroft.configuration import ConfigurationManager
from mycroft.util.log import LOG
# from mycroft_ekylibre_utils.tls_adapter import TlsAdapter
import requests


class EkylibreApi:
    """Ekylibre API class"""

    def __init__(self):
        self.config_api = ConfigurationManager.get().get("ekylibre_api")
        self.url = self.config_api.get('url')
        self.user = self.config_api.get('user')
        self.password = self.config_api.get('password')
        self.token = self.config_api.get('token')
        # self.session = None
        self.session = requests.Session()
        auth = "simple-token {} {}".format(self.user, self.token)
        self.session.headers.update({'Authorization': auth})

    def close_session(self):
        if self.session:
            self.session.close()

    def get(self, endpoint, payload=None):
        LOG.debug("GET")

        # self.start_session()

        try:
            url = self.url + endpoint
            LOG.debug("PAYLOAD -> {}".format(str(payload)))
            r = self.session.get(url, json=payload)

        except Exception as err:
            LOG.error("API POST error: {}".format(err))
            return "API GET error: {}".format(err)

        # finally:
        #     self.close_session()

        return r.json()

    def post(self, endpoint, payload):
        LOG.debug("POST")

        # self.start_session()

        try:
            url = self.url + endpoint
            LOG.debug("PAYLOAD -> {}".format(str(payload)))
            r = self.session.post(url, json=payload)

        except Exception as err:
            LOG.error("API POST error: {}".format(err))
            return "API POST error: {}".format(err)

        # finally:
        #     self.close_session()

        return r.json()

    # def get_token(self, session):
    #     LOG.info("GET TOKEN (simple_token={})".format(self.simple_token))
    #     try:
    #         endpoint = self.url + "tokens"
    #         payload = {'email': self.user, 'password': self.password}
    #
    #         r = session.post(endpoint, data=payload)
    #         LOG.info("response " + r.text)
    #
    #         if r.status_code == requests.codes.ok:
    #             token = r.json()
    #             self.simple_token = "simple-token {user} {token}".format(user=self.user, token=token['token'])
    #             self.session.headers.update({'Authorization': self.simple_token})
    #         else:
    #             LOG.error(r.status_code, r.content)
    #
    #     except Exception as err:
    #         LOG.error("Unable to get token: {0}".format(err))
    #         return "Unable to get token: {0}".format(err)
