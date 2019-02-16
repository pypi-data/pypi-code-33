# -*- coding: utf-8 -*-
# This file is part of the pycalver project
# https://github.com/mbarkhau/pycalver
#
# Copyright (c) 2018 Manuel Barkhau (@mbarkhau) - MIT License
# SPDX-License-Identifier: MIT
#
# pycalver/vcs.py (this file) is based on code from the
# bumpversion project: https://github.com/peritus/bumpversion
# Copyright (c) 2013-2014 Filip Noetzel - MIT License
"""Minimal Git and Mercirial API.

If terminology for similar concepts differs between git and
mercurial, then the git terms are used. For example "fetch"
(git) instead of "pull" (hg) .
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import os
import logging
import tempfile
import typing as typ
import subprocess as sp
str = getattr(__builtins__, 'unicode', str)
log = logging.getLogger('pycalver.vcs')
VCS_SUBCOMMANDS_BY_NAME = {'git': {'is_usable': 'git rev-parse --git-dir',
    'fetch': 'git fetch', 'ls_tags': 'git tag --list', 'status':
    'git status --porcelain', 'add_path': 'git add --update {path}',
    'commit': 'git commit --file {path}', 'tag':
    'git tag --annotate {tag} --message {tag}', 'push_tag':
    'git push origin {tag}', 'show_remotes':
    'git config --get remote.origin.url'}, 'hg': {'is_usable': 'hg root',
    'fetch': 'hg pull', 'ls_tags': 'hg tags', 'status': 'hg status -mard',
    'add_path': 'hg add {path}', 'commit': 'hg commit --logfile {path}',
    'tag': 'hg tag {tag} --message {tag}', 'push_tag': 'hg push {tag}',
    'show_remotes': 'hg paths'}}
Env = typ.Dict[str, str]


class VCS(object):
    """VCS absraction for git and mercurial."""

    def __init__(self, name, subcommands=None):
        self.name = name
        if subcommands is None:
            self.subcommands = VCS_SUBCOMMANDS_BY_NAME[name]
        else:
            self.subcommands = subcommands

    def __call__(self, cmd_name, env=None, **kwargs):
        """Invoke subcommand and return output."""
        cmd_tmpl = self.subcommands[cmd_name]
        cmd_str = cmd_tmpl.format(**kwargs)
        if cmd_name in ('commit', 'tag', 'push_tag'):
            log.info(cmd_str)
        else:
            log.debug(cmd_str)
        output_data = sp.check_output(cmd_str.split(), env=env, stderr=sp.
            STDOUT)
        _encoding = 'utf-8'
        return output_data.decode(_encoding)

    @property
    def is_usable(self):
        """Detect availability of subcommand."""
        if not os.path.exists('.{0}'.format(self.name)):
            return False
        cmd = self.subcommands['is_usable'].split()
        try:
            retcode = sp.call(cmd, stderr=sp.PIPE, stdout=sp.PIPE)
            return retcode == 0
        except OSError as e:
            if e.errno == 2:
                return False
            raise

    @property
    def has_remote(self):
        try:
            output = self('show_remotes')
            if output.strip() == '':
                return False
            return True
        except Exception:
            return False

    def fetch(self):
        """Fetch updates from remote origin."""
        if self.has_remote:
            self('fetch')

    def status(self):
        """Get status lines."""
        status_output = self('status')
        return [line[2:].strip() for line in status_output.splitlines() if 
            not line.strip().startswith('??')]

    def ls_tags(self):
        """List vcs tags on all branches."""
        ls_tag_lines = self('ls_tags').splitlines()
        log.debug('ls_tags output {0}'.format(ls_tag_lines))
        return [line.strip().split(' ', 1)[0] for line in ls_tag_lines]

    def add(self, path):
        """Add updates to be included in next commit."""
        try:
            self('add_path', path=path)
        except sp.CalledProcessError as ex:
            if 'already tracked!' in str(ex):
                return
            else:
                raise

    def commit(self, message):
        """Commit added files."""
        message_data = message.encode('utf-8')
        tmp_file = tempfile.NamedTemporaryFile('wb', delete=False)
        assert ' ' not in tmp_file.name
        fh = None
        with tmp_file as fh:
            fh.write(message_data)
        env = os.environ.copy()
        env['HGENCODING'] = 'utf-8'
        self('commit', env=env, path=tmp_file.name)
        os.unlink(tmp_file.name)

    def tag(self, tag_name):
        """Create an annotated tag."""
        self('tag', tag=tag_name)

    def push(self, tag_name):
        """Push changes to origin."""
        if self.has_remote:
            self('push_tag', tag=tag_name)

    def __repr__(self):
        """Generate string representation."""
        return "VCS(name='{0}')".format(self.name)


def get_vcs():
    """Detect the appropriate VCS for a repository.

    raises OSError if the directory doesn't use a supported VCS.
    """
    for vcs_name in VCS_SUBCOMMANDS_BY_NAME.keys():
        vcs = VCS(name=vcs_name)
        if vcs.is_usable:
            return vcs
    raise OSError('No such directory .git/ or .hg/ ')
