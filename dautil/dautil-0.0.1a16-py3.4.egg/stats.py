import numpy as np
from scipy.stats import describe
import pandas as pd
import math
from collections import namedtuple



def percentile_limits(a, percentile):
    Limit = namedtuple('Limit', ['min', 'max'])

    return Limit(np.percentile(a, percentile),
                 np.percentile(a, 100 - percentile))


def trimean(a):
    q1 = np.percentile(a, 25)
    q2 = np.percentile(a, 50)
    q3 = np.percentile(a, 75)

    return (q1 + 2 * q2 + q3)/4


def outliers(a, method='IRQ', factor=1.5, percentiles=(5, 95)):
    Outlier = namedtuple('Outlier', ['min', 'max'])
    outlier = None

    if method == 'IRQ':
        q1 = np.percentile(a, 25)
        q3 = np.percentile(a, 75)
        iqr = q3 - q1
        outlier = Outlier(q1 - factor * iqr, q3 + factor * iqr)
    elif method == 'percentiles':
        minmax = [np.percentile(a, p) for p in percentiles]
        outlier = Outlier(minmax[0], minmax[1])
    else:
        raise AssertionError('Unknown method expected IRQ or percentiles')

    return outlier


def clip_outliers(a):
    amin, amax = outliers(a)

    return np.clip(a, amin, amax)


def zscores(x):
    return (x - x.mean())/x.std()


def sqrt_bins(a):
    return int(math.sqrt(len(a)))


def ci(a, alpha=0.95):
    interval = 1 - alpha

    minmax = [interval/2, alpha + interval/2]

    return np.percentile(a, 100 * np.array(minmax))


def jackknife(x, func, alpha=0.95):
    n = len(x)
    idx = np.arange(n)

    low, high = ci([func(x[idx != i]) for i in range(n)], alpha)

    return func(x), low, high


class Distribution():
    def __init__(self, data, dist, nbins=20, cutoff=0.75, range=None):
        self.nbins = nbins
        self.train, self.test = self.split(data, cutoff)
        self.hist_values, edges = np.histogram(self.test, bins=self.nbins,
                                               range=range, density=True)
        self.x = 0.5 * (edges[1:] + edges[:-1])
        self.dist = dist
        self.residuals = None
        self.pdf_values = None

    def describe_residuals(self, *args, **kwds):
        _, _, mean, var, skew, kurtosis = describe(self.error(*args, **kwds))
        result = {}
        result['Mean'] = mean
        result['Var'] = var
        result['Skew'] = skew
        result['Kurtosis'] = kurtosis
        result = pd.DataFrame([result])
        result.index = ['Residuals Statistics']

        return result

    def error(self, *args, **kwds):
        if self.residuals is None:
            self.residuals = self.hist_values - self.pdf(*args, **kwds)

        return self.residuals

    def fit(self, *args):
        return self.dist.fit(self.train, *args)

    def mean(self):
        return self.train.mean()

    def mean_ad(self, *args, **kwds):
        ae = np.abs(self.error(*args, **kwds))

        return ae.mean()

    def pdf(self, *args, **kwds):
        if self.pdf_values is None:
            self.pdf_values = self.dist.pdf(self.x, *args, **kwds)

        return self.pdf_values

    def plot(self, ax):
        ax.hist(self.train, bins=self.nbins, normed=True, label='Data')
        ax.plot(self.x, self.pdf_values, label='PDF')
        ax.set_ylabel('Probability')
        ax.legend(loc='best')

    def rmse(self, *args, **kwds):
        se = self.error(*args, **kwds) ** 2

        return np.sqrt(se.mean())

    def rvs(self, *args, **kwds):
        return self.dist.rvs(*args, **kwds)

    def split(self, data, cutoff):
        n = len(data)
        n = int(cutoff * n)

        return data[:n], data[n:]

    def var(self):
        return self.train.var()
