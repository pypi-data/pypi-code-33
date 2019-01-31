#!/usr/bin/env python
import os
from optparse import OptionParser
from pathlib import Path

from chi1chi2.input.input_preparator import Input
from chi1chi2.utils.constants import XYZ_EXTENSION

usage = """
%prog [options]
this script prepares Lorentz tensor and charges for property calculations

required input:
- input file

default output:
- Lorentz tensor input (for the fortran program 'lorentz'; folder lorentz/)
- charge generation input (for the fortran program 'charge_generator'; folder charge/)
- individual molecule geometries (folder geom/)
- unit cell content geometry (folder geom/)
"""
parser = OptionParser(usage=usage)

parser.add_option("-i", "--input-file", dest="input_file", help="input file", action="store", type="string",
                  default=None)
parser.add_option("-r", "--radius", dest="radius_cutoff", help="input file", action="store", type="float",
                  default="100.")

(options, args) = parser.parse_args()

LORENTZ_DIR = "lorentz"
CHARGE_DIR = "charge"


def run():
    if options.input_file is None:
        parser.error("No input file given, provide input file")
    cwd = Path.cwd()

    inp = Input.from_file(options.input_file)

    # prepare Lorentz tensor input
    if not os.path.exists(LORENTZ_DIR):
        os.mkdir(str(cwd / LORENTZ_DIR))
    lorentz_inp_location = cwd / LORENTZ_DIR / "lorentz.inp"
    with open(str(lorentz_inp_location), 'w') as f:
        f.write(inp.for_lorentz())
        print(f"{lorentz_inp_location.relative_to(cwd)} file for Lorentz tensor calculations written")

    # prepare charges input
    charge_dir = cwd / CHARGE_DIR
    if not os.path.exists(charge_dir):
        os.mkdir(str(charge_dir))
    for i, chg_inp in enumerate(inp.for_charge_generation(r_cut=float(options.radius_cutoff))):
        charge_inp_location = charge_dir / ("chg" + str(i + 1) + ".inp")
        with open(str(charge_inp_location), 'w') as f:
            f.write(chg_inp)
            print(f"{charge_inp_location.relative_to(cwd)} file for charge generation calculations written")

    # write geometries of individual molecules
    for i, fra_molecule in enumerate(inp.fra_molecules):
        with open("o" + str(i + 1) + XYZ_EXTENSION, 'w') as f:
            f.write(str(fra_molecule.to_xyz_molecule()))
            print(f"{f.name} xyz for molecule {i + 1} written")
            print(f"charge of molecule {i + 1}: {fra_molecule.get_charge():.2f}")

    # write of the generated unit cell geometry
    with open("uc.xyz", 'w') as f:
        f.write(str(inp.get_fra_supermolecule(inp.flags).to_xyz_molecule()))
        print(f"{f.name} xyz for generated unit cell written")


if __name__ == '__main__':
    run()
