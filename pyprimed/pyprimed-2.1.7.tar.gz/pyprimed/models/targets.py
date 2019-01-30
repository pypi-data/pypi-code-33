from .base import SimpleCollection
from .target import Target


class Targets(SimpleCollection):
    _RESOURCE = Target
    _DEFAULT_SORTING = ["key", "ASC"]
    _DEFAULT_RANGE = [0, 100]
