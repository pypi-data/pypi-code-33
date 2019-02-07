import contextlib
import logging
import sys

import celery
from celery.utils.log import get_task_logger
from celery import signals

PY2 = sys.version_info[0] == 2


@signals.celeryd_init.connect
def configure_worker(conf=None, **kwargs):
    conf.setdefault('CUBICWEB_CELERYTASK_REDIS_URL',
                    'redis://localhost:6379/0')


@signals.task_failure.connect
def log_exception(**kwargs):
    logger = logging.getLogger("celery.task")
    if PY2:
        einfo = str(kwargs['einfo']).decode('utf8')
    else:
        einfo = str(kwargs['einfo'])
    logger.critical(u"unhandled exception:\n%s", einfo)


@signals.celeryd_after_setup.connect
def setup_cubicweb_logging(conf=None, **kwargs):
    """
    Set parent to "celery.task" for all instantiated logger names starting with
    "cube" or "cubicweb"
    """
    logall = conf.get('CUBICWEB_CELERYTASK_LOG_ALL', False)
    for logname in logging.root.manager.loggerDict.keys():
        if logname == 'celery' or logname.startswith('celery.'):
            # Logger name 'celery' is reserved
            continue
        if (logall or
           logname.startswith('cubes') or logname.startswith('cubicweb')):
            get_task_logger(logname)


@contextlib.contextmanager
def redirect_stdouts(logger):
    old_outs = sys.stdout, sys.stderr
    try:
        app = celery.current_app
        rlevel = app.conf.CELERY_REDIRECT_STDOUTS_LEVEL
        app.log.redirect_stdouts_to_logger(logger, rlevel)
        yield
    finally:
        sys.stdout, sys.stderr = old_outs
