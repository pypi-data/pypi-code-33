import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class TSExtractPrefix(BaseEstimator, TransformerMixin):
    """
        Extract samples based on their prefix
    """
    def __init__(self, searches=[]):
        """
            :param searches: string to be searched as a prefix
            :type searches: array of string
        """
        self.searches = searches 
        if not isinstance(searches, list):
            self.searches = [searches]

    def fit(self, x, y=None):
        return self

    def transform(self, input_series):
        if not isinstance(input_series, pd.Series):
            print("Input data is not a pd.Series (TODO throw)")
            return input_series

        idx = np.sort([x
                       for k in self.searches
                       for x in input_series.index[input_series.str.match(r"^"+k+".*")]])

        output_series = input_series[idx]

        # Changing the name of the output series
        output_series.name = str(output_series.name) if output_series.name else "f0"
        for k in self.searches:
            output_series.name += "_"+k

        return output_series


class TSExtractSuffix(BaseEstimator, TransformerMixin):
    """
        Extract samples based on their suffix 
    """
    def __init__(self, searches=[]):
        """
            :param searches: string to be searched as a prefix
            :type searches: array of string
        """
        self.searches = searches
        if not isinstance(searches, list):
            self.searches = [searches]

    def fit(self, x, y=None):
        return self

    def transform(self, input_series):
        """
            :param input_series: pandas series of strings
            :param input_series: pandas.Series
        """
        if not isinstance(input_series, pd.Series):
            print("Input data is not a pd.Series (TODO throw)")
            return input_series

        idx = np.sort([x
                       for k in self.searches
                       for x in input_series.index[input_series.str.match(r".*"+k+"$")]])

        output_series = input_series[idx]

        # Changing the name of the output series
        output_series.name = str(output_series.name) if output_series.name else "f0"
        for k in self.searches:
            output_series.name += "_"+k
        return output_series


class TSExtractText(BaseEstimator, TransformerMixin):
    """
        Extract samples based on a specific text content
        This would include prefix and suffix cases.
    """
    def __init__(self, searches=[]):
        """
            :param searches: string to be searched as a prefix
            :type searches: array of string
        """
        self.searches = searches
        if not isinstance(searches, list):
            self.searches = [searches]

    def fit(self, x, y=None):
        return self

    def transform(self, input_series):
        """
            :param input_series: pandas series of strings
            :param input_series: pandas.Series
        """
        if not isinstance(input_series, pd.Series):
            print("Input data is not a pd.Series (TODO throw)")
            return input_series

        idx = np.sort([x
                       for k in self.searches
                       for x in input_series.index[input_series.str.match(r".*"+k+".*")]])

        output_series = input_series[idx]

        # Changing the name of the output series
        output_series.name = str(output_series.name) if output_series.name else "f0"
        for k in self.searches:
            output_series.name += "_"+k
        return output_series
