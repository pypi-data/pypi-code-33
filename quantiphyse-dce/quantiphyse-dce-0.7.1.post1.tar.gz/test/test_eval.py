"""
Quantiphyse - Analysis process for DCE-MRI modelling

Copyright (c) 2013-2018 University of Oxford
"""

import sys
import os
import time
import numpy as np

test_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(test_dir, os.pardir))

from dce.pk_model import PyPk

KTRANS = 0.2
VE = 0.2
T1 = 1
FA = 12
R1 = 4.5
R2 = 4.5
TR = 4.5
TE = 1
FA = 12
DELT = 6
NTIMES = 25
INJT = 0

def eval(nt, delt, ktrans, ve, t1, r1, r2, injt, tr, te, fa, dose=0, model_choice=1):
    try:
        log = ""
        times = np.arange(0, nt)*delt
        # conversion to minutes
        times = times/60.0

        injtmins = injt/60.0

        # conversion to seconds
        dce_TR = tr/1000.0
        dce_TE = te/1000.0

        #specify variable upper bounds and lower bounds
        ub = [10, 1, 0.5, 0.5]
        lb = [0, 0.05, -0.5, 0]

        # contiguous array
        data = np.zeros((10, nt), dtype=np.double)
        t10 = np.ones((10, ), dtype=np.double)
        times = np.ascontiguousarray(times)

        Pkclass = PyPk(times, data, t10)
        Pkclass.set_bounds(ub, lb)
        Pkclass.set_parameters(r1, r2, fa, dce_TR, dce_TE, dose)
        Pkclass.rinit(model_choice, injtmins)
        Pkclass.get_curve(t1, ktrans, ve)
    except:
        raise

eval(NTIMES, DELT, KTRANS, VE, T1, R1, R2, INJT, TR, TE, FA)
