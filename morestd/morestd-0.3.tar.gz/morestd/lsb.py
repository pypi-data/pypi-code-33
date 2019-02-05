#
# morestd: More standard libraries for Python
#
# Copyright 2010-2019 Ferry Boender, released under the MIT license
#

import os
import re


def get_os():
    """
    Use various files and LSB to figure out OS information such as the family
    and version.

    See also https://www.freedesktop.org/software/systemd/man/os-release.html.
    """
    os_info = {
        'family': 'unknown',
        'os': 'unknown',
        'version': (0, 0),
    }

    if os.path.exists('/etc/lsb-release'):
        with open('/etc/lsb-release', 'r') as f:
            for line in f:
                if line.strip() == "":
                    continue
                key, value = line.strip().split('=', 1)
                if key == 'DISTRIB_ID':
                    os_info['os'] = value.strip('"\' ').lower()
                    if value.lower().startswith('ubuntu'):
                        os_info['family'] = 'debian'
                if key == 'DISTRIB_RELEASE':
                    version = value.strip('"\'').split('.')
                    if len(version) > 1:
                        os_info['version'] = (int(version[0]), int(version[1]))
                    else:
                        os_info['version'] = (int(version[0]), 0)

    if os.path.exists('/etc/os-release'):
        with open('/etc/os-release', 'r') as f:
            for line in f:
                if line.strip() == "":
                    continue
                key, value = line.strip().split('=', 1)
                if key == 'ID_LIKE':
                    os_info['family'] = value.strip('"\'').lower()
                elif key == 'ID':
                    os_info['os'] = value.strip('"\'').lower()
                elif key == 'VERSION_ID':
                    version = value.strip('"\'').split('.')
                    if len(version) > 1:
                        os_info['version'] = (int(version[0]), int(version[1]))
                    else:
                        os_info['version'] = (int(version[0]), 0)

    if os.path.exists('/etc/redhat-release'):
        os_reg = re.compile(r'^(.*?) release (\d+)\.(\d+).*$')
        os_info['family'] = 'redhat'
        with open('/etc/redhat-release', 'r') as f:
            for line in f:
                if line.strip() == "":
                    continue
                match = os_reg.match(line)
                if match:
                    if 'centos' in match.groups()[0].lower():
                        os_info['os'] = 'centos'
                    elif 'red hat' in match.groups()[0].lower():
                        os_info['os'] = 'redhat'
                    if len(match.groups()) > 1:
                        os_info['version'] = (int(match.groups()[1]),
                                              int(match.groups()[2]))
                    else:
                        os_info['version'] = (int(version[0]), 0)

    return os_info


if __name__ == '__main__':
    import doctest
    doctest.testmod()
