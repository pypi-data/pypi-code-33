from ..const import API_PATH
from .base import Resource


class User(Resource):
    PATH = API_PATH["users.user"]
