from .base import SimpleCollection
from .apikey import Apikey


class Apikeys(SimpleCollection):
    _RESOURCE = Apikey
    _DEFAULT_SORTING = ["name", "ASC"]
    _DEFAULT_RANGE = [0, 100]
