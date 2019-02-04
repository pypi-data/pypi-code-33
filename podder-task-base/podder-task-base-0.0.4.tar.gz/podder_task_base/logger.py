import logging
import time


class Logger(object):
    def __init__(self):
        self.start_time = time.time()
        logging.basicConfig(
            format='%(levelname)s:%(message)s', level=logging.DEBUG)

    def warning(self, msg, *args, **kwargs):
        logging.warning(self.add_time(msg), *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        logging.warning(self.add_time(msg), *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        logging.info(self.add_time(msg), *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        logging.debug(self.add_time(msg), *args, **kwargs)

    def log(self, msg, *args, **kwargs):
        logging.log(self.add_time(msg), *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        logging.error(self.add_time(msg), *args, **kwargs)

    def add_time(self, msg):
        time_spent = round((time.time() - self.start_time), 3)
        msg_with_time = "[{}] {}".format(time_spent, msg)
        return msg_with_time
