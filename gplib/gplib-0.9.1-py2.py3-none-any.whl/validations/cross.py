# -*- coding: utf-8 -*-
#
#    Copyright 2019 Ibai Roman
#
#    This file is part of GPlib.
#
#    GPlib is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    GPlib is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with GPlib. If not, see <http://www.gnu.org/licenses/>.

import numpy as np

from .validation import Validation

class Cross(Validation):
    """

    """
    def __init__(self, n_folds):
        self.n_folds = n_folds

    def get_folds(self, data_set):
        """

        :param data_set:
        :type data_set:
        :return:
        :rtype:
        """
        folds_n = list(range(self.n_folds))
        n = data_set['X'].shape[0]
        order = list(np.random.permutation(n))

        folds = []
        for fold_i in folds_n:
            rel_fold_len = int(np.ceil(float(n) / self.n_folds))
            cut1 = rel_fold_len * fold_i
            cut2 = rel_fold_len * (fold_i + 1)
            folds.append(
                Validation.split_data_set(
                    data_set, order, cut1, cut2
                )
            )

        return folds
