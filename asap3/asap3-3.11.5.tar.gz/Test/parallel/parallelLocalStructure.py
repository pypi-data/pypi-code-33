"""Test local crystal structure analysis (CNA and Coordination number)."""
from __future__ import print_function

from asap3 import *
from asap3.analysis import FullCNA, RestrictedCNA, CoordinationNumbers
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

for usepot in (True, False):
    if ismaster:
        atoms = bulk('Cu')
        atoms = atoms.repeat((10, 10, 10))
        if isparallel:
            atoms = atoms.repeat(cpulayout)
        del atoms[100]   #Create point defect
    else:
        atoms = None
    if isparallel:
        atoms = MakeParallelAtoms(atoms, cpulayout)
    natoms = atoms.get_number_of_atoms()
    if usepot:
        atoms.set_calculator(EMT())
        atoms.get_potential_energy()
    
    print("Testing CNA")
    RestrictedCNA(atoms)
    t = atoms.get_tags()
    counts = np.zeros(3, int)
    for i in range(3):
        counts[i] = (t == i).sum()
    world.sum(counts)
    
    ReportTest("CNA: fcc atoms", counts[0], natoms-12, 0)
    ReportTest("CNA: hcp atoms", counts[1], 0, 0)
    ReportTest("CNA: other atoms", counts[2], 12, 0)
    
    print()
    print("Testing coordination number")
    t = CoordinationNumbers(atoms)
    counts = np.zeros(20, int)
    wanted = np.zeros(20, int)
    wanted[11] = 12
    wanted[12] = natoms - 12
    for i in range(len(counts)):
        counts[i] = (t == i).sum()
    if isparallel:
        world.sum(counts)
    for i in range(len(counts)):
        ReportTest("Coordination number {0}".format(i), counts[i], wanted[i], 0)
        
    print()
    print("Testing Full CNA")
    cnacalc = FullCNA(atoms)
    cna = cnacalc.get_normal_cna()
    print(cna[0])
    ReportTest("Length of CNA vector", len(cna), len(atoms), 0)
    for i in range(len(atoms)):
        ReportTest("Number of CNA vectors (atom {0})".format(i), 
                   sum(cna[i].values()), t[i], 0, silent=True)
        if (t[i] == 12):
            ReportTest("Number of 421 bonds (atom {0})".format(i),
                       cna[i][(4,2,1)], 12, 0, silent=True)
      
ReportTest.Summary()
