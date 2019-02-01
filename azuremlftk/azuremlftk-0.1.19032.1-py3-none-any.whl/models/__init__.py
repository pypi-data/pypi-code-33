"""
Package for all time series forecasting models. 

Recursive forecasters (that can apply a short-horizon model equation 
recursively to get longer-horizon forecasts) 
inherit from :class:`ftk.models.recursiveforecaster.RecursiveForecaster`.
Machine-learning based models that plug in a regression forecaster after 
featurization steps can be made with 
:class:`ftk.models.regressionforecaster.RegressionForecaster`.
More generally, any scikit-compatible estimator can be wrapped in 
:class:`ftk.models.sklearnestimatorwrapper.SklearnEstimatorWrapper`.
"""

from .arima import Arima
from .naive import SeasonalNaive, Naive
from .exponential_smoothing import ExponentialSmoothing
from .recursive_forecaster import RecursiveForecaster
from .regression_forecaster import RegressionForecaster
from .sklearn_estimator_wrapper import SklearnEstimatorWrapper
from .forecaster_union import ForecasterUnion
from .best_of_forecaster import BestOfForecaster
from .deep_models import DeepLinearForecaster, TCNForecaster

