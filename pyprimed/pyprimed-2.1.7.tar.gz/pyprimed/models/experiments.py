from .base import SimpleCollection
from .experiment import Experiment


class Experiments(SimpleCollection):
    _RESOURCE = Experiment
    _DEFAULT_SORTING = ["name", "ASC"]
    _DEFAULT_RANGE = [0, 100]
