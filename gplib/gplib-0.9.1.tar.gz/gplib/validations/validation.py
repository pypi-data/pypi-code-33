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

class Validation(object):
    """

    """
    def get_folds(self, data_set):
        """

        :param data_set:
        :type data_set:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    @staticmethod
    def split_data_set(data_set, order, cut1, cut2):
        """

        :param data_set:
        :type data_set:
        :param order:
        :type order:
        :param cut1:
        :type cut1:
        :param cut2:
        :type cut2:
        :return:
        :rtype:
        """

        train_slice1 = slice(None, cut1, None)
        test_slice = slice(cut1, cut2, None)
        train_slice2 = slice(cut2, None, None)
        train_selection = order[train_slice1] + order[train_slice2]
        test_selection = order[test_slice]

        train_set = {
            name: element[train_selection, :]
            for name, element in data_set.items()
        }

        test_set = {
            name: element[test_selection, :]
            for name, element in data_set.items()
        }

        return train_set, test_set
