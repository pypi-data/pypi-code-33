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

class Unfold(Validation):
    """

    """
    def __init__(self, fold_len):
        self.fold_len = fold_len

    def get_folds(self, data_set):
        """

        :param data_set:
        :type data_set:
        :return:
        :rtype:
        """

        n = data_set['X'].shape[0]
        order = list(range(n))
        rel_fold_len = int(np.ceil(float(n) * self.fold_len))
        cut1 = n - rel_fold_len
        cut2 = n
        folds = [
            Validation.split_data_set(
                data_set, order, cut1, cut2
            )
        ]

        return folds