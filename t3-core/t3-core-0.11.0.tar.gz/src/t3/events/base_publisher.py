import logging
import pika

log = logging.getLogger(__name__)


class BasePublisher(object):
    """
    BasePublisher will run in a non-blocking way and close connection once the message has been sent.

    If RabbitMQ closes the connection, you should
    look at the output, as there are limited reasons why the connection may
    be closed, which usually are tied to permission related issues or
    socket timeouts.
    If the channel is closed, it will indicate a problem with one of the
    commands that were issued and that should surface in the output as well.
    """

    def __init__(self, amqp_url):
        """
        Create a new instance of the consumer class, passing in the AMQP URL used to connect to RabbitMQ.

        :param str amqp_url: The AMQP url to connect with
        """
        self._connection = None
        self._channel = None
        self._closing = False
        self._url = amqp_url

        self._exchange_name = ''
        self._exchange_type = 'direct'
        self._routing_key = ''
        self._message = ''

    def set_routing_key(self, routing_key):
        self._routing_key = routing_key

    def set_exchange(self, exchange_name, exchange_type='direct'):
        self._exchange_name = exchange_name
        self._exchange_type = exchange_type

    def set_message(self, message):
        self._message = message

    def connect(self):
        """
        Connect to RabbitMQ, returning the connection handle.

        When the connection is established, the on_connection_open method
        will be invoked by pika.
        :rtype: pika.SelectConnection
        """
        log.info('Connecting to %s', self._url)
        return pika.SelectConnection(pika.URLParameters(self._url),
                                     self.on_connection_open,
                                     self.on_connection_error,   # !! Handle error opening connection
                                     stop_ioloop_on_close=False)

    def on_connection_open(self, unused_connection):
        """
        Call by pika once the connection to RabbitMQ has been established.

        It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.
        :type unused_connection: pika.SelectConnection
        """
        log.info('Connection opened')
        self.add_on_connection_close_callback()
        self.open_channel()

    def on_connection_error(self, unused_connection, message):
        """
        Call by pika if the connection to RabbitMQ has failed to be established.

        It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.
        :type unused_connection: pika.SelectConnection
        """
        log.error('Connection failed: %s', message)

    def add_on_connection_close_callback(self):
        """Add an on close callback when RabbitMQ closes the connection to the publisher unexpectedly."""
        log.info('Adding connection close callback')
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        """
        Invoke by pika when the connection to RabbitMQ is closed unexpectedly.

        Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.
        :param pika.connection.Connection connection: The closed connection obj
        :param int reply_code: The server provided reply_code if given
        :param str reply_text: The server provided reply_text if given
        """
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            log.warning('Connection closed, reopening in 5 seconds: (%s) %s', reply_code, reply_text)

    def open_channel(self):
        """
        Open a new channel with RabbitMQ by issuing the Channel.Open RPC command.

        When RabbitMQ responds that the channel is open, the
        on_channel_open callback will be invoked by pika.
        """
        log.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """
        Invoke by pika when the channel has been opened.

        The channel object is passed in so we can make use of it.
        Since the channel is now open, we'll declare the exchange to use.
        :param pika.channel.Channel channel: The channel object
        """
        log.info('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self._exchange_name)

    def add_on_channel_close_callback(self):
        """Tell pika to call the on_channel_closed method if RabbitMQ unexpectedly closes the channel."""
        log.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        """
        Invoke by pika when RabbitMQ unexpectedly closes the channel.

        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.
        :param pika.channel.Channel: The closed channel
        :param int reply_code: The numeric reason the channel was closed
        :param str reply_text: The text reason the channel was closed
        """
        log.warning('Channel %i was closed: (%s) %s', channel, reply_code, reply_text)
        self._connection.close()

    def setup_exchange(self, exchange_name):
        """
        Start the exchange on RabbitMQ by invoking the Exchange.Declare RPC command.

        When it is complete, the on_exchange_declareok method will
        be invoked by pika.
        :param str|unicode exchange_name: The name of the exchange to declare
        """
        log.info('Declaring exchange %s', exchange_name)
        self._channel.exchange_declare(self.on_exchange_declareok,
                                       exchange_name,
                                       self._exchange_type)

    def on_exchange_declareok(self, unused_frame):
        """
        Invoke by pika when RabbitMQ has finished the Exchange.Declare RPC command.

        :param pika.Frame.Method unused_frame: Exchange.DeclareOk response frame
        """
        log.info('Exchange declared')
        self.start_publishing()

    def start_publishing(self):
        """Enable delivery confirmations and schedule the first message to be sent to RabbitMQ."""
        log.info(f'Sending message {self._message} to routing key {self._routing_key} '
                 f'on exchange {self._exchange_name}')
        self._connection.add_timeout(0.1, self._send_message)

    def _send_message(self):
        """Send message to the declared queue on the declared exchange."""
        self._channel.basic_publish(self._exchange_name, self._routing_key, self._message,
                                    pika.BasicProperties(content_type='text/plain', delivery_mode=1))
        log.info(f'Message {self._message} published, closing connection')
        self._connection.add_timeout(0.1, self.stop)

    def run(self):
        """Connect to RabbitMQ and then starting the IOLoop to block and allow the SelectConnection to operate."""
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
        """Close channels and connection, stop."""
        log.info('Sending a Basic.Cancel RPC command to RabbitMQ')
        self._closing = True
        log.info('Closing channel & connection')
        self._channel.close()
        self._connection.ioloop.stop()
        log.info('Stopped')
