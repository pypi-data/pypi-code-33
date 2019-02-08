"""Test local crystal structure analysis (CNA and Coordination number)."""
from __future__ import print_function


from asap3.analysis import RestrictedCNA, CoordinationNumbers, FullCNA
from asap3.testtools import ReportTest
from ase.lattice import bulk
import numpy as np

atoms = bulk('Cu')
atoms = atoms.repeat((10, 10, 10))
del atoms[100]   #Create point defect

print("Testing CNA")
RestrictedCNA(atoms)
t = atoms.get_tags()
counts = [0,] * 3
for i in range(3):
    counts[i] = (t == i).sum()
    print("CNA mode {0}: {1} atoms.".format(i, counts[i]))
    
ReportTest("CNA: fcc atoms", counts[0], len(atoms)-12, 0)
ReportTest("CNA: hcp atoms", counts[1], 0, 0)
ReportTest("CNA: other atoms", counts[2], 12, 0)

print()
print("Testing coordination number")
t = CoordinationNumbers(atoms)
counts = np.zeros(20, int)
wanted = np.zeros(20, int)
wanted[11] = 12
wanted[12] = len(atoms) - 12
for i in range(len(counts)):
    counts[i] = (t == i).sum()
    print("Coordination number {0}: {1} atoms.".format(i, counts[i]))
    ReportTest("Coordination number {0}".format(i), counts[i], wanted[i], 0)
    
print()
print("Testing Full CNA")
cnacalc = FullCNA(atoms)
cna, totalcna = cnacalc.get_normal_and_total_cna()
counts = {(4,2,1): 0, (3,1,1):0}
ReportTest("Length of CNA vector", len(cna), len(atoms), 0)
for i in range(len(atoms)):
    ReportTest("Number of CNA vectors (atom {0})".format(i), 
               sum(cna[i].values()), t[i], 0, silent=True)
    for key, value in cna[i].items():
        counts[key] += value
    if (t[i] == 12):
        ReportTest("Number of 421 bonds (atom {0})".format(i),
                   cna[i][(4,2,1)], 12, 0, silent=True)
    
ReportTest("Global 421 count", totalcna[(4,2,1)]*2, counts[(4,2,1)], 0)
ReportTest("Global 311 count", totalcna[(3,1,1)]*2, counts[(3,1,1)], 0)   


ReportTest.Summary()
