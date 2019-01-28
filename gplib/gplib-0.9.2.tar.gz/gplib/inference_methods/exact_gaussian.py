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

from .inference_method import InferenceMethod
from ..gaussian_process import GaussianProcess


class ExactGaussian(InferenceMethod):
    """

    """

    def marginalize_gp(self, data):
        """ Get mean and covariance of following points """

        # Data assertions
        assert len(data['X']) == len(data['Y']), "Data is not consistent"
        assert not np.isnan(data['X']).any(), "NaN values in data['X']"
        assert not np.isinf(data['X']).any(), "Inf values in data['X']"
        assert not np.isnan(data['Y']).any(), "NaN values in data['Y']"
        assert not np.isinf(data['Y']).any(), "Inf values in data['Y']"

        mean = self.gp.mean_function.marginalize_mean(data['X'])
        covariance = self.gp.covariance_function.marginalize_covariance(
            data['X'])
        l_matrix = GaussianProcess.safe_chol(covariance)
        alpha = scipy.linalg.cho_solve((l_matrix, True), data['Y'] - mean)

        marginal = {
            'mean': mean,
            'l_matrix': l_matrix,
            'alpha': alpha
        }

        return marginal

    def loocv(self, data):
        """

        :param data:
        :type data:
        :return:
        :rtype:
        """
        covariance = self.gp.covariance_function.marginalize_covariance(
            data['X']
        )
        l_matrix = GaussianProcess.safe_chol(covariance)

        inv_cov = scipy.linalg.cho_solve(
            (l_matrix, True),
            np.eye(l_matrix.shape[0])
        )

        diag_inv_cov = np.diagonal(inv_cov)[:, None]

        mean = data['Y'] - \
               np.divide(np.dot(inv_cov, data['Y']), diag_inv_cov)

        var = np.divide(1.0, diag_inv_cov)

        return mean, var
