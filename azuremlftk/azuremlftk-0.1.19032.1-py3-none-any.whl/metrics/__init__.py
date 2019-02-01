"""
Classes and functions related to time series forecasting evalution metrics.
"""

from ftk.metrics.metrics import calc_mape, calc_mae, calc_rmse, calc_smape, \
    calc_mase_single_grain
from ftk.metrics.scorer import make_forecast_scorer