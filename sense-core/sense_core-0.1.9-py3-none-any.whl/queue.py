from .queue0 import *
from .log import log_exception, log_info
from .utils import sleep

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
            self.close()
        except Exception as ex:
            log_exception(str(ex))


class RabbitConsumer(RabbitConsumer0):

    def execute_safely(self, caller, prefetch_count=2):
        while True:
            try:
                self.execute(caller, prefetch_count)
            except ConnectionResetError as ex:
                log_info("rabbit connection reset")
                sleep(2)
            except Exception as ex:
                log_exception(ex)
                raise ex
