from ..const import API_PATH, API_OPERATIONS
from .base import Resource
from .abvariants import Abvariants


class Experiment(Resource):
    PATH = API_PATH["experiments.experiment"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.abvariants = Abvariants(
            self, API_PATH["abvariants"], API_OPERATIONS["abvariants"]
        )
