import numpy as np
from scipy.stats import describe
import pandas as pd


def zscores(x):
    return (x - x.mean())/x.std()


def jackknife(x, func, alpha=0.95):
    n = len(x)
    idx = np.arange(n)
    interval = 1 - alpha
    minmax = [interval/2, alpha + interval]

    low, high = np.percentile([func(x[idx != i]) for i in range(n)], minmax)

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

    def split(self, data, cutoff):
        n = len(data)
        n = int(cutoff * n)

        return data[:n], data[n:]

    def var(self):
        return self.train.var()
