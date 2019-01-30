# -*- coding: utf-8 -*-
from ..const import API_OPERATIONS, API_PATH
from .base import Resource, SimpleCollection
from .signals import Signals


class Model(Resource):
    PATH = API_PATH["models.model"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.signals = Signals(self, API_PATH["signals"], API_OPERATIONS["signals"])
