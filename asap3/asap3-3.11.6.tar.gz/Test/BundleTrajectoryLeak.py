from __future__ import print_function
from asap3 import *
from asap3.md.verlet import VelocityVerlet
from ase.lattice.cubic import FaceCenteredCubic
#from asap3.io.bundletrajectory import BundleTrajectory
from ase.io.bundletrajectory import BundleTrajectory
from ase.io import write
from numpy import *
import sys, os, time
from asap3.testtools import ReportTest

#DebugOutput("output.%d")
print_version(1)
delete = False #True

initial = FaceCenteredCubic(size=(10,10,10), symbol="Cu", pbc=(1,0,0))
initial.set_momenta(zeros((len(initial),3)))
initial.set_tags(arange(len(initial)))

atoms = initial.copy()
atoms.set_calculator(EMT())
print("Writing trajectory")
traj = BundleTrajectory("traj1.bundle", "w", atoms)
traj.write()
traj.close()


