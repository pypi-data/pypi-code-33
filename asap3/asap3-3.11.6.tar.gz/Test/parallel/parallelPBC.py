"""Test periodic boundary conditions in parallel simulations."""
from __future__ import print_function

from asap3 import *
from asap3.analysis.localstructure import RestrictedCNA, CoordinationNumbers
from asap3.testtools import ReportTest
from asap3.mpi import world
from ase.lattice import bulk
import numpy as np

debug = 0
if debug == 1:
    DebugOutput("parallel%d.log", nomaster=True)
elif debug == 2:
    time.sleep(world.rank)
    print("PID:", os.getpid())
    time.sleep(20)

ismaster = world.rank == 0
isparallel = world.size != 1
if world.size == 1:
    cpulayout = None
elif world.size == 2:
    cpulayout = [2,1,1]
elif world.size == 3:
    cpulayout = [1,3,1]
elif world.size == 4:
    cpulayout = [2,1,2]

pbc_list = [(True, True, False),
            (False, True, True),
            (True, False, True)]

def makesystem():
    atoms = bulk('Cu')
    atoms = atoms.repeat((25, 25, 25))
    return atoms

seratoms = makesystem()
seratoms.set_pbc(pbc_list[-1])
seratoms.set_calculator(EMT())
old_energy = seratoms.get_potential_energy()

for pbc in pbc_list:
    # Make parallel nb list
    if ismaster:
        atoms = makesystem()
        atoms.set_pbc(pbc)
    else:
        atoms = None
    if isparallel:
        atoms = MakeParallelAtoms(atoms, cpulayout)
    natoms = atoms.get_number_of_atoms()
    atoms.set_calculator(EMT())
    energy = atoms.get_potential_energy()
    ReportTest("PBC={0}".format(str(pbc)), energy, old_energy, 1e-6)

ReportTest.Summary()
