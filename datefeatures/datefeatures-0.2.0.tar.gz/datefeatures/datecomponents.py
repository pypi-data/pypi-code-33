from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
import numpy as np


class DateComponents(BaseEstimator, TransformerMixin):
    # suffix to name features
    suffix_ = {
        'is_leap_year': 'leap',
        'year': 'year',
        'is_quarter_end': 'eoq',
        'quarter': 'quarter',
        'is_month_end': 'eom',
        'month': 'month',
        'dayofyear': 'dy',
        'dayofweek': 'dw',
        'week': 'week',  # weekofyear
        'day': 'day',
        'hour': 'hour',
        'minute': 'min',
        'second': 'sec',
        'microsecond': 'ms'
    }
    # datatype mapping
    dtype_ = {
        'is_leap_year': np.bool,
        'year': np.int16,
        'is_quarter_end': np.bool,
        'quarter': np.int8,
        'is_month_end': np.bool,
        'month': np.int8,
        'dayofyear': np.int16,
        'dayofweek': np.int8,
        'week': np.int8,
        'day': np.int8,
        'hour': np.int8,
        'minute': np.int8,
        'second': np.int8,
        'microsecond': np.int32
    }

    def __init__(self, df=True,
                 year=False, month=True, day=True,
                 hour=False, minute=False, second=False,
                 microsecond=False, missing=True):
        # set what date components should be processed
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.microsecond = microsecond
        # missing value indicator
        self.missing = missing
        # other settings
        self.df = df

    def fit(self, X, y=None):
        # pandas Timestamp object attributes
        self.date_attr_ = []
        self.date_attr_ += ['is_leap_year', 'year'] if self.year else []
        if self.month:
            self.date_attr_ += [
                'is_quarter_end', 'quarter', 'is_month_end', 'month']
        if self.day:
            self.date_attr_ += ['dayofyear', 'dayofweek', 'week', 'day']
        self.date_attr_ += ['hour'] if self.hour else []
        self.date_attr_ += ['minute'] if self.minute else []
        self.date_attr_ += ['second'] if self.second else []
        self.date_attr_ += ['microsecond'] if self.microsecond else []

        # generate the columns/fields names
        if isinstance(X, pd.DataFrame):
            flds = X.columns
        else:
            flds = [str(e) for e in range(X.shape[1])]

        self.feature_names_ = []
        for fld in flds:
            if self.missing:
                self.feature_names_.append(str(fld) + "_na")
            for attr in self.date_attr_:
                self.feature_names_.append(
                    str(fld) + "_" + self.suffix_[attr])

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

            for attr in self.date_attr_:
                dtype = self.dtype_[attr]
                colnam = str(fld) + "_" + self.suffix_[attr]
                if colnam not in self.feature_names_:
                    raise Exception('unknown raw columns')

                # get date component
                Z[colnam] = getattr(X_[fld].dt, attr)
                if self.missing:
                    dtype = np.int8 if dtype is np.bool else dtype
                    Z.loc[Z[str(fld) + "_na"], colnam] = -1

                # convert to smaller datatype
                Z[colnam] = Z[colnam].astype(dtype, errors='ignore')

        # output results
        if self.df:
            return Z
        else:
            return Z.values  # numpy array
