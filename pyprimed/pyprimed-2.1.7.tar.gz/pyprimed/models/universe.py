# -*- coding: utf-8 -*-
from ..const import API_OPERATIONS, API_PATH
from .base import Resource
from .targets import Targets
from .campaigns import Campaigns


class Universe(Resource):
    PATH = API_PATH["universes.universe"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.targets = Targets(self, API_PATH["targets"], API_OPERATIONS["targets"])

        self.campaigns = Campaigns(
            self, API_PATH["campaigns"], API_OPERATIONS["campaigns"]
        )
