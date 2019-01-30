from .base import SimpleCollection
from .user import User


class Users(SimpleCollection):
    _RESOURCE = User
    _DEFAULT_SORTING = ["name", "ASC"]
    _DEFAULT_RANGE = [0, 100]
