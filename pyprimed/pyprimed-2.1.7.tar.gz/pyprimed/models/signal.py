# -*- coding: utf-8 -*-
from ..const import API_PATH
from .base import Resource


class Signal(Resource):
    PATH = API_PATH["signals.signal"]
