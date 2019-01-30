import pandas as pd
import numpy as np
import sys
from sklearn.base import BaseEstimator, TransformerMixin

class TSNumericalToDate(BaseEstimator, TransformerMixin):
    """ Transforms a non-Unix time in the numerical form YYYYMMDD(.0) or any
    lower values for month or year resolution into a timestamp object. It also
    contains the dates in given limits when given.

       :param past_limit: string for an ISO date to bound the past, or anything
       pd.to_datetime can handle

       :param future_limit: string for an ISO date to bound the future, or
       anything pd.to_datetime can handle
    """
    def __init__(self, past_limit="", future_limit=""):
        self.past_limit = None
        self.future_limit = None
        try:
            if isinstance(past_limit, str) and len(past_limit) > 0:
                self.past_limit = pd.to_datetime(past_limit)
            if isinstance(future_limit, str) and len(future_limit) > 0:
                self.future_limit = pd.to_datetime(future_limit)
        except Exception as eee:
            self.past_limit = None
            self.future_limit = None
            print("Past or future limit has bad input; are they ISO dates ?", file=sys.stderr)

    def fit(self, X, y=None):
        return self

    def transform(self, input_s):
        assert isinstance(input_s, pd.Series), \
            "requires pandas Series as input"
        #assert isinstance(input_s.dtype, (np.number, np.floating)), \
        #    "requires specific type class as input: numerical Series"

        # Transforms a year only to day resolution on first of january
        year_res = input_s[(input_s >= 1e3) & (input_s < 1e4)].apply(lambda x: x*10000+101)
        # Transforms a month resolution date to day resolution on first of the given month
        month_res = input_s[(input_s >= 1e5) & (input_s < 1e6)].apply(lambda x: x*100+1)
        # Don't Transforms day resolution dates, just select
        day_res   = input_s[(input_s >= 1e7) & (input_s < 1e8)]

        valid_dates = day_res.combine_first(month_res).combine_first(year_res)

        # Converts to datetime with errors=coerce to generate NaT when appropriate
        valid_dates = valid_dates.apply(lambda x: pd.to_datetime(str(x), format="%Y%m%d", errors="coerce"))

        # Reindex and Invalidate all other dates
        all_dates = valid_dates.reindex(input_s.index, fill_value=pd.NaT)

        if self.past_limit is not None:
            all_dates[all_dates < self.past_limit] = self.past_limit

        if self.future_limit is not None:
            all_dates[all_dates > self.future_limit] = self.future_limit

        return all_dates

