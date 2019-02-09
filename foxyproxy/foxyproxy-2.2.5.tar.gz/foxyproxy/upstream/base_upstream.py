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

__author__ = "Petr Svenda, Smart Arcs"
__copyright__ = 'Enigma Bridge Ltd, Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Beta'

# Based on Simple socket upstream using threads by Silver Moon
# (https://www.binarytides.com/python-socket-server-code-example/)
import logging
import coloredlogs

logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)
# logger.addHandler(ch)
# fh = logging.FileHandler('foxyproxy.log')
# fh.setLevel(logging.INFO)
# logger.addHandler(fh)

coloredlogs.install(level='INFO')
# coloredlogs.install(level='DEBUG', logger=logger) # to suppress logs from libs

logging.basicConfig(level=logging.DEBUG)


class BaseUpstream(object):
    """
    Abstract class for upstream signers
    """
    def __init__(self, server_config):
        """
        :type server_config: type(BaseUpstreamConfig)
        """
        self.server = server_config
        pass

    def cmd(self, command, terminal, reset=0):
        """

        :param command:
        :type command: str|list|None
        :param terminal: the identification of the token
        :type terminal: str
        :param reset: a flag wither the token should be reset before the command execution
        :type reset: int
        :return:
        """
        return NotImplementedError("Please implement 'cmd'")

    def set_uptime(self):
        """
        Flags the server as refreshed
        :return:
        """
        if self.server:
            self.server.stale = False

    def is_down(self):
        """
        If the upstream server can be down, this method needs to be implemented in its handler class
        :return:
        """
        return False

    def downtime(self):
        """
        Checks if the signer has been reset since the last time
        :return:
        """
        return NotImplementedError("Please implement 'downtime'")

    def inventory(self):
        """
        Returns a list of available signers
        :return:
        """
        return NotImplementedError("Please implement 'inventory'")

    def refresh(self):
        """
        Request a refresh of all available signers
        :return:
        """
        return NotImplementedError("Please implement 'refresh'")


class BaseUpstreamConfig(object):
    """
    Abstract class for upstream signer configuration
    """
    def __init__(self):
        """
        An object to hide all relevant configuration parameters.
        """
        self.stale = True
        pass
