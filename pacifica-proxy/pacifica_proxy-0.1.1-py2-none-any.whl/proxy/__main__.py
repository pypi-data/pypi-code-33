#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Main proxy module."""
from __future__ import print_function
from argparse import ArgumentParser, SUPPRESS
from time import sleep
from threading import Thread
import cherrypy
import requests
from .rest import Root, error_page_default
from .globals import CHERRYPY_CONFIG
from .config import get_config


def try_meta_connect(attempts=0):
    """Try to connect to the metadata service see if its there."""
    try:
        ret = requests.get(
            get_config().get('metadata', 'status_url').encode('utf-8')
        )
        if ret.status_code != 200:
            raise Exception('try_meta_connect: {0}\n'.format(ret.status_code))
    # pylint: disable=broad-except
    except Exception as ex:
        # pylint: enable=broad-except
        if attempts < get_config().getint('metadata', 'status_attempts'):
            sleep(get_config().getint('metadata', 'status_wait'))
            attempts += 1
            try_meta_connect(attempts)
        else:
            raise ex


def stop_later(doit=False):
    """Used for unit testing stop after 10 seconds."""
    if not doit:  # pragma: no cover
        return

    def sleep_then_exit():
        """sleep for 10 seconds then call cherrypy exit."""
        sleep(10)
        cherrypy.engine.exit()
    sleep_thread = Thread(target=sleep_then_exit)
    sleep_thread.daemon = True
    sleep_thread.start()


def main():
    """Main method for running the server."""
    parser = ArgumentParser(description='Run the proxy server.')
    parser.add_argument('-c', '--config', metavar='CONFIG', type=str,
                        default=CHERRYPY_CONFIG, dest='config',
                        help='cherrypy config file')
    parser.add_argument('-p', '--port', metavar='PORT', type=int,
                        default=8180, dest='port',
                        help='port to listen on')
    parser.add_argument('-a', '--address', metavar='ADDRESS',
                        default='localhost', dest='address',
                        help='address to listen on')
    parser.add_argument('--stop-after-a-moment', help=SUPPRESS,
                        default=False, dest='stop_later',
                        action='store_true')
    args = parser.parse_args()
    stop_later(args.stop_later)
    cherrypy.config.update({'error_page.default': error_page_default})
    cherrypy.config.update({
        'server.socket_host': args.address,
        'server.socket_port': args.port
    })
    cherrypy.quickstart(Root(), '/', args.config)


if __name__ == '__main__':
    main()
