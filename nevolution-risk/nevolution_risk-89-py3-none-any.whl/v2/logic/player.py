import numpy as np
from numpy import float32

from nevolution_risk.constants.colors import white


class Player(object):
    def __init__(self, name, troops=0, color=white, actions=0):
        self.name = name
        self.troops = troops
        self.color = color
        self.valid_actions = np.zeros(actions, dtype=float32)
