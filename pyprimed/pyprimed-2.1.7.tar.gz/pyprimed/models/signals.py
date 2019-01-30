from .base import SimpleCollection
from .signal import Signal


class Signals(SimpleCollection):
    _RESOURCE = Signal
    _DEFAULT_SORTING = ["key", "ASC"]
    _DEFAULT_RANGE = [0, 100]
