"""
ftk is the top-level package for the AzureML Package for Forecasting. 

When using the Forecasting Package, you build 
:class:`ftk.pipeline.AzureMLForecastingPipeline`s you can then deploy 
into Azure.

The core components of pipelines, familiar from scikit-learn, are 
:mod:`ftk.models` (estimators) and :mod:`ftk.transforms`.

Meta-learning is the concept of selecting the best models and reporting error 
confidence bounds from evaluation. The Forecasting Package provides model and 
parameter sweeps, based on cross-validation, which can be tricky to do 
correctly with time series. The meta-learning classes classes are contained 
in the :mod:`ftk.model_selection` package.

Facilities for deployment (creating Azure web services that forecast) are 
found in the directory named :mod:`ftk.operationalization`.

"""

from .abstract_test_data_provider import AbstractTestDataProvider
from .dominicks_test_data_provider import DominicksTestDataProvider
from .mock_estimator import MockEstimator
from .table_tools import *
from .pipeline_functions import *

# Add __version__ attribute
# this is method 4 of
# https://packaging.python.org/guides/single-sourcing-package-version/
import os
__version_file_loc = os.path.join(os.path.dirname(os.path.realpath(
    os.path.expanduser(__file__))), '..', 'VERSION.txt')
if os.path.exists(__version_file_loc):
    with open(__version_file_loc) as version_file:
        __version__ = version_file.read().strip()
else:
    # Don't fail, don't warn, we are in package init
    print("Could not find VERSION.txt file. Something is quite wrong.")
