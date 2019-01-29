# -*- coding:utf-8 -*-

import numpy as np
from scipy.sparse import csr_matrix


__all__ = ['calc_bilinear_para', 'GridTransformer', 'transform_grid']


def calc_bilinear_para(float_i, float_j, nx=None, ny=None):
    """
    Calculate bilinear interpolate parameter (i, j, weight) for a given position.
    :param float_i: x position (float number)
    :param float_j: y position (float number)
    :param nx: X grid num (for limitation)
    :param ny: Y grid num (for limitation)
    :return: {"i": i_arr, "j": j_arr, "weight": weight_arr}

    The result can be used like this:
    >>> v_interp = np.sum(v_arr[para["j"], para["i"]] * para["weight"])
    """
    ai = float_i % 1
    aj = float_j % 1

    i1 = int(np.floor(float_i))
    i2 = i1 + 1
    j1 = int(np.floor(float_j))
    j2 = j1 + 1

    has_i1 = i1 >= 0
    has_j1 = j1 >= 0
    has_i2 = nx is None or i2 <= nx-1
    has_j2 = ny is None or j2 <= ny-1

    if has_i1 and has_j1:
        if has_i2 and has_j2:
            # has 4 points: (i1, j1), (i2, j1), (i1, j2), (i2, j2)
            i_list = [i1, i2, i1, i2]
            j_list = [j1, j1, j2, j2]
            weight_list = [(1.0-ai)*(1.0-aj), ai*(1.0-aj), (1.0-ai)*aj, ai*aj]
        elif has_i2 and not has_j2:
            # has 2 points: (i1, j1), (i2, j1)
            i_list = [i1, i2]
            j_list = [j1, j1]
            weight_list = [1.0-ai, ai]
        elif not has_i2 and has_j2:
            # has 2 points: (i1, j1), (i1, j2)
            i_list = [i1, i1]
            j_list = [j1, j2]
            weight_list = [1.0-aj, aj]
        else:
            # only 1 point: (i1, j1)
            i_list = [i1]
            j_list = [j1]
            weight_list = [1.0]
    elif has_i1 and not has_j1:
        if has_i2:
            # has 2 points: (i1, j2), (i2, j2)
            i_list = [i1, i2]
            j_list = [j2, j2]
            weight_list = [1.0-ai, ai]
        else:
            # only 1 point: (i1, j2)
            i_list = [i1]
            j_list = [j2]
            weight_list = [1.0]
    elif not has_i1 and has_j1:
        if has_j2:
            # has 2 points: (i2, j1), (i2, j2)
            i_list = [i2, i2]
            j_list = [j1, j2]
            weight_list = [1.0-aj, aj]
        else:
            # only 1 point: (i2, j1)
            i_list = [i2]
            j_list = [j1]
            weight_list = [1.0]
    else:
        # only 1 point: (i2, j2)
        i_list = [i2]
        j_list = [j2]
        weight_list = [1.0]

    return {"i": np.array(i_list), "j": np.array(j_list), "weight": np.array(weight_list)}


class GridTransformer(object):
    def __init__(self, grid1, grid2):
        self.grid1 = grid1
        self.grid2 = grid2
        self.matrix = self.gen_matrix()

    def gen_matrix(self):
        I, J = self.grid1.x2i(self.grid2.X.flatten(), self.grid2.Y.flatten(), int_index=False)
        I1 = np.floor(I).astype('i4')
        I2 = I1 + 1
        J1 = np.floor(J).astype('i4')
        J2 = J1 + 1
        X = I % 1.0
        Y = J % 1.0

        ROW_IND1 = ROW_IND2 = ROW_IND3 = ROW_IND4 = np.arange(self.grid2.nx*self.grid2.ny, dtype='i4')
        WHERE_OUT = (I1 < 0) | (I2 >= self.grid1.nx) | (J1 < 0) | (J2 >= self.grid1.ny)

        COL_IND1 = J1 * self.grid1.nx + I1
        COL_IND2 = J1 * self.grid1.nx + I2
        COL_IND3 = J2 * self.grid1.nx + I1
        COL_IND4 = J2 * self.grid1.nx + I2
        COL_IND1[WHERE_OUT] = 0
        COL_IND2[WHERE_OUT] = 0
        COL_IND3[WHERE_OUT] = 0
        COL_IND4[WHERE_OUT] = 0

        DATA1 = (1.0 - X) * (1.0 - Y)
        DATA2 = X * (1.0 - Y)
        DATA3 = (1.0 - X) * Y
        DATA4 = X * Y
        DATA1[WHERE_OUT] = np.nan
        DATA2[WHERE_OUT] = np.nan
        DATA3[WHERE_OUT] = np.nan
        DATA4[WHERE_OUT] = np.nan

        ROW_IND = np.concatenate((ROW_IND1, ROW_IND2, ROW_IND3, ROW_IND4))
        COL_IND = np.concatenate((COL_IND1, COL_IND2, COL_IND3, COL_IND4))
        DATA = np.concatenate((DATA1, DATA2, DATA3, DATA4))

        matrix = csr_matrix((DATA, (ROW_IND, COL_IND)), shape=(len(I), self.grid1.nx*self.grid1.ny))
        return matrix

    def __call__(self, data):
        data = np.asarray(data)
        return self.matrix.dot(data.flatten()).reshape((self.grid2.ny, self.grid2.nx))


def transform_grid(grid1, grid2, data):
    transformer = GridTransformer(grid1, grid2)
    return transformer(data)