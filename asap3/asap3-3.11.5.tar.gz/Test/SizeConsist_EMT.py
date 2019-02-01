from __future__ import print_function
from asap3 import *
from numpy import *
from asap3.testtools import ReportTest
from ase.lattice.cubic import *
from ase.lattice.compounds import L1_2
from OpenKIM_modelname import openkimmodel
from ase.data import reference_states, atomic_numbers

element = 'Au'
element2 = 'Ag'
sizes = arange(10,0,-1)

energy = None
force = None
for s in sizes:
    atoms = FaceCenteredCubic(symbol=element, size=(s,s,s), pbc=True)
    r = atoms.get_positions()
    for i in range(0, len(r), 4):
        r[i][0] += 0.1
    atoms.set_positions(r)
    atoms.set_calculator(EMT())
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

# Lattice constant for alloy
lc = [reference_states[atomic_numbers[s]]['a'] for s in (element, element2)]
lc = (3*lc[0] + lc[1])/4.0

energy = None
force = None
for s in sizes:
    atoms = L1_2(symbol=(element,element2), size=(s,s,s), latticeconstant=lc, pbc=True)
    r = atoms.get_positions()
    for i in range(1, len(r), 4):
        r[i][0] += 0.1
    atoms.set_positions(r)
    atoms.set_calculator(EMT())
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
