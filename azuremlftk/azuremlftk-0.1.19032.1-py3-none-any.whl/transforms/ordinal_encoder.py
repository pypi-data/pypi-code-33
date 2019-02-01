"""
Encode categorical features as numbers from 0 to N.
"""

import numpy as np
import pandas as pd
from warnings import warn

from ftk import verify
from ftk.base_estimator import AzureMLForecastTransformerBase, loggable
from ftk.exception import EstimatorTypeException, EstimatorValueException


class OrdinalEncoder(AzureMLForecastTransformerBase):
    """

    .. _sklearn.prepreprocessing.LabelEncoder: http://scikit-learn.org/stable/
                    modules/generated/sklearn.preprocessing.LabelEncoder.html

    This transform encodes Data Frame columns in an ordinal representation.

    For each column, it maps the column values into the natural numbers,
    `X[<column>] -> {0, 1, ..., N_distinct - 1}`,
    where N_distinct is the number of unique values in the column.
    Missing values will be coded with the value returned by OrdinalEncoder.na_code().

    Internally, the transform uses pandas Categorical codes.

    :param cols:
        Columns to encode into ordinal representations.
        Default is to encode any column with `dtype="object."`
    :type cols: list, str

    """

    @classmethod
    def na_code(cls):
        """
        Integer code corresponding to a missing value
        """
        return pd.Categorical(np.nan).codes[0]

    def __init__(self, cols=None):

       self.cols = cols

    @property
    def cols(self):
        """
        Names of columns to encode.
        """
        return self._cols
        
    @cols.setter
    def cols(self, vals):
        if verify.is_iterable_but_not_string(vals):
           if all(isinstance(c, str) for c in vals):
               # Cast to set to remove duplicates
               self._cols = list(set(vals))
           else:
               raise EstimatorTypeException(
                    'column names must all be strings.')

        elif isinstance(vals, str):
            self._cols = [vals]

        elif vals is None:
            self._cols = None

        else:
           raise EstimatorTypeException(
                    'column names can be None, a string, '\
                        + 'or an iterable containing strings')

    @loggable
    def fit(self, X, y=None):
       """
       Fit encoders for requested columns

       :param X: Input data
       :type X: pandas.DataFrame
       :param y: Ignored. Necessary for pipeline compatibility
       :returns: fitted transform
       :rtype: OrdinalEncoder

       """

       # Filter out columns that aren't in X
       self._fit_cols = [col for col in self._cols
                         if col in X.columns]
       
       self._categories_by_col = {col: pd.Categorical(X[col]).categories
                                  for col in self._fit_cols}

       return self

    @loggable
    def transform(self, X, y=None):
       """
       Transform requested columns via the encoder

       :param X: Input data
       :type X: pandas.DataFrame
       :param y: Ignored. Necessary for pipeline compatibility
       :returns: Encoded data
       :rtype: pandas.DataFrame
       """

       # Check if X categoricals have categories not present at fit
       # If so, warn that they will be coded as NAs 
       for col in self._fit_cols:
           now_cats = pd.Categorical(X[col]).categories
           fit_cats = self._categories_by_col[col]
           new_cats = set(now_cats) - set(fit_cats)
           if len(new_cats) > 0:
               warn(
                    ('OrdinalEncoder.transform: Column {0} contains '\
                    + 'categories not present at fit: {1}. '\
                    + 'These categories will be set to NA prior to encoding.').
                    format(col, new_cats))

       # Get integer codes according to the categories found during fit 
       assign_dict = {col: 
                      pd.Categorical(X[col], 
                                     categories=self._categories_by_col[col])
                      .codes
                      for col in self._fit_cols}

       return X.assign(**assign_dict)







