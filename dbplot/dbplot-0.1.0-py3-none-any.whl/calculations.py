import ibis
import numpy as np
import pandas as pd


def hist(table, column, nbins=10, binwidth=None):
    if nbins is None and binwidth is None:
        raise ValueError("Must indicate nbins or binwidth")
    elif nbins is None and binwidth is not None:
        raise ValueError("nbins and binwidth are mutually exclusive")

    min_, max_ = table[column].min().execute(), table[column].max().execute()
    min_, max_ = float(min_), float(max_)  # From numpy.float to python.float

    if binwidth is None:
        binwidth = (max_ - min_) / (nbins)

    buckets = [min_ + i * binwidth for i in range(nbins + 1)]

    bucketed = table[table[column] != ibis.null()][column].bucket(buckets).name("bucket")
    bucket_counts = bucketed.value_counts().execute()

    weights = bucket_counts["count"].values

    return weights, buckets
