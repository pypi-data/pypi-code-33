from __future__ import print_function
import argparse
import logging
import sys

import sleekxmpp

from . import LVAlertClient, DEFAULT_SERVER


def parser():
    parser = argparse.ArgumentParser(prog='lvalert')
    parser.add_argument('-l', '--log', help='Log level', default='error',
                        choices='critical error warning info debug'.split())
    parser.add_argument('-n', '--netrc',
                        help='netrc file (default: read from NETRC '
                        'environment variable or ~/.netrc)')
    parser.add_argument('-r', '--resource',
                        help='XMPP resource (default: random)')
    parser.add_argument('-s', '--server', default=DEFAULT_SERVER,
                        help='LVAlert server hostname')
    parser.add_argument('-u', '--username',
                        help='User name (default: look up in netrc file)')

    subparsers = parser.add_subparsers(dest='action', help='sub-command help')
    subparsers.required = True

    subparser = subparsers.add_parser(
        'listen', help='Listen for LVAlert messages and print them to stdout.')

    subparser = subparsers.add_parser(
        'subscriptions', help='List your subscriptions')

    subparser = subparsers.add_parser(
        'nodes', help='List available pubsub nodes')

    subparser = subparsers.add_parser(
        'subscribe', help='Subscribe to one or more nodes')
    subparser.add_argument(
        'node', nargs='+', help='a pubsub node (e.g. cbc_gstlal)')

    subparser = subparsers.add_parser(
        'unsubscribe', help='Unsubscribe from one or more nodes')
    subparser.add_argument(
        'node', nargs='+', help='a pubsub node (e.g. cbc_gstlal)')

    return parser


def show(node, payload):
    print('Got item for node:', node)
    print(payload)
    print()


def main(args=None):
    opts = parser().parse_args(args)

    if opts.log is not None:
        logging.basicConfig(level=opts.log.upper())

    xmpp = LVAlertClient(username=opts.username,
                         resource=opts.resource,
                         server=opts.server,
                         netrc=opts.netrc,
                         interactive=True)

    if not xmpp.connect(reattempt=False):
        sys.exit(1)

    try:
        if opts.action == 'listen':
            xmpp.listen(show)
            xmpp.process(block=True)
        else:
            xmpp.auto_reconnect = False
            xmpp.process(block=False)
            if opts.action == 'nodes':
                print(*xmpp.get_nodes(), sep='\n')
            elif opts.action == 'subscriptions':
                print(*xmpp.get_subscriptions(), sep='\n')
            elif opts.action == 'subscribe':
                xmpp.subscribe(*opts.node)
            elif opts.action == 'unsubscribe':
                xmpp.unsubscribe(*opts.node)
    except sleekxmpp.exceptions.IqError as e:
        print('XMPP error:', e.iq['error'], file=sys.stderr)
    finally:
        xmpp.disconnect()
