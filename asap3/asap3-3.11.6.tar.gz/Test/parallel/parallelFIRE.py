"""Test local crystal structure analysis (CNA and Coordination number)."""
from __future__ import print_function


#from asap3.analysis.localstructure import RestrictedCNA, CoordinationNumbers, FullCNA
from asap3 import *
from asap3.testtools import ReportTest
from asap3.mpi import world
from asap3.analysis.localstructure import RestrictedCNA, CoordinationNumbers

from asap3.optimize.fire import FIRE
from ase.lattice import bulk
import numpy as np

ismaster = world.rank == 0
isparallel = world.size != 1
cpulayout = [1, 1, world.size]
#set_verbose(1)

if ismaster:
    atoms = bulk('Cu')
    atoms = atoms.repeat((10, 10, 100))
    dx = 0.3 * np.sin(42 * np.arange(3 * len(atoms)))
    dx.shape = (-1, 3)
    atoms.set_array("perturbation", dx)
else:
    atoms = None
if isparallel:
    atoms = MakeParallelAtoms(atoms, cpulayout)    

print("Testing FIRE relaxation")
atoms.set_calculator(EMT())
e0 = atoms.get_potential_energy()
natoms = atoms.get_number_of_atoms()
ReportTest("Number of atoms", natoms, 10000, 0)
print("Potential energy before perturbation:", e0, e0/natoms)

atoms.set_positions(atoms.get_array("perturbation") + atoms.get_positions())
e1 = atoms.get_potential_energy()
print("Potential energy after perturbation:", e1, e1/natoms)

dyn = FIRE(atoms)
dyn.run(0.005)
e2 = atoms.get_potential_energy()
print("Potential energy after perturbation:", e2, e2/natoms)
ReportTest("Energy after relaxation", e2, e0, 0.02)
ReportTest("Number of FIRE steps", dyn.nsteps, 252, 5)

RestrictedCNA(atoms)
t = atoms.get_tags()
nwrong = np.not_equal(t, 0).sum()
ReportTest("Number of non-FCC atoms", nwrong, 0, 0)

ReportTest.Summary()
