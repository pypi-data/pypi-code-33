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
import logging
import threading
import time
from traceback import print_exc
import datetime

__author__ = "Smart Arcs"
__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Development'

logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)
# logger.addHandler(ch)

# noinspection PyUnusedLocal
class BeaconThread(threading.Thread):
    """
    Class starts a thread, which regularly connects to a restful upstream and re-builds a dictionary of certificates
    when the upstream restarts
    """

    def __init__(self, signer, interval=10):
        """
        :param signer: an instance of the signer - crypto provider, which also wraps the upstream server configuration
        :type signer: BaseCryptoService
        :param interval: how often we check whether the upstream server needs refresh
        :type interval: int
        """
        threading.Thread.__init__(self)
        self.server = signer
        self.interval = interval
        pass

    def run(self):
        throwaway = datetime.datetime.strptime('20110101', '%Y%m%d')

        while True:
            # noinspection PyBroadException
            try:
                self.server.init()

                time.sleep(10)  # every this many seconds, we will check up-time
                pass  # end of the infinite cycle loop
            except Exception as ex:
                # we ignore exceptions, keep running
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                logging.error(template.format(type(ex).__name__, ex.args))
                logging.debug(print_exc())

                pass
        pass
