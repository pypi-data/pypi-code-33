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

import scipy.linalg

from ..parameters import WithParameters


class CovarianceFunction(WithParameters):
    """

    """
    def __init__(self, hyperparams):

        super(CovarianceFunction, self).__init__(hyperparams)

    def __copy__(self):

        copyed_object = self.__class__()

        copyed_object.set_hyperparams(self.get_hyperparams())

        return copyed_object

    def marginalize_covariance(self, mat_a, mat_b=None,
                               only_diagonal=False,
                               dk_dx_needed=False,
                               dk_dtheta_needed=False,
                               trans=False):
        """
        Measures the distance matrix between solutions of A and B, and
        applies the kernel function element-wise to the distance matrix.

        :param mat_a: List of solutions in lines and dimensions in columns.
        :type mat_a:
        :param mat_b: List of solutions in lines and dimensions in columns.
        :type mat_b:
        :param only_diagonal:
        :type only_diagonal:
        :param dk_dx_needed: It should be true if the derivative in x is needed.
        :type dk_dx_needed:
        :param trans:
        :type trans:
        :param dk_dtheta_needed: It should be true if the derivative in
            theta is needed.
        :type dk_dtheta_needed:
        :return: Result matrix with kernel function applied element-wise.
        :rtype:
        """
        covariance = self.covariance(
            mat_a, mat_b=mat_b, only_diagonal=only_diagonal)

        result = (covariance, )

        if dk_dx_needed:
            dk_dx = self.dk_dx(
                mat_a, mat_b=mat_b)
            result += (dk_dx, )

        if dk_dtheta_needed:
            dk_dtheta = self.dk_dtheta(
                mat_a, mat_b=mat_b, trans=trans)
            result += (dk_dtheta, )

        if len(result) == 1:
            result = result[0]

        return result

    def is_psd(cov, dims=1, items=100, n_data_sets=20):
        """

        :param cov:
        :type cov:
        :param items:
        :type items:
        :param n_data_sets:
        :type n_data_sets:
        :return:
        :rtype:
        """
        cov_is_psd = True
        i_data_set = 0
        while cov_is_psd and i_data_set < n_data_sets:
            data = np.vstack((
                np.zeros(dims),
                np.random.rand(1, dims) * 100 +
                    np.random.randn(int(items / 2.0), dims),
                np.random.rand(int(items / 2.0), dims) * 100
            ))
            cov_matrix = cov.marginalize_covariance(data)
            cov_is_psd = CovarianceFunction.check_psd_matrix(cov_matrix)
            i_data_set += 1

        return cov_is_psd

    @staticmethod
    def check_psd_matrix(cov_matrix):
        """

        :param cov_matrix:
        :type cov_matrix:
        :return:
        :rtype:
        """

        # Non finite values in covariance matrix
        if not np.all(np.isfinite(cov_matrix)):
            return False
        # Negative in the main diagonal of the covariance matrix
        if np.any(np.diagonal(cov_matrix) < 0.0):
            return False
        # Covariance matrix is not symmetric
        if np.any(np.abs(cov_matrix - cov_matrix.T) > 0.001):
            return False
        # Covariance matrix is Noise
        selection = np.logical_not(np.eye(cov_matrix.shape[0], dtype=bool))
        diagless_matrix = cov_matrix[selection]
        if (np.max(diagless_matrix) - np.min(diagless_matrix)) < 0.001:
            return False

        l_mat, error = scipy.linalg.lapack.dpotrf(
            np.ascontiguousarray(
                cov_matrix + 1e-10 * np.eye(cov_matrix.shape[0])
            ),
            lower=1
        )
        if error != 0:
            return False

        # L*L' != M
        if np.max(cov_matrix - np.dot(l_mat, l_mat.T)) > 0.001:
            return False

        return True

    def covariance(self, mat_a, mat_b=None, only_diagonal=False):
        """
        Measures the distance matrix between solutions of A and B, and
        applies the kernel function element-wise to the distance matrix.

        :param mat_a: List of solutions in lines and dimensions in columns.
        :type mat_a:
        :param mat_b: List of solutions in lines and dimensions in columns.
        :type mat_b:
        :param only_diagonal:
        :type only_diagonal:
        :return: Result matrix with kernel function applied element-wise.
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def dk_dx(self, mat_a, mat_b=None):
        """
        Measures gradient of the distance between solutions of A and B in X.

        :param mat_a: List of solutions in lines and dimensions in columns.
        :type mat_a:
        :param mat_b: List of solutions in lines and dimensions in columns.
        :type mat_b:
        :return: 3D array with the gradient in every dimension of X.
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def dk_dtheta(self, mat_a, mat_b=None, trans=False):
        """
        Measures gradient of the distance between solutions of A and B in the
        hyper-parameter space.

        :param mat_a: List of solutions in lines and dimensions in columns.
        :type mat_a:
        :param mat_b: List of solutions in lines and dimensions in columns.
        :type mat_b:
        :param trans: Return results in the transformed space.
        :type trans:
        :return: 3D array with the gradient in every
         dimension the length-scale hyper-parameter space.
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")
