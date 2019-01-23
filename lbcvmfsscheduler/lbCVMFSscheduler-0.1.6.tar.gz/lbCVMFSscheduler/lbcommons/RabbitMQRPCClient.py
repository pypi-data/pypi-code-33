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
rp
:author: Stefan-Gabriel CHITIC
'''
from Common import Messenger
import pika
import uuid


class RPCClient(Messenger):
    '''
    Class used by cvmfs-lhcbdev.cern.ch to communicate with the outside world
    '''
    def __init__(self, caller_back,
                 vhost='/lhcb',
                 topic='topic.cvmfs', *args, **kwargs):
        '''
        Initialize props
        '''
        super(RPCClient, self).__init__(vhost=vhost,
                                        *args, **kwargs)
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.caller_back = caller_back
        self._topic_name = topic

    def publish(self, queueName, body):
        '''
        Send a message to the client
        '''
        self.channel.basic_publish(exchange=self._topic_name,
                                   routing_key=queueName,
                                   properties=pika.BasicProperties(
                                         reply_to=self.callback_queue,
                                         correlation_id=self.corr_id,
                                         delivery_mode=2,
                                         ),
                                   body=body)

    def _onResponse(self, ch, method, props, body):
        """ Callback function"""
        if self.corr_id == props.correlation_id:
            self.response = body

    def setupClient(self, bindingKeys=None):
        '''
        Setups the basic config for RPC client
        '''
        self.connection = self._getConnection()
        self.channel = self._setupChannel(self.connection.channel())

        result = self.channel.queue_declare(exclusive=True)
        queueName = result.method.queue

        if bindingKeys is None:
            bindingKeys = [queueName]
        # Now binding the queue to the topic
        for bindingKey in bindingKeys:
            self.channel.queue_bind(exchange=self._topic_name,
                                    queue=queueName,
                                    routing_key=bindingKey)

        self.callback_queue = result.method.queue
        self.channel.basic_consume(self._onResponse, no_ack=True,
                                   queue=self.callback_queue)
