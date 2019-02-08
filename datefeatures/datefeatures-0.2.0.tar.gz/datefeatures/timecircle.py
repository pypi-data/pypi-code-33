from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
import numpy as np
from datetime import datetime


seconds_ = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}


def to_frac(d: datetime, unit: str, intv: int):
    ds = seconds_[unit] * intv
    return (d.timestamp() % ds) / ds


def to_sin(u: float):
    return np.sin(2e0 * np.pi * u)


def to_cos(u: float):
    return np.cos(2e0 * np.pi * u)


class TimeCircle(BaseEstimator, TransformerMixin):

    def __init__(self, freq={'s': [5], 'm': [15], 'h': [3], 'd': [1, 7]},
                 out=['sin', 'cos'], missing=True, df=True):
        self.freq = freq
        self.out = out
        # missing value indicator
        self.missing = missing
        # other settings
        self.df = df

    def fit(self, X, y=None):
        """generate column names only"""
        # generate the columns/fields names
        if isinstance(X, pd.DataFrame):
            flds = X.columns
        else:
            flds = [str(e) for e in range(X.shape[1])]

        self.feature_names_ = []
        for fld in flds:
            if self.missing:
                self.feature_names_.append(str(fld) + "_na")

            for unit, intervals in self.freq.items():
                for intv in intervals:
                    prefix = str(fld) + "_" + unit + str(intv)
                    if 'sin' in self.out:
                        self.feature_names_.append(prefix + '_sin')
                    if 'cos' in self.out:
                        self.feature_names_.append(prefix + '_cos')
                    if 'frac' in self.out:
                        self.feature_names_.append(prefix + '_frac')

        return self

    def transform(self, X, copy=None):
        # convert to pandas dataframe and Timestamp
        X_ = pd.DataFrame(X, copy=copy)

        # create output (don't pre-allocate columns)
        Z = pd.DataFrame(index=X_.index)

        # loop over each raw variable
        for fld in X_.columns:
            # missing value indicator
            if self.missing:
                Z[str(fld) + "_na"] = pd.isnull(X_[fld])

            # generate circle/wave feature
            for unit, intervals in self.freq.items():
                # e.g. unit='s' and intervals=[1,5]
                for intv in intervals:
                    # time fraction, e.g. of 5sec intervals
                    tmp_frac = X_[fld].dropna().apply(
                        lambda d: to_frac(d, unit, intv))

                    # prefix for column name
                    prefix = str(fld) + "_" + unit + str(intv)

                    if 'sin' in self.out:
                        Z[prefix + '_sin'] = tmp_frac.apply(to_sin)

                    if 'cos' in self.out:
                        Z[prefix + '_cos'] = tmp_frac.apply(to_cos)

                    if 'frac' in self.out:
                        Z[prefix + '_frac'] = tmp_frac

        # output results
        if self.df:
            return Z
        else:
            return Z.values  # numpy array
