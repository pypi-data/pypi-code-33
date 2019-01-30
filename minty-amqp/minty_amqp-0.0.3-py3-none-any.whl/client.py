import importlib
import threading
import time

from amqpstorm import AMQPConnectionError, AMQPError, UriConnection
from minty import Base
from minty.cqrs import CQRS

from .consumer import BaseConsumer


class AMQPClient(Base):
    """AMQPClient manages the connection to and consumers of RabbitMQ.

    The client holds one connection to the AMQP server, subsequently one channel
    (virtual connection) for each registered consumer is created.

    `amqpstorm` library manages heartbeats (keepalives) in the background.
    """

    def __init__(
        self, rabbitmq_url: str, max_retries: int = None, cqrs: CQRS = None
    ):
        """Initialize AMQPClient.

        :param rabbitmq_url: url to rabbitmq server.
        :type rabbitmq_url: str
        :param max_retries: max_retries to get connection, defaults to None
        :type max_retries: int, optional
        :param cqrs: CQRS layer injected in consumers, defaults to None
        :type cqrs: CQRS, optional
        """
        self.rabbitmq_url = rabbitmq_url
        self.max_retries = max_retries
        self.cqrs = cqrs

        self._threading_events = []
        self._connection = None
        self._active_consumers = []
        self._stopped = threading.Event()
        self._registered_consumers = []

    def start(self):
        """Create new connection to AMQP server, starts and recovers consumers.

        Loop runs continually until `stop` method is called. Each loop the
        connection and consumer(s) health are checked and will be recovered if
        any failures are detected.

        `self.threading_events` is checked after a consumer is started or re-started
        to allow time for initialization of the consumer.
        """
        self._stopped.clear()
        if not self._connection or self._connection.is_closed:
            self._create_connection()

        while not self._stopped.is_set():
            try:
                self._connection.check_for_errors()
                if self._connection.is_closed:
                    raise AMQPConnectionError("connection closed")
                self._update_consumers()
                for event in self._threading_events:
                    event.wait(timeout=1)
                self._check_consumers()
                self._cleanup_thread_events()
            except AMQPError as error:
                self.logger.warning(error)
                self._stop_consumers()
                self._create_connection()
            time.sleep(1)

    def stop(self):
        """Stop all consumers and close connection to AMQP server."""
        while self._active_consumers:
            consumer = self._active_consumers.pop()
            consumer.stop()
        self._stopped.set()
        self._connection.close()

    def _create_connection(self):
        """Create a connection to the AMQP server."""
        attempts = 0
        while not self._stopped.is_set():
            attempts += 1
            try:
                self._connection = UriConnection(self.rabbitmq_url)
                break
            except AMQPError as error:
                self.logger.warning(error)
                if self.max_retries and attempts > self.max_retries:
                    raise Exception("max number of retries reached")
                time.sleep(min(attempts * 2, 30))

    def _update_consumers(self):
        """Start consumers in `_registered_consumers` and append to `_active_consumers`."""
        for consumer in self._registered_consumers:
            if not any(consumer == c for c in self._active_consumers):
                self._start_consumer(consumer)
                self._active_consumers.append(consumer)

    def _check_consumers(self):
        """Check if all consumers are active and restart if needed."""
        for consumer in self._active_consumers:
            if not consumer.active:
                self._start_consumer(consumer)

    def _stop_consumers(self):
        """Call `stop` method on consumers in `_active_consumers`."""
        for consumer in self._active_consumers:
            consumer.stop()

    def _start_consumer(self, consumer: BaseConsumer):
        """Start a consumer in a new thread.

        `threading.Event` is set in `self.thread_events` to signal when
        consumer is done  with initialization.

        :param consumer: rabbitmq consumer.
        :type consumer: BaseConsumer
        """
        event = threading.Event()
        self._threading_events.append(event)

        thread = threading.Thread(
            target=consumer.start, args=(self._connection, event)
        )
        thread.daemon = True
        thread.start()

    def _cleanup_thread_events(self):
        """Iterate over `_threading_events` and discard set / True events."""
        for event in self._threading_events:
            self._threading_events = [
                event for event in self._threading_events if not event.is_set()
            ]

    def register_consumer_from_config(self, config: dict):
        """Register and Initialize consumer from given config dict.

        :param config: contains all params needed to register consumer
        :type config: dict
        """
        consumer = self._import_class_from_string(config["class"])
        for i in range(config["number_of_channels"]):
            initialized_consumer = consumer(
                queue=config["queue_name"],
                routing_key=config["routing_key"],
                exchange=config["exchange"],
                cqrs=self.cqrs,
            )
            self._registered_consumers.append(initialized_consumer)

    def _import_class_from_string(self, name: str):
        """Import class from string in config dict.

        'minty_amqp.client.AMQPClient' would import the `AMQPClient` class

        :param name: path to class
        :type name: str
        :return: Specified object
        :rtype: class
        """
        class_name = name.split(".")[-1]
        module_path = name.replace(f".{class_name}", "")
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
