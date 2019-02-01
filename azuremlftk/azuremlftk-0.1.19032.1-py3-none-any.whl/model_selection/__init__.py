"""
Classes to use the time-series cross-validation (TS CV) evaluation paradigm
TSCV must respect the time structure of data to provide a valid estimate of generalization error.
"""

from ftk.model_selection.search import TSGridSearchCV, TSRandomizedSearchCV
from ftk.model_selection.cross_validation import RollingOriginValidator