from .base import UsingRelationshipCollection
from .prediction import Prediction
from .model import Model
from .universe import Universe


class Predictions(UsingRelationshipCollection):
    _RESOURCE = Prediction
    _LEFT = Model
    _RIGHT = Universe
    _DEFAULT_SORTING = ["score", "DESC"]
    _DEFAULT_RANGE = [0, 100]
