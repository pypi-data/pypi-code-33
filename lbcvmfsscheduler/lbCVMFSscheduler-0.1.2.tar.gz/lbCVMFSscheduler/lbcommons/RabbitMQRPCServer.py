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
    def __init__(self, caller_back, *args, **kwargs):
        '''
        Initialize props
        '''
        super(RPCServer, self).__init__(*args, **kwargs)
        self.caller_back = caller_back
        self._topic_name = "topic.cvmfs_scheduler"
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

    def publish(self, body):
        '''
        Send a message to the client
        '''
        if not self.useBackup:
            if self.method is None or self.channel is None:
                self.backLog.append(body)
                return
            if len(self.backLog) > 0:
                b = self.backLog.pop(0)
                self.publish(b)
                time.sleep(0.1)
        try:
            cor_id = self.props.correlation_id
            self.channel.basic_publish(exchange=self._topic_name,
                                       routing_key=self.props.reply_to,
                                       properties=pika.BasicProperties(
                                           correlation_id=cor_id,
                                           delivery_mode=2),
                                       body=body)
        except:
            # Declare backup connection to persist logs from server
            with self._getConnection() as connection:
                self.backupChannel = connection.channel()
                self.backupChannel.queue_declare(queue="persisted_logs",
                                                 durable=1)
                prop = pika.BasicProperties(delivery_mode=2)
                self.backupChannel.basic_publish(exchange='',
                                                 routing_key='persisted_logs',
                                                 properties=prop,
                                                 body=body)
        # if self._exitCodeFound(body):
            #self.channel.basic_ack(delivery_tag=self.method.delivery_tag)

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
                queue=queueName, no_ack=True)
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
