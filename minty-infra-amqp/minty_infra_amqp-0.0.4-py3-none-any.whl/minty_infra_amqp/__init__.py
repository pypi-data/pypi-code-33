__version__ = "0.0.4"

from minty import Base
import amqpstorm
from amqpstorm import AMQPChannelError, AMQPConnectionError

import threading


class AMQPInfrastructure(Base):
    __slots__ = ["cache_lock", "connection", "channels"]

    def __init__(self):
        """Initialize the AMQP infrastructure"""
        self.cache_lock = threading.Lock()
        self.channels = {}
        self.connection = None

    def __call__(self, config: dict):
        """Create a new AMQP connection using the specified configuration

        :param config: Configuration to read amqp:// URL from
        :type config: dict
        :return: A handle for a channel on a connection to an AMQP server.
        :rtype: amqpstorm.Connection
        """

        rmq_url = config["amqp"]["url"]

        with self.cache_lock:
            try:
                channel = self.channels[rmq_url]
                channel.check_for_errors()
            except KeyError:
                channel = self._create_connection_and_channel(rmq_url)
            except AMQPConnectionError:
                channel = self._create_connection_and_channel(rmq_url)
            except AMQPChannelError:
                channel = self.connection.channel()
                self.channels[rmq_url] = channel

        return channel

    def _create_connection_and_channel(
        self, rmq_url: str
    ) -> amqpstorm.Channel:
        """Create connection and channel.

        :param rmq_url:  amqp:// URL
        :type rmq_url: str
        :return: channel
        :rtype: amqpstorm.Channel
        """
        self.connection = amqpstorm.UriConnection(rmq_url)
        self.channels[rmq_url] = self.connection.channel()
        return self.channels[rmq_url]
