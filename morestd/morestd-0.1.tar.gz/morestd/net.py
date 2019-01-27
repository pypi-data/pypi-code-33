#
# morestd: More standard libraries for Python
#
# Copyright 2010-2018 Ferry Boender, released under the MIT license
#

import socket


def fqdn():
    """
    Return Fully qualified domain name for this machine.

    Many machines have their fully qualified domain name (fqdn) incorrectly
    configured. For example, the hostname may contain the fqdn while the
    domainname part is empty. This function attempts to return a correct FQDN.
    """
    fqdn = socket.gethostname()
    if '.' not in fqdn:
        fqdn = socket.getfqdn()
    return fqdn


def ip4_hex_to_int(hex_ip):
    """
    Convert a little-indian hex IPv4 as found in /proc/net/tcp to a integer.

    >>> ip4_hex_to_int("0E01A8C0")  # 192.168.1.14
    3232235790
    """
    little_indian_int_ip = int(hex_ip, 16)
    big_indian_int_ip = socket.htonl(little_indian_int_ip)
    return big_indian_int_ip


if __name__ == '__main__':
    import doctest
    doctest.testmod()
