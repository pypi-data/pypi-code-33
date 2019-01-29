import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class TS(BaseEstimator, TransformerMixin):
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


