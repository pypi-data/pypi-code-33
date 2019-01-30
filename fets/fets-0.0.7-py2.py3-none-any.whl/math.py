import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class TSPolynomialAB(BaseEstimator, TransformerMixin):
    """Transforms a normalized series
       into polynomial function y = (1 - x^a)^b
    """
    def __init__(self, power_a=2, power_b=2):
        self.power_a = power_a
        self.power_b = power_b

    def fit(self, X, y=None):
        return self

    def transform(self, input_s):
       return (1 - (1- input_s)**self.power_a)**self.power_b


class TSScale(BaseEstimator, TransformerMixin):
    """
        The series is truncated to min and max interval.
    """
    def __init__(self, bound_min=-1, bound_max=-1, scale_min=0, scale_max=1.0):
        self.bound_min =  bound_min
        self.bound_max =  bound_max
        self.scale_min =  scale_min
        self.scale_max =  scale_max

    def fit(self, X, y=None):
        return self

    def transform(self, input_s):
        if not isinstance(input_s, pd.Series):
            print("Input data is not a pd.Series (TODO throw)")
            return input_s

        # In case bound_min and bound_max were not defined.
        if self.bound_min == -1 and self.bound_max == self.bound_min:
            self.bound_min = input_s.min()
            self.bound_max = input_s.max()

        # Truncating origin data to selected bounds
        input_s[input_s > self.bound_max] = self.bound_max
        input_s[input_s < self.bound_min] = self.bound_min

        # Scale the series to 0;1]
        scaled_s = (input_s - self.bound_min) / (self.bound_max - self.bound_min)
        scaled_s = scaled_s * (self.scale_max - self.scale_min) + self.scale_min

        return scaled_s


class TSInterpolation(BaseEstimator, TransformerMixin):
    """ Interpolate according to a new given index
        linearly with respect to time or number of samples

    """
    def __init__(self, new_index=None, period="5min", method="time"):
        """
            :param new_index: Final desired index
            :param period: Used period if no index is given
            :param method: default is 'time', points will be interpolated wrt
            time. Another possible value is 'linear' wrt to index number.
        """
        self.new_index = new_index 
        self.period = period
        self.method = method

    def fit(self, X, y=None):
        return self

    def transform(self, input_s):
        if not isinstance(input_s, pd.Series):
            print("Input data is not a pd.Series (TODO throw)")
            return input_s
        
        if self.new_index is None:
            # create new index starting and ending as input series
            # with frequency according to indicated period
            self.new_index = pd.date_range(input_s.index[0], input_s.index[-1], freq=self.period)

        output_s = pd.Series(data=[np.nan for i in self.new_index],
                             index=self.new_index)


        # after new step this we'll get a timeseries full of NaN but with
        # the few original points that are going to be interpolated
        output_s = input_s.combine_first(output_s)
        output_s = output_s.interpolate(method=self.method)
        output_s = output_s.reindex(self.new_index, method='nearest')

        return output_s


class TSIntegrale(BaseEstimator, TransformerMixin):
    """ Sum past values in different past periods.
        TODO
    """
    def __init__(self, period="5min", period_offset="", integrate_in_past=True, method="constant"):
        """
            :param period: Used period to sum on
            :param period_offset: Offset time before counting period
            :param integrate_in_past: True to integrate in the past else offset
            and period are used in the future
            :param method: "constant" is a classical integration, "linear"
            linearly decrease weight on integration time period, "invlinear"|"exp"|"square"

            return: itegrated series or dataframe
        """
        self.period = period
        self.period_offset = period_offset
        self.integrate_in_past = integrate_in_past

    def fit(self, X, y=None):
        return self

    def transform(self, input_s):
        if not isinstance(input_s, pd.Series):
            print("Input data is not a pd.Series.")
            return input_s
        
        if self.integrate_in_past == True:
            if self.period_offset == "":
                output_s = input_s.rolling(period=self.period, min_periods=1).sum()
            else:
                output_s = input_s \
                           .shift(period=self.period_offset) \
                           .rolling(period=self.period, min_periods=1).sum()
              

        # TODO
        output_s = None

        return output_s


