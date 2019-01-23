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
from Common import Messenger
import pika
import time


class RPCServer(Messenger):
    '''
    Class used by cvmfs-lhcbdev.cern.ch to communicate with the outside world
    '''
    def __init__(self, vhost, topic, caller_back, *args, **kwargs):
        '''
        Initialize props
        '''
        super(RPCServer, self).__init__(vhost=vhost, *args, **kwargs)
        self.caller_back = caller_back
        self._topic_name = topic
        self._timeout = 5  # Number of seconds to wait for a message
        self.last_request_time = None
        self.method = None
        self.props = None
        self.channel = None
        self.backLog = []
        # Flag used to force the use of backup channel instead of backLog
        # since we know that the server will never server (e.g Fail to get
        # lock)
        self.useBackup = False

    def forceBackupUse(self):
        """
        Forces the use of the backup channel
        :return:
        """
        self.useBackup = True

    def start_consume(self, channel, queueName):
        """
        Queue consume function to handle demon termination after a timeout
        has been reached since the last consumed message.
        This is needed since the connection.add_timeout is triggered only once
        and does not take into account the time since last consumed message.

        :param channel:
        :param queueName:
        :return:
        """
        if self.last_request_time is None:
            self.last_request_time = time.time()
        while True:
            time_diff = time.time() - self.last_request_time
            method_frame, header_frame, body = channel.basic_get(
                queue=queueName)
            if method_frame is None and time_diff > self._timeout:
                break
            if method_frame:
                self._onRequest(channel, method_frame, header_frame, body)

    def _onRequest(self, channel, method, props, body):
        """
        Waits for the client request and forwards it to its parent.
        :param chanel:
        :param method:
        :param props:
        :param body:
        :return:
        """
        self.last_request_time = time.time()
        self.channel = channel
        self.method = method
        self.props = props
        self.caller_back(body)
        self.channel.basic_ack(delivery_tag=method.delivery_tag)

    def setupServer(self, queueName, bindingKeys=None):
        '''
        Setups the basic config for RPC Server
        '''

        with self._getConnection() as self.connection:
            channel = self._setupChannel(self.connection.channel())
            channel.queue_declare(queue=queueName, durable=1)
            channel.basic_qos(prefetch_count=1)
            if bindingKeys is None:
                bindingKeys = [queueName]
            # Now binding the queue to the topic
            for bindingKey in bindingKeys:
                channel.queue_bind(exchange=self._topic_name,
                                   queue=queueName,
                                   routing_key=bindingKey)
            self.start_consume(channel, queueName)
