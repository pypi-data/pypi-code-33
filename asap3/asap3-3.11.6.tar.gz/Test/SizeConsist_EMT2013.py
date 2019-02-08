from __future__ import print_function
from asap3 import *
from numpy import *
from asap3.testtools import ReportTest
from ase.lattice.cubic import *
from ase.lattice.compounds import *
from OpenKIM_modelname import openkimmodel
from asap3.EMT2013Parameters import sihb_PtY_parameters

element = 'Pt'
element2 = ('Y', 'Pt')
lc2 = 4.125
sizes = arange(10,0,-1)

energy = None
force = None


for s in sizes:
    atoms = FaceCenteredCubic(symbol=element, size=(s,s,s), pbc=True)
    r = atoms.get_positions()
    for i in range(0, len(r), 4):
        r[i][0] += 0.1
    atoms.set_positions(r)
    atoms.set_calculator(EMT2013(sihb_PtY_parameters))
    e = atoms.get_potential_energy() / len(atoms)   
    print("%5i atoms: E = %.5f eV/atom" % (len(atoms), e))
    if energy is None:
        energy = e
    else:
        ReportTest("Energy for size %i (%i atoms)" % (s, len(atoms)),
                   e, energy, 1e-8)
    f = atoms.get_forces()
    if force is None:
        force = f[:4]
    else:
        for i in range(len(f)):
            for j in range(3):
                ReportTest("Force for size %i atom %i of %i component %i"
                           % (s, i, len(atoms), j),
                           f[i,j], force[i % 4, j], 1e-8, silent=True)
        #print force
        #print f[:10]
    del atoms


energy = None
force = None

for s in sizes:
    atoms = L1_2(symbol=element2, size=(s,s,s), latticeconstant=lc2, pbc=True)
    r = atoms.get_positions()
    for i in range(0, len(r), 4):
        r[i][0] += 0.1
    atoms.set_positions(r)
    atoms.set_calculator(EMT2013(sihb_PtY_parameters))
    e = atoms.get_potential_energy() / len(atoms)   
    print("%5i atoms: E = %.5f eV/atom" % (len(atoms), e))
    if energy is None:
        energy = e
    else:
        ReportTest("Energy for size %i (%i atoms)" % (s, len(atoms)),
                   e, energy, 1e-8)
    f = atoms.get_forces()
    if force is None:
        force = f[:4]
    else:
        for i in range(len(f)):
            for j in range(3):
                ReportTest("Force for size %i atom %i of %i component %i"
                           % (s, i, len(atoms), j),
                           f[i,j], force[i % 4, j], 1e-8, silent=True)
        #print force
        #print f[:10]
    del atoms


ReportTest.Summary()
