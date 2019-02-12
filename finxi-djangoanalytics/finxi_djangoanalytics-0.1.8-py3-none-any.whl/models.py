from .behaviors.agents import Indentifiable, Trackable, get_variables
from .behaviors.hits import Hit


class Cid(Trackable):
    pass


class User(Indentifiable):
    pass


class RawHit(Hit):
    pass
