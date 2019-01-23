from __future__ import absolute_import

import logging


class _Logger(object):
    def __init__(self):
        self.log = logging.getLogger(__name__)

    def get_logger(self, **kwargs):
        return logging.LoggerAdapter(self.log, kwargs)


Logger = _Logger()
