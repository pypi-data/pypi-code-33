import time
import logging
import logging.handlers
import logging.config

from tornado.options import options, define

from .request_id import get

LOGGER_NAME = 'tort'
tort_log = logging.getLogger(LOGGER_NAME)


define('tort_logformat', default='%(asctime)s %(levelname)s %(name)s:%(lineno)d %(request_id)s | %(message)s')


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        try:
            record.request_id = get()
        except LookupError:
            record.request_id = None

        return True


def configure_logging(log_file=None, log_level=logging.DEBUG, additional_loggers=None):
    additional_loggers = additional_loggers or []

    log_handler = None

    if log_file:
        log_handler = logging.handlers.WatchedFileHandler(log_file)
        log_handler.setFormatter(logging.Formatter(options.tort_logformat))
        log_handler.setLevel(log_level)

    for log_name in [LOGGER_NAME, 'tornado.access', 'tornado.application', 'tornado.general'] + additional_loggers:
        logger = logging.getLogger(log_name)
        logger.addFilter(RequestIdFilter())
        logger.setLevel(log_level)
        for handler in logger.handlers:
            handler.setFormatter(logging.Formatter(options.tort_logformat))

        if log_handler:
            logger.addHandler(log_handler)


class PageLogger(logging.LoggerAdapter):
    class StageInfo(object):
        def __init__(self, start):
            self.start = start
            self.end = None
            self.counter = 1

        def __str__(self):
            if self.end:
                return '{0:.2f}'.format(1000 * (self.end - self.start))
            else:
                return 'infinite'

    def __init__(self, request, request_id, handler_name):
        self.request = request
        logging.LoggerAdapter.__init__(self, tort_log, {'request_id': str(request_id), 'event_queue': None})
        self.started = time.time()
        self.request_id = request_id
        self.handler_name = handler_name
        self._completed = False
        self.debug(f'Started {request.method} {request.uri}')

    def process(self, msg, kwargs):
        if 'extra' not in kwargs:
            kwargs['extra'] = self.extra
        else:
            kwargs['extra'].update(self.extra)
        return msg, kwargs

    def request_started(self, request):
        name = 'Retrying' if request.is_retry else 'Requesting'
        self.debug(f'{name} {request.request.method} {request.request.url}')

    def request_complete(self, resp):
        level = logging.DEBUG
        if 400 <= resp.code < 500:
            level = logging.INFO
        elif resp.code >= 500:
            level = logging.WARNING

        log = f'Complete {resp.code} {resp.request.method} {resp.request.url} in {int(resp.request_time * 1000.0)}ms'
        self.log(level, log)

    def complete_logging(self, status_code, additional_data=None):
        if self._completed:
            return

        if additional_data is None:
            additional_data = []

        data = [
                   ('handler', self.handler_name),
                   ('method', self.request.method),
                   ('code', status_code),
                   ('total', int(1000 * self.request.request_time()))
               ] + additional_data

        self.info('TORT {}'.format(' '.join('{}={}'.format(k, v) for (k, v) in data)))

        self._completed = True
