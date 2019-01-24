from .queue0 import *
from .log import log_exception


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
