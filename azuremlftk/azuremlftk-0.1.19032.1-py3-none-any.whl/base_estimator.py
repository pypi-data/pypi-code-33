"""
This is a module to be used as a reference for building other modules
"""
from abc import ABCMeta
from sklearn.base import BaseEstimator, RegressorMixin, TransformerMixin
from ftk import TimeSeriesDataFrame
from ftk.constants import *
import warnings

_can_use_core_telemetry = True
try:
    from ftk.time_series_logging import TimeSeriesLogger
except ImportError:
    warnings.warn('Unable to import TimeSeriesLogger. '
                  + 'Logging/Telemetry will be disabled.',
                  UserWarning)
    _can_use_core_telemetry = False

def loggable(fun):
        """
        The function wrapper writing the telemetry information.
        
        :param fun: The function to be wrapped.
        :type fun: function
        
        :returns: the wrapped function.
        :rtype: function
        
        """
        def wrapped_fun(self, X, *args, **kwargs):
            #Send the telemetry information.
            if _can_use_core_telemetry:
                telemetry_values={}
                telemetry_values[TELEMETRY_COMPONENT] = 'forecastingEstimator'
                telemetry_values[TELEMETRY_FUNCION] = fun.__name__
                telemetry_values[TELEMETRY_MODULE] = self.__class__.__module__
                telemetry_values[TELEMETRY_CLASS] = self.__class__.__name__
                telemetry_values[TELEMETRY_PIPELINE_ID] = self.pipeline_id
                telemetry_values[TELEMETRY_RUN_ID] = self.pipeline_run_id
        
                if not X is None:
                    telemetry_values[TELEMETRY_NUM_ROWS] = X.shape[0]
                    if isinstance(X, TimeSeriesDataFrame):
                        telemetry_values[TELEMETRY_TIME_COLUMN] = X.time_colname
                        if X.grain_colnames:
                            telemetry_values[TELEMETRY_GRAIN_COLUMNS] = ', '.join(X.grain_colnames)
                        if X.origin_time_colname:
                            telemetry_values[TELEMETRY_ORIGIN_COLUMN] = X.origin_time_colname
                        if X.ts_value_colname:
                            telemetry_values[TELEMETRY_TARGET_COLUMN] = X.ts_value_colname
                        if X.group_colnames:
                            telemetry_values[TELEMETRY_GROUP_COLUMNS] = ', '.join(X.group_colnames)
                        telemetry_values[TELEMETRY_DATA_COLUMNS] = ', '.join([X.time_colname]+list(X.columns.values))
                for key in dict(kwargs).keys():
                    telemetry_values[key] = str(kwargs[key])
                logger = TimeSeriesLogger()
                logger.log_info("{}.{}.{}".format(self.__class__.__module__, self.__class__.__name__, fun.__name__),
                                "{} started".format(fun.__name__), custom_dimensions=telemetry_values)
            #Run the function.
            return fun(self, X, *args, **kwargs)
            
        return wrapped_fun

class AzureMLForecastEstimatorBase(BaseEstimator, metaclass=ABCMeta):
    """ Base estimator for all AzureMLForecastSDK.

    """
    
    def __init__(self, *args, **kwargs):
        for dictionary in args:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])


    @property
    def pipeline_id(self):
        """
        Get or set the pipeline ID.
        
        :returns: pipeline uuid.
        :rtype: str
        
        """
        if hasattr(self, '_pipeline_id'):
            #Many transformer constructors are defining their own constructors. 
            #We may not have the _pipeline_id defined.
            return self._pipeline_id
        else:
            return "No ID"
    
    @pipeline_id.setter
    def  pipeline_id(self, value):
        """
        Pipeline ID setter.
        """
        self._pipeline_id = value

    @property
    def pipeline_run_id(self):
        """
        Get or set the pipeline run ID.
        
        :returns: pipeline uuid.
        :rtype: str
        
        """
        if hasattr(self, "_run_id"):
            #Many transformer constructors are defining their own constructors. 
            #We may not have the _run_id defined.
            return self._run_id
        else:
            return "No ID"
    
    @pipeline_run_id.setter
    def  pipeline_run_id(self, value):
        """
        Pipeline run ID setter.
        """
        #Many transformer constructors are defining their own constructors. 
        #Make sure that we have the _run_id definbed.
        self._run_id = value        
    
        
    """
    def fit(self, X, y):
        A reference implementation of a fitting function

        Parameters
        ----------
        X : array-like or sparse matrix of shape = [n_samples, n_features]
            The training input samples.
        y : array-like, shape = [n_samples] or [n_samples, n_outputs]
            The target values (class labels in classification, real numbers in
            regression).

        Returns
        -------
        self : object
            Returns self.

        X, y = check_X_y(X, y)
        # Return the estimator
        return self
                

    def predict(self, X):
        A reference implementation of a predicting function.

        Parameters
        ----------
        X : array-like of shape = [n_samples, n_features]
            The input samples.

        Returns
        -------
        y : array of shape = [n_samples]
            Returns :math:`x^2` where :math:`x` is the first column of `X`.
        X = check_array(X)
        return X[:, 0]**2        
        pass
    """

class AzureMLForecastRegressorBase(AzureMLForecastEstimatorBase, RegressorMixin):

    """ Base classifier for AzureMLForecastSDK.

    :param demo_param: str, optional
        A parameter used for demonstation of how to pass and store paramters.

    :Attributes:
    X_ : array, shape = [n_samples, n_features]
        The input passed during :meth:`fit`
    y_ : array, shape = [n_samples]
        The labels passed during :meth:`fit`

    """

class AzureMLForecastTransformerBase(AzureMLForecastEstimatorBase, TransformerMixin):
    """ Base transformer for AzureMLForecastSDK ..

    :param demo_param: str, optional
        A parameter used for demonstation of how to pass and store paramters.

    :Attributes:
    input_shape: tuple
        The shape the data passed to :meth:`fit`

    def fit(self, X, y):
        A reference implementation of a fitting function for a transformer.

        :Parameters:
        X : array-like or sparse matrix of shape = [n_samples, n_features]
            The training input samples.
        y : None
            There is no need of a target in a transformer, yet the pipeline API
            requires this parameter.

        :Returns:
        self: object
            Returns self.

    def transform(self, X):
        A reference implementation of a transform function.

        :Parameters:
        X : array-like of shape = [n_samples, n_features]
            The input samples.

        :Returns:
        X_transformed : array of int of shape = [n_samples, n_features]
            The array containing the element-wise square roots of the values
            in `X`

        # Check is fit had been called
        check_is_fitted(self, ['input_shape_'])

        # Input validation
        X = check_array(X)

        # Check that the input is of the same shape as the one passed
        # during fit.
        if X.shape != self.input_shape_:
            raise ValueError('Shape of input is different from what was seen'
                             'in `fit`')
        return np.sqrt(X)

    """
