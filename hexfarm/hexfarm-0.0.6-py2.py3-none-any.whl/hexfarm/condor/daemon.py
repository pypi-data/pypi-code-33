# -*- coding: utf-8 -*- #
#
# hexfarm/condor/daemon.py
#
#
# MIT License
#
# Copyright (c) 2018-2019 Brandon Gomes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

"""
Daemon Utilities for the HTCondor Parallel Computing Framework.

"""

# -------------- Standard Library -------------- #

from dataclasses import dataclass
from inspect import cleandoc as clean_source

# -------------- External Library -------------- #

from paramiko import SSHClient, AutoAddPolicy
from path import Path

# -------------- Hexfarm  Library -------------- #

from ..util import classproperty, value_or
from .core import *


__all__ = (
    'clean_source',
    'ssh_connection',
    'sftp_connection',
    'get_data',
    'put_data'
)


def ssh_connection(hostname, port=22, username=None, password=None, *, missing_host_key_policy=AutoAddPolicy, **kwargs):
    """Establish SSH Connection."""
    client = SSHClient()
    client.set_missing_host_key_policy(missing_host_key_policy())
    connection = client.connect(hostname=hostname,
                                port=port,
                                username=username,
                                assword=password,
                                **kwargs)
    return connection, client


def sftp_connection(hostname, port=22, username=None, password=None, *args, **kwargs):
    """Establish SFTP Connection."""
    connection, client = ssh_connection(hostname,
                                        port=port,
                                        username=username,
                                        password=password,
                                        *args,
                                        **kwargs)
    return connection, client.open_sftp()


def get_data(connection, *, remove_source=False):
    """Get Data from Connection."""
    def inner_get(localpath, remotepath):
        atrributes = connection.put(localpath, remotepath)
        if remove_source:
            try:
                connection.remove(remotepath)
            except IOError:
                connection.rmdir(remotepath)
        return attributes
    return inner_put


def put_data(connection, *, remove_source=False):
    """Put Data Across Connection."""
    def inner_put(localpath, remotepath):
        atrributes = connection.put(localpath, remotepath)
        if remove_source:
            localpath = Path(localpath)
            if localpath.isdir():
                localpath.removedirs_p()
            elif localpath.isfile():
                localpath.remove_p()
        return attributes
    return inner_put


class PseudoDaemon:
    """
    Condor PseudoDaemon.

    """

    @classproperty
    def source_header(cls):
        """Default Source Header."""
        return clean_source('''
            #!/usr/bin/env python3
            # -*- coding: utf-8 -*-

            import sys
            import time
            import logging

            logger = logging.getLogger(__name__)
            ''')

    @classproperty
    def source_hexfarm_import(cls):
        """Default Hexfarm Import."""
        return 'from hexfarm import run_main'

    @classproperty
    def source_footer(cls):
        """Default Footer."""
        return '\n\n'

    @classproperty
    def default_source(cls):
        """Default Source Code."""
        return '\n\n'.join((cls.source_header,
                            cls.source_hexfarm_import,
                            clean_source('''
                                @run_main()
                                def main(argv):
                                    argv = argv[1:]
                                    print(argv, len(argv), 'args')
                                    return 0
                                '''),
                            cls.source_footer))

    def __init__(self, name):
        """Initialize PseudoDaemon."""
        return NotImplemented

    @property
    def is_built_from_source(self):
        """Check if Daemon is Built From Source Code."""
        return hasattr(self, source)

    def start(self, *args, **kwargs):
        """Start PseudoDaemon."""
        return NotImplemented
