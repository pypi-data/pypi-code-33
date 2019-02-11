import logging

import asks

from .errors import ApiError
from .factories import make_api


asks.init('trio')

logging.getLogger(__name__).addHandler(logging.NullHandler())
