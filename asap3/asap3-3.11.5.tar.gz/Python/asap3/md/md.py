"""Molecular Dynamics."""

import numpy as np

try:
    from ase.optimize.optimize import Dynamics
except ImportError:
    # Fallback to old placement
    from ase.optimize import Dynamics
from ase.data import atomic_masses
from ase.md import MDLogger

_counter = 0  # Prevents identical prefixes


class ParallelMolDynMixin:
    def __init__(self, prefix, atoms):
        global _counter
        self.prefix = prefix+str(_counter)+"_"
        _counter += 1
        self._uselocaldata = not getattr(atoms, "parallel", False)
        self._localdata = {}
        
    def set(self, name, var):
        """Set a local variable.

        If the local variable is a scalar, it is stored locally.  If
        it is an array it is stored on the atoms.  This allows for
        parallel Asap simulations, where such arrays will have to
        migrate among processors along with all other data for the
        atoms.
        """
        if self._uselocaldata or getattr(var, "shape", ()) == ():
            self._localdata[name] = var
        else:
            if name in self._localdata:
                del self._localdata[name]
            self.atoms.set_array(self.prefix+name, var)

    def get(self, name):
        try:
            return self._localdata[name]
        except KeyError:
            return self.atoms.get_array(self.prefix+name, copy=False)
