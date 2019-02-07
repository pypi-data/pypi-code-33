import logging

from .version import __version__  # flake8: noqa
from .client import Client
from .settings import enable_log, script_params  # flake8: noqa

from . import io_tools

enable_log()

logger = logging.getLogger(__name__)
logger.info('Using Serenytics python client %s' % __version__)
