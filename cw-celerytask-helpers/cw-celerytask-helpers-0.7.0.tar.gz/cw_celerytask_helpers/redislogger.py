"""Helpers for managing logging in redis in cubicweb-celerytask workers

Add this module 'cw_celerytask_helpers.redislogger' to CELERY_IMPORTS
"""
from __future__ import absolute_import

import json
import datetime
import logging

from celery._state import get_current_task
from celery import signals

from .utils import get_redis_client

LOG_KEY_PREFIX = "cw:celerytask:log"


class UnknownTaskId(Exception):
    pass


def get_log_key(task_id):
    return "{0}:{1}".format(LOG_KEY_PREFIX, task_id)


@signals.celeryd_after_setup.connect
def setup_redis_logging(conf=None, **kwargs):
    logger = logging.getLogger('celery.task')
    redis_client = get_redis_client()
    logger.addHandler(RedisPubHandler(
        channel=LOG_KEY_PREFIX,
        redis_client=redis_client,
        level=logging.DEBUG))
    store_handler = RedisStoreHandler(
        prefix=LOG_KEY_PREFIX,
        redis_client=redis_client,
        level=logging.DEBUG)
    store_handler.setFormatter(logging.Formatter(
        fmt="%(levelname)s %(asctime)s %(module)s %(process)d %(message)s\n"))
    logger.addHandler(store_handler)


def get_task_logs(task_id):
    """
    Get task logs by id
    """
    redis_client = get_redis_client()
    return redis_client.get(get_log_key(task_id))


def flush_task_logs(task_id):
    """Delete task logs"""
    redis_client = get_redis_client()
    return redis_client.delete(get_log_key(task_id))


class RedisFormatter(logging.Formatter):
    def format(self, record):
        """
        JSON-encode a record for serializing through redis.

        Convert date to iso format, and stringify any exceptions.
        """
        task = get_current_task()
        if task and task.request:
            record.__dict__.update(task_id=task.request.id,
                                   task_name=task.name)
        else:
            raise UnknownTaskId()

        message = super(RedisFormatter, self).format(record)

        data = {
            'name': record.name,
            'level': record.levelno,
            'levelname': record.levelname,
            'filename': record.filename,
            'line_no': record.lineno,
            'message': message,
            'time': datetime.datetime.utcnow().isoformat(),
            'funcname': record.funcName,
            'traceback': record.exc_info,
            'task_id': record.task_id,
            'task_name': record.task_name,
        }

        # stringify exception data
        if record.exc_text:
            data['traceback'] = record.exc_text  # XXX should we format it?

        return json.dumps(data)


class RedisPubHandler(logging.Handler):
    """
    Publish messages to redis channel.
    """

    def __init__(self, channel, redis_client, *args, **kwargs):
        """
        Create a new logger for the given channel and redis_client.
        """
        super(RedisPubHandler, self).__init__(*args, **kwargs)
        self.channel = channel
        self.redis_client = redis_client
        self.formatter = RedisFormatter()

    def emit(self, record):
        """
        Publish record to redis logging channel
        """
        try:
            self.redis_client.publish(self.channel, self.format(record))
        except UnknownTaskId:
            pass


class RedisStoreHandler(logging.Handler):
    """
    Send logging messages to a redis store.
    """

    def __init__(self, prefix, redis_client, *args, **kwargs):
        """
        Create a new logger for the given channel and redis_client.
        """
        super(RedisStoreHandler, self).__init__(*args, **kwargs)
        self.prefix = prefix
        self.redis_client = redis_client

    def emit(self, record):
        """
        Publish record to redis logging channel
        """
        # See celery.app.log.TaskFormatter
        if record.task_id not in ('???', None):
            key = get_log_key(record.task_id)
            self.redis_client.append(key, self.format(record))
