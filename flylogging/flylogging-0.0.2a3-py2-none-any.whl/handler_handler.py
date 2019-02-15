from __future__ import print_function
import sys
import logging
import yaml
import time
import os
import warnings
import gevent
import threading
from logging import handlers

from .json_formatter import JSONLogFormatter

log = logging.getLogger(__name__)

try:
    import gevent_inotifyx as inotify
    LIVE_RELOAD = True
except ImportError:
    LIVE_RELOAD = False
    warnings.warn('inotify not installed, live logging config reload not supported')

def init_flywheel_logging(config_file, handler=None, tag=None):
    """Initialize the python logging hierarchy to watch a config file that specifies the logging levels of individual loggers"""

    def update_logging():
        with open(config_file, 'r') as fp:
            try:
                log_config = yaml.load(fp)
            except yaml.YAMLError as e:
                logging.error(e)
                print(e, file=sys.stderr)
        handler.setLevel(log_config['logging_level'])
        log.info('Setting logging level of handler %s to %s', id(handler), log_config['logging_level'])
        for named_logger in log_config.get('named_loggers', []):
            logging.getLogger(named_logger['name']).setLevel(named_logger['level'])

    def watch_file():
        fd = inotify.init()
        log.debug('Watching %s for changes', config_file)
        try:
            wd = inotify.add_watch(fd, os.path.dirname(config_file), inotify.IN_MODIFY | inotify.IN_CLOSE_WRITE)
            while True:
                for event in inotify.get_events(fd):
                    log.debug('Got inotify event %s - %s', event.name, event.get_mask_description())
                    if event.name == os.path.basename(config_file):
                        log.debug('Updating logging')
                        update_logging()
        finally:
            os.close(fd)

    if handler is None:
        syslog_host = os.getenv('SYSLOG_HOST', 'logger')
        syslog_port = int(os.getenv('SYSLOG_PORT', '514'))
        log.info('Sending syslogs to %s:%s', syslog_host, syslog_port)
        handler = logging.handlers.SysLogHandler(address=(syslog_host, syslog_port))
    formatter = JSONLogFormatter(tag=tag)
    handler.setFormatter(formatter)
    log.debug('Setting formatter for handler %s', id(handler))
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel('DEBUG')

    if not os.path.exists(config_file):
        log.error('No logging file configured')
        return

    update_logging()

    if LIVE_RELOAD:
        t = threading.Thread(target=watch_file)
        t.daemon = True
        t.start()
