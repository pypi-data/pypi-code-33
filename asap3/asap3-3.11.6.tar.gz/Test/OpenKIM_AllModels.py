from __future__ import print_function
from asap3 import *
from ase.lattice.cubic import FaceCenteredCubic
from asap3.testtools import ReportTest
import numpy as np
from numpy.random import RandomState
from ase.data import reference_states, atomic_numbers, chemical_symbols
from ase.build import bulk
import sys

brokenmodels = [
    'ex_model_Ar_P_Morse_MultiCutoff',                           # Does not set Destroy pointer.
    'EAM_IMD_BrommerGaehler_2006B_AlNiCo__MO_128037485276_003',  # Force and energy inconsistent
    'EAM_NN_Johnson_1988_Cu__MO_887933271505_002',               # Force and energy inconsistent
    'EAM_Magnetic2GQuintic',                                     # Crash with Intel compiler.
    'EAM_MagneticCubic',                                         # Crash with Intel compiler.
    ]

# Some models require a specific primary and secondary element,
# e.g. if it is aiming at impurity calculations, and using the wrong
# element as host brings it outside its comfort zone.
explicit_elements = {
    'EAM_Dynamo_HepburnAckland_2008_FeC__MO_143977152728_005': ('Fe', 'C'),   # C impurity in Fe
    'EAM_Dynamo_SmirnovaKuskinStarikov_2013_UMoXe__MO_679329885632_005': ('U', 'Mo'),
    }
    
tolerance = 1e-4
#set_verbose(1)

if OpenKIMsupported:
    openkimmodels = OpenKIMavailable()
else:
    openkimmodels = []
    print("OpenKIM support is not compiled into Asap.")
    
#rnd = RandomState(42)  # We want deterministic random numbers
rnd = RandomState()

known_states = ['bcc', 'fcc', 'hcp', 'diamond', 'sc']

delta = 0.001

if len(sys.argv) > 1:
    openkimmodels = sys.argv[1:]
    brokenmodels = []

skipped = []
crashed = []

#rnd.shuffle(openkimmodels)

for model in openkimmodels:
    broken = False
    for brk in brokenmodels:
        if model.startswith(brk):
            broken = True
    if broken:
        print("\nSkipping broken KIM model:", model)
        skipped.append((model, "Blacklisted"))
        continue
    print("\nKIM model:", model)
    if model == 'EMT':
        calculator = EMT()
        elements = ('Cu', 'Au', 'Ag')
    else:
        calculator = OpenKIMcalculator(model)
        elements = calculator.get_supported_elements(user=False)
    print("Supported elements:", elements)
    overrule_elements = model in explicit_elements
    if overrule_elements:
        elements = explicit_elements[model]
    if len(elements) == 1:
        main = elements[0]
        other = None
        state = reference_states[atomic_numbers[main]]
    else:
        if not overrule_elements:
            elements = list(elements)
            rnd.shuffle(elements)
        for i in range(len(elements)):
            main = elements[i]
            other = elements[i-1]
            state = reference_states[atomic_numbers[main]]
            if state and state['symmetry'] in known_states:
                break
    if state['symmetry'] not in known_states:
        print("Cannot simulate {}, reference state '{}' not supported".format(main, state['symmetry']))
        print("SKIPPING MODEL!")
        continue

    for case in range(2):
        if case == 0:
            init_atoms = bulk(main, orthorhombic=True).repeat((7,7,7))
        elif case == 1:
            init_atoms = bulk(main).repeat((1,2,7))
            # We cannot reuse the OpenKIMcalculator
            if model != "EMT":
                calculator = OpenKIMcalculator(model)
        else:
            raise RuntimeError("Unknown case "+str(case))
        r = init_atoms.get_positions()
        r += rnd.normal(0.0, 0.1, r.shape)
        init_atoms.set_positions(r)
        z = init_atoms.get_atomic_numbers()
        if other:
            some_atoms = rnd.randint(0, 20, len(init_atoms)) == 0
            z[some_atoms] = atomic_numbers[other]
            init_atoms.set_atomic_numbers(z)
            z_other = atomic_numbers[other]
        else:
            z_other = 0
        print ("Generated a %s system with %i %s-atoms and %i %s-atoms"
                   % (state['symmetry'], 
                          np.equal(z, atomic_numbers[main]).sum(),
                          main,
                          np.equal(z, z_other).sum(),
                          other))
        print("Lattice constant a =", state['a']) 
        old_energy = old_forces = None
        rndat = rnd.randint(len(init_atoms))



        #print "Testing %s with %s" % (model, nbl)
        atoms = Atoms(init_atoms)
        try:
            atoms.set_calculator(calculator)
            e = atoms.get_potential_energy()
            f = atoms.get_forces()
        except (RuntimeError, ValueError, AsapError) as exc:
            txt = "{} (case {}) raised exception {}: {}".format(model, case, str(type(exc)), str(exc))
            print(txt)
            crashed.append(txt)
            continue

        atoms[rndat].position[0] += delta
        de = atoms.get_potential_energy() - e
        f = 0.5 * f + 0.5 * atoms.get_forces()
        exp_de = -delta * f[rndat,0]
        #print "Old energy: %.9f.   Change: %.9f    Expected: %.9f   Abs: %.9e   Relative: %.9f" % (e, de, exp_de, de-exp_de, (de-exp_de)/exp_de)
        ReportTest("{} (case {}) force consistent".format(model, case), de, exp_de, tolerance)

    
print("Skipped models:")
if skipped:
    for m in skipped:
        print("   {}: \t{}".format(*m))
else:
    print("    None")
print("Crashing models:")
if crashed:
    for m in crashed:
        print("   ", m)
else:
    print("    None")
ReportTest.Summary()
