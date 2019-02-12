#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 jack <jack@localhost>
#
# Distributed under terms of the MIT license.

"""
shell command wrapper
"""

import os.path
import subprocess

from idevops.utils import *

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

def play_wrap(inventory, playbook, subset, *args, **kargs):
    extra = []
    for e in args:
        extra.append("-e")
        extra.append(e)

    cmd = [ 'ansible-playbook', '-b',
            '-i', inventory,
            '-l', subset,
            ] + extra + [find_playbook(playbook)]

    if 'verbose' in kargs and kargs['verbose']:
        print(cmd)

    subprocess.call(cmd, env=ENV)

