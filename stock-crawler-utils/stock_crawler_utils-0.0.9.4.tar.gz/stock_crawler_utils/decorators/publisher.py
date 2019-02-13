import pika
import pickle
import logging
from functools import wraps
from stock_crawler_utils.tasks import delay_task_queue


class Publisher:
    def __init__(self, publisher_func, publisher_args=None, publisher_kwargs=None, rabbit_cfg=None, ttl_timeout=0):
        if rabbit_cfg is None:
            rabbit_cfg = {}
        self.__rabbit_host = rabbit_cfg.get('host', 'localhost')
        self.__rabbit_username = rabbit_cfg.get('username', 'guest')
        self.__rabbit_password = rabbit_cfg.get('password', 'guest')
        self.__rabbit_publish_queue = rabbit_cfg.get('publish_queue')
        self.__rabbit_dead_queue = 'dead_queue'
        self.__publisher_func = publisher_func
        self.__publisher_args = publisher_args or tuple()
        self.__publisher_kwargs = publisher_kwargs or {}
        self.__ttl_timeout = ttl_timeout

    def __push(self, ch, queue, channel_data):
        logging.debug("Pushing message to Rabbit")
        ch.queue_declare(queue=queue, durable=True)

        if self.__ttl_timeout > 0:
            delay_task_queue(ttl_delay=self.__ttl_timeout, queue=queue, channel=ch, task=channel_data)
        else:
            ch.basic_publish(
                exchange='', routing_key=queue, body=pickle.dumps(channel_data),
                properties=pika.BasicProperties(delivery_mode=2)
            )

    def publish(self):
        data = self.__publisher_func(*self.__publisher_args, **self.__publisher_kwargs)
        if data is None:
            return
        logging.debug("Got data to publish")

        connection = None
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.__rabbit_host,
                    credentials=pika.PlainCredentials(self.__rabbit_username, self.__rabbit_password)
                )
            )
            channel = connection.channel()
            logging.debug("Connected to Rabbit server")
            self.__push(channel, self.__rabbit_publish_queue, data)
            return

        finally:
            if connection and connection.is_open:
                connection.close()


def publish(rabbit_cfg, ttl_timeout=0):
    def decorator(func):
        @wraps(func)
        def publish_wrap(*args, **kwargs):
            publisher = Publisher(publisher_func=func, publisher_args=args, publisher_kwargs=kwargs,
                                  rabbit_cfg=rabbit_cfg, ttl_timeout=ttl_timeout)
            publisher.publish()

        return publish_wrap

    return decorator
