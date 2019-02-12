import pika
import pickle
import psycopg2
import logging
# import redis
from stock_crawler_utils.tasks import delay_task_queue
from stock_crawler_utils.exceptions import ConsumerNotReadyException
from functools import wraps


class Consumer:

    def __init__(self, consumer_func, consumer_args=None, consumer_kwargs=None, rabbit_cfg=None, ttl_delay=None):
        if rabbit_cfg is None:
            rabbit_cfg = {}
        self.__rabbit_host = rabbit_cfg.get('host', 'localhost')
        self.__rabbit_username = rabbit_cfg.get('username', 'guest')
        self.__rabbit_password = rabbit_cfg.get('password', 'guest')
        self.__rabbit_consume_queue = rabbit_cfg.get('consume_queue')
        self.__rabbit_dead_queue = 'dead_queue'
        self.__consumer_func = consumer_func
        self.__consumer_args = consumer_args or tuple()
        self.__consumer_kwargs = consumer_kwargs or {}
        self.__ttl_delay = ttl_delay or 300

        if self.__rabbit_consume_queue is None:
            raise AttributeError("RabbbitMQ consume queue is not specified")

    def consume(self):
        creds = pika.PlainCredentials(username=self.__rabbit_username, password=self.__rabbit_password)
        params = pika.ConnectionParameters(host=self.__rabbit_host, credentials=creds, heartbeat_interval=0)
        connection = pika.BlockingConnection(parameters=params)
        logging.debug("Connected to Rabbit server")
        channel = connection.channel()
        channel.queue_declare(self.__rabbit_consume_queue, durable=True)
        msg = channel.consume(self.__rabbit_consume_queue, inactivity_timeout=1)
        if msg is not None:
            logging.debug("Got a message from Rabbit")
            self.__consumer_callback(self.__rabbit_consume_queue, channel, *msg)

    def __consumer_callback(self, queue, channel, method, properties, body):
        task = None
        try:
            task = pickle.load(body)
            self.__consumer_func(task, *self.__consumer_args, **self.__consumer_kwargs)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except (psycopg2.OperationalError,
                # redis.exceptions.ConnectionError,
                ConsumerNotReadyException) as e:
            channel.basic_ack(delivery_tag=method.delivery_tag)
            delay_task_queue(self.__ttl_delay, self.__rabbit_consume_queue, channel, task)
        except Exception as e:
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            self.publish_dead(queue, channel, task, e)

    def publish_dead(self, queue, channel, task, e):
        logging.warning("Pushing to dead queue")
        channel.queue_declare(queue=self.__rabbit_dead_queue, durable=True)
        task['parent_queue'] = queue
        task['exception'] = e
        channel.basic_publish(exchange='', routing_key=self.__rabbit_dead_queue, body=pickle.dumps(task),
                              properties=pika.BasicProperties(delivery_mode=2))


def consume(rabbit_cfg, ttl_delay_task=None):

    def decorate(func):
        @wraps(func)
        def start_consuming(*args, **kwargs):
            consumer = Consumer(rabbit_cfg=rabbit_cfg, consumer_func=func, consumer_args=args,
                                consumer_kwargs=kwargs, ttl_delay=ttl_delay_task)
            consumer.consume()

        return start_consuming
    return decorate
