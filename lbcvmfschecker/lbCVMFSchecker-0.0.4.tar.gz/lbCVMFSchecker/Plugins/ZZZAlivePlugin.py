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


:author: Stefan-Gabriel CHITIC
'''

from lbCVMFSchecker.LbCVMFSCheckerPluginBase import PluginBase
import urllib2


class ZZZAlivePlugin(PluginBase):

    def __init__(self):
        super(ZZZAlivePlugin, self).__init__()

    def execute(self):
        try:
            r = urllib2.urlopen(
                "https://lbnightlies.cern.ch/updateCVMFSmonitor/")
            r.read()
        except urllib2.HTTPError as e:
            self.messages.append(e.code)


