import numpy as np


class RandomSatisfaction():
    def __init__(self):
        pass

    def satisfaction(self, agent, omegas):
        o = np.reshape(omegas, (1, 3))
        return np.asscalar(np.dot(o, self.satisfiers(agent)))

    def satisfiers(self, agent):
        """
        Gives the satisfaction per category

        Currently assumes 3 categories:
          * Social
          * Economic
          * Environmental
        """
        return np.random.rand(3, 1)
