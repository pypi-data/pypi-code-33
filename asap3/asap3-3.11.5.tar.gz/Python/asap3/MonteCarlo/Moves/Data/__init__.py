from __future__ import absolute_import
from ase.data import atomic_numbers, chemical_symbols, reference_states
from ase.units import *

from . import fcc

lattice = {'fcc': fcc.data,
          }

