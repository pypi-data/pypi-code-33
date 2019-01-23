import numpy as np
from numpy import float32

from nevolution_risk.constants.colors import white


class Player(object):
    def __init__(self, name, troops=0, color=white, action_len=0):
        self.name = name
        self.troops = troops
        self.color = color
        self.valid_actions = np.zeros(action_len, dtype=float32)


if __name__ == '__main__':
    print(np.zeros(0))
