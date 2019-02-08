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
from path import Path

# -------------- External Library -------------- #

from paramiko import SSHClient, AutoAddPolicy

# -------------- Hexfarm  Library -------------- #

from .core import *


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
