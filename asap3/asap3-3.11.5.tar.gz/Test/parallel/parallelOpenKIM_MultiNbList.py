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
from asap3.mpi import world

print_version(1)

verbose = False

model = 'ex_model_Ar_SLJ_MultiCutoff'   # Requires multiple neighbor lists.
sizes = [(25,25,25)]

if world.size == 1:
    cpulayout = None
elif world.size == 2:
    cpulayout = [2,1,1]
elif world.size == 3:
    cpulayout = [1,3,1]
elif world.size == 4:
    cpulayout = [2,1,2]
    
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
    ismaster = world.rank == 0
    for size in sizes:
        if ismaster:
            atoms = bulk('Ar', 'fcc', 5.26).repeat(size)
        else:
            atoms = None
        atoms = MakeParallelAtoms(atoms, cpulayout)
        calc = OpenKIMcalculator(model)   # Reuse of OpenKIM objects not yet supported.
        atoms.set_calculator(calc)

        e = atoms.get_potential_energy()/atoms.get_number_of_atoms()
        if ismaster:
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
        v_cell = v0 * 4 / atoms.get_number_of_atoms()
        a0 = v_cell**(1/3)
        if ismaster:
            print("Lattice constant:", a0)
            print("Bulk modulus:", B)
        ReportTest("Lattice constant {}".format(str(size)), a0, 5.26, 1e-5)
        
