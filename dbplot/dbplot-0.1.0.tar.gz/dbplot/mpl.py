import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from dbplot import calculations


def hist(table, column, nbins=10, binwidth=None, *args, **kwargs):
    weights, buckets = calculations.hist(table, column, nbins=nbins, binwidth=binwidth)

    # We need to remove the last item to pass it to Matplotlib an array with the same length as the weights
    x = np.linspace(buckets[0], buckets[-1], len(weights))
    return plt.hist(x, len(x), weights=weights, *args, **kwargs)
