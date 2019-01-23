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
Command line client that interfaces to the Installer class

:author: Stefan-Gabriel CHITIC
'''

from lbmessaging.CvmfsDevExchange import CvmfsDevExchange
from lbmessaging.CvmfsConDBExchange import CvmfsConDBExchange
from lbmessaging.CvmfsProdExchange import CvmfsProdExchange

from lbmessaging.Common import get_connection
import lbmessaging

from lbCVMFSscheduler import exchangeManager


class RPCSchedulerExecutor(object):
    def __init__(self, vhost, command, args=[],
    			 exchangeType='CvmfsDevExchange'):
        self.command = command
        self.args = args
        connection = get_connection(vhost=vhost)
        exchangeType = exchangeManager.get(exchangeType, 'CvmfsDevExchange')
        self.broker = exchangeType(connection)
        self.priority = lbmessaging.priority(lbmessaging.NORMAL)
        self._call()

    def _call(self):
        self.broker.send_command(self.command, self.args,
                                 priority=self.priority)
