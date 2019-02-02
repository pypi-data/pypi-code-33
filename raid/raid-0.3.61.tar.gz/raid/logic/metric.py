# -*- coding: utf-8 -*-

"""
Use this to track training session progress.
"""

from typing import List
import numpy as np

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class Metric:
    def __init__(self, title: str="loss", capacity: int=100):
        self.title: str = title
        self._capacity: int = capacity
        self._short_history: List[float] = []
        self._aggregate_history: List[float] = []

    def add_short(self, value: float):
        """ Add a new value to the history of this metric, """
        self._short_history.append(value)

        # Keep the list within capacity.
        if 0 < self._capacity < len(self.short_history):
            self._short_history = self._short_history[1:]

    def add_fixed(self, value: float):
        """ Add a new value to the history of this metric, """
        self._aggregate_history.append(value)

    def aggregate(self) -> float:
        """ This will take the average of the current history"""
        # Add the rolling average.
        value = float(np.mean(self._short_history))
        self.add_fixed(value)
        return value

    # ===================================================================================================
    # Read Only.
    # ===================================================================================================

    @property
    def capacity(self):
        return self._capacity

    @property
    def short_history(self):
        return self._short_history

    @property
    def aggregate_history(self):
        return self._aggregate_history

    # @property
    # def max_value(self) -> float:
    #     return float(np.max(self._short_history))
    #
    # @property
    # def min_value(self) -> float:
    #     return float(np.min(self._short_history))
