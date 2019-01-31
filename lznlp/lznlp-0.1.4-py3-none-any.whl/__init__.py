# -*- coding: utf-8 -*-

import logging

__VERSION__ = '0.0.3'

from .client import LZNLP
from .client import WordVector
from .client import TextClassifierV1
from .client import XGBoost
from .client import DeepLearningBaseline
from .client import NerBaseline
from .rabbit import Rabbit
from .exceptions import HTTPError, TaskNotFoundError, TaskError, TimeoutError

# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
