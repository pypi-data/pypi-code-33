from .queue0 import *
from .log import log_exception, log_info
from .utils import sleep
from pika.exceptions import *


class RabbitProducer(RabbitProducer0):

    def send_safely(self, topic, message):
        try:
            self.send(topic, message)
            return True
        except Exception as ex:
            log_exception(str(ex))
            self.close_safely()
            return False

    def close_safely(self):
        try:
            self.close_connection()
        except Exception as ex:
            log_exception(str(ex))


class RabbitConsumer(RabbitConsumer0):

    def _close_safely(self):
        try:
            self.close_connection()
        except Exception as ex:
            log_exception(str(ex))

    def execute_safely(self, caller, prefetch_count=2):
        while True:
            try:
                self.execute(caller, prefetch_count)
            except ConnectionClosed as ex:
                log_info("rabbit ConnectionClosed reset")
                self._close_safely()
                sleep(2)
            except ChannelClosed as ex:
                log_info("rabbit ChannelClosed reset")
                self._close_safely()
                sleep(2)
            except Exception as ex:
                log_exception(ex)
                self._close_safely()
                raise ex
