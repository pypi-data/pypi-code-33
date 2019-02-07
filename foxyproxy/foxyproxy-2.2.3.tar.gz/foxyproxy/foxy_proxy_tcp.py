#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
"""
***
Module:
***

 Copyright (C) Smart Arcs Ltd, registered in the United Kingdom.
 This file is owned exclusively by Smart Arcs Ltd.
 Unauthorized copying of this file, via any medium is strictly prohibited
 Proprietary and confidential
 Written by Smart Arcs <support@smartarchitects.co.uk>, May 2018
"""
import logging
import socket
import sys
import time

from foxyproxy.client_thread import ClientThread

__author__ = "Smart Arcs"
__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Development'


class FoxyProxyTCP(object):
    """
    Request processing for TCP requests
    """
    PROXY_PORT = 4001

    def __init__(self):
        pass

    @staticmethod
    def start_server(downstream_port, signer):
        """
        we start one monitoring thread, while the main thread will start spawning TCP upstream threads
        when the monitoring thread detects restart of the RESTful upstream, it will load all certificates from connected
        smart-cards, these are needed for requests coming from jsignpdf - SIGN - where responses consist of
        a list of certificates and a result of signing.

        :param downstream_port: the port for the FoxyProxy server
        :type downstream_port: int
        :param signer: an instance of a subclass derived from BaseCryptoService
        :type signer: BaseCryptoService
        """

        if downstream_port is None or downstream_port == 0:
            downstream_port = FoxyProxyTCP.PROXY_PORT

        bound = False
        tries = 10
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.debug('FoxyProxy TCP listening socket created')

        while tries > 0 and not bound:
            try:
                soc.bind(('', downstream_port))
                logging.info('FoxyProxy socket bind complete. host:{0}, port:{1}'
                              .format("", downstream_port))
                bound = True
            except socket.error as msg:
                logging.error('FoxyProxy bind failed. Error Code : %s' % str(msg))
                soc.close()
                tries -= 1
                time.sleep(5)
                soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if not bound:
            logging.error("The port %d is used by another process" % downstream_port)
            sys.exit()

        # Start listening on socket
        soc.listen(128)  # default somaxconn
        logging.info('TCP API of FoxyProxy is up and running, listening on port %d' % downstream_port)

        # now keep talking with the client
        while True:
            # wait to accept a connection - blocking call
            conn, addr = soc.accept()
            ip, port = str(addr[0]), str(addr[1])
            logging.info('A new connection from ' + ip + ':' + port)

            # start new thread takes with arguments
            new_client = ClientThread("TCP", conn, signer)

            new_client.start()
            new_client.join()  # commenting this out -> multi-threaded processing

        # soc.close()  #  unreachable
