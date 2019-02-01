"""Test OpenKIM Lennard Jones potential, including parameter modifications."""

from __future__ import print_function, division
from asap3 import *
from ase.build import bulk
import numpy as np
from asap3.testtools import ReportTest

model = 'LennardJones612_UniversalShifted__MO_959249795837_003'

if OpenKIMsupported:
    try:
        calc = OpenKIMcalculator(model)
    except AsapError as oops:
        if oops.args[0].startswith('Failed to initialize OpenKIM model'):
            print("OpenKIM model {} not installed - skipping test.".format(openkimmodel))
            calc = None
        else:
            raise

if OpenKIMsupported and calc is not None:

    p = calc.parameters
    # Get some parameters
    epsilon_He = p.get_parameter('epsilons', 'ut')[1,1]
    sigma_He = p.get_parameter('sigmas', 'ut')[1,1]
    # Set a parameter
    p['shift'] = 0

    helium = bulk("He", 'fcc', np.sqrt(2) * 2**(1/6) * sigma_He).repeat((5,5,5))
    helium.set_calculator(calc)

    e = helium.get_potential_energy() / len(helium)
    ReportTest("Helium energy", e, -8.24646294 * epsilon_He, 1e-6)

    calc2 = OpenKIMcalculator(model)
    eps = calc2.parameters.get_parameter('epsilons', 'ut')
    eps[1,1] = 2 * epsilon_He
    calc2.parameters.set_parameter('epsilons', eps, 'ut')
    calc2.parameters['shift'] = 0

    helium.set_calculator(calc2)
    e2 = helium.get_potential_energy() / len(helium)

    ReportTest("Modified Helium energy", e2, 2*e, 1e-6)


    ReportTest.Summary()
