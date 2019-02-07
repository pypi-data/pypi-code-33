import random
import scipy.stats


class RandomNormalBounded():
    """
    Generates numbers from a normal distribution with range limits.
    """

    def __init__(self, mean: float = 0.0, std: float = 1.0, *, lower: float = 0.0, upper: float = 1.0, snap_limit: bool = False,
                 sanity: float = 0.01):

        assert lower <= upper

        self.mean = mean
        self.std = std
        self.snap_limit = snap_limit
        self.lower = lower
        self.upper = upper
        self.sanity_limit = sanity

        if not snap_limit:
            # Check that this won't discard too many generated values.
            dist = scipy.stats.norm(mean, std)
            if dist.cdf(self.upper) - dist.cdf(self.lower) < self.sanity_limit:
                raise ValueError("Normal curve overlaps acceptable range ({1},{2}) by less than {0}"
                                 .format(self.sanity_limit, self.lower, self.upper))

    def __iter__(self):
        return self

    def __next__(self) -> float:
        p = self.lower - 1
        while not (self.lower <= p <= self.upper):
            p = random.normalvariate(self.mean, self.std)

            # Snap out-of-bounds values in bounds.
            if self.snap_limit:
                p = min(max(p, self.lower), self.upper)
        return p
