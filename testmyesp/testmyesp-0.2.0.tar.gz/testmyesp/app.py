
import asyncio

from testmyesp import jobs


def init(webapp, loop):
    asyncio.ensure_future(jobs.exec_loop())


# def get_health():
#     # return your health status or raise app.HealthException()
#
#     return {
#         'healthy': 'yes'
#     }
#
