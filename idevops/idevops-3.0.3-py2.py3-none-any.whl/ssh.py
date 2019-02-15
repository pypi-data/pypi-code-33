#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 jack <jack@iOSTdeMacBook-Pro.local>
#
# Distributed under terms of the MIT license.

"""
ssh
"""

import click
import subprocess
import sys
import warnings

from utils import *

def issh(name, node):
    """Interactive ssh"""
    host, key = get_host_and_key(name, node)
    if host:
        status = subprocess.call('ssh -o StrictHostKeyChecking=no -o' +
                'UserKnownHostsFile=/dev/null -i ' + key + ' ' + host, shell=True)

def ssh_cmd(name, node, cmd):
    """Non-interactice ssh"""
    host, key = get_host_and_key(name, node)
    if host:
        ssh = subprocess.Popen(['ssh', '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null', '-i', key, host] + list(cmd),
                shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = ssh.stdout.readlines()
        if result == []:
            for error in ssh.stderr.readlines():
                click.echo(error, err=True, nl=False)
        else:
            for line in result:
                click.echo(line, nl=False)

def gen_key_pair(name, is_overwrite=False):
    """Create local key pair.
    Prompt if exists.
    """
    key = get_path(name, name)
    if os.path.exists(key) and is_overwrite:
        yes = subprocess.Popen(['yes', 'y'], stdout=subprocess.PIPE)
        subprocess.call(['ssh-keygen', '-b', '2048', '-t', 'rsa', '-f', key, '-N', '', '-q']
                , stdin=yes.stdout)
        yes.terminate()
    else:
        subprocess.call(['ssh-keygen', '-b', '2048', '-t', 'rsa', '-f', key, '-N', '', '-q'])

def scp(name, par1, par2):
    """Copy file using scp."""

    # parse argument
    grp1 = par1.split(':')
    grp2 = par2.split(':')
    if len(grp1) == 2:
        assert len(grp2) == 1, 'scp <remote_host>:<remote_path> <local_path>'
        host, key = get_host_and_key(name, grp1[0])
        scp_par = [host + ':' + grp1[1], grp2[0]]
    else:
        assert len(grp1) == 1 and len(grp2) == 2, 'scp <local_path> <remote_host>:<remote_path>'
        host, key = get_host_and_key(name, grp2[0])
        scp_par = [grp1[0], host + ':' + grp2[1]]

    if host:
        ssh = subprocess.Popen(['scp', '-o', 'StrictHostKeyChecking=no', '-o',
            'UserKnownHostsFile=/dev/null', '-i', key] + scp_par,
                shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = ssh.stdout.readlines()
        if result == []:
            for error in ssh.stderr.readlines():
                click.echo(error, err=True, nl=False)
        else:
            for line in result:
                click.echo(line, nl=False)
