# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
***
Module: foxyproxy - CloudFoxy proxy - TCP proxy for flexible access to CloudFoxy RESTful API
***

# Copyright (C) Smart Arcs Ltd registered in the United Kingdom.
# Unauthorized copying of this file, via any medium is strictly prohibited
#
# This file is provided under a license as specified in the "LICENSE" file, which is part
# of this software package.
#
# Written by Smart Arcs <support@smartarchitects.co.uk>, August 2018
"""
import sys
import logging
import getopt
import os

from foxyproxy.beacon_thread import BeaconThread
from foxyproxy.foxy_proxy_tcp import FoxyProxyTCP
from foxyproxy.foxy_proxy_rest import FoxyProxyREST
from foxyproxy.csp import Register

__author__ = "Smart Arcs"
__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Beta'

proxy_version = '2.2.5'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)


def print_help():
    print("foxyproxy, version %s. (c) Smart Arcs Ltd. Visit https://gitlab.com/cloudfoxy .\n\n"
          "The proxy accepts the following parameters:" % proxy_version)
    print("  -h, --help - this help, if present it will stop the process\n")
    print("  -r, --register - will attempt to create certification request(s)\n")
    print("  -p <port>, --port <port> - port where the proxy listens, 4001 if not set\n")
    print("  -p2 <port>, --port2 <port> - port where proxy's RESTful and WS server listens, 4443 if not set\n")
    print("  -k <path>, --keys <path> - location of keys for downstream RESTfull HTTPS (folder must contain files ")
    print("        'privkey.pem' and 'fullchain.pem' files in LetsEncrypt format; if not present, HTTP only\n")
    print("  -s <url:port|path>, --server <url:port|path> - address of the upstream server, e.g., ")
    print("        FoxyRest - http://upstream.cloudfoxy.com:8081\n")
    print("  -c <signer>, --signer <signer> - identification of the signature provider; currently supported are "
          "\"ICA\", \"PGP\"\n")
    print("  -t <token>, --token <token> - authorization token / API key for the signing API")


def main():
    # noinspection PyUnusedLocal
    foxyproxy_port = None
    upstream_server = None
    token = None
    register = False
    key_folder = None  # if none, RESTful will be HTTP only
    signer_name = 'ica'
    foxyproxy_port = 0
    foxyproxy_port2 = 0
    if len(sys.argv) > 1:
        try:
            opts, args = getopt.getopt(sys.argv[1:], 'hrp:s:t:c:',
                                       ['help', 'register', 'port=', 'server=', 'signer=', 'token='])
        except getopt.GetoptError:
            # print help information and exit:
            print_help()
            print("You provided %s" % ' '.join(sys.argv[1:]))
            sys.exit(2)

        for o, a in opts:
            if o in ('-h', '--help'):
                print_help()
                exit(0)
            else:
                if o in ('-r', '--register'):
                    register = True
                if o in ('-p', '--port'):
                    if a.isdigit():
                        foxyproxy_port = int(a)
                    else:
                        print("Invalid value of the port, it has to be a number")
                if o in ('-p2', '--port2'):
                    if a.isdigit():
                        foxyproxy_port2 = int(a)
                    else:
                        print("Invalid value of the port2, it has to be a number")
                if o in ('-s', '--server'):
                    upstream_server = a.strip()
                if o in ('-c', '--signer'):
                    signer_name = a.strip().lower()
                if o in ('-t', '--token'):
                    token = a.strip()
                if o in ('-k', '-keys'):
                    key_folder = a.strip()

    upstream_test = upstream_server.lower().split('://')
    if ((len(upstream_test) < 2) or ((upstream_test[0] != 'file') and (upstream_test[0] != 'http')
                                     and (upstream_test[0] != 'https'))) and (upstream_test[0] != 'python'):
        print("Upstream signer must start with 'file://' or 'http://' or 'https://' or 'python")
        exit(-1)

    if (foxyproxy_port == foxyproxy_port2) and foxyproxy_port > 0:
        print("port and port2 must be different")
        exit(-1)
    if upstream_test[0] == 'file':
        # let's try to open the file
        file_path = upstream_test[1]
        if not os.path.isfile(file_path):
            print("Can't open the local signer %s" % file_path)
            exit(-1)
        if not os.access(file_path, os.R_OK):
            print("The local signer %s is not readable" % file_path)
            exit(-1)

    cmd_line = dict(upstream=upstream_server, signer=signer_name, token=token, register=register)

    # create an instance of the signing service according to the CLI parameters, default is:
    #  'ica', http://localhost:8081, token='b'
    signer = Register.get_service(cmd_line)

    # let's start checking the status of the upstream server - it works even when the upstream is just a
    # local command
    new_beacon = BeaconThread(signer)
    new_beacon.start()

    if not register:
        # and we finally start the proxy itself to accept client requests
        # first RESTful API

        restful = FoxyProxyREST(signer, downstream_port=foxyproxy_port, key_folder=key_folder)
        restful.start()

        # and then TCP server
        FoxyProxyTCP.start_server(downstream_port=foxyproxy_port, signer=signer)


if __name__ == '__main__':
    main()
