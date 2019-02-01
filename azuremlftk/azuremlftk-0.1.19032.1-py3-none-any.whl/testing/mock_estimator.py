from sklearn.base import BaseEstimator

class MockEstimator(BaseEstimator):
    """
    The mock class created to test the pipelines
    
    :param return_sum: If true return the sum of all values in all columns, otherwise return the same data frame.
                       on predict.
    :type return_sum: bool
    
    """
    def __init__(self, return_sum:bool=True):
        """
        Conctructor
        
        """
        self._return_sum = return_sum
        
    def fit(self, X, y):
        """
          :param X: unused.
          :param y: unused.
          :returns: The fit object.
          :rtype: MockEstimator
          
        """
        return self
    
    def transform(self, X):
        """
          Just return the DataFrame as is.
        
          :param X: DataFrame to transform.
          :type X: DataFrame
          :returns: X
          :rtype: DataFrame
          
        """
        return X
    
    def predict(self, X, **kwargs):
        """
          :param X: DataFrame
          :returns: The sum of all the values.
          :rtype: float64 or DataFrame
          
        """
        if self._return_sum:
            return X.values.sum()
        return X
    