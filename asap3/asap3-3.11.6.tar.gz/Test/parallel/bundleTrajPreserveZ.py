from __future__ import print_function
from asap3 import *
from ase.md.verlet import VelocityVerlet
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.lattice.compounds import L1_2
from ase import data
from asap3.io.trajectory import *
from numpy import *
import sys, os, time
from asap3.testtools import ReportTest
from asap3.mpi import world

set_printoptions(threshold='nan')

cu = ase.data.atomic_numbers['Cu']
au = ase.data.atomic_numbers['Au']
cu3au_a = 3.72977

print_version(1)
#set_verbose(1)

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

delete = True
dosim = True
# precision = 1e-8


def check_z(a):
    try:
        id = a.get_ids()
    except AttributeError:
        id = np.arange(len(a))
    z = a.get_atomic_numbers()
    z_expect = np.where(id % 4, cu, au)
    if ismaster:
        print(z[:11])
        print(z_expect[:11])
    assert (z == z_expect).all()

if ismaster:
    initial = L1_2(size=(15,15,15), symbol=(au,cu),
                   latticeconstant=cu3au_a, pbc=(1,0,0))
else:
    initial = None
if isparallel:
    atoms = MakeParallelAtoms(initial, cpulayout)
    print("Min ID", atoms.get_ids().min())
else:
    atoms = initial.copy()
  
check_z(atoms)

if dosim:
    print("Simulation: create the bundle")
    # Give a momentum distribution likely to cause migration
    MaxwellBoltzmannDistribution(atoms, 5000*units.kB)
    p = atoms.get_momenta()
    pz = p[10,2]
    p[:,2] += pz

    atoms.set_calculator(EMT())
    if isparallel:
        traj = BundleTrajectory("preservez.bundle", "w", atoms, split=True)
    else:
        traj = BundleTrajectory("preservez.bundle", "w", atoms)
    dyn = VelocityVerlet(atoms, 5*units.fs)
    dyn.attach(traj, interval=50)
    dyn.attach(check_z, interval=25, a=atoms)
    traj.write()
    dyn.run(150)
    traj.close()
else:
    print("Only reading, hope its there!")

print("Reading in serial mode:")
if dosim:
    traj = BundleTrajectory("preservez.bundle")
    for i, atoms in enumerate(traj):
        print("Task {0}, step {1}: found {2} atoms".format(world.rank, i, len(atoms)))
        check_z(atoms)
    traj.close()

world.barrier()
print("Reading in parallel mode.")
traj = BundleTrajectory("preservez.bundle")
for i in range(len(traj)):
    atoms = traj.get_atoms(i, cpulayout)
    print("Task {0}, step {1}: found {2} atoms".format(world.rank, i, len(atoms)))
    check_z(atoms)
traj.close()
del traj

world.barrier()
if delete:
    #if ismaster:
    print("Deleting trajectory")
    BundleTrajectory.delete_bundle("preservez.bundle")

print("Not crashed: test has passed!")
