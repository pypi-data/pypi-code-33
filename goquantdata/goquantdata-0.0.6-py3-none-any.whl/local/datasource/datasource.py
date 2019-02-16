import logging
import goquantdata.util.util as util


class DataSource(object):
    def __init__(self, name=__name__, logging_level=logging.INFO):
        self.logger = util.get_logger(name=name, level=logging_level)
        self.connect()

    def connect(self):
        raise NotImplemented()

    def get_daily(self, start_date, end_date, ids, market):
        raise NotImplemented()


