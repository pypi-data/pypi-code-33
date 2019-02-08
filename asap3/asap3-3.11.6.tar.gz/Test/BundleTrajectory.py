from __future__ import print_function
from asap3 import *
from asap3.md.verlet import VelocityVerlet
from ase.lattice.cubic import FaceCenteredCubic
from asap3.io.trajectory import *
#from ase.io.bundletrajectory import BundleTrajectory
from ase.io import write
from numpy import *
import sys, os, time
from asap3.testtools import ReportTest

#DebugOutput("output.%d")
print_version(1)
delete = True
#precision = 1.5e-4  # We store positions in single precision.
precision = 1e-8

def maketraj(atoms, t, nstep):
    e = [atoms.get_potential_energy()]
    dyn = VelocityVerlet(atoms, 5*units.fs)
    for i in range(nstep):
        dyn.run(10)
        e.append(atoms.get_potential_energy())
        if t is not None:
            t.write()
    return e

def maketraj_no_e(atoms, t, nstep):
    dyn = VelocityVerlet(atoms, 5*units.fs)
    for i in range(nstep):
        dyn.run(10)
        if t is not None:
            t.write()

def checktraj(t, e, recalc=True):
    i = 0
    for atoms in t:
        if recalc:
            atoms.set_calculator(EMT())
        ReportTest("Checking frame %d" % (i,), atoms.get_potential_energy(),
                   e[i], precision)
        i += 1

initial = FaceCenteredCubic(size=(10,10,10), symbol="Cu", pbc=(1,0,0))
initial.set_momenta(zeros((len(initial),3)))
initial.set_tags(arange(len(initial)))

atoms = initial.copy()
atoms.set_calculator(EMT())
print("Writing trajectory")
traj = BundleTrajectory("traj1.bundle", "w", atoms, singleprecision=False)
traj.write()
energies = maketraj(atoms, traj, 10)
traj.close()

print("Reading trajectory (recalculating energies)")
traj = BundleTrajectory("traj1.bundle")
checktraj(traj, energies)

print("Reading trajectory (stored energies)")
traj = BundleTrajectory("traj1.bundle")
checktraj(traj, energies, recalc=False)

print("Repeating simulation")
atoms = traj[5]
atoms.set_calculator(EMT())
energies2 = maketraj(atoms, None, 5)
for i in range(5):
    ReportTest("Rerun[%d]" % (i,), energies2[i], energies[i+5], precision)
traj.close()

print("Appending to trajectory")
atoms = BundleTrajectory("traj1.bundle")[-1]
atoms.set_calculator(EMT())
traj = BundleTrajectory("traj1.bundle", "a", atoms)
energies2 = maketraj(atoms, traj, 5)
traj.close()

print("Reading longer trajectory")
traj = BundleTrajectory("traj1.bundle")
checktraj(traj, energies + energies2[1:])

print("Writing trajectory with write")
write("traj2.bundle", atoms, format='bundletrajectory')

print("Writing a trajectory without precalculated energies.")
atoms = initial.copy()
atoms.set_calculator(EMT())
traj = BundleTrajectory("traj3.bundle", "w", atoms, singleprecision=False)
traj.write()
maketraj_no_e(atoms, traj, 10)
traj.close()
traj = BundleTrajectory("traj3.bundle")
checktraj(traj, energies, recalc=False)

if delete:
    print("Deleting trajectory")
    BundleTrajectory.delete_bundle("traj1.bundle")
    BundleTrajectory.delete_bundle("traj2.bundle")
    BundleTrajectory.delete_bundle("traj3.bundle")

    
ReportTest.Summary()
