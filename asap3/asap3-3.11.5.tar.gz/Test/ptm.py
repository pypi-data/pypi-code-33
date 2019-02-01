#!/usr/bin/env python
"""
Tests that polyhedral template matching works on the simplest possible system.

Name: ptm.py

Description: Part of the Asap test suite.  Tests the analysis.ptm module

Usage: python ptm.py

Expected result: The output should end with 'ALL TESTS SUCCEEDED'.
"""
from __future__ import print_function

from ase.lattice.cubic import FaceCenteredCubic, BodyCenteredCubic
from ase.lattice.hexagonal import HexagonalClosedPacked
from ase.build import bulk
from asap3.testtools import ReportTest
from asap3.analysis import PTM
import numpy as np
#from ase.visualize import view

atoms = FaceCenteredCubic("Cu", size=(7,7,7), pbc=False)
x = atoms.get_positions()
#atoms.set_positions(x + 0.01 * np.random.standard_normal(x.shape))

data = PTM(atoms, rmsd_max=0.1, calculate_strains=True)
print("DONE")
cnt = np.bincount(data['structure'])
print(cnt)
print(data['info'])

ReportTest("Number of FCC atoms", cnt[1], 6*6*6*4, 0)
ReportTest("Number of non-classified atoms", cnt[0], len(atoms) - 6*6*6*4, 0)

data = PTM(atoms, rmsd_max=0.1, calculate_strains=True, quick=True)
cnt = np.bincount(data['structure'])
print(cnt)
print(data['info'])

ReportTest("Number of FCC atoms", cnt[1], 6*6*6*4, 0)
ReportTest("Number of non-classified atoms", cnt[0], len(atoms) - 6*6*6*4, 0)

data = PTM(atoms, rmsd_max=0.1, target_structures=('fcc', 'hcp'))
cnt = np.bincount(data['structure'])
print(cnt)
print(data['info'])

ReportTest("Number of FCC atoms", cnt[1], 6*6*6*4, 0)
ReportTest("Number of non-classified atoms", cnt[0], len(atoms) - 6*6*6*4, 0)

atoms = BodyCenteredCubic("Fe", size=(7,7,7), pbc=(True,True,False))
data = PTM(atoms, rmsd_max=0.001)
cnt = np.bincount(data['structure'])
print(cnt)
print(data['info'])

ReportTest("Number of BCC atoms", cnt[3], 7*7*5*2, 0)
ReportTest("Number of non-classified atoms", cnt[0], len(atoms) - 7*7*5*2, 0)

atoms = HexagonalClosedPacked("Mg", size=(7,7,7), pbc=(True,True,False))
data = PTM(atoms, rmsd_max=0.01)  # Need a slightly larger rmsd as c/a deviates from ideal.
cnt = np.bincount(data['structure'])
print(cnt)
print(data['info'])

ReportTest("Number of HCP atoms", cnt[2], 7*7*6*2, 0)
ReportTest("Number of non-classified atoms", cnt[0], len(atoms) - 7*7*6*2, 0)
#atoms.set_tags(data['structure'])
#view(atoms)

atoms = bulk("Mg", orthorhombic=True)
atoms = atoms.repeat((7,7,7))
atoms.set_pbc((True, True, False))
data = PTM(atoms, rmsd_max=0.01)  # Need a slightly larger rmsd as c/a deviates from ideal.
cnt = np.bincount(data['structure'])
print(cnt)
print(data['info'])

ReportTest("Number of HCP atoms", cnt[2], 7*7*6*4, 0)
ReportTest("Number of non-classified atoms", cnt[0], len(atoms) - 7*7*6*4, 0)

# Make a combined system

atoms = bulk("Mg", orthorhombic=True)
atoms = atoms.repeat((7,4,7))

atoms2 = bulk("Fe", orthorhombic=True).repeat((3,3,3))
uc1 = atoms.get_cell()
uc2 = atoms2.get_cell()
factor1 = uc1[0,0] / uc2[0,0]
factor2 = uc1[1,1] / uc2[1,1]
uc2 = uc2 * np.array((factor1, factor2, 0.5*(factor1+factor2)))
atoms2.set_cell(uc2, scale_atoms=True)
# Combine unit cell, stack BCC atoms on top of HCP atoms.
uc3 = np.array(uc1)
dz = uc3[2,2]
uc3[2,2] += uc2[2,2]
atoms.set_cell(uc3, scale_atoms=False)
atoms2.set_positions(atoms2.get_positions() + np.array((0.1,0.1,dz))[np.newaxis,:])
atoms.extend(atoms2)

data = PTM(atoms, rmsd_max=0.005)
cnt = np.bincount(data['structure'])
print(cnt)
print(data['info'])

ReportTest("Number of HCP atoms", cnt[2], 7*4*6*4, 0)
ReportTest("Number of BCC atoms", cnt[3], 3*3*1*2, 0)
ReportTest("Number of FCC atoms", cnt[1], 0, 0)
ReportTest("All classes of atoms", cnt[:4].sum(), len(atoms), 0)

#atoms.set_tags(data['structure'])
#view(atoms)

ReportTest.Summary()
