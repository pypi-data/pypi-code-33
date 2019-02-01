import numpy as np

class NonParametricDist(object):
    """
    .. py:class: NonParametricDist

    A class defined one example of nonparametric distributions.

    :param samples: the emprical samples where the nonparametric distribution
        will be built on.
    :param cdf: the cumulative distribution function of the distribution.
        optional.
    :param pdf: the probability density function of the distribution.
        optional.

    :examples:
    >>> samples = [1,5,7,3,8,2]
    >>> rv = NonParametricDist(samples)
    >>> rv.rvs(size=100)
    array([7, 5, 3, 8, 3, 5, 2, 1, 8, 8, 7, 7, 5, 8, 5, 2, 2, 5, 2, 3, 1, 7, 7,
           1, 8, 2, 5, 5, 3, 5, 8, 2, 5, 5, 3, 3, 8, 7, 5, 7, 7, 5, 3, 3, 8, 2,
           5, 5, 1, 3, 2, 8, 8, 3, 3, 7, 7, 2, 7, 7, 2, 8, 8, 7, 3, 1, 3, 2, 8,
           1, 7, 5, 7, 3, 7, 7, 7, 1, 7, 8, 3, 3, 2, 1, 5, 2, 8, 3, 3, 5, 8, 8,
           8, 1, 1, 1, 1, 1, 7, 5])
    >>> rv.interval(0.9)
    (1.25, 7.75)

    """
    def __init__(self, samples, cdf=None, pdf=None):
        self.samples = np.array(samples)
        self.cdf = cdf # empirical distribution could be used here.
        self.pdf = pdf # kernel extimatoin methods could be used here in the

    def interval(self, alpha):
        lower = 0.5*(1-alpha)
        upper = 0.5*(1+alpha)
        return(np.percentile(self.samples, lower*100), np.percentile(self.samples, upper*100))

    def rvs(self, size):
        return(np.random.choice(self.samples, size=size))

