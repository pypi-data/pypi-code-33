"""Test local crystal structure analysis (CNA and Coordination number)."""
from __future__ import print_function

from asap3 import *
from asap3.analysis.localstructure import RestrictedCNA, CoordinationNumbers
from asap3.testtools import ReportTest
from asap3.mpi import world
from ase.build import bulk
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

nbl_cutoff = 4.5

def makesystem():
    atoms = bulk('Cu')
    atoms = atoms.repeat((15, 15, 15))
    if cpulayout:
        atoms = atoms.repeat(cpulayout)
    atoms.set_pbc((True, False, True))
    #atoms.set_pbc((False, True, True))
    del atoms[87]   #Create point defect
    return atoms

for usepot in (True, False):
    # Make serial nb list.
    seratoms = makesystem()
    sernblist = FullNeighborList(nbl_cutoff, seratoms)

    # Make parallel nb list
    if ismaster:
        atoms = makesystem()
    else:
        atoms = None
    if isparallel:
        atoms = MakeParallelAtoms(atoms, cpulayout)
    natoms = atoms.get_number_of_atoms()
    if usepot:
        atoms.set_calculator(EMT())
        old_energy = atoms.get_potential_energy()
        print(atoms.get_calculator().get_cutoff())
        print(len(atoms), atoms.get_number_of_atoms())
        #assert atoms.get_calculator().get_cutoff() >= nbl_cutoff
    
    print("Testing parallel neighbor locator (usepot = {0})".format(usepot))
    nblist = FullNeighborList(nbl_cutoff, atoms)
    print("Length of neighbor locator", len(nblist), len(atoms))
    print(nblist[-1])
    if isparallel:
        ids = atoms.get_ids()
    else:
        ids = range(len(atoms))
    maxlen = -1
    minlen = 1e100
    for i in range(len(atoms)):
        l = len(nblist[i])
        l_exp = len(sernblist[ids[i]])
        ReportTest("NBlist length (i={0}, id={1})".format(i, ids[i]), 
                   l, l_exp, 0, silent=True)
        if l > maxlen:
            maxlen = l
        if l < minlen:
            minlen = l
        if l == l_exp:
            snbl = set((n for n in sernblist[ids[i]]))
            for nb in nblist[i]:
                if nb < len(atoms):
                    assert ids[nb] in snbl

    print("Neighbor list length:", minlen, '-', maxlen)
    if usepot:
        atoms[1].position += np.array((1e-5,0,0))
        ReportTest("Energy", atoms.get_potential_energy(), old_energy, 1e-4)
 

#ReportTest.Summary()
