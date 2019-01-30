from .base import SimpleCollection
from .universe import Universe


class Universes(SimpleCollection):
    _RESOURCE = Universe
    _DEFAULT_SORTING = ["name", "ASC"]
    _DEFAULT_RANGE = [0, 100]
