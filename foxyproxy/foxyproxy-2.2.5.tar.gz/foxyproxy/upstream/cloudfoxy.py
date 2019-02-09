#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
***
Module:
***

#
# Copyright (C) Smart Arcs Ltd registered in the United Kingdom.
# Unauthorized copying of this file, via any medium is strictly prohibited
#
# This file is provided under a license as specified in the "LICENSE" file, which is part
# of this software package.
#
# Written by Smart Arcs <support@smartarchitects.co.uk>, August 2018
from foxyproxy.upstream.base_upstream import BaseUpstream
"""
import logging
import coloredlogs
import requests
from requests import adapters

from foxyproxy.upstream.base_upstream import BaseUpstream

__author__ = "Petr Svenda, Smart Arcs"
__copyright__ = 'Enigma Bridge Ltd, Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Beta'


# noinspection PyProtectedMember

logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)
# logger.addHandler(ch)
# fh = logging.FileHandler('foxyproxy.log')
# fh.setLevel(logging.INFO)
# logger.addHandler(fh)

coloredlogs.install(level='INFO', logger=logger)

logging.basicConfig(level=logging.DEBUG)


class CloudFoxy(BaseUpstream):
    """
    CloudFoxy server
    """
    def __init__(self, server_config):
        """
        Accepts a configuration of the upstream - using the SignerConfig object below

        :param server_config: an object with configuration parameters of the signing upstream, this object will be
                                stored in the attribute 'server'
        :type server_config: CloudFoxyConfig
        """
        super(CloudFoxy, self).__init__(server_config)

        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=3, pool_connections=60)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        pass

    # Function for parsing input request
    # ><reader name>|><cmd ID>:<"APDU" / "RESET" / "ENUM">:<optional hexa string, e.g. "00A4040304">|

    def cmd(self, command, terminal, reset=0):
        """

        :type command: str|None
        :type terminal: str
        :type reset: int
        """
        if command is None:
            payload = {'reset': str(reset), 'terminal': terminal}
        else:
            payload = {'reset': str(reset), 'terminal': terminal, 'apdu': command}

        return self._get_request(self.server.upstream_cmd, payload)

    def is_down(self):
        """
        Test if the upstream responds
        :return: time of the upstream server running time
        :rtype int
        """

        response_data = self._get_request(self.server.upstream_uptime, None)
        # let's parse the response, which is of 3 lines
        if response_data is None or len(response_data) == 0:
            return True
        else:
            return False

    def downtime(self):
        """

        :return: time of the upstream server running time
        :rtype int
        """

        response_data = self._get_request(self.server.upstream_uptime, None)
        # let's parse the response, which is of 3 lines
        if response_data is None:
            # logging.error("Hello request returns incorrect data None")
            return False  # it's probably down just now
        elif len(response_data) < 3:
            logging.error("Hello request returns incorrect data %s " % '|'.join(response_data))
            return False

        # let's take the second string on 2nd line, convert to integer
        new_uptime = int(response_data[1].split()[1])
        if new_uptime < self.server.up_time:
            self.server.stale = True
        self.server.up_time = new_uptime
        return self.server.stale

    def inventory(self):
        """
        Method requests a list of smartcards available at the upstream server
        :return:
        """
        return self._get_request(self.server.upstream_inventory, None)

    # #########################################################################
    # Private methods
    # #########################################################################
    def _get_request(self, cmd, payload):
        response_data = None

        # noinspection PyBroadException
        try:
            logging.debug('Going to send request to CloudFoxy ...')
            with self.session as s:
                s.headers.update({'Connection': 'close'})
                r = s.get(self.server.upstream_url + cmd, params=payload, headers=self.server.upstream_headers)
        except requests.ConnectionError:
            logging.error('Problem with connection - check the upstream FoxyRest\'s host and port are correct %s' %
                          self.server.upstream_url)
        except Exception as ex:
            template = "Connection {0} error: an exception of type {1} occurred. Arguments:\n{2!r}"
            logging.error(template.format(self.server.upstream_url + cmd, type(ex).__name__, ex.args))
        else:
            # process response
            content = r.content.decode()
            logging.debug('Response received: ' + content)
            response_data = []
            for line in content.splitlines():
                if line != 'null' and len(line) > 0:
                    response_data.append(line)
        finally:
            if self.session:
                self.session.close()

        return response_data


class CloudFoxyConfig(object):
    """
    Configuration for CloudFoxy server
    """
    CLOUD_FOXY_HOST = 'http://localhost:8081'

    def __init__(self, server=None, token='b'):
        if server is None:
            self.upstream_url = CloudFoxyConfig.CLOUD_FOXY_HOST
        else:
            self.upstream_url = server

        print("FoxyProxy will connect to an upstream CloudFoxy at %s" % self.upstream_url)

        #  rest proxy for CloudFoxy hardware platform, use basicj for more info
        self.upstream_cmd = '/api/v1/basic'
        self.upstream_uptime = '/api/v1/hello'
        self.upstream_inventory = '/api/v1/inventory'

        self.upstream_headers = {'X-Auth-Token': token}

        # #####################################################################
        # status information

        # up-time of the signer, if it can return the value - detection of resets
        self.up_time = 0

        # a flag showing, whether the configuration of the upstream server / crypto providers needs to be updated
        self.stale = True
