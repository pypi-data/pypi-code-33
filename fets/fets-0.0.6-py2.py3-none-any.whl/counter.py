import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class TSCount(BaseEstimator, TransformerMixin):
    """ Transforms any numerical or non-numerical series into a series of
    integer representing the count of samples per period.
    """
    def __init__(self, period):
        """
            :param period: period of time for each count bin
        """
        self.period = period

    def fit(self, X, y=None):
        return self

    def transform(self, input_series):
        if not isinstance(input_series, pd.Series):
            print("Input data is not a pd.Series (TODO throw)")
            return input_series

        return input_series.resample(self.period).count()


class TSTimerIncrement(BaseEstimator, TransformerMixin):
    """ Increment between each START-STOP entries

        Input series should look like:
            t1 START
            t2 STOP
            t3 START
            t4 STOP
            ... (2 by 2)
        If the last element is not paired, it will be ignored.
        Values of the series will be ignored. Only the tie is considered.
    """
    def __init__(self, freq, cap=0):
        """
            :param freq: sampling frequency
            :param cap: max number of seconds to cap the increments to.
            if cap <= 0 then it is disabled
        """
        self.freq = freq
        self.cap = cap

    def fit(self, X, y=None):
        return self

    def transform(self, input_series):
        """
        """
        if not isinstance(input_series, pd.Series):
            print("Input type is not correct")
            return input_series

        # --- preparing the output with NaN filled series
        new_index = pd.date_range(input_series.index[0],
                                  input_series.index[-1],
                                  freq=self.freq)
        output_series = pd.Series(np.zeros(new_index.size)*np.nan, index=new_index)

        # --- Calculating timer increments on pairs of entries
        jump = 0
        for k in range(input_series.size-1):
            if jump == 0:
                print(input_series.index[k])
                print(input_series.index[k+1])
                cumul = self.extrapolate(input_series.index[k],
                                         input_series.index[k+1])
                output_series = output_series.combine_first(cumul)
                jump = 1
            else:
                jump = 0

        output_series.fillna(0, inplace=True)
        return output_series

    def extrapolate(self, t_start, t_stop):
        """ Counting the number of minutes enlapsed
            between t_start and t_stop
        """
        new_index = pd.date_range(t_start,
                                  t_stop,
                                  freq=self.freq)

        deltas = new_index - t_start 
        seconds = map(lambda d: (d.days*1440 + d.seconds/60), deltas)
        values = []
        if self.cap > 0:
            values = [x if x <= self.cap else self.cap for x in seconds]
        else:
            values = [x for x in seconds]

        # At t_stop we go back to 0 minutes
        if  len(values) > 0:
            values[-1] = 0

        extra_series = pd.Series(values, index=new_index)
        return extra_series


