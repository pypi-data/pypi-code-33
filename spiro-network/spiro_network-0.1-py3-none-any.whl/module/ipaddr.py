"""
Find the instance's external IP address.
"""

import random
import logging
try:
    import requests
except ImportError:
    pass

from salt.utils.decorators import depends


def _get(url):
    with requests.Session() as s:
        resp = s.get(url, timeout=5)
        resp.raise_for_status()
        return resp


IP4_FINDERS = [
    # https://whatismyipaddress.com/api
    lambda: (_get('https://ipv4bot.whatismyipaddress.com/').text.strip()),
    # http://api.ident.me/
    lambda: (_get('https://v4.ident.me/').text.strip()),
    # https://seeip.org
    lambda: (_get('https://ip4.seeip.org/').text.strip()),
    # https://wtfismyip.com/
    lambda: (_get('https://ipv4.wtfismyip.com/text').text.strip()),
    # https://major.io/icanhazip-com-faq/
    lambda: (_get('https://ipv4.icanhazip.com/').text.strip()),
]

IP6_FINDERS = [
    # https://whatismyipaddress.com/api
    lambda: (_get('https://ipv6bot.whatismyipaddress.com/').text.strip()),
    # http://api.ident.me/
    lambda: (_get('https://v6.ident.me/').text.strip()),
    # https://seeip.org
    lambda: (_get('https://ip6.seeip.org/').text.strip()),
    # https://wtfismyip.com/
    lambda: (_get('https://ipv6.wtfismyip.com/text').text.strip()),
    # https://major.io/icanhazip-com-faq/
    lambda: (_get('https://ipv6.icanhazip.com/').text.strip()),
]


def _find_one(pile):
    log = logging.getLogger('ipaddr.module')
    for _ in range(5):
        req = random.choice(pile)
        log.debug('Attempting %r', req)
        try:
            return req() or ''
        except Exception as e:
            log.debug(e)
            continue
    return ''


@depends('requests')
def external_four():
    """
    Queries an external service for the IPv4 address.

    A list of several services are used, selected at random.
    """
    return _find_one(IP4_FINDERS)


@depends('requests')
def external_six():
    """
    Queries an external service for the IPv6 address.

    A list of several services are used, selected at random.
    """
    return _find_one(IP6_FINDERS)


def four():
    """
    Tries to find as many external IPs as possible, looking in as many sources
    as possible.

    Currently looks at:
    * Network interfaces
    * AWS EC2 Metadata
    * External services
    """
    addrs = __salt__['network.ipaddrs'](type='public')

    extra = __salt__['grains.get']('meta-data:public-ipv4')
    if extra:
        addrs += [extra]
    
    if 'ipaddr.external_four' in __salt__:
        ext = __salt__['ipaddr.external_four']()
        if ext:
            addrs += [ext]

    return list(set(
        a
        for a in addrs
        if ':' not in a
    ))


def six():
    """
    Tries to find as many external IPs as possible, looking in as many sources
    as possible.

    Currently looks at:
    * Network interfaces
    * AWS EC2 Metadata
    * External services
    """
    addrs = __salt__['network.ipaddrs6']()

    extra = __salt__['grains.get']('meta-data:public-ipv6')
    if extra:
        addrs += [extra]

    if 'ipaddr.external_six' in __salt__:
        ext = __salt__['ipaddr.external_six']()
        if ext:
            addrs += [ext]

    return list(set(
        a 
        for a in addrs
        if not a.lower().startswith('fe80:') and '.' not in a
    ))
