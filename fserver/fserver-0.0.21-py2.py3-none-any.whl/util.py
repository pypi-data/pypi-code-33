# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import re
import sys

from fserver import conf
from fserver.path_util import to_unicode_str


def debug(*args):
    if conf.DEBUG:
        pretty_print(sys.stdout, *args)


def warning(*args):
    pretty_print(sys.stderr, *args)


def pretty_print(file, *args):
    min_len = 40
    msg = ''
    for i in args:
        j = to_unicode_str(i)
        msg += j + ' '
    msg = '| ' + msg.replace('\n', '\n| ')
    ln = max([len(i) + 3 for i in msg.split('\n')])
    ln = ln if ln > min_len else min_len
    print('_' * ln, file=file)
    print(msg, file=file)
    print('=' * ln, file=file)


def _get_ip_v4_ipconfig():
    ips = set()
    try:
        ip_cmd = os.popen('ipconfig 2>&1').read().split('\n')
        for line in ip_cmd:
            if 'ip' not in line.lower():
                continue
            [ips.add(i) for i in line.replace('\r', '').split(' ')  # filter ip mask
             if is_ip_v4(i) and not i.startswith('255') and not i.endswith('.0')]
        # [ips.append(s[s.index(':') + 2:]) for s in ip_cmd if 'ipv4' in s.lower()]
        ips.add('127.0.0.1')
    except Exception as e:
        debug(e)
    return ips


def _get_ip_v4_ifconfig():
    ips = set()
    sh = r"""ifconfig 2>&1 | \
    awk -F '[ :]' 'BEGIN{print "succeed"}/inet /{ for (i=1;i<=NF;i++){ if ($i~/[0-9]\./) {print $i;break }} }' 2>&1 """
    try:
        ip_cmd = os.popen(sh).read()
        if 'succeed' in ip_cmd:
            [ips.add(i) for i in ip_cmd.split('\n') if i != '' and i != 'succeed']
        ips.add('127.0.0.1')
    except Exception as e:
        debug(e)
    return ips


def _get_ip_v4_ip_add():
    ips = set()
    sh = r"""ip -4 add 2>&1 |awk 'BEGIN{print "succeed"} $2 ~/^[0-9]+\./ {print $2}' | awk -F/ '{print $1}'"""
    try:
        ip_cmd = os.popen(sh).read()
        if 'succeed' in ip_cmd:
            [ips.add(i) for i in ip_cmd.split('\n') if i != '' and i != 'succeed']
        ips.add('127.0.0.1')
    except Exception as e:
        debug(e)
    return ips


def get_ip_v4():
    if os.name == 'nt':
        ips = _get_ip_v4_ipconfig()
    elif os.name == 'posix':
        ips = _get_ip_v4_ip_add()
        [ips.add(i) for i in _get_ip_v4_ipconfig()]

    for ip in [i for i in ips]:
        if ip.startswith('169.254.'):
            ips.remove(ip)

    return ips


def is_ip_v4(str):
    r = re.match(r'((?:(?:25[0-5]|2[0-4]\d|(?:1\d{2}|[1-9]?\d))\.){3}(?:25[0-5]|2[0-4]\d|(?:1\d{2}|[1-9]?\d)))', str)
    if r is not None and r.span()[1] == len(str):
        return True
    else:
        return False


if __name__ == '__main__':
    print(_get_ip_v4_ipconfig())
    print(_get_ip_v4_ip_add())
    print(_get_ip_v4_ifconfig())
    print(is_ip_v4('127.1.1.1'))
    print(is_ip_v4('127.a.1.1'))
    print(is_ip_v4('0.0.0.0'))
