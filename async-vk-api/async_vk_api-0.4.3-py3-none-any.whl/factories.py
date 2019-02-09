import asks
from asks.errors import BadHttpResponse

from . import utils
from .api import Api
from .throttler import Throttler


def make_api(access_token, version, session=None, throttler=None, retry=None):
    if session is None:
        session = make_session()

    if throttler is None:
        throttler = make_throttler()

    if retry is None:
        retry = make_retry()

    return Api(
        access_token=access_token,
        version=version,
        session=session,
        throttler=throttler,
        retry=retry
    )


def make_session(
    base_location='https://api.vk.com',
    endpoint='/method',
    connections=1,
    **kwargs
):
    return asks.Session(
        base_location=base_location,
        endpoint=endpoint,
        connections=connections,
        **kwargs
    )


def make_throttler(frequency=3):
    return Throttler(frequency=frequency)


def make_retry(exceptions=BadHttpResponse, attempts=2, delay=0):
    return utils.retry(
        exceptions=exceptions,
        attempts=attempts,
        delay=delay
    )
