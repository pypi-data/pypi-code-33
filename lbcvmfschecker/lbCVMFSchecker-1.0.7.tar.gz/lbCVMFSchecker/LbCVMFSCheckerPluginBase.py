###############################################################################
# (c) Copyright 2016 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''

Module that allows to load all the checker Plugins

:author: Stefan-Gabriel CHITIC
'''
import logging
log = logging.getLogger()


class PluginBase(object):

    messages = []

    def __init__(self):
        self.messages = []
        self.info_messages = []
        self.name = self.__class__.__name__
        log.info("Loaded %s plugin" % self.name)

    def check(self):
        self.messages = []
        log.info("Performing checks for %s plugin" % self.name)
        self.execute()
        if len(self.messages) > 0:
            for msg in self.messages:
                log.error(msg)
        else:
            log.info("No errors in %s" % self.name)
        for msg in self.info_messages:
            log.info(msg)

    def execute(self):
        raise NotImplementedError

