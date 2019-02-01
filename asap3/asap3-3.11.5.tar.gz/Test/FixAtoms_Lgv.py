from __future__ import print_function
from ase.units import kB, fs
from asap3 import EMT
from ase.build import fcc111
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from asap3.md.langevin import Langevin
from asap3.constraints import FixAtoms
from asap3.testtools import ReportTest
import numpy as np

def print_momenta(atoms):
    p = atoms.get_momenta()
    p1 = p[:len(atoms)//2]
    p2 = p[len(atoms)//2:]
    print("Momenta:", (p1*p1).sum(), (p2*p2).sum())

T = 4
print("Expecting temperature around {} K\n".format(T))

atoms = fcc111('Au', size=(4,4,4),vacuum=10.0)
atoms.set_calculator(EMT())

n_atoms = atoms.get_number_of_atoms()
c = FixAtoms(indices=range(n_atoms//2))
atoms.set_constraint(c)

print_momenta(atoms)
MaxwellBoltzmannDistribution(atoms, 300*kB)
print_momenta(atoms)
dyn = Langevin(atoms, timestep=0.5*fs, temperature=T*kB, friction=1e-1)
total_run = (2000, 10000)
dyn.attach(lambda: print(atoms.get_temperature()), interval=100)
dyn.run(total_run[0])

print("Computing average temperature.")
temp_data = []
dyn.attach(lambda: temp_data.append(atoms.get_temperature()), interval=10)
dyn.run(total_run[1])
Tmean = np.mean(temp_data)
print_momenta(atoms)

print("Average temperature is:", Tmean, "K")
ReportTest("Average temperature", Tmean, T, T/4.0)
ReportTest.Summary()

