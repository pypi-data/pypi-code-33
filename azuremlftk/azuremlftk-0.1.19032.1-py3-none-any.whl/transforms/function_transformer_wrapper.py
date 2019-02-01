from sklearn.base import TransformerMixin

class FunctionTransformerWrapper(TransformerMixin):
    """
    .. py::class: FunctionTransformerWrapper
    
      FunctionTransformerWrapper wraps the function to be called in AzureMLForecastPipeline for 
      simple modifications of pandas data frames.
      
    """
    _WrongFunctionError = "The function func should accept a"
    def __init__(self, func, *args, **kwargs):
        """Constructor.
          :param func: the function to be applied to the data frame. The function should accept DataFrame as a parameter and return DataFrame.
          :type func: function.
           
        """
        if not callable(func):
            raise TypeError('func should be of a function type.')
        if func.__code__.co_argcount < 1:
            raise TypeError('func should accept at least one argument.')
        self._function = func
        
    def transform(self, X):
        """
        .. py::method: transforms(X)
        
          Apply the function to data frame.
        
          :param X: data frame to be fitted
          :type X: DataFrame.
          :returns: the transformed DataFrame.
          :rtype: DataFrame.
          
        """
        return self._function(X)
    
    def fit(self, X, y=None):
        """
        .. py::method: fit(X, y=None)
        
          Present to implement the TransformerMixin interface, nothing needs to be done here.
        
          :param X: data frame to be fitted
          :type X: DataFrame.
          :param y: fitting parameter.
          :type y: str.
          :returns: The fitted FunctionTransformerWrapper.
          :rtype: FunctionTransformerWrapper.
          
        """
        return self
    
    def fit_transform(self, X, y=None):
        """
        .. py::method: fit_transform(X, y=None)
        
          Apply the function to data frame.
        
          :param X: data frame to be fitted
          :type X: DataFrame.
          :param y: fitting parameter.
          :type y: str.
          :returns: The fitted FunctionTransformerWrapper.
          :rtype: FunctionTransformerWrapper.
          
        """
        return self.transform(X)
    
    def predict(self, X, **fit_params):
        """
        .. py::method: predict(X, **fit_params)
        
          This method is not applicable to the function wrapper, rise an exception.
        
          :param X: Unused
          :type X: data frame.
          :rises: NotImplementedError
        
        """
        raise NotImplementedError('The predicting function is not applicable to function wrapper.')
    
        
    def fit_predict(self, *args, **kwargs):
        """
        .. py::method: fit_predict(*args, **kwargs)
        
          This method is not applicable to the function wrapper, rise an exception.
        
          :rises: NotImplementedError
          
        """
        raise NotImplementedError('The predicting function is not applicable to function wrapper.')
    
    def predict_proba(self, *args, **kwargs):
        """
        .. py::method: predict_proba(*args, **kwargs)
        
          This method is not applicable to the function wrapper, rise an exception.
        
          :rises: NotImplementedError
          
        """
        raise NotImplementedError('The predict_proba function is not applicable to function wrapper.')
    
    def predict_log_proba(self, *args, **kwargs):
        """
        .. py::method: predict_log_proba(*args, **kwargs)
        
          This method is not applicable to the function wrapper, rise an exception.
        
          :rises: NotImplementedError
          
        """
        raise NotImplementedError('The predict_log_proba function is not applicable to function wrapper.')
    
    def decision_function(self, *args, **kwargs):
        """
        .. py::method: decision_function(*args, **kwargs)
        
          This method is not applicable to the function wrapper, rise an exception.
        
          :rises: NotImplementedError
          
        """
        raise NotImplementedError('The decision_function function is not applicable to function wrapper.')
    
    def score(self, *args, **kwargs):
        """.. py::method: score(*args, **kwargs)
        
          This method is not applicable to the function wrapper, rise an exception.
        
          :rises: NotImplementedError
          
        """
        raise NotImplementedError('The score function is not applicable to function wrapper.')