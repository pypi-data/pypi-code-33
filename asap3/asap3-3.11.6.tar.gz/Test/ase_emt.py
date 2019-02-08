"""Check that ASE.calculators.emt and asap3.EMT give the same."""

from __future__ import print_function
from ase.lattice.compounds import *
from ase.lattice.cubic import *
from ase.calculators.emt import EMT as EMT_ASE
from asap3 import EMT as EMT_ASAP
from asap3.testtools import ReportTest
import numpy as np

elements = ("Ni", "Cu", "Pd", "Ag", "Pt")

for e1 in elements:
    for e2 in elements:
        atoms = FaceCenteredCubic(directions=[[1,0,0],[0,1,0],[0,0,1]], size=(1,1,2),
                                  symbol=e1, pbc=(1,0,1), debug=0)
        atoms.set_calculator(EMT_ASE(asap_cutoff=True))
        e_e1_ase = atoms.get_potential_energy()
        atoms.set_calculator(EMT_ASAP())
        e_e1_asap = atoms.get_potential_energy()
        natoms = len(atoms)

        print("{0} energy (ASE) \t{1:.5f}".format(e1, e_e1_ase/natoms))
        print("{0} energy (ASAP)\t{1:.5f}".format(e1, e_e1_asap/natoms))

        atoms = FaceCenteredCubic(directions=[[1,0,0],[0,1,0],[0,0,1]], size=(1,1,2),
                                  symbol=e2, pbc=(1,0,1), debug=0)
        atoms.set_calculator(EMT_ASE(asap_cutoff=True))
        e_e2_ase = atoms.get_potential_energy()
        atoms.set_calculator(EMT_ASAP())
        e_e2_asap = atoms.get_potential_energy()

        print("{0} energy (ASE) \t{1:.5f}".format(e2, e_e2_ase/natoms))
        print("{0} energy (ASAP)\t{1:.5f}".format(e2, e_e2_asap/natoms))

        atoms = L1_2(directions=[[1,0,0],[0,1,0],[0,0,1]], size=(1,1,2),
                     symbol=(e1, e2), latticeconstant=3.95, pbc=(1,0,1), 
                     debug=0)
        
        atoms.set_calculator(EMT_ASE(asap_cutoff=True))
        e_alloy_ase = atoms.get_potential_energy() - (2*e_e1_ase + 6*e_e2_ase)/8
        atoms.set_calculator(EMT_ASAP())
        e_alloy_asap = atoms.get_potential_energy() - (2*e_e1_asap + 6*e_e2_asap)/8

        print("Alloy energy (ASE) \t{0:.5f}".format(e_alloy_ase/natoms))
        print("Alloy energy (ASAP)\t{0:.5f}".format(e_alloy_asap/natoms))
        ReportTest("{0}{1}_3 alloy energy".format(e1, e2), e_alloy_ase, e_alloy_asap, 1e-4)

ReportTest.Summary()

