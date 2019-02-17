
import asyncio

from colibris import app
from colibris import persist

from testmyesp import jobs


def init(webapp, loop):
    asyncio.ensure_future(jobs.exec_loop())


def get_health():
    if not persist.connectivity_check():
        raise app.HealthException('database connectivity check failed')

    return 'healthy'
