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
try:
    from urllib.request import urlopen
    from urllib.error import HTTPError
except Exception as e:
    from urllib2 import urlopen, HTTPError
import ssl


class ZZZAlivePlugin(PluginBase):

    def __init__(self):
        super(ZZZAlivePlugin, self).__init__()

    def execute(self):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        try:
            r = urlopen(
                "https://lhcb-nightlies.cern.ch/updateCVMFSmonitor/",
                context=ctx)
            r.read()
        except HTTPError as e:
            self.messages.append(e.code)


