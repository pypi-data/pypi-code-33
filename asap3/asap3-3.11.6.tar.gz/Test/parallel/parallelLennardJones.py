from __future__ import print_function
from asap3 import *
from ase.md.verlet import VelocityVerlet
from ase.lattice.cubic import FaceCenteredCubic
from asap3.io.trajectory import *
from numpy import *
from asap3.mpi import world
import sys, os, time
from asap3.testtools import ReportTest

debug = 0
if debug == 1:
    DebugOutput("parallelLJ%d.log", nomaster=True)
elif debug == 2:
    time.sleep(world.rank)
    print("PID:", os.getpid())
    time.sleep(20)
    
#DebugOutput("output.%d")
print_version(1)

worldsize = world.size
ismaster = world.rank == 0

if worldsize == 1:
    layout = [None]
elif worldsize == 2:
    layout = [(2,1,1), (1,2,1), (1,1,2)]
elif worldsize == 3:
    layout = [(3,1,1), (1,1,3)]
elif worldsize == 4:
    layout = [(1,2,2), (2,1,2), (2,2,1)]
elif worldsize == 8:
    layout = [(2,2,2), (1,2,4)]
else:
    raise ValueError("Cannot run on %d CPUs." % (worldsize,))

elements = [29]
epsilon  = [0.15]
sigma    = [2.7]


if ismaster:
    initial = FaceCenteredCubic(directions=((1,0,0),(0,1,0),(0,0,1)),
                                size=(40,40,40), symbol="Cu",
                                latticeconstant=1.09*sigma[0]*1.41,
                                pbc=(1,1,0))
    momenta = sqrt(2*63.5 * units.kB * 400) * sin(arange(3*len(initial)))
    momenta.shape = (-1,3)
    initial.set_momenta(momenta)
    stdout = sys.stdout
    print("Number of atoms:", len(initial))
else:
    initial = None
    stdout = open("/dev/null", "w")

for cpulayout in layout:
    if cpulayout:
        print("Test with layout "+str(cpulayout), file=stdout)
        atoms = MakeParallelAtoms(initial, cpulayout)
        natoms = atoms.get_number_of_atoms()
    else:
        print("Serial test", file=stdout)
        atoms = Atoms(initial)
        natoms = len(atoms)
    print("Number of atoms:", natoms)
    temp = atoms.get_kinetic_energy() / (1.5*units.kB*natoms)
    print("Temp:", temp, "K", file=stdout)
    ReportTest("Initial temperature", temp, 400.0, 1.0)
    atoms.set_calculator(LennardJones(elements, epsilon, sigma, -1.0, True))

    epot = atoms.get_potential_energy()
    print("Potential energy:", epot, file=stdout)
    ReportTest("Initial potential energy", epot, -301358.3, 0.5)
    etot = epot + atoms.get_kinetic_energy()


    dyn = VelocityVerlet(atoms, 3*units.fs)
    if 0:
        traj = Trajectory("llj.traj", "w", atoms)
        dyn.attach(traj, interval=2)
                
    etot2 = None
    for i in range(5):
        dyn.run(15)
        newetot = atoms.get_potential_energy()+ atoms.get_kinetic_energy()
        print("Total energy:", newetot, file=stdout)
        temp = atoms.get_kinetic_energy() / (1.5*units.kB*natoms)
        print("Temp:", temp, "K", file=stdout)
        if etot2 == None:
            ReportTest("Total energy (first step)", newetot, etot, 40.0)
            etot2=newetot
        else:
            ReportTest(("Total energy (step %d)" % (i+1,)),
                       newetot, etot2, 20.0)
    print(" *** This test completed ***", file=stdout)

ReportTest.Summary()
