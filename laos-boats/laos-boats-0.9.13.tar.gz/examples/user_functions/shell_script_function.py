# This file is an interface between BOSS and a shell script.
#
# Please edit:
# (0) A common path for the following functionality, to keep things tidy
# (1) Name of the dummy file where x will be written
# (2) Command that executes your .sh -script, getting its input from (1)
# (3) Name of the file where your script writes (just) the resulting energy

import numpy as np
import os

def f(x): # We get x in the format: [[x1, x2, ... , xN]]
    x = x[0]
    path = "/wrk/vparkkin/boss_user/C60/"   # <- EDIT 0

    # Write variables x into file
    f = open(path + "C60_input.dat", 'w')   # <- EDIT 1
    for i in range(len(x)):
        f.write(str(x[i]) + '\n')
    f.close()

    # Run with variables x
    os.system(path + "run_aims_ab.sh C60")  # <- EDIT 2

    # Read result
    f = open(path + "energy.dat", 'r')      # <- EDIT 3
    l = f.readline()
    f.close()

    return(float(l)) # ... and it returns the energy!


