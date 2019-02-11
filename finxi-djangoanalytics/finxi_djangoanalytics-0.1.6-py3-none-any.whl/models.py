from .behaviors.agents import Indentifiable, Trackable
from .behaviors.hits import Hit


class RawCid(Trackable):
    pass


class RawUser(Indentifiable):
    pass


class RawHit(Hit):
    pass
