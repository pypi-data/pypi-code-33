# -*- coding: utf-8 -*-
from ..const import API_PATH
from .base import Resource


class Target(Resource):
    PATH = API_PATH["targets.target"]

    @property
    def value(self):
        return self.value_
