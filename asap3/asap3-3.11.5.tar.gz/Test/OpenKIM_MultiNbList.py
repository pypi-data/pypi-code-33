from __future__ import print_function
from __future__ import division
from asap3 import *
import pickle
from numpy import *
from ase.build import bulk
from asap3.testtools import ReportTest
import ase.data
from ase.eos import EquationOfState
import numpy as np

print_version(1)

verbose = False

model = 'ex_model_Ar_SLJ_MultiCutoff'   # Requires multiple neighbor lists.
sizes = [(1,1,1), (2,2,2), (5,5,5)]

if OpenKIMsupported:
    try:
        calc = OpenKIMcalculator(model)
    except AsapError as oops:
        if oops.args[0].startswith('Failed to initialize OpenKIM model'):
            print("OpenKIM model {} not installed - skipping test.".format(model))
            calc = None
        else:
            raise

if OpenKIMsupported and calc is not None:
    for size in sizes:
        atoms = bulk('Ar', 'fcc', 5.26).repeat(size)
        calc = OpenKIMcalculator(model)   # Reuse of OpenKIM objects not yet supported.
        atoms.set_calculator(calc)

        e = atoms.get_potential_energy()/len(atoms)
        print("Potential energy:", e)
        ReportTest("Potential energy {}".format(str(size)), e, -0.0104, 1e-6)

        eq_cell = atoms.get_cell()
        scales = np.linspace(0.99, 1.01, 7)
        energies = []
        volumes = []
        for s in scales:
            atoms.set_cell(s * eq_cell, scale_atoms=True)
            energies.append(atoms.get_potential_energy())
            volumes.append(atoms.get_volume())
        eos = EquationOfState(volumes, energies)
        v0, e0, B = eos.fit()
        v_cell = v0 * 4 / len(atoms)
        a0 = v_cell**(1/3)
        print("Lattice constant:", a0)
        print("Bulk modulus:", B)
        ReportTest("Lattice constant {}".format(str(size)), a0, 5.26, 1e-5)
        
