import abc
import threading
import time

from amqpstorm import AMQPError, Connection, Message
from minty import Base
from minty.cqrs import CQRS


class BaseConsumer(abc.ABC, Base):
    def __init__(
        self,
        queue: str,
        routing_key: str,
        exchange: str,
        cqrs: CQRS,
        qos_prefetch_count: int = 1,
    ):
        self.cqrs = cqrs
        self.queue = queue
        self.exchange = exchange
        self.routing_key = routing_key
        self.channel = None
        self.active = False
        self.qos_prefetch_count = qos_prefetch_count

    def start(self, connection: Connection, ready: threading.Event):
        """Initialize channel, declare queue and start consuming.

        This method should not be overloaded in subclassed consumers.

        :param connection: Connection to rabbitmq
        :type connection: Connection
        :param ready: signals if initialization is done
        :type ready: threading.Event
        """
        self.channel = None
        try:
            self.channel = connection.channel(rpc_timeout=10)
            self.active = True
            self.channel.basic.qos(self.qos_prefetch_count)
            self.channel.queue.declare(queue=self.queue, durable=True)
            self.channel.queue.bind(
                queue=self.queue,
                exchange=self.exchange,
                routing_key=self.routing_key,
            )
            self.channel.basic.consume(self, self.queue, no_ack=False)

            ready.set()

            # start_consuming() blocks indefinitely or until channel is closed.
            self.channel.start_consuming()

            self.channel.close()
        except AMQPError as err:
            self.logger.warning(err)
            time.sleep(1)
        finally:
            self.active = False

    def stop(self):
        """Stop consumer and close channel."""
        if self.channel:
            self.channel.close()

    @abc.abstractmethod
    def __call__(self, message: Message):
        """Process received message in sublassed consumer.

        Subclassed consumers should implement the message processing logic when
        overloading this method. This should result in a call to
        `message.ack()` on success and a call to `message.nack()` on failure.

        :param message: received amqp message
        :type message: Message
        """
        print(f"received message: {message.body}")
        message.ack()
