from ..util import random_point_within
from .base_init import BaseInitialization

import numpy as np


class RandomInitialization(BaseInitialization):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def next(self, name, model):
        chosen_location = np.random.choice(model.locations)

        return self.AgentClass(name, model, random_point_within(chosen_location.shape), chosen_location, **self.kwargs)
