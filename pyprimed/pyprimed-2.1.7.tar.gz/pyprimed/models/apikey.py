from ..const import API_PATH
from .base import Resource


class Apikey(Resource):
    PATH = API_PATH["apikeys.apikey"]
