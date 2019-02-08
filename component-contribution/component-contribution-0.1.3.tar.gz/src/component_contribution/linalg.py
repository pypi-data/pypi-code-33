# The MIT License (MIT)
#
# Copyright (c) 2018 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from typing import Tuple

import numpy as np
from numpy.linalg import pinv
from scipy.linalg import svd


class LINALG(object):

    @staticmethod
    def _invert_project(A: np.array, eps: float = 1e-10
                        ) -> Tuple[np.array, float, np.array, np.array]:
        M, N = A.shape

        U, s, Vh = svd(A,
                       full_matrices=True,
                       compute_uv=True,
                       check_finite=True,
                       lapack_driver='gesvd')

        assert U.shape == (M, M), "SVD decomposition dimensions are wrong"
        assert Vh.shape == (N, N), "SVD decomposition dimensions are wrong"

        S = np.zeros((M, N))
        np.fill_diagonal(S, s)
        inv_A = Vh.T @ pinv(S) @ U.T

        r = (S > eps).sum()
        P_R   = U[:, :r] @ U[:, :r].T
        P_N   = U[:, r:] @ U[:, r:].T

        assert inv_A.shape == (N, M), "Pseudoinverse dimensions are wrong"
        assert P_R.shape == (M, M), "Orthogonal projection dimensions are wrong"
        assert P_N.shape == (M, M), "Orthogonal projection dimensions are wrong"

        return inv_A, r, P_R, P_N

    @staticmethod
    def _row_uniq(A: np.array) -> Tuple[np.array, np.array]:
        """
            A procedure usually performed before linear regression (i.e. solving Ax = y).
            If the matrix A contains repeating rows, it is advisable to combine
            all of them to one row, and the observed value corresponding to that
            row will be the average of the original observations.

            Input:
                A - a 2D NumPy array

            Returns:
                A_unique, P_row

                where A_unique has the same number of columns as A, but with
                unique rows.
                P_row is a matrix that can be used to map the original rows
                to the ones in A_unique (all values in P_row are 0 or 1).
        """
        # convert the rows of A into tuples so we can compare them
        A_tuples = [tuple(A[i,:].flat) for i in range(A.shape[0])]
        A_unique = list(sorted(set(A_tuples), reverse=True))

        # create the projection matrix that maps the rows in A to rows in
        # A_unique
        P_col = np.zeros((len(A_unique), len(A_tuples)), dtype=float)

        for j, tup in enumerate(A_tuples):
            # find the indices of the unique row in A_unique which correspond
            # to this original row in A (represented as 'tup')
            i = A_unique.index(tup)
            P_col[i, j] = 1.0

        return np.array(A_unique, ndmin=2), P_col

    @staticmethod
    def _col_uniq(A: np.array) -> Tuple[np.array, np.array]:
        A_unique, P_col = LINALG._row_uniq(A.T)
        return A_unique.T, P_col.T
