# coding: utf-8
from __future__ import print_function

import sys
import logging
import time

import six

from celery import current_app as app, chord
from celery.utils.log import get_task_logger

from cw_celerytask_helpers.utils import get_redis_client
from cw_celerytask_helpers import redirect_stdouts

cw_logger = logging.getLogger('cubes.tasks')
dummy_logger = logging.getLogger('dummy')
logger = get_task_logger(__name__)


@app.task(name='success')
def success(n):
    return n


@app.task(name='fail')
def fail():
    raise RuntimeError('fail')


@app.task(bind=True, name='exc_encoding')
def exc_encoding(self):
    if six.PY2:
        raise RuntimeError(u'Cette tâche a échoué'.encode('utf8'))
    else:
        raise RuntimeError('Cette tâche a échoué')


@app.task(name='buggy_task')
def buggy_task():
    rdb = get_redis_client()
    while True:
        if rdb.get('buggy_task_revoked') == b'yes':
            break
        logger.error('evil')
        time.sleep(1)


@app.task(name='log')
def log():
    for out in [sys.stdout, sys.stderr]:
        print('should not be in logs', file=out)

    with redirect_stdouts(logger):
        print('out should be in logs')
        print('err should be in logs', file=sys.stderr)

    for out in [sys.stdout, sys.stderr]:
        print('should not be in logs', file=out)

    for name, l, state in [
        ('cw', cw_logger, 'be'),
        ('celery', logger, 'be'),
        ('dummy', dummy_logger, 'not be')
    ]:
        for key in ('debug', 'info', 'warning', 'error', 'critical'):
            getattr(l, key)('%s %s should %s in logs', name, key, state)
        try:
            raise RuntimeError("fail")
        except RuntimeError:
            l.exception('%s exception should be in logs', name)

    raise Exception("oops")


@app.task(name="add")
def add(x, y):
    return x + y


@app.task(name="tsum")
def tsum(args):
    return sum(args)


@app.task(bind=True, name="spawn")
def spawn(self):
    return {
        "celerytask_subtasks": chord((success.s(i) for i in range(10)),
                                     tsum.s() | add.s(-45))().as_tuple(),
    }
