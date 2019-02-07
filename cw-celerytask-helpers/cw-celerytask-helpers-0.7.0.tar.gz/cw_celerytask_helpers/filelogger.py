"""Helpers for managing logging to file in cubicweb-celerytask workers

Add this module 'cw_celerytask_helpers.filelogger' to CELERY_IMPORTS

You can control where logs are stored with the CUBICWEB_CELERYTASK_LOGDIR
config, the directory must exist and be writable.
"""
from __future__ import absolute_import

import errno
import logging
import gzip
import os
import sys

import celery
from celery import signals

PY2 = sys.version_info[0] == 2
LOG_KEY_PREFIX = "cw:celerytask:log"


class UnknownTaskId(Exception):
    pass


def get_log_filename(task_id):
    logdir = celery.current_app.conf.get('CUBICWEB_CELERYTASK_LOGDIR')
    if not logdir:
        raise RuntimeError(
            "You asked for file-based log storage of the task logs "
            "but CUBICWEB_CELERYTASK_LOGDIR is not configured. "
            "Please set CUBICWEB_CELERYTASK_LOGDIR in your "
            "celery configuration.")
    return os.path.join(logdir, 'celerytask-{}.log.gz'.format(task_id))


def get_log_key(task_id):
    return "{0}:{1}".format(LOG_KEY_PREFIX, task_id)


@signals.celeryd_after_setup.connect
def setup_file_logging(conf=None, **kwargs):
    logger = logging.getLogger('celery.task')
    store_handler = FileStoreHandler(level=logging.DEBUG)
    store_handler.setFormatter(logging.Formatter(
        fmt="%(levelname)s %(asctime)s %(module)s %(process)d %(message)s\n"))
    logger.addHandler(store_handler)


def get_task_logs(task_id):
    """
    Get task logs by id
    """
    try:
        with gzip.open(get_log_filename(task_id), 'rb') as f:
            return f.read()
    except IOError as exc:
        if exc.errno != errno.ENOENT:
            raise
        return None


def flush_task_logs(task_id):
    """Delete task logs"""
    try:
        os.unlink(get_log_filename(task_id))
    except OSError as exc:
        if exc.errno != errno.ENOENT:
            raise


class FileStoreHandler(logging.Handler):
    """
    Send logging messages to a file in
    """

    def emit(self, record):
        """
        Append logs to gzip log file in `self.logdir`
        """
        # See celery.app.log.TaskFormatter
        if record.task_id not in ('???', None):
            fname = get_log_filename(record.task_id)
            with gzip.open(fname, 'a') as f:
                f.write(self.format(record).encode('utf-8'))
