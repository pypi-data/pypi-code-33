#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) Smart Arcs Ltd registered in the United Kingdom.
# Unauthorized copying of this file, via any medium is strictly prohibited
#
# This file is provided under a license as specified in the "LICENSE" file, which is part
# of this software package.
#
# Written by Smart Arcs <support@smartarchitects.co.uk>, August 2018
# import shlex
# import subprocess
import importlib

from foxyproxy.upstream.base_upstream import BaseUpstream

__author__ = "Smart Arcs"
__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Beta'

import logging
import coloredlogs
import requests
# from python_ica import python_ica
# from python_postsignum import python_postsignum

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
# coloredlogs.install(level='DEBUG', logger=logger) # to suppress logs from libs

logging.basicConfig(level=logging.DEBUG)


class PythonCard(BaseUpstream):
    """
    Main class for smartcard / updstream simulators for testing
    """
    def __init__(self, server_config):
        """
        Accepts a configuration of the upstream - using the SignerConfig object below

        :param server_config: an object with configuration parameters of the signing upstream, this object will be
                                stored in the attribute 'server'
        :type server_config: LinuxShellConfig
        """
        super(PythonCard, self).__init__(server_config)
        # dynamicallly resolve the module with Python card simulator
        try:
            card_module = importlib.import_module("upstream")
            card_class = getattr(card_module, server_config.upstream_url)
            self.server.readers['CloudFoxy'] = card_class('CloudFoxy')
            if card_class is None:
                raise Exception()
        except Exception as ex:
            logger.error("Requested upstream server implementation not found: %s (error: %s)"
                         % server_config.upstream_url, ex.message)
            exit(-1)
        pass

    # Function for parsing input request
    # ><reader name>|><cmd ID>:<"APDU" / "RESET" / "ENUM">:<optional hexa string, e.g. "00A4040304">|

    def cmd(self, payload, terminal, reset=0):
        """

        :type payload: str|list
        :type terminal: str
        :param reset: not used in this module
        :type reset:int
        """
        if ((payload is None) and (reset == 0)) or (terminal is None):
            logging.error("Requesting a command via LinuxShell requires the terminal and commands to be defined")
            exit(5)

        if payload is not None:
            if isinstance(payload, str):
                payload = [payload]
            counter = len(payload)
            raw_data = self._get_request(self.server.upstream_cmd, payload, terminal, reset)
            # TODO we may want to normalize commands and match them to responses from _get_request
            response = []
            for line in raw_data:
                line = ''.join(line.upper().split())
                response.append(line)  # and take the last part
                counter -= 1
                if counter < 1:
                    break

            return response

    def downtime(self):
        """

        :return: time of the upstream server running time
        :rtype int
        """

        downtime = False
        for reader_name in self.server.readers.keys():
            downtime = downtime or self.server.readers[reader_name].is_reset()
            self.server.readers[reader_name].up_time = self.server.up_time

        self.server.stale = False
        return downtime

    def inventory(self):

        reader_list = self.server.readers.keys()
        return reader_list

    # #########################################################################
    # Private methods
    # #########################################################################

    def _get_request(self, cmd, payload_in='', token=None, reset=0):
        """
        Upstream dependent request processing.
        :type cmd: str
        :type payload_in: str|list|None
        :type token: str|None
        """
        response_data = None
        if payload_in is None or len(payload_in) == 0:  # len should work for string as well as list
            payload = []
        elif isinstance(payload_in, list):
            payload = [payload_in.pop(0)]
            for each_cmd in payload_in:
                payload.append(each_cmd)
        else:
            payload = [payload_in]

        if token is None:
            terminal = ''
            return ['6AX2']  # we require reader name as it's only used here for cmd, not listing
        else:
            terminal = token

        effective_reader = None
        if terminal not in self.server.readers:
            logger.error("Requested a reader that is not available - PythonCard: %s" % terminal)
            return ['C000']

        effective_reader = self.server.readers[terminal]  # type: python_ica

        response_data = []

        if reset:
            response_data.append(self.server.readers[terminal].reset())

        for each_cmd in payload:
            # noinspection PyBroadException
            try:
                logging.debug('Going to send request to Python card provider ...')
                response_data.append(effective_reader.execute(each_cmd))
            except requests.ConnectionError:
                logging.error('Problem with connection - check that the command is correct: %s' %
                              self.server.upstream_url)
            except Exception as ex:
                template = "Connection {0} error: an exception of type {1} occurred. Arguments:\n{2!r}"
                logging.error(template.format(self.server.upstream_url + cmd, type(ex).__name__, ex.args))

        return response_data


class PythonCardConfig(object):
    PY_DEFAULT = 'ica'
    CARDS = {
        'ica': 'python_ica',
        'postsignum': 'python_postsignum'
    }

    def __init__(self, server=None, token='b'):
        self.token = token
        if token is None:
            self.upstream_url = PythonCardConfig.PY_DEFAULT
        elif token not in PythonCardConfig.CARDS:
            logger.error("This trust provider is not supported in Python modules: %s" % token)
            exit(-1)
        else:
            self.upstream_url = PythonCardConfig.CARDS[token]

        print("Python module is part of FoxyProxy - %s " %  self.upstream_url)

        #  rest proxy for CloudFoxy hardware platform, use basicj for more info
        self.upstream_cmd = ''
        self.upstream_uptime = ''
        self.upstream_inventory = ''
        self.test_local_reader = None

        self.upstream_headers = None
        # #####################################################################
        # status information

        # up-time of the signer, if it can return the value - detection of resets
        self.up_time = 0

        # a flag showing, whether the configuration of the upstream server / crypto providers needs to be updated
        self.stale = False

        # list of readers
        self.readers = dict()
        self.pending_readers = dict()
