import asyncio
import sched
import datetime
import threading
import time
import traceback
from copy import copy

from datetime import timedelta
from itertools import chain

from dateutil.relativedelta import relativedelta
from sanic.log import logger

from longitude.models.postgresqlmodel import PostgresqlModel


def delay_datetime(datetime):
    if datetime != 0:
        time.sleep(datetime.seconds + datetime.microseconds/10**6)


def keep_alive():
    global scheduler

    scheduler.enter(timedelta(seconds=5*60*60), 1, keep_alive)

    logger.debug('%s[%d]: keep alive', threading.current_thread().name, id(scheduler))


def start(task_initializer):
    """

    """

    def _boostrap():
        global scheduler
        scheduler = sched.scheduler(datetime.datetime.now, delay_datetime)

        scheduler_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(scheduler_loop)

        sql_model = scheduler_loop.run_until_complete(PostgresqlModel.instantiate())

        task_initializer(sql_model)

        keep_alive()
        scheduler.run()

    th = threading.Thread(
        name='Scheduler',
        target=_boostrap,
        daemon=True
    )

    th.start()


def repeat(delta: relativedelta, fn, *args, from_datetime=None, **kwargs):

    global scheduler

    if 'scheduler' not in globals():
        raise RuntimeError(
            'You can only call the scheduler functions in a call nested to the task_initializer '
            'callback of the scheduler.start function.'
        )

    now = datetime.datetime.now()

    if from_datetime is None:
        from_datetime = now

    next_call = from_datetime + delta

    if next_call < now:
        logger.info(
            (
                'Retrospectively calling %s.%s at %s'
                ', from datetime %s with delta %s.'
            ),
            fn.__module__,
            fn.__name__,
            str(next_call),
            str(from_datetime),
            str(delta)
        )
    else:
        logger.info(
            (
                'Scheduling call to %s.%s at %s'
                ', from datetime %s with delta %s.'
            ),
            fn.__module__,
            fn.__name__,
            str(next_call),
            str(from_datetime),
            str(delta)
        )

    def call_fn(_next_call):

        try:
            res = fn(_next_call, *args, **kwargs)

            if asyncio.iscoroutine(res):
                asyncio.get_event_loop().run_until_complete(res)
        except BaseException as e:
            logger.error('{}\n{}'.format(str(e), traceback.format_exc()))

    while next_call < now:
        call_fn(next_call)
        next_call = next_call + delta
        logger.info(
            (
                'Scheduling call to %s.%s at %s'
                ', from datetime %s with delta %s.'
            ),
            fn.__module__,
            fn.__name__,
            str(next_call),
            str(from_datetime),
            str(delta)
        )

    _kwargs = copy(kwargs)
    _kwargs['from_datetime'] = next_call

    scheduler.enterabs(next_call, 0, repeat, chain((delta, fn,), args), _kwargs)
    scheduler.enterabs(next_call, 1, lambda: call_fn(next_call))
