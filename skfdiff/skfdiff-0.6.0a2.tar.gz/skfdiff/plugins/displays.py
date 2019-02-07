#!/usr/bin/env python
# coding=utf-8

import logging
import warnings
from collections import deque, defaultdict
from uuid import uuid4
from typing import Sequence, Tuple, Optional, Dict
from functools import partial

from holoviews import Curve, DynamicMap, Image, Layout, streams
from path import Path  # noqa

from ..core.simulation import Simulation

log = logging.getLogger(__name__)
log.handlers = []
log.addHandler(logging.NullHandler())


class Display:
    def __init__(self, skel_data, plot_function):

        self.on_disk = None
        self._plot_pipe = streams.Pipe(data=skel_data)
        self._dynmap = DynamicMap(plot_function, streams=[self._plot_pipe])
        self._writers = []

    def _repr_mimebundle_(self, *args, **kwargs):
        return self.hv_curve._repr_mimebundle_(*args, **kwargs)

    def connect(self, stream, n=1):
        stream.partition(n).pluck(-1).sink(self._plot_pipe.send)

    @property
    def hv_curve(self):
        return self._dynmap.collate()

    def show(self):
        return self.hv_curve

    def __add__(self, other):
        if isinstance(other, Display):
            return self._dynmap + other._dynmap
        return self._dynmap + other

    def __mul__(self, other):
        if isinstance(other, Display):
            return self._dynmap * other._dynmap
        self._dynmap * other

    @staticmethod
    def display_fields(
        simul: Simulation, keys="all", n=1, dim_allowed=(0, 1, 2), plot_parameters=False
    ):
        _0D_history: Dict[str, Sequence[Tuple[float, float]]] = defaultdict(list)

        def plot_function(keys, _0D_history, data):
            curves = {"0D": [], "1D": [], "2D": []}
            keys = data.fields.data_vars if keys == "all" else keys
            keys = keys if not isinstance(keys, str) else [keys]
            if not plot_parameters:
                parameters = [par.name for par in simul.model.pdesys.parameters]
                keys = set(keys).difference(parameters)

            for var in keys:
                displayed_field = data.fields[var]
                if 0 in dim_allowed and len(displayed_field.dims) == 0:
                    _0D_history[var].append((simul.t, float(data.fields[var])))
                    curve = Curve(_0D_history[var], kdims="t", vdims=var, label=var)
                    curves["0D"].append(curve)

                if 1 in dim_allowed and len(displayed_field.dims) == 1:
                    curves["1D"].append(Curve((displayed_field.squeeze()), label=var))
                elif 2 in dim_allowed and len(displayed_field.dims) == 2:
                    curves["2D"].append(Image((displayed_field.squeeze()), label=var))
                else:
                    continue
            return Layout(curves["0D"]) + Layout(curves["1D"]) + Layout(curves["2D"])

        display = Display(simul, partial(plot_function, keys, _0D_history))
        display.cols = display.hv_curve.cols
        display.connect(simul.stream, n)
        return display

    @staticmethod
    def display_probe(simul, function, xlabel=None, ylabel=None, buffer=None, n=1):
        history = deque([], buffer)
        if not xlabel:
            xlabel = str(uuid4())[:6]
        if not ylabel:
            ylabel = function.__name__
        if ylabel == "<lambda>":
            warnings.warn(
                "Anonymous function used, appending random prefix "
                "to avoid label confusion"
            )
            ylabel += str(uuid4())[:8]

        def plot_function(data):
            history.append(function(simul))
            return Curve(history, kdims=xlabel, vdims=ylabel)

        display = Display(simul, plot_function)
        display.connect(simul.stream, n)
        return display
