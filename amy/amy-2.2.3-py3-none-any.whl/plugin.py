from threading import Thread
import pika
import json

from .env import *


class MetaPlugin(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        name = kwargs.get('name', args[0] if len(args) else None)
        if not name:
            ret = super().__call__(*args, **kwargs)
            ret.name = name
            return ret
        if name not in cls._instances:
            cls._instances[name] = super().__call__(*args, **kwargs)
            cls._instances[name].name = name
        return cls._instances[name]

    def remove(cls, name):
        del cls._instances[name]


class Plugin(metaclass=MetaPlugin):
    queueParams = pika.ConnectionParameters(host=AMY_Q_HOST)

    @classmethod
    def __connect(cls):
        cls.__connection = pika.BlockingConnection(cls.queueParams)
        cls._channel_messages = cls.__connection.channel()
        cls._channel_messages.queue_declare(queue='messages')
        cls._channel_user = cls.__connection.channel()
        cls._channel_user.queue_declare(queue='users')
        cls._channel_user.basic_consume(
            cls._onNewUser, queue='users', no_ack=True)

    @classmethod
    def platformName(cls):
        return cls.__class__.__name__

    def __repr__(self):
        return f'<{self.platformName()} {getattr(self, "username", "Anonymous")}>'

    @classmethod
    def _onNewUser(cls, ch, method, properties, body):
        # cls.platformName().upper() == properties.headers['platform'].upper()
        if hasattr(cls, 'onNewUser'):
            cls.onNewUser(json.loads(body))
        else:
            print(body)

    @classmethod
    def startUserListener(cls):
        if not hasattr(cls, '__connection'):
            cls.__connect()
        cls._thread_user = Thread(
            target=cls._channel_user.start_consuming)
        cls._thread_user.start()

    @classmethod
    def stopUserListener(cls):
        if hasattr(cls, '_thread_user'):
            cls._channel_user.stop_consuming()
            cls._thread_user.join()

    @classmethod
    def publischMessage(cls, message):
        if not hasattr(cls, '__connection'):
            cls.__connect()
        if type(message) is dict:
            message = json.dumps(message)
        cls._channel_messages.basic_publish(exchange='',
                                            routing_key='messages',
                                            body=message)

    def runThread(self, cb):
        self._thread = Thread(target=cb)
        self._thread.start()
        return self._thread

    def stopThread(self):
        if hasattr(self, '_thread'):
            self._thread.join()
