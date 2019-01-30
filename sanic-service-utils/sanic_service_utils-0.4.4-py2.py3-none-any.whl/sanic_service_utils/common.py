import asyncio
import logging

from sanic import Blueprint, Sanic


__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.4.4"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = [
    'anji_orm_configuration', 'sentry_configuration', 'background_task_configuration',
    'aiohttp_session_configuration', 'jinja_session_configuration', 'log_configuration',
    'sanic_session_configuration'
]

LOG_FORMAT = '[%(asctime)s] %(name)s:%(levelname)s: %(message)s'
anji_orm_configuration = Blueprint('Anji ORM Configuration')  # pylint: disable=invalid-name
sentry_configuration = Blueprint('Sentry Configuration')  # pylint: disable=invalid-name
background_task_configuration = Blueprint('Background Task Configuration')  # pylint: disable=invalid-name
aiohttp_session_configuration = Blueprint('AIOHttp Configuration')  # pylint: disable=invalid-name
jinja_session_configuration = Blueprint('Jinja Configuration')  # pylint: disable=invalid-name
sanic_session_configuration = Blueprint('Sanic-Session Configuration')  # pylint: disable=invalid-name
log_configuration = Blueprint('Log Configuration')  # pylint: disable=invalid-name


@sentry_configuration.listener('before_server_start')
async def sentry_check(sanic_app, _loop) -> None:
    import sentry_sdk
    from sentry_sdk.integrations.sanic import SanicIntegration

    if 'SENTRY_DSN' in sanic_app.config:
        sentry_sdk.init(
            dsn=sanic_app.config.get('SENTRY_DSN'),
            release=sanic_app.config.get('VERSION', '0.1.0'),
            environment=sanic_app.config.get('ENVIRONMENT', 'dev'),
            integrations=[SanicIntegration()]
        )


@aiohttp_session_configuration.listener('before_server_start')
async def init_aiohttp_session(sanic_app, _loop) -> None:
    import aiohttp

    session_kwargs = {}
    if not sanic_app.config.get('VERIFY_SSL', True):
        session_kwargs['connector'] = aiohttp.TCPConnector(verify_ssl=False)
    sanic_app.async_session = aiohttp.ClientSession(**session_kwargs)  # type: ignore


@aiohttp_session_configuration.listener('after_server_stop')
async def close_aiohttp_session(sanic_app, _loop) -> None:
    await sanic_app.async_session.close()


@log_configuration.listener('before_server_start')
async def logging_configuration(sanic_app, _loop) -> None:
    root_logger = logging.getLogger(sanic_app.name)
    sanic_utils_root_logger = logging.getLogger('sanic_service_utils')
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    root_logger.addHandler(handler)
    sanic_utils_root_logger.addHandler(handler)
    logging_level = logging.DEBUG if sanic_app.debug else logging.INFO
    root_logger.setLevel(logging_level)
    sanic_utils_root_logger.setLevel(logging_level)


@jinja_session_configuration.listener('before_server_start')
async def jinja_configuration(sanic_app: Sanic, _loop) -> None:
    from sanic_jinja2 import SanicJinja2

    sanic_app.jinja = SanicJinja2(sanic_app, enable_async=True, pkg_name=sanic_app.name)


@anji_orm_configuration.listener('before_server_start')
async def initial_configuration(sanic_app, _loop) -> None:
    from anji_orm import orm_register

    extensions = {}
    if 'ANJI_ORM_FILE_EXTENSION_CONNECTION_STRING' in sanic_app.config:
        extensions['file'] = sanic_app.config.get('ANJI_ORM_FILE_EXTENSION_CONNECTION_STRING')

    orm_register.init(
        sanic_app.config.get('ANJI_ORM_CONNECTION_STRING', 'rethinkdb://'),
        {},
        async_mode=True,
        extensions=extensions
    )
    await orm_register.async_load()


@anji_orm_configuration.listener('after_server_stop')
async def stop_anji_orm(_sanic_app, _loop) -> None:
    from anji_orm import orm_register

    await orm_register.async_close()


@background_task_configuration.listener('before_server_start')
async def run_background_tasks(sanic_app, _loop: asyncio.AbstractEventLoop) -> None:
    sanic_app.tasks_list = []


@background_task_configuration.listener('before_server_stop')
async def stop_background_tasks(sanic_app, _loop) -> None:
    for task in sanic_app.tasks_list:
        task.cancel()

    await asyncio.wait(sanic_app.tasks_list)


@sanic_session_configuration.middleware('request')
async def add_session_to_request(request):
    # before each request initialize a session
    # using the client's request
    await request.app.session_interface.open(request)


@sanic_session_configuration.middleware('response')
async def save_session(request, response):
    # after each request save the session,
    # pass the response to set client cookies
    await request.app.session_interface.save(request, response)
