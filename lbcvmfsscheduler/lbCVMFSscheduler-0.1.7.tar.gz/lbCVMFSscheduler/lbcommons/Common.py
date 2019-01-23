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

:author: Ben Couturier
'''

import os
import pika
from Messages import RbMessage


class Messenger(object):
    '''
    Class used to send messages to the build system message broker
    '''
    def __init__(self, host=None,
                 user=None, passwd=None,
                 port=5671, vhost='/lhcb'):
        '''
        Initialize the messaging class
        '''
        # Setup the credential variables
        if host is None:
            host = "lbmessagingbroker.cern.ch"
        self._host = host
        if user is None or passwd is None:
            (username, passwd) = self._getPwdFromSys()
            if user is None:
                user = username
        self._credentials = pika.PlainCredentials(user, passwd)
        # And the connection params
        self._port = port
        self._vhost = vhost

    def _getConnection(self, socket_timeout=None):
        '''
        Creates connection to rabbitMQ ond ended
        '''
        heart_beat = 60*60*18
        params = pika.ConnectionParameters(self._host,
                                           ssl=True,
                                           port=self._port,
                                           virtual_host=self._vhost,
                                           heartbeat_interval=heart_beat,
                                           credentials=self._credentials)
        if socket_timeout:
            params.socket_timeout = socket_timeout
        return pika.BlockingConnection(params)

    def _getPwdFromSys(self):
        '''
        Get the RabbitMQ password from the environment of from a file on disk
        '''
        # First checking the environment
        res = os.environ.get("RMQPWD", None)
        # Checking for the password in $HOME/private/rabbitmq.txt
        if res is None:
            fname = os.path.join(os.environ["HOME"], "private", "rabbitmq.txt")
            if os.path.exists(fname):
                with open(fname, "r") as f:
                    data = f.readlines()
                    if len(data) > 0:
                        res = data[0].strip()
        # Separate the username/password
        (username, password) = res.split("/")
        return (username, password)

    def _setupChannel(self, channel):
        channel.exchange_declare(exchange=self._topic_name,
                                 durable=True,
                                 exchange_type='direct')
        return channel

    def _exitCodeFound(self, body):
        """
        Looks for the exit message in the payload
        :param body: the payload
        :return: Tru if exit is required
        """
        if body is None:
            return False
        message = RbMessage()
        try:
            message.updateFromJson(body)
            tmp = message.getPayload()
            if tmp.get('exit', None):
                return True
        except Exception as e:
            print(e)
            return False
        return False
