import pika
from .config import config


class BaseRabbit(object):

    def __init__(self, label='rabbit'):
        self._host = config(label, 'host')
        self._port = int(config(label, 'port'))
        self._user = config(label, 'user')
        password = config(label, 'password', '')
        if password == '':
            password = config(label, 'pass', '')
        self._password = password
        self._connection = None
        self._channel = None
        self._caller = None
        self.init_connection()

    def init_connection(self):
        credentials = pika.PlainCredentials(self._user, self._password)
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(self._host, self._port, '/', credentials))
        self._channel = self._connection.channel()


class RabbitProducer0(BaseRabbit):

    def __init__(self, label='rabbit'):
        super(RabbitProducer0, self).__init__(label)

    def send(self, topic, message):
        if self._connection is None:
            self.init_connection()
        self._channel.queue_declare(queue=topic, durable=True)
        self._channel.basic_publish(exchange='',
                                    routing_key=topic,
                                    body=message,
                                    properties=pika.BasicProperties(
                                        delivery_mode=2,  # 使得消息持久化
                                    ))
        self._connection.close()
        self._connection = None

    def close(self):
        if self._connection is not None:
            self._connection.close()
            self._connection = None


class RabbitConsumer(BaseRabbit):

    def __init__(self, topic, label='rabbit'):
        self._topic = topic
        super(RabbitConsumer, self).__init__(label)

    def callback(self, ch, method, properties, body):
        self._caller(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def execute(self, caller, prefetch_count=2):
        self._caller = caller
        channel = self._connection.channel()
        channel.basic_qos(prefetch_count=prefetch_count)
        channel.basic_consume(self.callback,
                              queue=self._topic,
                              no_ack=False)
        channel.start_consuming()
