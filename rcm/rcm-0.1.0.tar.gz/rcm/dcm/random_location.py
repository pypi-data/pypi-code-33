import numpy as np


class RandomLocationModel:
    def __init__(self):
        pass

    def choose_location(self, agent):
        return np.random.choice(agent.model.locations)
