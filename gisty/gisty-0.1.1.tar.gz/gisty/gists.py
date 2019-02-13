#!/usr/bin/python3
# -*- coding: latin-1 -*-
# gists.py
# Author Patrick McEvoy <patrick.mcevoy@gmail.com>

from typing import List
from types import SimpleNamespace
import requests
from requests.auth import HTTPBasicAuth
from colorama import Fore, Back, Style
import sys
import time
import datetime
import signal

import maya
from tabulate import tabulate

from .colourprint import ColourPrint
from .conf import parse_configuration

GITHUB_URI = 'https://api.github.com/users/{0}/gists'


def signal_handler(sig, frame):
    sys.exit(0)


def get_gists(conf: SimpleNamespace):
    url = GITHUB_URI.format(conf.username)
    if conf.since:
        url = '{}?since={}'.format(url, conf.since.iso8601())
    r_kwargs = {}
    if conf.auth:
        r_kwargs = {'auth': HTTPBasicAuth(conf.auth[0], conf.auth[1])}

    r = requests.get(url, **r_kwargs)

    if r.status_code == 404:
        return ('not_found', [])
    if r.status_code == 200:
        gists = r.json()
        return ('ok', gists)
    if r.status_code == 403:
        return ('rate_limited', {
            'limit': r.headers['X-RateLimit-Limit'],
            'remaining': r.headers['X-RateLimit-Remaining'],
            'reset': r.headers['X-RateLimit-Reset']
        })
    if not r.status_code == 200:
        return ('error', [])


def tabula_prepare(gists: List, columns: List):
    return list(map(lambda x: [x[c] for c in columns if c in columns], gists))


def print_tabula_gists(gists: List, columns: List):
    # Don't print blank lines when --watch
    if len(gists) > 0:
        cols = ['created_at', 'description', 'html_url']
        tbl = tabulate(tabula_prepare(gists, cols), headers=cols)
        print(tbl)


def print_list_gists(gists: List, cp: ColourPrint):
    for g in gists:
        created_at = maya.parse(g['created_at'])
        desc = g['description'] or '<< No description >>'

        cp.print('{created_at}', colour=Fore.WHITE,
                 created_at=created_at.rfc2822())
        cp.print('{desc}', colour=Fore.CYAN, desc=desc)
        cp.print('Files', colour=Fore.GREEN)
        for f in g['files']:
            cp.print(' - {name} [{lang}]', name=f,
                     lang=g['files'][f]['language'])
            cp.print('{url}', colour=Fore.BLUE, url=g['html_url'])
            cp.print('--', colour=Fore.MAGENTA)


def main():
    # Cleanly handle Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    conf = parse_configuration(sys.argv[1:])

    cp = ColourPrint(conf.colour)

    count = 0
    while True:
        gists_resp = get_gists(conf)

        if gists_resp[0] == 'not_found':
            cp.print('Username {username} was not found on GitHub',
                     colour=Fore.RED, username=username, error=True)
            sys.exit(1)

        if gists_resp[0] == 'rate_limited':
            reset = gists_resp[1]['reset']
            reset_date = datetime.datetime.fromtimestamp(int(reset))
            reset_human = maya.parse(reset_date).slang_time()

            cp.print((
                "Hit API rate limit. Will reset in {reset}. "
                "Consider using authentication with --auth"
            ), colour=Fore.RED, reset=reset_human, error=True)
            sys.exit(1)

        if gists_resp[0] == 'error':
            cp.print('Error connecting GitHub API',
                     colour=Fore.RED, error=True)
            sys.exit(1)

        gists = gists_resp[1] or []
        if len(gists) == 0 and not conf.watch:
            msg = "Username {username} doesn't have any public gists"
            if not conf.since:
                cp.print(msg + " yet",
                         colour=Fore.RED, username=conf.username, error=True)
            else:
                cp.print(msg + " since {since}",
                         colour=Fore.RED, username=conf.username,
                         since=conf.since.rfc2822(), error=True)
            sys.exit(1)

        if gists is not None and conf.order == 'asc':
            gists = gists[::-1]

        if conf.format == 'list':
            print_list_gists(gists, cp)
        else:
            print_tabula_gists(gists, cp)

        if not conf.watch:
            sys.exit(1)

        conf.since = maya.now()
        count += 1
        time.sleep(conf.n)


if __name__ == '__main__':
    main()
