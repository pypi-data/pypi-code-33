from types import SimpleNamespace
import argparse
import logging
import http.client

import requests
import maya


def parse_configuration(args):
    parser = argparse.ArgumentParser(description='Gisty. For querying gists on GitHub')
    parser.add_argument('username', help='GitHub username')
    parser.add_argument('--since', nargs=1, metavar='DATE',
                        help="Filter since human friendly date. eg. '1 day' or '6 months'")
    parser.add_argument('--watch', help='Poll for new gists',
                        action='store_true')
    parser.add_argument('-n', help='Poll for new gists every n seconds',
                        type=int, default=5)
    parser.add_argument('--colour', help='Colour output in list format',
                        action='store_true')
    parser.add_argument('--format', help='Output as list or table', nargs=1,
                        choices=['list', 'table'], default='table')
    parser.add_argument('--order', help='Order by created date', nargs=1,
                        choices=['desc', 'asc'], default=['asc'])
    parser.add_argument('--auth', help='Credentials to increase rate limit for GitHub API. Use format user:token',
                        nargs=1)
    parser.add_argument('-v', help='Increase verbosity to include requests logging',
                        action='store_true')

    args = parser.parse_args(args)

    # General
    args_dict = vars(args)
    simple_args = ['colour', 'username', 'watch', 'n']

    conf = SimpleNamespace(**{k : v for k,v in filter(lambda t: t[0] in simple_args, args_dict.items())})

    # Override desc sort when --watch
    conf.order = args.order[0]
    if args.watch:
        conf.order = 'desc'

    # Validate --since is parsed
    conf.since = None
    try:
        if args.since:
            conf.since = maya.when(args.since[0])
    except ValueError:
        cp.print("--since value {since} was not valid. Try '5 days', '3 months', '1 year', 'yesterday'.",
                 colour=Fore.RED, since=args.since, error=True)
        sys.exit(2)

    # Parse auth
    conf.auth = None
    try:
        if args.auth:
            conf.auth = (auth_username, auth_token) = args.auth[0].split(':')
    except ValueError:
        cp.print("--auth value was not valid. Use format user:token",
                 colour=Fore.RED, error=True)
        sys.exit(2)

    # Format to str
    conf.format = args.format[0]

    # Enable debugging
    if args.v:
        conf.verbose = True
        http.client.HTTPConnection.debuglevel = 1
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        req_log = logging.getLogger('requests.packages.urllib3')
        req_log.setLevel(logging.DEBUG)
        req_log.propagate = True

    return conf
