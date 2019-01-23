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

from lbCVMFSscheduler.lbcommons.RabbitMQRPCClient import RPCClient

from lbCVMFSscheduler.lbcommons.Messages import RbMessage


class RPCSchedulerExecutor(object):
    def __init__(self, command, args=[]):
        self.client = RPCClient(self.result)
        self.command = command
        self.args = args
        self.client.setupClient()
        self.id = self.client.corr_id
        self.returnCode = None
        self._call()

    def result(self, body):
        message = RbMessage()
        message.updateFromJson(body)
        payload = message.getPayload()
        id = message.getId()
        status = payload.get('status', None)
        content = payload.get('message', None)
        if not status or not content:
            return
        if content[-1] == '\n':
            content = content[0:len(content)-1]
        if id != 0:
            console_message = "[%s - %s] %s" % (status, id, content)
        else:
            console_message = "[%s] %s" % (status, content)
        if status in ["SUCCESS", "FAILED"]:
            self.returnCode = int(content.split(":")[-1])
        print(console_message)

    def _call(self):
        message = RbMessage(id=self.id, payload={
            'command': self.command,
            'args': self.args
        })
        self.client.publish('commands', message.convertToJson())

