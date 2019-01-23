###############################################################################
# (c) Copyright 2017 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Module grouping the common build functions.
'''

import datetime
import json
import logging
import os
import pika

from collections import namedtuple
__author__ = 'Ben Couturier <ben.couturier@cern.ch>'


# Utility class to ease the use of the messages
Message = namedtuple('Message', ['body', 'method_frame', 'header_frame'],
                     rename=True)


# Our own exception to signal that the processing was interrupted and
# we shouldn't ack the message
class InterruptedProcessing(Exception):
    pass


# Various utilities for connection management
def _get_pwd_from_sys():
    """
    Get the RabbitMQ password from the environment of from a file on disk
    """
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
    return username, password


def get_connection(host=None,
                   username=None, passwd=None,
                   port=5671, vhost='/lhcb', use_ssl=True):
    """
    Create a connection to RabbitMQ
    """

    envhost = os.environ.get("RMQHOST", None)
    if envhost:
        host = envhost
    if host is None:
        host = "lbmessagingbroker.cern.ch"

    envvhost = os.environ.get("RMQVHOST", None)
    if envvhost:
        vhost = envvhost

    if os.environ.get("RMQNOSSL", None):
        use_ssl = False

    if os.environ.get("RMQPORT", None):
        port = int(os.environ.get("RMQPORT"))

    if username is None or passwd is None:
        (username, passwd) = _get_pwd_from_sys()
    credentials = pika.PlainCredentials(username, passwd)
    cpar = " ".join([str(x) for x in [ host, use_ssl, port, vhost]])
    logging.debug("Connection paremeters: %s" % cpar)
    params = pika.ConnectionParameters(host,
                                       ssl=use_ssl,
                                       port=port,
                                       virtual_host=vhost,
                                       credentials=credentials)
    return pika.BlockingConnection(params)


def check_channel(channel, connection=None):
    """
    Ugly hack to keep backwards compatibility
    We should receive a pika.Channel, but if we are given a pika.BlockingConnection,
    We just create a new channel from it....
    """
    checked_channel = None
    if connection is not None:
        checked_channel = connection.channel()
    else:
        if isinstance(channel, pika.BlockingConnection):
            checked_channel = channel.channel()
        else:
            checked_channel = channel
    return checked_channel


class QueueHelper(object):
    """
    Utility class to access the rabbitmq broker
    """

    def __init__(self, channel=None, connection=None):
        """
        Initialize the messenger class
        """
        self._channel = check_channel(channel, connection)

    def _setup_exchange(self, channel, exchange_name):
        """
        Creates an exchange with the desired echange_type
        """
        channel.exchange_declare(exchange=exchange_name,
                                 exchange_type='topic',
                                 durable=True)

    def basic_publish(self, exchange_name, routing_key, body, priority=1,
                      max_retry=3, headers=None):
        """
        Send a message to the topic defined for the builds
        """
        channel = self._channel
        self._setup_exchange(channel, exchange_name)
        now = datetime.datetime.utcnow().isoformat()
        ipd = now
        if headers and headers.get('initial_publish_date'):
            ipd = headers.get('initial_publish_date')
        props = pika.BasicProperties(delivery_mode=2, priority=priority,
                                     headers={'max_retry': max_retry,
                                              'initial_publish_date': ipd,
                                              # make message persistent
                                              'publish_date': now})
        channel.basic_publish(exchange=exchange_name,
                              routing_key=routing_key,
                              body=body,
                              properties=props)

    def bind_queue_to_exchange(self, queue_name, exchange_name,
                               binding_keys=None):
        """
        Binds the queue to an exchange, make sure the queue is persistent
        """

        self._setup_queue(self._channel, exchange_name,
                          queue_name, binding_keys)

    def _setup_queue(self, channel, exchange_name, queue_name=None,
                     binding_keys=None):
        """
        Setup a queue and binds
        """
        self._setup_exchange(channel, exchange_name)
        if queue_name is None:
            # Anonymous queue is NOT persistent
            logging.info("Declaring anonymous queue: %s" % queue_name)
            result = channel.queue_declare(exclusive=True,
                                           arguments={"x-max-priority": 255})
            queue_name = result.method.queue
        else:
            # Named queues are persistent...
            logging.info("Declaring durable queue: %s" % queue_name)
            result = channel.queue_declare(durable=1, queue=queue_name,
                                           arguments={"x-max-priority": 255})

        # defaults to the wildcard for topic channels
        if binding_keys is None:
            binding_keys = ["#"]

        # Now binding the queue to the topic
        for binding_key in binding_keys:
            logging.info("Binding %s to %s for '%s'" % (queue_name,
                                                        exchange_name,
                                                        binding_key))
            channel.queue_bind(exchange=exchange_name,
                               queue=queue_name,
                               routing_key=binding_key)
        return queue_name


class Sender(QueueHelper):
    """
    Class used by cvmfs-lhcbdev.cern.ch to communicate with the outside world
    """

    def __init__(self, exchange, *args, **kwargs):
        """
        Initialize props
        """
        super(Sender, self).__init__(*args, **kwargs)
        self._exchange_name = exchange

    def send_message(self, routing_key, payload, priority=1, max_retry=3):
        """
        Sends a message to the exchange
        """
        body = json.dumps(payload)
        self.basic_publish(self._exchange_name, routing_key, body,
                           priority=priority, max_retry=max_retry)
        logging.info("Publish done to %s" % (self._exchange_name))

    def resend_message(self, message, keep_retry_count=False):
        """
        Resend a message based on a received header frame payload
        """
        exchange_name = message.method_frame.exchange
        routing_key = message.method_frame.routing_key

        bodyjson = json.dumps(message.body)
        new_max_retry = message.header_frame.headers.get('max_retry', 0)
        if not keep_retry_count and 'max_retry' in message.header_frame.\
                headers.keys():
            new_max_retry = message.header_frame.headers['max_retry'] - 1

        self.basic_publish(exchange_name, routing_key, bodyjson,
                           priority=message.header_frame.priority,
                           max_retry=new_max_retry,
                           headers=message.header_frame.headers)
        logging.info("resend done to %s" % (exchange_name))


class Receiver(QueueHelper):
    """
    Initializes a queue to receive messages
    """

    def __init__(self, exchange, queue, binding_keys=None, *args, **kwargs):
        """
        Initialize props
        """
        super(Receiver, self).__init__(*args, **kwargs)
        self._exchange_name = exchange
        self._queue_name = queue
        self.bind_queue_to_exchange(queue, exchange, binding_keys)

    def receive_messages(self):
        """
        Receive all messages in the queue and returns the list
        """
        message_list = []
        while True:
            message = self.receive_message()
            if message is None:
                break
            message_list.append(message)
        return message_list

    def receive_message(self, runBeforeAck=None):
        """
        Receive a message from the queue
        :param runBeforeAck: A method to be invoked before sending the ACK back
                             to the message broker
        :return: the message itself
        """
        message = None
        channel = self._channel
        method_frame, header_frame, body = channel.basic_get(
            queue=self._queue_name)
        if method_frame is not None:
            try:
                t = json.loads(body.decode('UTF-8'))
            except:
                t = body
            message = Message(t, method_frame, header_frame)
            if runBeforeAck:
                runBeforeAck(message)
            channel.basic_ack(method_frame.delivery_tag)
        return message


    def consume_message(self, processor):
        """
        Receive a message from the queue
        :param processor: A method to be invoked for each message, it receives a message and the channel in parameter
        and should return True to acknowledge the message/ False  to avoid doing so.
        """
        channel = self._channel
        def wrapper(channel, method_frame, header_frame, body):
            t = json.loads(body.decode('UTF-8'))
            message = Message(t, method_frame, header_frame)
            try:
                rc = processor(message)
                if rc:
                    channel.basic_ack(method_frame.delivery_tag)
            except StopIteration as e:
                # This is the normal exit method, we should consume the last message so that it does not stay
                # the queue
                channel.basic_ack(method_frame.delivery_tag)
                channel.stop_consuming()

        channel.basic_consume(wrapper, queue=self._queue_name)
        try:
            channel.start_consuming()
        except InterruptedProcessing:
            channel.stop_consuming()
        except Exception as e:
            channel.stop_consuming()
            raise e
