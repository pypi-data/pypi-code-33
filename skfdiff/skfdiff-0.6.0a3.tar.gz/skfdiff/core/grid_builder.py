#!/usr/bin/env python
# coding=utf-8

import logging
from functools import partial
from itertools import accumulate
from tempfile import mkdtemp
from typing import Tuple, Sequence

import attr
import numpy as np
from joblib import Memory
from sympy import Matrix, lambdify
from cachetools import cachedmethod, Cache
from cachetools.keys import hashkey

from .system import PDESys

logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger(__name__)

cachedir = mkdtemp()
memory = Memory(location=cachedir)


def retrieve_cache(key, self):
    try:
        return self._cache[key]
    except KeyError:
        self._cache[key] = Cache(maxsize=128)
        return self._cache[key]


def list_to_tuple_key(*args, **kwargs):
    args = [tuple(arg) if isinstance(arg, list) else arg for arg in args]
    kwargs = {
        key: tuple(value) if isinstance(value, list) else value
        for key, value in kwargs.items()
    }
    key = hashkey(*args, **kwargs)
    return key


class GridBuilder:
    def __init__(self, system: PDESys):
        self.system = system
        self._cache = {}
        self._convert_inputs()
        self._lambda_shapes = [
            lambdify(self.sizes, shape, modules="numpy") for shape in self.shapes
        ]

        # lambdify the size computation for each dep. var. (shape product)
        self._lambda_sizes = [
            lambdify(self.sizes, self.system.sizes[dvar], modules="numpy")
            for dvar in self.system.dependent_variables
        ]

        self._lambda_conds = []

        for sys in self.system._system:
            conds, _ = zip(*sys)
            lambda_cond = lambdify(self.inputs_cond, Matrix(conds), modules=["numpy"])
            self._lambda_conds.append(lambda_cond)

    def _convert_inputs(self):
        self.ndim = len(self.system.independent_variables)
        self.dvars = [dvar.symbol for dvar in self.system.dependent_variables]
        self.sizes = [ivar.N for ivar in self.system.independent_variables]
        self.idxs = [ivar.idx for ivar in self.system.independent_variables]
        self.idxs_map = [
            tuple(
                [
                    self.system.independent_variables.index(ivar)
                    for ivar in dvar.independent_variables
                ]
            )
            for dvar in self.system.dependent_variables
        ]

        self.shapes = [
            self.system.shapes[dvar] for dvar in self.system.dependent_variables
        ]

        self.inputs_cond = [*self.idxs, *self.sizes]

    @cachedmethod(
        cache=partial(retrieve_cache, "build_flat_from_idxs_mapper"),
        key=list_to_tuple_key,
    )
    def build_flat_from_idxs_mapper(self, sizes: Tuple[int]):
        mapper = {}
        gridinfo = self.compute_gridinfo(sizes)
        for row in gridinfo:
            mapper[tuple(row[:-2])] = row[-1]
        return mapper

    @cachedmethod(
        cache=partial(retrieve_cache, "build_idxs_from_flat_mapper"),
        key=list_to_tuple_key,
    )
    def build_idxs_from_flat_mapper(self, sizes: Tuple[int]):
        mapper = {}
        gridinfo = self.compute_gridinfo(sizes)
        for row in gridinfo:
            mapper[int(row[-1])] = row[:-2]
        return mapper

    def compute_flat_from_idxs(self, idxs, sizes: Tuple[int]):
        mapper = self.build_flat_from_idxs_mapper(sizes)
        if np.array(idxs).ndim == 1:
            return mapper[tuple(idxs)]
        else:
            return np.array([mapper[tuple(idx)] for idx in idxs])

    def compute_idxs_from_flat(self, flatindex, sizes: Tuple[int]):
        mapper = self.build_idxs_from_flat_mapper(sizes)
        if np.array(flatindex).ndim == 0:
            return mapper[int(flatindex)]
        else:
            return np.array([mapper[int(idx)] for idx in flatindex])

    def compute_pivot_idx(self, shapes: Tuple[int]):
        if np.alltrue(shapes == shapes[0]):
            return np.arange(self.ndim)
        return np.argsort(np.sum(shapes, axis=0))[::-1]

    @cachedmethod(
        cache=partial(retrieve_cache, "compute_shapes"), key=list_to_tuple_key
    )
    def compute_shapes(self, sizes: Tuple[int]):
        """
        compute the shapes of all the model fields.
        """
        return tuple([lambda_shape(*sizes) for lambda_shape in self._lambda_shapes])

    @cachedmethod(cache=partial(retrieve_cache, "compute_steps"), key=list_to_tuple_key)
    def compute_steps(self, sizes, lenghts):
        """
        compute the stepsize of all the independent variables.
        """
        return tuple([lenght / (size - 1) for lenght, size in zip(lenghts, sizes)])

    @cachedmethod(cache=partial(retrieve_cache, "compute_sizes"), key=list_to_tuple_key)
    def compute_sizes(self, sizes: Tuple[int]):
        """
        compute the sizes of all the model fields.
        """
        return tuple([lambda_size(*sizes) for lambda_size in self._lambda_sizes])

    @cachedmethod(
        cache=partial(retrieve_cache, "compute_indices"), key=list_to_tuple_key
    )
    def compute_indices(self, sizes: Tuple[int]):
        """
        compute grid indices of all the model fields.
        """
        shapes = self.compute_shapes(sizes)
        return [np.indices(np.stack(shape)) for shape in shapes]

    @cachedmethod(
        cache=partial(retrieve_cache, "compute_domains"), key=list_to_tuple_key
    )
    def compute_domains(self, sizes: Tuple[int]):
        """
        compute grid indices of all the model fields.
        """
        indices = self.compute_indices(sizes)
        cursor = 0
        domains = []
        for lambda_cond, indice in zip(self._lambda_conds, indices):
            cond_grid = lambda_cond(*indice, *sizes)
            domain_grid = np.select(
                cond_grid, np.arange(cursor, cursor + cond_grid.shape[0])
            ).squeeze()
            cursor = domain_grid.max() + 1
            domains.append(domain_grid)
        return domains

    @cachedmethod(
        cache=partial(retrieve_cache, "compute_gridinfo"), key=list_to_tuple_key
    )
    def compute_gridinfo(self, sizes: Tuple[int]):
        system_sizes = self.compute_sizes(sizes)
        system_size = sum(system_sizes)
        shapes = self.compute_shapes(sizes)
        indices = self.compute_indices(sizes)
        domains = self.compute_domains(sizes)
        ndim = self.ndim

        pivot_idx = self.compute_pivot_idx(shapes)
        cursors = list(accumulate([0, *system_sizes]))

        dvar_info = np.zeros((system_size,), dtype="int32")
        idxs_info = np.zeros((ndim, system_size), dtype="int32")
        domains_info = np.zeros((system_size,), dtype="int32")

        for i, (cursor, size, indice, domain) in enumerate(
            zip(cursors, system_sizes, indices, domains)
        ):
            dvar_info[cursor : cursor + size] = np.repeat(i, size)
            idxs_info[:, cursor : cursor + size] = indice.reshape((-1, size))
            domains_info[cursor : cursor + size] = domain.flatten()

        full_grid = np.concatenate(
            [idxs_info[pivot_idx, :], dvar_info[None, :]], axis=0
        )

        perm_vector = np.lexsort(full_grid[::-1])

        permuted_idxs_info = idxs_info[:, perm_vector]
        permuted_dvar_info = dvar_info[None, perm_vector]
        permuted_domains_info = domains_info[None, perm_vector]
        flatten_idx = np.arange(system_size, dtype="int32")

        gridinfo = np.concatenate(
            [
                permuted_dvar_info,
                permuted_idxs_info,
                permuted_domains_info,
                flatten_idx[None, :],
            ],
            axis=0,
        ).T

        return gridinfo

    @cachedmethod(
        cache=partial(retrieve_cache, "compute_flat_maps"), key=list_to_tuple_key
    )
    def compute_flat_maps(self, sizes: Tuple[int]):
        shapes = self.compute_shapes(sizes)
        gridinfo = self.compute_gridinfo(sizes)
        flatmaps = [
            np.compress(gridinfo[:, 0] == i, gridinfo[:, -1], axis=0).reshape(shape)
            for i, shape in enumerate(shapes)
        ]
        return flatmaps

    @cachedmethod(
        cache=partial(retrieve_cache, "compute_subgrids"), key=list_to_tuple_key
    )
    def compute_subgrids(self, sizes: Tuple[int]):
        gridinfo = self.compute_gridinfo(sizes)
        domains = sorted(
            set(
                np.concatenate(
                    [domain.flatten() for domain in self.compute_domains(sizes)]
                ).tolist()
            )
        )
        condlists = [gridinfo[:, -2] == i for i in domains]
        subgrids = [np.compress(condlist, gridinfo, axis=0) for condlist in condlists]
        return subgrids

    @cachedmethod(
        cache=partial(retrieve_cache, "compute_flat_to_dvars"), key=list_to_tuple_key
    )
    def compute_flat_to_dvars(self, sizes: Tuple[int]):
        gridinfo = self.compute_gridinfo(sizes)
        idxs_grids = [
            self.compute_flat_from_idxs(
                np.compress(gridinfo[:, 0] == i, gridinfo[:, :-2], axis=0), sizes
            )
            for i in range(len(self.dvars))
        ]

        return idxs_grids

    @cachedmethod(
        cache=partial(retrieve_cache, "compute_dvars_to_flat"), key=list_to_tuple_key
    )
    def compute_dvars_to_flat(self, sizes: Tuple[int]):
        system_sizes = self.compute_sizes(sizes)
        system_size = sum(system_sizes)
        ptrs = self.compute_idxs_from_flat(np.arange(system_size, dtype="int32"), sizes)
        return ptrs

    @cachedmethod(cache=partial(retrieve_cache, "compute_idxs"), key=list_to_tuple_key)
    def compute_idxs(self, sizes: Tuple[int]):
        system_sizes = self.compute_sizes(sizes)
        indices = self.compute_indices(sizes)
        indices = [
            indice.reshape(-1, size) for indice, size in zip(indices, system_sizes)
        ]
        dvar_idx = np.concatenate(
            [np.repeat(i, size) for i, size in enumerate(system_sizes)]
        )
        idxs = np.concatenate(
            [indices[i] for i, size in enumerate(system_sizes)], axis=1
        )
        return np.stack([dvar_idx, *idxs], axis=0)

    @cachedmethod(
        cache=partial(retrieve_cache, "get_relevant_ptrs"), key=list_to_tuple_key
    )
    def get_relevant_ptrs(self, i: int, sizes: Tuple[int]):
        system_sizes = self.compute_sizes(sizes)
        system_size = sum(system_sizes)
        shapeinfos = self.compute_shapes(sizes)
        pivot_idx = self.compute_pivot_idx(shapeinfos)
        idxs = np.arange(system_size)
        ptrs = self.compute_dvars_to_flat(sizes)
        relevant_idxs = np.extract(ptrs[:, 0] == i, idxs)
        relevant_ptrs = ptrs[relevant_idxs, 1:].T[pivot_idx]
        return relevant_idxs, tuple(relevant_ptrs)

    def U_routine(self, dvars, sizes: Tuple[int]):
        system_sizes = self.compute_sizes(sizes)
        system_size = sum(system_sizes)
        U = np.empty(system_size)

        for i, dvar in enumerate(dvars):
            relevant_idxs, relevant_ptrs = self.get_relevant_ptrs(i, sizes)
            U[relevant_idxs] = dvar[relevant_ptrs]
        return U

    def U_from_fields(self, fields, t=0):
        dvars = [
            fields[varname]
            for varname in [dvar.name for dvar in self.system.dependent_variables]
        ]
        sizes = [
            fields[varname].size
            for varname in [ivar.name for ivar in self.system.independent_variables]
        ]
        shapeinfos = self.compute_shapes(sizes)
        pivot_idx = self.compute_pivot_idx(shapeinfos)
        ivars = list(map(str, np.array(self.system.independent_variables)[pivot_idx]))

        dvars = [
            dvar.expand_dims(set(fields.dims).difference(set(dvar.dims)))
            .transpose(*ivars)
            .values
            for dvar in dvars
        ]

        return self.U_routine(dvars, sizes)

    def fields_routine(self, U, sizes: Tuple[int]):
        shapes = self.compute_shapes(sizes)
        idxs_grids = self.compute_flat_to_dvars(sizes)
        pivots = self.compute_pivot_idx(shapes)

        return [
            U[grid].reshape(np.array(shape)[pivots])
            for grid, shape in zip(idxs_grids, shapes)
        ]

    def fields_from_U(self, U, fields, t=None):
        varnames = [dvar.name for dvar in self.system.dependent_variables]
        fields = fields.copy()

        ivars = [
            fields[varname]
            for varname in [ivar.name for ivar in self.system.independent_variables]
        ]
        sizes = [ivar.size for ivar in ivars]
        shapes = self.compute_shapes(sizes)
        pivots = self.compute_pivot_idx(shapes)
        dvars = self.fields_routine(U, sizes)
        sys_ivars = self.system.independent_variables
        for varname, dvar, ivars in zip(
            varnames,
            dvars,
            [dvar.independent_variables for dvar in self.system.dependent_variables],
        ):
            coords = [sys_ivars[i].name for i in pivots if sys_ivars[i] in ivars]
            fields[varname] = coords, dvar.squeeze()
        return fields.transpose(*[ivar.name for ivar in sys_ivars])
