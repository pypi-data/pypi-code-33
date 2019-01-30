# -*- coding: utf-8 -
#
# This file is part of tripod released under the MIT license.
#
"""
module daemon.py
------------------
Defines the tripod daemon/long-running application.
"""
from __future__ import print_function
import sys
import atexit


class DaemonApplication(object):
    """
    An application interface for configuring and loading
    the various necessities for any given daemon process.
    """
    def __init__(self, app_hooks, config, main_func=None):
        self.config = config
        self.logger = None
        # application events
        self.events = app_hooks
        if main_func is not None:
            self.main = main_func
        # register at_exit function to be called when any terminate signal is captured
        atexit.register(self.at_exit)
        self.events.on_app_init.send(self)

    def at_exit(self):
        self.events.on_app_exit.send(self)

    def run(self):
        try:
            self.main()
        except RuntimeError as e:
            print("\nError: %s\n" % e, file=sys.stderr)
            sys.stderr.flush()
            sys.exit(1)

    def main(self, *args, **kwargs):
        pass
