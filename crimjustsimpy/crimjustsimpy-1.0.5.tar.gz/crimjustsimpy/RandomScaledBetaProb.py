import random


class RandomScaledBetaProb():
    """
    Generates probabilities using a Beta distribution.
    """

    def __init__(self, *, lower: float = 0.0, upper: float = 1.0, shape: float = 2.0, middle: float = None):
        """
        Create a probability generator using a Beta distribution.
        The ratio between traditional alpha and beta parameters to the Beta distribution
        will be calculated from the mean, with their absolute magnitude described by the scale.

        :param lower: Lowest probability that can be generated.
        :param middle: Mean probability.
        :param upper: Highest probability that can be generated.
        :param shape: A shaping factor controlling the shape of the curve.
        """

        if middle is None:
            middle = (lower + upper) / 2

        assert lower <= middle <= upper
        assert shape > 0

        # Save parameters.
        self.lower = lower
        self.middle = middle
        self.upper = upper
        self.shape = shape

        # Calculate derived values.
        self.width = self.upper - self.lower
        self.mu = (middle - self.lower) / self.width
        self.alpha = shape
        self.beta = shape * (1 - self.mu) / self.mu

    def __iter__(self):
        return self

    def __next__(self):
        """
        Generate a probability from the specified pattern.
        :return: A probability.
        """

        # Get a random draw from the Beta distribution.
        p = random.betavariate(self.alpha, self.beta)

        # Scale it to the requested range.
        return p * self.width + self.lower
