# -*- coding: utf8 -*-
import numpy as np


class Phase(object):
    def __init__(self):
        self.metrics = {}

    def add_metric(self, name, value):
        self.metrics[name] = value


class PhaseTest(Phase):
    def __init__(self):
        super(PhaseTest, self).__init__()

        self.y_test = []
        self.y_pred = []
        self.labels = []

    @classmethod
    def _make_list(cls, name, lst):
        if lst is None:
            return lst

        if isinstance(lst, np.ndarray):
            lst = lst.tolist()

        if not isinstance(lst, (tuple, list)):
            raise ValueError('not supported type for %s %s' % (name, lst))

        return lst

    def set_test_data(self, y_test, y_pred, labels=None):
        self.y_test = self._make_list('y_test', y_test)
        self.y_pred = self._make_list('y_pred', y_pred)
        self.labels = self._make_list('labels', labels)
