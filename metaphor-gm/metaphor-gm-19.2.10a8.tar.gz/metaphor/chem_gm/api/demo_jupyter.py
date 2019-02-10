#!python
# -*- coding: ISO-8859-1 -*-

import os, sys
fil = os.path.abspath(__file__)
ppath = os.path.dirname(os.path.dirname(os.path.dirname(fil)))
if not ppath in sys.path:
    sys.path.append(ppath)

from chem_gm.api import gm_apidemo
def run(argv=[]):
    
    gm_apidemo.run(argv)

if __name__ == "__main__":
    run()