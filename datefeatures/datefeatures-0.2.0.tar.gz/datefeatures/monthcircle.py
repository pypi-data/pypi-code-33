from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
import numpy as np
from .timecircle import to_cos, to_sin
from calendar import monthrange  # for 'frac_month'


def frac_sec(ms: int):
    """time elapsed with a second"""
    return ms / 1e6


def frac_min(sc: int, ms: int = 0):
    """time elapsed within a minute"""
    return (sc + frac_sec(ms)) / 6e1


def frac_hour(mi: int, sc: int = 0, ms: int = 0):
    """time elapsed within an hour"""
    return (mi + frac_min(sc, ms)) / 6e1


def frac_day(hr: int, mi: int = 0, sc: int = 0, ms: int = 0):
    """time elapsed within a day"""
    return (hr + frac_hour(mi, sc, ms)) / 2.4e1


def frac_month(yrs: int, mth: int, day: int,
               hr: int = 0, mi: int = 0, sc: int = 0, ms: int = 0):
    """time elapsed wihtin a month
    requires the year and month!
    """
    n_days = monthrange(yrs, mth)[1]
    return (day + frac_day(hr, mi, sc, ms)) / n_days


class MonthCircle(BaseEstimator, TransformerMixin):

    def __init__(self, out=['sin', 'cos'], missing=True, df=True):
        # types of outputs
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
            prefix = str(fld) + '_month'
            if self.missing:
                self.feature_names_.append(prefix + "_na")
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
            # monthly fraction
            tmp_frac = X_[fld].dropna().apply(
                lambda d: frac_month(
                    d.year, d.month, d.day, d.hour,
                    d.minute, d.second, d.microsecond))
            # assign to dataframe
            prefix = str(fld) + '_month'
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
