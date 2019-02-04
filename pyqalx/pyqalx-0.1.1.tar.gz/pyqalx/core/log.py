import json
import logging
import multiprocessing
import sys
import threading
import traceback
import os
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler


# The default values to use in configs for logging.
# Override the `get_context` method to change this on a per config
# basis
LOGGING_DEFAULTS = {
    'LEVEL': logging._levelToName[logging.ERROR],
    'CONFIG_PATH': None,
    'LOG_FILE_PATH': os.path.join(os.path.expanduser("~"), '.qalx.log')
}


class MultiProcessingLogHandler(logging.Handler):
    # https://gist.github.com/JesseBuesking/10674086
    def __init__(self, filename, mode, maxBytes, backupCount):
        logging.Handler.__init__(self)

        self._handler = RotatingFileHandler(filename, mode,
                                            maxBytes, backupCount)
        self.queue = multiprocessing.Queue(-1)

        t = threading.Thread(target=self.receive)
        t.daemon = True
        t.start()

    def setFormatter(self, fmt):
        logging.Handler.setFormatter(self, fmt)
        self._handler.setFormatter(fmt)

    def receive(self):
        while True:
            try:
                record = self.queue.get()
                self._handler.emit(record)
            except (KeyboardInterrupt, SystemExit):
                raise
            except EOFError:
                break
            except:
                traceback.print_exc(file=sys.stderr)

    def send(self, s):
        self.queue.put_nowait(s)

    def _format_record(self, record):
        # ensure that exc_info and args have been stringified. Removes any
        # chance of unpickleable things inside and possibly reduces message
        # size sent over the pipe
        if record.args:
            record.msg = record.msg % record.args
            record.args = None
        if record.exc_info:
            dummy = self.format(record)
            record.exc_info = None

        return record

    def emit(self, record):
        try:
            s = self._format_record(record)
            self.send(s)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def close(self):
        self._handler.close()
        logging.Handler.close(self)


def build_default_config(LEVEL, DEFAULT_HANDLER, DEFAULT_MP_HANDLER, LOG_FILE_PATH):
    """
    Builds the default config for pyqalx.

    :param LEVEL: The level from the `LOGGING_LEVEL` variable in the
                  users config
    :param DEFAULT_HANDLER: The default log handler we should use.  If a user
        specifies `LOGGING_CONFIG` in their config then this will be
        `nullhandler` (because we assume they know what they are doing and want
        to override various bits of the config). Otherwise it is `filehandler`
        and will log based on the level specified in LEVEL
    :param DEFAULT_MP_HANDLER: The default multiprocessing log handler we
        should use.  If a user specifies `LOGGING_CONFIG` in
        their config then this will be `nullhandler` (because we assume
        they know what they are doing and want to override various bits of
        the config). Otherwise it is `filehandler` and will log based on the
        level specified in LEVEL
    :param LOG_FILE_PATH: The path to the log file to be used when using
        `filehandler` or `mp_filehandler`
    :return: dict: The default config for pyqalx to use.
    """
    DEFAULT_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s %(name)-12s %(levelname)-8s '
                          '%(process)d %(message)s',
                },
        },
        'handlers': {
            'nullhandler': {
                'class': 'logging.NullHandler',
                'level': LEVEL,
            },
            'filehandler': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': LOG_FILE_PATH,
                # 10 MB
                'maxBytes': 10*1024*1024,
                'backupCount': 10,
                'mode': 'w',
                'formatter': 'default',
                'level': LEVEL
            },
            'mp_filehandler': {
                'class': 'pyqalx.core.log.MultiProcessingLogHandler',
                'filename': LOG_FILE_PATH,
                # 10 MB
                'maxBytes': 10*1024*1024,
                'backupCount': 10,
                'mode': 'w',
                'formatter': 'default',
                'level': LEVEL
            }
        },
        'loggers': {
            'pyqalx.core': {
                'handlers': [DEFAULT_HANDLER],
                'level': LEVEL
            },
            'pyqalx.bot': {
                'handlers': [DEFAULT_HANDLER, DEFAULT_MP_HANDLER],
                'level': LEVEL
            },
            'pyqalx.config': {
                'handlers': [DEFAULT_HANDLER],
                'level': LEVEL
            },
            'pyqalx.transport': {
                'handlers': [DEFAULT_HANDLER],
                'level': LEVEL
            },
        },
    }
    return DEFAULT_CONFIG


def configure_logging(config):
    """
    Given a `Config` instance will attempt to get the configurable logging
    values from the profile - falling back to sensible defaults.
    It then configures the logger with our defaults and then overrides as
    necessary depending on if the user has specified a custom logging config
    :param config: An instance of `Config`
    """
    logging_config_func = dictConfig

    LOGGING_LEVEL = config.get('LOGGING_LEVEL').upper()  # noqa
    LOGGING_CONFIG_PATH = config.get('LOGGING_CONFIG_PATH')
    LOG_FILE_PATH = config.get('LOG_FILE_PATH')

    valid_levels = logging._levelToName.values()

    assert LOGGING_LEVEL in valid_levels, \
        'LOGGING_LEVEL must be one of ' \
        '{VALID_LEVELS}.  ' \
        'Value is {VALUE}'.format(VALID_LEVELS=', '.join(valid_levels),
                                  VALUE=LOGGING_LEVEL)

    LEVEL = getattr(logging, LOGGING_LEVEL.upper())

    # If a user is specifying their own config then we modify the default
    # config to use `nullhandler` as we assume the user knows what they are
    # doing and want to override things.  We use 'filehandler' as an easy
    # way to get logs for users who don't want to have the hassle of
    # configuring a logging config themselves
    DEFAULT_HANDLER = 'filehandler' if LOGGING_CONFIG_PATH is None else 'nullhandler'  # noqa
    DEFAULT_MP_HANDLER = 'mp_filehandler' if LOGGING_CONFIG_PATH is None else 'nullhandler'  # noqa

    logging_config_func(build_default_config(LEVEL=LEVEL,
                                             DEFAULT_HANDLER=DEFAULT_HANDLER,
                                             DEFAULT_MP_HANDLER=DEFAULT_MP_HANDLER,  # noqa
                                             LOG_FILE_PATH=LOG_FILE_PATH))

    if LOGGING_CONFIG_PATH is not None:
        assert os.path.exists(LOGGING_CONFIG_PATH), \
            'LOGGING_CONFIG_PATH path does not exist. ' \
            'Path is {LOGGING_CONFIG_PATH}'.format(
                LOGGING_CONFIG_PATH=LOGGING_CONFIG_PATH)
        # They have specified their own config.  Merge it in with the default
        with open(LOGGING_CONFIG_PATH) as f:
            config = json.load(f)
        logging_config_func(config)
