# -*- coding: utf-8 -*-
from ..const import API_PATH
from .base import Relationship


class Prediction(Relationship):
    PATH = API_PATH["predictions.prediction"]
