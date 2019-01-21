# envconfg.py - set config options via an environment variable
#
# Copyright 2017 Sean Farley.
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
"""Set config options via an environment variable (EXPERIMENTAL)

This extension lets you specify an environment variable to set config options.
For example,

  HGCONFIG="ui.debug=True\ndiff.git=True" hg log -pr .

The benefit of this is so that other processes inherit the same config without
the need of writing or reading a file. Helpful in server configurations.

"""

from __future__ import absolute_import

import os

from mercurial.dispatch import _parseconfig
from mercurial.extensions import wrapfunction
from mercurial.hgweb.hgweb_mod import hgweb
from mercurial.util import safehasattr

testedwith = '3.9.2 4.0 4.0.1 4.0.2 4.1'


def uisetup(ui):
    class envconfigui(ui.__class__):
        def __init__(self, src=None):
            self._environ = None
            if src:
                self._environ = src.environ
            super(envconfigui, self).__init__(src)

        @property
        def environ(self):
            if not safehasattr(self, '_environ'):
                self._environ = os.environ
            return self._environ

        @environ.setter
        def environ(self, environ):
            _setenviron(self, environ)
            self._environ = environ

    def env_runwsgi(orig, hgweb, req, res, repo):
        _setenviron(repo.ui, repo.ui.environ)
        return orig(hgweb, req, res, repo)

    wrapfunction(hgweb, '_runwsgi', env_runwsgi)
    ui.__class__ = envconfigui


def _setenviron(ui, environ):
    config = environ.get('HGCONFIG')
    if config:
        # it's hard to insert an actual newline in an environment
        # variable, so replace a user writing '\n' with an actual
        # newline
        config = config.replace('\\n', '\n')

        # TODO: move this to util and refactor it a tad for use in this
        # case
        _parseconfig(ui, config.splitlines())
