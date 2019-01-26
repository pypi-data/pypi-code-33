# coding:utf-8
import random
import cli_print as cp
from ip_query import ip_query
from qwert import (list_fn, file_fn)


def requests_proxies(protocol: str = 'socks5',
                     host: str = '127.0.0.1',
                     port: int = 1080,
                     username: str = None,
                     password: str = None,
                     ):
    """
    Generate a dict for python requests.

    :param str protocol: Protocol
    :param str host: Host
    :param int port: Port number
    :param str username: Username
    :param str password: Password
    :return: dict or None
    """
    if username and password:
        proxy_string = '{protocol}://{username}:{password}@{host}:{port}'.format(protocol=protocol,
                                                                                 host=host,
                                                                                 port=port,
                                                                                 username=username,
                                                                                 password=password,
                                                                                 )
    else:
        proxy_string = '{protocol}://{host}:{port}'.format(protocol=protocol,
                                                           host=host,
                                                           port=port,
                                                           )

    return string2requests_proxies(proxy_string)


def line2dict(line: str, _internal: bool = False):
    """
    Convert text line to dict.

    :param str line: Text line
    :param bool _internal: ...
    :return: dict
    """
    r = dict()

    try:
        t = list_fn.remove(line.split(' '))

        length = len(t)
        if 3 <= length:
            r['protocol'] = t[0]
            r['host'] = t[1]
            r['port'] = int(t[2])

        if 5 <= length:
            r['username'] = t[3]
            r['password'] = t[4]
    except Exception as e:
        cp.error('[proxy_fn] {}'.format(e))
        return None

    if not _internal and not r:
        cp.error('[proxy_fn] Cannot parse a proxy from string: "{}"'.format(line))
        return None

    return r


def dict2string(proxy: dict, _internal: bool = False):
    """
    Convert a proxy dict to string.

    :param dict proxy: Proxy dict
    :param bool _internal: ...
    :return: str or None
    """
    length = len(proxy)

    try:
        if 5 <= length:
            return '{protocol}://{username}:{password}@{host}:{port}'.format(
                protocol=proxy['protocol'],
                username=proxy['username'],
                password=proxy['password'],
                host=proxy['host'],
                port=proxy['port'],
            )

        elif 3 <= length:
            return '{protocol}://{host}:{port}'.format(
                protocol=proxy['protocol'],
                host=proxy['host'],
                port=proxy['port'],
            )

    except Exception as e:
        cp.error('[proxy_fn] {}'.format(e))
        return None

    if not _internal:
        cp.error('[proxy_fn] Cannot parse a proxy from dict: {}'.format(proxy))

    return None


def dict2pyrogram_dict(proxy: dict, _internal: bool = False):
    """
    Convert a proxy dict for pyrogram.

    :param dict proxy: Proxy dict
    :param bool _internal: ...
    :return: dict or None
    """
    try:
        if proxy['protocol'] == 'socks5':
            length = len(proxy)
            if 5 <= length:
                return {
                    'hostname': proxy['host'],
                    'port': proxy['port'],
                    'username': proxy['username'],
                    'password': proxy['password'],
                }

            elif 3 <= length:
                return {
                    'hostname': proxy['host'],
                    'port': proxy['port'],
                }

    except Exception as e:
        cp.error('[proxy_fn] {}'.format(e))
        return None

    if not _internal:
        cp.error('[proxy_fn] Cannot parse a proxy from dict: {}'.format(proxy))

    return None


def line2string(line: str, _internal: bool = False):
    """
    Convert a text line to string.

    :param str line: Text line
    :param bool _internal: ...
    :return: str or None
    """
    return dict2string(line2dict(line, _internal=True), _internal)


def line2requests_proxies(line: str):
    """
    Convert a text line for python requests.

    :param str line: Text line
    :return: dict or None
    """
    return string2requests_proxies(line2string(line, _internal=True))


def line2pyrogram_dict(line: str):
    """
    Convert a text line for pyrogram.

    :param str line: Text line
    :return: dict or None
    """
    return dict2pyrogram_dict(line2dict(line, _internal=True))


def dict2requests_proxies(proxy: dict):
    """
    Convert a proxy dict for python requests.

    :param dict proxy: Proxy dict
    :return: dict or None
    """
    return string2requests_proxies(dict2string(proxy, _internal=True))


def string2requests_proxies(string: str):
    """
    Convert a proxy string for python requests.

    :param str string: Proxy string
    :return: dict
    """
    return {
        'http': string,
        'https': string,
    }


def random_a_proxy_dict_from_file(path_to_file: str):
    """
    Random a proxy dict from a certain file, with verification.

    :param str path_to_file: /path/to/file
    :return: dict or None
    """
    lines = file_fn.read_to_list(path_to_file)

    if lines:
        while len(lines) > 0:
            cp.getting('Random a proxy')

            # random
            _line = random.choice(lines)
            proxy_dict = line2dict(_line)

            # verify
            if proxy_dict:
                cp.wr('{host}:{port} '.format(host=proxy_dict['host'],
                                              port=proxy_dict['port'],
                                              ))
                cp.step(with_spaces=1)

                try:
                    ip = ip_query(requests_proxies=dict2requests_proxies(proxy_dict))

                    if ip:
                        cp.value(ip['ip'], inline=True)
                        if ip['country']:
                            cp.value(' ({})'.format(ip['country']), inline=True)
                        cp.fx()

                        return proxy_dict
                except Exception as e:
                    cp.error('[proxy_fn] {}'.format(e))

            lines.remove(_line)

    return None


def random_pyrogram_dict_from_file(path_to_file: str):
    """
    Random a proxy for pyrogram, from a certain file, with verification.

    :param str path_to_file: /path/to/file
    :return: dict or None
    """
    proxy = random_a_proxy_dict_from_file(path_to_file=path_to_file)
    if proxy:
        return dict2pyrogram_dict(proxy, _internal=True)

    return None
