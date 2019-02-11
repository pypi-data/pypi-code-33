# coding: utf-8
import inspect
import re

from logging import Logger
from dophon_mq.properties import properties
from dophon_mq.function_unit import Producer, Consumer

producer = Producer.producer

consumer = Consumer.consumer

try:
    logger = __import__('dophon.logger', fromlist=['dophon'])
    logger.inject_logger(globals())
except Exception as e:
    logger = Logger(__name__)

__all__ = [
    'producer', 'consumer', 'ConsumerCenter'
]


def log_center_init(f):
    def method(*args, **kwargs):
        logger.info(f'初始化({getattr(f,"__qualname__")})')
        f(*args, **kwargs)

    return method


class ConsumerCenter:
    """
    消息消费者封装(带自动运行)
    """

    @log_center_init
    def __init__(self):
        """
        注意!!!!
        重写该类的init方法必须显式执行该类的init方法,否则定义的消息消费将失效
        """
        self.before_init()
        for name in dir(self):
            item = getattr(self, name)
            if not re.match('__.+__', name) and \
                    callable(item) and \
                    re.match('consumer.<locals>.method.<locals>.*', getattr(getattr(item, '__func__'), '__qualname__')):
                fields = inspect.getfullargspec(item).args
                # 清除自对象参数
                self.before_exec_consumer()
                staticmethod(item(*fields))
                self.after_exec_consumer()
        self.after_init()

    def before_init(self):
        pass

    def after_init(self):
        pass

    def before_exec_consumer(self):
        pass

    def after_exec_consumer(self):
        pass
