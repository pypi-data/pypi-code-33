from __future__ import print_function
from asap3 import *
import pickle
from numpy import *
from ase.build import bulk
from asap3.testtools import ReportTest
import ase.data
import numpy as np

print_version(1)

verbose = False

picklefile = "PortingKIM.pickle"
boundaries = [(True, True, True), (True, True, False), (False, False, False)]
#boundaries = [(True, True, True),]

if OpenKIMsupported:
    models = [ ('ex_model_Ar_P_Morse_07C', 'Ar'),
               ('ex_model_Ar_P_MLJ_Fortran', 'Ar'),
               #('Three_Body_Stillinger_Weber_Si__MO_405512056662_004', 'Si'), # Not yet updated to parameter_name
             ]
    if os.path.exists(picklefile):
        data = pickle.load(open(picklefile, "rb"))
    else:
        data = {}
else:
    models = []
    print("OpenKIM support is not compiled into Asap.")

savedata = False
for model, element in models:
    if model[-4:-1] == '_00':
        modelname = model[:-4]
    else:
        modelname = model
    for pbc in boundaries:
        print("Running test on {} / {} with model {}".format(element, pbc, model))

        try:
            modeldata = data[(modelname, pbc)]
        except KeyError:
            modeldata = None
            newdata = {}
            print("WARNING:  No data for model '{}' / {}: Creating it.".format(model, pbc))
            savedata = True
            data[(modelname, pbc)] = newdata

        atoms = bulk(element).repeat((3,3,3))
        atoms.set_cell(atoms.get_cell()*0.98, scale_atoms=True)
        atoms.set_pbc(pbc)
        atoms.set_calculator(OpenKIMcalculator(model, verbose=verbose))

        # Test initial forces
        print("\n"*10)
        forces = atoms.get_forces()
        print("Got the forces!")
        if modeldata:
            diff = np.abs(forces - modeldata['initforces']).max()
            ReportTest("Maximal deviation of initial forces", diff, 0, 1e-9)
        else:
            newdata['initforces'] = forces
        
        # Test energy conservation during Verlet dynamics
        dyn = VelocityVerlet(atoms, 1 * units.fs)
        dyn.attach(MDLogger(dyn, atoms, '-', peratom=True), interval=5)    
        etot = None
    
        for i in range(10):
            dyn.run(20)
            epot = atoms.get_potential_energy() / len(atoms)
            ekin = atoms.get_kinetic_energy() / len(atoms)
            if etot is None:
                etot = epot + ekin
            else:
                ReportTest("Energy conservation:", epot + ekin, etot, 0.001)
                print(epot, ekin, etot)

        # Test final positions and forces
        pos = atoms.get_positions()
        forces = atoms.get_forces()
        if modeldata:
            diff = np.abs(pos - modeldata['finalpos']).max()
            ReportTest("Maximal deviation of final positions", diff, 0, 1e-9)
            diff = np.abs(forces - modeldata['finalforces']).max()
            ReportTest("Maximal deviation of final forces", diff, 0, 1e-9)
        else:
            newdata['finalpos'] = pos
            newdata['finalforces'] = forces

        # Test stress
        sc = atoms.get_calculator().supported_calculations
        if sc.get('partialParticleVirial', False) or sc.get('particleVirial', False):
            stress = atoms.get_stress()
            print("Stress", stress)

ReportTest.Summary()

    
if savedata:
    print("New data generated - saving it!")
    with open(picklefile, "wb") as pfile:
        pickle.dump(data, pfile)
        
