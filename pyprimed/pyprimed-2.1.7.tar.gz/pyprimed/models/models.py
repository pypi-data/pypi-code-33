from .base import SimpleCollection
from .model import Model


class Models(SimpleCollection):
    _RESOURCE = Model
    _DEFAULT_SORTING = ["name", "ASC"]
    _DEFAULT_RANGE = [0, 100]
