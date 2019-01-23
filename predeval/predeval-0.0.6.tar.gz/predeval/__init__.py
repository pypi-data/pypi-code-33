# -*- coding: utf-8 -*-

"""Top-level package for predeval."""

__author__ = """Dan Vatterott"""
__email__ = 'dvatterott@gmail.com'
__version__ = '0.0.6'

from .continuous import ContinuousEvaluator
from .categorical import CategoricalEvaluator
from .utilities import evaluate_tests

__all__ = ['ContinuousEvaluator',
           'CategoricalEvaluator',
           'evaluate_tests']
