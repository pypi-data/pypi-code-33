import scipy.stats
from scipy.stats import poisson


class RandomPoissonBounded():
    """
    Generates numbers from a Poisson distribution with range limits.
    """

    def __init__(self, *, mean: float = 1, loc: int = 0, lower: float = 0, upper: float = 1000,
                 sanity: float = 0.01):

        assert lower <= mean <= upper

        self.mean = mean
        self.loc = loc
        self.lower = lower
        self.upper = upper
        self.sanity_limit = sanity

        self.mu = self.mean - self.loc

        # Check that this won't discard too many generated values.
        dist = scipy.stats.poisson(self.mu)
        if dist.cdf(self.upper) - dist.cdf(self.lower) < self.sanity_limit:
            raise ValueError("Poisson curve overlaps acceptable range ({1},{2}) by less than {0}"
                             .format(self.sanity_limit, self.lower, self.upper))

    def __iter__(self):
        return self

    def __next__(self) -> int:
        n = self.raw_draw()
        while not (self.lower <= n <= self.upper):
            n = self.raw_draw()
        return n

    def raw_draw(self) -> int:
        return poisson.rvs(self.mu, loc=self.loc)
