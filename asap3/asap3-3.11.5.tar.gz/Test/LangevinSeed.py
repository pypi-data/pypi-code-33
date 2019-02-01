from ase.units import kB, fs
from asap3 import EMT
from asap3.md.langevin import Langevin
from asap3.io import Trajectory
from ase.build import fcc111

from asap3.testtools import ReportTest
import numpy as np


for seed in [1, None]:
    positions = []
    for i_run in range(2):

        atoms = fcc111('Au', size=(3,3,3), vacuum=10.0)
        atoms.set_calculator(EMT())

        dyn = Langevin(atoms, timestep=5.0*fs, temperature=300*kB, friction=1e-1, seed=seed)
        dyn.run(1000)

        positions.append(atoms.get_positions())

    p1, p2 = positions
    is_pos_equal = np.allclose(p1, p2)
    print("Max difference:", abs(p1 - p2).max())
    if seed is None:
        ReportTest.BoolTest("Runs differ when not seeded", not is_pos_equal)
    else:
        ReportTest.BoolTest("Runs are equal when seeded", is_pos_equal)
ReportTest.Summary()
