# -*- coding: utf-8 -*-

# Copyright © 2018, Institut Pasteur
#   Contributor: François Laurent

# This file is part of the TRamWAy software available at
# "https://github.com/DecBayComp/TRamWAy" and is distributed under
# the terms of the CeCILL license as circulated at the following URL
# "http://www.cecill.info/licenses.en.html".

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.


from tramway.inference.base import smooth_infer_init
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from collections import OrderedDict
from copy import copy



def extract_snr(cells, maps, **kwargs):
    # initial values and common calculations
    index, reverse_index, n, _, _, _, _ = smooth_infer_init(cells)
    index = np.asarray(index)
    nnz = 1 < n
    D = maps['diffusivity']
    # compute diffusivity gradient g (defined at cells `g_index`)
    g_index, g = [], []
    g_defined = np.zeros(len(index), dtype=bool)
    for j, i in enumerate(index):
        gradD = cells.grad(i, D, reverse_index)
        if gradD is not None and nnz[j]:
            # the nnz condition does not prevent the gradient to be defined
            # but such cases are excluded anyway in the calculation of zeta_spurious
            g_defined[j] = True
            g_index.append(i)
            g.append(gradD[np.newaxis,:])
    g = np.concatenate(g, axis=0)
    # compute mean displacement m and variances V and V_prior (defined at cells `index`)
    sum_pts  = lambda a: np.sum(a, axis=0, keepdims=True)
    sum_dims = lambda a: np.sum(a, axis=1, keepdims=True)
    m, dts, dr, dr2 = [], [], [], []
    for i in index:
        cell = cells[i]
        m.append(np.mean(cell.dr, axis=0, keepdims=True))
        dr.append(sum_pts(cell.dr))
        dr2.append(sum_pts(cell.dr * cell.dr))
        dts.append(cell.dt)
    m   = np.concatenate(m, axis=0)
    dts = np.concatenate(dts)
    n   = n[:,np.newaxis]
    dr  = np.concatenate(dr, axis=0)
    dr2 = np.concatenate(dr2, axis=0)
    V   = sum_dims(dr2 - dr * dr / n) / n #(n - 1)
    n_prior   = np.sum(n)    - n
    dr_prior  = sum_pts(dr)  - dr
    dr2_prior = sum_pts(dr2) - dr2
    V_prior   = sum_dims(dr2_prior - dr_prior * dr_prior / n_prior) / n_prior #(n_prior - 1)
    # compute zeta_total (defined at cells `index`) and zeta_spurious (defined at cells `g_index`)
    sd = np.sqrt(V)
    zeta_total = m / sd
    dt = np.median(dts)
    zeta_spurious = g * dt / sd[g_defined]
    # format the output
    result = pd.DataFrame(
        np.concatenate((n, dr, dr2), axis=1),
        index=index,
        columns=['n'] + \
            ['dr '+col for col in cells.space_cols] + \
            ['dr2 '+col for col in cells.space_cols],
        )
    result = result.join(pd.DataFrame(
        np.concatenate((V, D[:,np.newaxis], zeta_total), axis=1)[nnz],
        index=index[nnz],
        columns=['V'] + \
            ['diffusivity'] + \
            ['zeta_total '+col for col in cells.space_cols],
        ))
    result = result.join(pd.DataFrame(
        zeta_spurious,
        index=g_index,
        columns=['zeta_spurious '+col for col in cells.space_cols],
        ))
    new_maps = copy(maps)
    new_maps.maps = result
    return new_maps

